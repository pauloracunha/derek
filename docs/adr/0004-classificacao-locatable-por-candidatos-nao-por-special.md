---
status: accepted
---

# `is_locatable` é decidido por `candidates` não-vazio, não pela presença de uma identificação `special`

`definitions.md` §2.3 e `data-model.md` (antes desta correção) assumiam que cada `Place` tem uma classificação única: normal, ou `special` com um motivo (`unknown_place`, `not_a_place`, etc.), e que `not_a_place`/`not_a_proper_name`/`recursive` significam "excluir o lugar inteiro".

A inspeção real de `ancient.jsonl` mostrou que um `Place` pode ter **múltiplas identificações concorrentes**, algumas `special` e outras não, ao mesmo tempo:

- 123 lugares têm uma identificação `special` **e** `modern_associations` não-vazio simultaneamente
- Dessas, **120 têm especificamente `special ∈ {not_a_place, not_a_proper_name, recursive}` junto com candidatos reais** — ou seja, um estudioso/fonte identificou o termo como não sendo um lugar, mas outro estudioso/fonte, na mesma entrada, propôs um lugar real com coordenadas

Excluir esses 120 lugares porque *uma* identificação diz "não é um lugar" jogaria fora candidatos de localização reais e válidos — exatamente a falha que o projeto existe para corrigir (Constitution I), só que aplicada à existência do lugar em vez de à sua localização.

Decidimos: `is_locatable` e a exclusão do catálogo são decididos por **`candidates` (via `modern_associations`), não pela presença de uma identificação `special`**:

1. `modern_associations` não-vazio → `is_locatable=true`, candidatos normalizados exibidos — **mesmo que exista uma identificação `special` concorrente** dizendo o contrário.
2. `modern_associations` vazio, com identificação `special` de razão "mantida" (`unknown_place`\|`nonspecific_place`\|`multiple_locations`) → `is_locatable=false`, `special_reason` = essa razão.
3. `modern_associations` vazio, com identificação `special` de razão "excludente" (`not_a_place`\|`not_a_proper_name`\|`recursive`) e SEM razão "mantida" concorrente → `Place` excluído do catálogo.
4. `modern_associations` vazio, com AMBOS os tipos de razão presentes (caso raro, 1 ocorrência no dataset) → prevalece a razão "mantida" (nunca desaparecer é mais forte que excluir — Constitution II).
5. `modern_associations` vazio e nenhuma identificação `special` (1 ocorrência no dataset — ver `docs/adr/0003`... não, ver sessão de grill Q3) → `is_locatable=false`, `special_reason="no_candidates_resolved"` (razão sintética, nunca deixar `special_reason` nulo com `is_locatable=false`).

Alternativa rejeitada: excluir o lugar sempre que qualquer identificação for `special` de tipo excludente, ignorando candidatos concorrentes. Rejeitada por descartar dado geográfico real e válido — o comportamento documentado em `definitions.md` só fazia sentido sob a suposição (falsa nos dados reais) de que cada lugar tem uma única identificação.
