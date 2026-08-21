import { render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import UnlocatablePanel from '../../src/components/UnlocatablePanel'
import { useAtlasStore } from '../../src/state/store'
import type { Place } from '../../src/services/dataLoader'

function makePlace(overrides: Partial<Place>): Place {
  return {
    place_id: 'p1',
    name: 'Lugar',
    slug: 'lugar',
    type: 'city',
    is_locatable: true,
    special_reason: null,
    verses: [],
    mention_count: 1,
    chapters: [1],
    candidates: [],
    candidate_count: 0,
    dispersion_index: 0,
    sources: [],
    ...overrides,
  }
}

// Regressão do Princípio II (CLAUDE.md): 100% dos lugares is_locatable === false devem
// aparecer, cada um com razão explícita — nunca descartados silenciosamente.
describe('UnlocatablePanel', () => {
  beforeEach(() => {
    useAtlasStore.setState({
      places: [
        makePlace({ place_id: 'a', name: 'Localizável', is_locatable: true }),
        makePlace({ place_id: 'b', name: 'Desconhecido', is_locatable: false, special_reason: 'unknown_place' }),
        makePlace({ place_id: 'c', name: 'Simbólico', is_locatable: false, special_reason: 'nonspecific_place' }),
        makePlace({ place_id: 'd', name: 'Múltiplos locais', is_locatable: false, special_reason: 'multiple_locations' }),
      ],
    })
  })

  afterEach(() => {
    useAtlasStore.setState({ places: [] })
  })

  it('lista exatamente o número de lugares não localizáveis, nem a mais nem a menos', () => {
    render(<UnlocatablePanel />)
    const expectedCount = useAtlasStore.getState().places.filter((p) => !p.is_locatable).length
    expect(expectedCount).toBe(3)
    expect(screen.getByText(/Lugares sem localização conhecida \(3\)/)).toBeInTheDocument()
    expect(screen.queryByText('Localizável')).not.toBeInTheDocument()
  })

  it('cada lugar não localizável exibe uma razão explícita e legível', () => {
    render(<UnlocatablePanel />)
    expect(screen.getByText('Desconhecido')).toBeInTheDocument()
    expect(screen.getByText(/Localização geográfica desconhecida/)).toBeInTheDocument()
    expect(screen.getByText(/Referência simbólica ou profética/)).toBeInTheDocument()
    expect(screen.getByText(/Refere-se a múltiplos locais/)).toBeInTheDocument()
  })
})
