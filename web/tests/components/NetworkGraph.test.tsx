import { describe, expect, it } from 'vitest'
import { edgeInChapterRange } from '../../src/components/NetworkGraph'
import type { GraphEdge } from '../../src/services/dataLoader'

function makeEdge(chapters: number[]): GraphEdge {
  return { source: 'a', target: 'b', weight: 1, chapters }
}

describe('edgeInChapterRange', () => {
  it('sem filtro (range null), toda aresta é visível', () => {
    expect(edgeInChapterRange(makeEdge([5]), null)).toBe(true)
  })

  it('aresta com capítulo dentro da faixa é visível', () => {
    expect(edgeInChapterRange(makeEdge([3, 7]), { from: 1, to: 8 })).toBe(true)
  })

  it('aresta sem nenhum capítulo dentro da faixa não é visível', () => {
    expect(edgeInChapterRange(makeEdge([20]), { from: 1, to: 8 })).toBe(false)
  })

  it('aresta com capítulo na borda da faixa é visível (inclusivo)', () => {
    expect(edgeInChapterRange(makeEdge([8]), { from: 1, to: 8 })).toBe(true)
  })
})
