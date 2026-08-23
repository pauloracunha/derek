// Peso visual: linear com piso mínimo — nenhum candidato de baixa probabilidade fica
// invisível/inclicável (Princípio I; CONTEXT.md § Peso Visual, grill 2026-08-19 Q1).
export function opacityForProbability(probability: number): number {
  return 0.15 + 0.85 * probability
}

export function radiusForProbability(probability: number): number {
  return 4 + 12 * probability
}

// Anel de precisão posicional: escala log contínua sobre precision_meters observado no
// dataset (5m–5000m — três ordens de grandeza, log evita que candidatos de baixa precisão
// dominem visualmente). null = precisão desconhecida, sem anel (nunca inventar valor).
const PRECISION_MIN_M = 5
const PRECISION_MAX_M = 5000
const HALO_MIN_PX = 6
const HALO_MAX_PX = 30

export function haloRadiusForPrecision(precisionMeters: number | null): number | null {
  if (precisionMeters === null || precisionMeters <= 0) return null
  const clamped = Math.min(Math.max(precisionMeters, PRECISION_MIN_M), PRECISION_MAX_M)
  const t = (Math.log10(clamped) - Math.log10(PRECISION_MIN_M)) / (Math.log10(PRECISION_MAX_M) - Math.log10(PRECISION_MIN_M))
  return HALO_MIN_PX + (HALO_MAX_PX - HALO_MIN_PX) * t
}
