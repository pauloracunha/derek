// Tipos espelham specs/001-atlas-atos/contracts/*.schema.json — ver docs/data-contracts.md
// para o racional de cada campo (score pode ser negativo, sources é por Lugar não por
// candidato, lonlat_type pode ser null).

export type LonLatType = 'point' | 'center' | 'representative point' | 'settlement' | null

export interface LocationCandidate {
  modern_id: string
  name: string
  lon: number
  lat: number
  score: number
  probability: number
  lonlat_type: LonLatType
  // null = mismatch ontológico ponto-vs-área (região/ilha/via), não incerteza posicional.
  // Ver docs/data-contracts.md.
  precision_meters: number | null
}

export type SpecialReason =
  | 'unknown_place'
  | 'nonspecific_place'
  | 'multiple_locations'
  | 'no_candidates_resolved'
  | null

export interface Source {
  source_id: string
  citation: string
  locator: string | null
}

export interface Place {
  place_id: string
  name: string
  slug: string
  type: string
  is_locatable: boolean
  special_reason: SpecialReason
  verses: string[]
  mention_count: number
  chapters: number[]
  candidates: LocationCandidate[]
  candidate_count: number
  dispersion_index: number
  sources: Source[]
}

// Espelha specs/001-atlas-atos/contracts/graph.schema.json — grafo de coocorrência por
// capítulo. Métricas topológicas nunca variam com incerteza de localização (Constitution VI).
export interface GraphNode {
  place_id: string
  degree: number
  weighted_degree: number
  betweenness: number
  community: number
  // false sinaliza comunidade internamente desconexa (FR-011/FR-006) — nunca omitido.
  community_is_connected?: boolean
}

export interface GraphEdge {
  source: string
  target: string
  weight: number
  chapters: number[]
}

export interface Graph {
  unit: 'chapter'
  nodes: GraphNode[]
  edges: GraphEdge[]
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) {
    throw new Error(`Falha ao carregar ${path}: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export function loadPlaces(): Promise<Place[]> {
  return fetchJson<Place[]>('/data/places.json')
}

export function loadGraph(): Promise<Graph> {
  return fetchJson<Graph>('/data/graph.json')
}
