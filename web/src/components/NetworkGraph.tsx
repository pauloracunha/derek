import { useMemo } from 'react'
import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from 'd3-force'
import type { Graph, GraphEdge, GraphNode } from '../services/dataLoader'
import { useAtlasStore } from '../state/store'

const WIDTH = 480
const HEIGHT = 360
const COMMUNITY_COLORS = ['#7a5cff', '#ff6b6b', '#4ecdc4', '#ffd93d', '#6bc26b', '#c77dff', '#ff9f1c']

interface SimNode extends SimulationNodeDatum, GraphNode {}
interface SimLink extends SimulationLinkDatum<SimNode> {
  weight: number
}

export function edgeInChapterRange(edge: GraphEdge, range: { from: number; to: number } | null): boolean {
  if (range === null) return true
  return edge.chapters.some((c) => c >= range.from && c <= range.to)
}

function communityColor(community: number): string {
  return COMMUNITY_COLORS[community % COMMUNITY_COLORS.length]
}

// Layout: força padrão (charge/link/collide) + força customizada que atrai cada nó a um
// centroide fixo por comunidade, dispostos em círculo — técnica de cluster sem lib nova
// (research.md #3, CONTEXT.md, grill 2026-08-19 Q4).
function layoutGraph(graph: Graph): { nodes: SimNode[]; links: SimLink[] } {
  const communities = Array.from(new Set(graph.nodes.map((n) => n.community))).sort((a, b) => a - b)
  const centroids = new Map<number, { x: number; y: number }>()
  communities.forEach((community, i) => {
    const angle = (2 * Math.PI * i) / communities.length
    centroids.set(community, {
      x: WIDTH / 2 + (WIDTH / 3) * Math.cos(angle),
      y: HEIGHT / 2 + (HEIGHT / 3) * Math.sin(angle),
    })
  })

  const nodes: SimNode[] = graph.nodes.map((n) => ({ ...n }))
  const nodeById = new Map(nodes.map((n) => [n.place_id, n]))
  const links: SimLink[] = graph.edges
    .filter((e) => nodeById.has(e.source) && nodeById.has(e.target))
    .map((e) => ({ source: e.source, target: e.target, weight: e.weight }))

  const simulation = forceSimulation(nodes)
    .force('charge', forceManyBody().strength(-30))
    .force('link', forceLink<SimNode, SimLink>(links).id((d) => d.place_id).distance(24))
    .force('collide', forceCollide(8))
    .force('clusterX', forceX<SimNode>((d) => centroids.get(d.community)?.x ?? WIDTH / 2).strength(0.15))
    .force('clusterY', forceY<SimNode>((d) => centroids.get(d.community)?.y ?? HEIGHT / 2).strength(0.15))
    .stop()

  for (let i = 0; i < 300; i++) simulation.tick()

  return { nodes, links }
}

export default function NetworkGraph() {
  const graph = useAtlasStore((s) => s.graph)
  const chapterRange = useAtlasStore((s) => s.chapterRange)
  const selectPlace = useAtlasStore((s) => s.selectPlace)
  const selectedPlaceId = useAtlasStore((s) => s.selectedPlaceId)

  const layout = useMemo(() => (graph ? layoutGraph(graph) : null), [graph])

  const visibleLinks = useMemo(() => {
    if (!layout || !graph) return []
    return layout.links.filter((_l, i) => edgeInChapterRange(graph.edges[i], chapterRange))
  }, [layout, graph, chapterRange])

  if (!graph || !layout) {
    return <div className="network-graph network-graph--empty">Carregando grafo…</div>
  }

  const nodeById = new Map(layout.nodes.map((n) => [n.place_id, n]))

  return (
    <svg className="network-graph" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} width="100%" height="100%">
      <g className="network-graph__links">
        {visibleLinks.map((l, i) => {
          const source = typeof l.source === 'object' ? l.source : nodeById.get(l.source as unknown as string)
          const target = typeof l.target === 'object' ? l.target : nodeById.get(l.target as unknown as string)
          if (!source || !target) return null
          return (
            <line
              key={i}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="#ccc"
              strokeWidth={1}
            />
          )
        })}
      </g>
      <g className="network-graph__nodes">
        {layout.nodes.map((n) => (
          <circle
            key={n.place_id}
            cx={n.x}
            cy={n.y}
            r={n.place_id === selectedPlaceId ? 6 : 4}
            fill={communityColor(n.community)}
            stroke={n.community_is_connected === false ? '#c00' : '#333'}
            strokeWidth={n.community_is_connected === false ? 2 : 0.5}
            strokeDasharray={n.community_is_connected === false ? '2,2' : undefined}
            style={{ cursor: 'pointer' }}
            onClick={() => selectPlace(n.place_id)}
          >
            <title>
              {n.place_id}
              {n.community_is_connected === false ? ' — comunidade internamente desconexa' : ''}
            </title>
          </circle>
        ))}
      </g>
    </svg>
  )
}
