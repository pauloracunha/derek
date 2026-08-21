import { create } from 'zustand'
import type { Graph, Place } from '../services/dataLoader'

export interface ChapterRange {
  from: number
  to: number
}

interface AtlasState {
  places: Place[]
  setPlaces: (places: Place[]) => void

  graph: Graph | null
  setGraph: (graph: Graph) => void

  selectedPlaceId: string | null
  selectPlace: (placeId: string | null) => void

  // Faixa de capítulos: null = sem filtro (mostra tudo). Compartilhada por Map e
  // NetworkGraph — spec.md US3 Acceptance Scenario 3 (grill 2026-08-02, Q6).
  chapterRange: ChapterRange | null
  setChapterRange: (range: ChapterRange | null) => void
}

export const useAtlasStore = create<AtlasState>((set) => ({
  places: [],
  setPlaces: (places) => set({ places }),

  graph: null,
  setGraph: (graph) => set({ graph }),

  selectedPlaceId: null,
  selectPlace: (placeId) => set({ selectedPlaceId: placeId }),

  chapterRange: null,
  setChapterRange: (range) => set({ chapterRange: range }),
}))

export function placeInChapterRange(place: Place, range: ChapterRange | null): boolean {
  if (range === null) return true
  return place.chapters.some((c) => c >= range.from && c <= range.to)
}
