import { formatVerseRef } from '../services/dataLoader'
import { useAtlasStore } from '../state/store'

export default function PlaceDetail() {
  const places = useAtlasStore((s) => s.places)
  const selectedPlaceId = useAtlasStore((s) => s.selectedPlaceId)

  const place = selectedPlaceId ? places.find((p) => p.place_id === selectedPlaceId) : null

  if (!place) {
    return <div className="place-detail place-detail--empty">Selecione um lugar no mapa ou no grafo.</div>
  }

  return (
    <div className="place-detail">
      <h2>{place.name}</h2>
      <p className="place-detail__meta">
        Mencionado em: {place.verses.map(formatVerseRef).join(', ')}
      </p>

      <h3>Candidatos de localização ({place.candidate_count})</h3>
      <ul className="place-detail__candidates">
        {place.candidates.map((c) => (
          <li key={c.modern_id}>
            <strong>{c.name}</strong> — probabilidade {(c.probability * 100).toFixed(0)}%
            {c.lonlat_type && c.lonlat_type !== 'point' ? ' (área aproximada)' : ''}
          </li>
        ))}
      </ul>

      {place.sources.length > 0 && (
        <>
          <h3>Fontes</h3>
          <ul className="place-detail__sources">
            {place.sources.map((s) => (
              <li key={s.source_id}>
                {s.citation}
                {s.locator ? ` (${s.locator})` : ''}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
