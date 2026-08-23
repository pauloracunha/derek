import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import type { LonLatType, Place } from '../services/dataLoader'
import { haloRadiusForPrecision, opacityForProbability, radiusForProbability } from '../services/visualWeight'
import { placeInChapterRange, useAtlasStore } from '../state/store'

// Bbox real de alcance de Atos (Jerusalém a Roma, incluindo Etiópia) — docs/adr/0005.
const ATOS_BBOX: [[number, number], [number, number]] = [
  [10, 15],
  [48, 43],
]

// Forma do marcador codifica lonlat_type — canal independente de opacidade/tamanho
// (probabilidade) e de cor (reservada à Comunidade em NetworkGraph). CONTEXT.md § Forma
// do Marcador, grill Q3.
function isAreaType(lonlatType: LonLatType): boolean {
  return lonlatType === 'center' || lonlatType === 'representative point' || lonlatType === 'settlement'
}

const CANDIDATE_LINK_COLOR = '#7a5cff'

export default function Map() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<maplibregl.Marker[]>([])
  const linkSourceAddedRef = useRef(false)

  // Alguns navegadores/ambientes (GPU desabilitada por sandbox/política) não conseguem
  // criar contexto WebGL nem em fallback — achado real de uso. Sem isso, o mapa quebrava
  // a aplicação inteira; com o fallback, US2/Legend/Footer continuam funcionando.
  const [webglUnsupported, setWebglUnsupported] = useState(false)

  const places = useAtlasStore((s) => s.places)
  const chapterRange = useAtlasStore((s) => s.chapterRange)
  const selectedPlaceId = useAtlasStore((s) => s.selectedPlaceId)
  const selectPlace = useAtlasStore((s) => s.selectPlace)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    try {
      const map = new maplibregl.Map({
        container: containerRef.current,
        style: 'https://demotiles.maplibre.org/style.json',
        bounds: ATOS_BBOX,
      })
      map.on('error', (e) => {
        if (String(e.error?.message ?? '').toLowerCase().includes('webgl')) {
          map.remove()
          mapRef.current = null
          setWebglUnsupported(true)
        }
      })
      mapRef.current = map
    } catch {
      queueMicrotask(() => setWebglUnsupported(true))
      return
    }
    return () => {
      mapRef.current?.remove()
      mapRef.current = null
    }
  }, [])

  // Marcadores: um por candidato de localização de cada lugar localizável e visível na
  // faixa de capítulos atual. Nunca renderiza só o candidato de maior score (Princípio I).
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    const visiblePlaces = places.filter(
      (p: Place) => p.is_locatable && placeInChapterRange(p, chapterRange),
    )

    for (const place of visiblePlaces) {
      for (const candidate of place.candidates) {
        const wrapper = document.createElement('div')
        wrapper.className = 'candidate-marker-wrap'
        wrapper.dataset.placeId = place.place_id
        // Tamanho fixo igual ao marcador (não ao halo): maplibre mede offsetWidth/Height
        // deste elemento raiz para calcular o offset de centralização. Se o halo (maior)
        // influenciasse essa medida, cada marcador desviaria do ponto real por um valor
        // diferente — foi exatamente o bug de "pontos fora do lugar".
        const size = radiusForProbability(candidate.probability) * 2
        wrapper.style.width = `${size}px`
        wrapper.style.height = `${size}px`
        const precisionLabel = candidate.precision_meters === null
          ? 'precisão posicional desconhecida'
          : `precisão posicional ±${candidate.precision_meters}m`
        wrapper.title = `${place.name} — ${candidate.name} (prob. ${(candidate.probability * 100).toFixed(0)}%, ${precisionLabel})`
        wrapper.addEventListener('click', (e) => {
          e.stopPropagation()
          selectPlace(place.place_id)
        })

        const haloRadius = haloRadiusForPrecision(candidate.precision_meters)
        if (haloRadius !== null) {
          const halo = document.createElement('div')
          halo.className = 'candidate-marker-halo'
          const haloSize = haloRadius * 2
          halo.style.width = `${haloSize}px`
          halo.style.height = `${haloSize}px`
          wrapper.appendChild(halo)
        }

        const el = document.createElement('div')
        el.className = isAreaType(candidate.lonlat_type) ? 'candidate-marker candidate-marker--area' : 'candidate-marker candidate-marker--point'
        el.style.width = '100%'
        el.style.height = '100%'
        el.style.opacity = String(opacityForProbability(candidate.probability))
        if (place.place_id === selectedPlaceId) el.classList.add('candidate-marker--selected')
        wrapper.appendChild(el)

        const marker = new maplibregl.Marker({ element: wrapper })
          .setLngLat([candidate.lon, candidate.lat])
          .addTo(map)
        markersRef.current.push(marker)
      }
    }
  }, [places, chapterRange, selectPlace, selectedPlaceId])

  // Vínculo visual entre candidatos do mesmo lugar: linha tracejada + cor compartilhada,
  // só quando esse lugar está selecionado (CONTEXT.md § Vínculo Visual, grill Q2).
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const render = () => {
      const selected = selectedPlaceId ? places.find((p) => p.place_id === selectedPlaceId) : null
      const coords = selected && selected.candidates.length > 1
        ? selected.candidates.map((c) => [c.lon, c.lat] as [number, number])
        : []

      const data = {
        type: 'Feature' as const,
        properties: {},
        geometry: { type: 'LineString' as const, coordinates: coords.length > 1 ? coords : [] },
      }

      const source = map.getSource('candidate-links') as maplibregl.GeoJSONSource | undefined
      if (source) {
        source.setData(data)
        return
      }

      if (!linkSourceAddedRef.current) {
        map.addSource('candidate-links', { type: 'geojson', data })
        map.addLayer({
          id: 'candidate-links-layer',
          type: 'line',
          source: 'candidate-links',
          paint: {
            'line-color': CANDIDATE_LINK_COLOR,
            'line-width': 2,
            'line-dasharray': [2, 2],
          },
        })
        linkSourceAddedRef.current = true
      }
    }

    if (map.isStyleLoaded()) {
      render()
    } else {
      map.once('load', render)
    }
  }, [selectedPlaceId, places])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    const onBackgroundClick = () => selectPlace(null)
    map.on('click', onBackgroundClick)
    return () => {
      map.off('click', onBackgroundClick)
    }
  }, [selectPlace])

  if (webglUnsupported) {
    const visiblePlaces = places.filter(
      (p: Place) => p.is_locatable && placeInChapterRange(p, chapterRange),
    )
    return (
      <div className="map-fallback" role="status">
        <p>
          Este navegador não consegue exibir o mapa interativo (WebGL indisponível). A
          lista abaixo mostra os mesmos lugares e candidatos de localização, sem perder a
          incerteza — nenhum candidato é omitido.
        </p>
        <ul>
          {visiblePlaces.map((place) => (
            <li key={place.place_id}>
              <button type="button" onClick={() => selectPlace(place.place_id)}>
                {place.name}
              </button>
              <ul>
                {place.candidates.map((c) => (
                  <li key={c.modern_id}>
                    {c.name} — probabilidade {(c.probability * 100).toFixed(0)}%
                    {isAreaType(c.lonlat_type) ? ' (área aproximada)' : ''}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    )
  }

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}
