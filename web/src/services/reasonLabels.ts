import type { SpecialReason } from './dataLoader'

// Traduz o motivo técnico de não-localização para texto legível — princípio não
// negociável 2 (CLAUDE.md): lugar sem localização nunca desaparece silenciosamente,
// sempre com razão explícita.
const REASON_LABELS: Record<Exclude<SpecialReason, null>, string> = {
  unknown_place: 'Localização geográfica desconhecida.',
  nonspecific_place: 'Referência simbólica ou profética, sem localização geográfica específica.',
  multiple_locations: 'Refere-se a múltiplos locais ao mesmo tempo, sem um ponto único válido.',
  no_candidates_resolved: 'Nenhum candidato de localização pôde ser resolvido a partir dos dados de origem.',
}

export function describeUnlocatableReason(reason: SpecialReason): string {
  if (reason === null) {
    return 'Razão não especificada nos dados de origem.'
  }
  return REASON_LABELS[reason]
}
