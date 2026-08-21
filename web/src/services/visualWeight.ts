// Peso visual: linear com piso mínimo — nenhum candidato de baixa probabilidade fica
// invisível/inclicável (Princípio I; CONTEXT.md § Peso Visual, grill 2026-08-19 Q1).
export function opacityForProbability(probability: number): number {
  return 0.15 + 0.85 * probability
}

export function radiusForProbability(probability: number): number {
  return 4 + 12 * probability
}
