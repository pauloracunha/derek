import { describe, expect, it } from 'vitest'
import { opacityForProbability, radiusForProbability } from '../../src/services/visualWeight'

// Regressão do Princípio I (CLAUDE.md): nenhum candidato de localização, mesmo de
// probabilidade muito baixa, pode ficar visualmente invisível ou inclicável (opacidade/
// raio no chão). maplibre-gl exige WebGL real (indisponível em jsdom), então o
// comportamento visual central — o mapeamento probability → peso visual — é testado
// diretamente aqui; ver CONTEXT.md § Peso Visual (grill 2026-08-19 Q1).
describe('peso visual de candidatos de localização', () => {
  it('nunca deixa opacidade abaixo do piso mínimo, mesmo com probabilidade 0', () => {
    expect(opacityForProbability(0)).toBeCloseTo(0.15)
    expect(opacityForProbability(0)).toBeGreaterThan(0)
  })

  it('nunca deixa raio abaixo do piso mínimo, mesmo com probabilidade 0', () => {
    expect(radiusForProbability(0)).toBeCloseTo(4)
    expect(radiusForProbability(0)).toBeGreaterThan(0)
  })

  it('atinge o teto quando probabilidade é 1', () => {
    expect(opacityForProbability(1)).toBeCloseTo(1)
    expect(radiusForProbability(1)).toBeCloseTo(16)
  })

  it('é monotônico crescente em probability', () => {
    expect(opacityForProbability(0.8)).toBeGreaterThan(opacityForProbability(0.2))
    expect(radiusForProbability(0.8)).toBeGreaterThan(radiusForProbability(0.2))
  })
})
