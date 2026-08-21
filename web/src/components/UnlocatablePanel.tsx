import { useAtlasStore } from '../state/store'
import { describeUnlocatableReason } from '../services/reasonLabels'

// Princípio não negociável 2 (CLAUDE.md): NUNCA descartar silenciosamente lugares
// não localizáveis. Todo place com is_locatable === false aparece aqui, nunca no mapa
// (Map.tsx filtra por is_locatable) — ver spec.md US2 / FR-004.
export default function UnlocatablePanel() {
  const places = useAtlasStore((s) => s.places)
  const unlocatable = places.filter((p) => !p.is_locatable)

  return (
    <div className="unlocatable-panel">
      <h2>Lugares sem localização conhecida ({unlocatable.length})</h2>
      {unlocatable.length === 0 ? (
        <p>Nenhum lugar sem localização conhecida neste conjunto de dados.</p>
      ) : (
        <ul>
          {unlocatable.map((p) => (
            <li key={p.place_id}>
              <strong>{p.name}</strong>
              <p>{describeUnlocatableReason(p.special_reason)}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
