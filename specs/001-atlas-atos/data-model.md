# Data Model: Atlas de Atos

Entidades derivadas do spec (`Key Entities`) e do formato de origem **verificado nos dados reais** (`docs/data-contracts.md`, inspeção de 2026-08-02) — não do exemplo truncado de `definitions.md` §2, que se mostrou incompleto em pontos importantes (score negativo, relação com Fonte, `lonlat_type` nulo). Campos marcados **(origem)** vêm diretamente do dataset bruto; campos marcados **(derivado)** são calculados pelo pipeline.

## Place (Lugar)

Representa um lugar mencionado no texto de Atos.

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `place_id` | string (7 chars, inicia com `a`) | origem (`ancient.id`) | Chave primária. Único em `ancient.jsonl`. |
| `name` | string | origem (`friendly_id`) | Único dentro de `ancient.jsonl`, **não** no dataset inteiro — nunca usar como chave de join fora deste arquivo (Constitution / armadilha §2.4). |
| `slug` | string | origem (`url_slug`) | — |
| `type` | string | origem (`type`) | ~40 valores possíveis (ex. `settlement`). |
| `is_locatable` | boolean | derivado | `true` sempre que `candidates` (via `modern_associations`) é não-vazio — **mesmo que uma identificação `special` concorrente diga o contrário** (ver `docs/adr/0004`). Só é `false` quando não há candidato real algum. |
| `special_reason` | string \| null | derivado | Preenchido apenas quando `is_locatable = false` (i.e. `candidates` vazio). Prioridade: (1) razão "mantida" (`unknown_place`\|`nonspecific_place`\|`multiple_locations`) de qualquer identificação `special`, mesmo que outra identificação seja "excludente"; (2) se só houver razão excludente (`not_a_place`\|`not_a_proper_name`\|`recursive`) e nenhuma mantida, o `Place` é excluído do catálogo inteiro, não gera linha de saída; (3) se não houver identificação `special` alguma e ainda assim `candidates` vazio (caso raro), usar razão sintética `"no_candidates_resolved"` — nunca deixar `special_reason` nulo quando `is_locatable=false`. Regra completa e contagens reais em `docs/adr/0004-classificacao-locatable-por-candidatos-nao-por-special.md`. |
| `verses` | string[] (sort, BBCCCVVV) | origem (`verses[].sort`), **filtrado** | String, nunca inteiro (Constitution IV). Ordenado ascendente. A origem guarda TODAS as menções bíblicas do lugar (ex. Jerusalém também aparece em Gênesis, Salmos, Apocalipse) — este campo DEVE conter **só** as entradas com `sort` começando em `"44"`. Nunca copiar `verses[]` da origem sem esse filtro (ver CONTEXT.md, termo "Lugar"). |
| `mention_count` | int | derivado | `len(verses)` **já filtrado** a Atos. |
| `chapters` | int[] | derivado | Capítulos distintos extraídos de `verses[].sort` (`sort[2:5]`, 3 dígitos — BBCCCVVV, não "posições 5-6") **já filtrado** a Atos — nunca inclui capítulo de outro livro. |
| `candidates` | LocationCandidate[] | derivado | Ver abaixo. **Nunca truncado a um único item quando a origem tem mais de um** (Constitution I / FR-002). |
| `candidate_count` | int | derivado | `len(candidates)`. DEVE ser igual à contagem de chaves em `modern_associations` da origem (teste "Preservação de candidatos", §10). |
| `dispersion_index` | float [0,1] | derivado | Métrica de dispersão da distribuição de probabilidade dos candidatos (ex. entropia normalizada); 0 = candidato único ou totalmente dominante, próximo de 1 = candidatos igualmente prováveis. Consumido pela UI para ordenar/destacar lugares mais disputados (US1). Nome antigo `uncertainty_index` — renomeado para não colidir com o termo guarda-chuva "incerteza" (ver CONTEXT.md). |
| `sources` | Source[] | origem (`identification_sources`) | Lista de fontes bibliográficas usadas para identificar este lugar (nível `Place`, não por candidato — ver seção Source abaixo). Pode ser vazia. |

**Filtro de inclusão**: um `Place` entra no conjunto se possuir ao menos um item em `verses` cujo `sort` comece com `"44"` (livro de Atos).

## LocationCandidate (Candidato de Localização)

Um candidato de localização geográfica dentro de `Place.candidates`.

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `modern_id` | string (inicia com `m`) | origem (`modern_associations` key) | — |
| `name` | string | origem (`modern_associations[].name`) | — |
| `lon` | float | origem, via `modern.jsonl`/`resolutions[].lonlat` | `lonlat` de origem é `"longitude,latitude"` — **ordem invertida do senso comum**. Testado contra bbox do Mediterrâneo oriental (lon 20–50) (Constitution III). |
| `lat` | float | idem | Testado contra bbox (lat 25–45). |
| `score` | int | origem (`modern_associations[].score`) | Confiança agregada bruta. **Pode ser negativo ou zero** — é voto líquido da comunidade, não uma confiança sempre-positiva (confirmado em 20,5% dos lugares com múltiplos candidatos; ver `docs/data-contracts.md`). |
| `probability` | float [0,1] | derivado | `max(score,0) / Σ max(score_j,0)` de todos os candidatos do mesmo `Place`; se todos os scores do lugar forem ≤0, usar distribuição uniforme (`1/N`) como fallback. Nunca dividir por Σ negativo/zero sem fallback. Σ de todas as `probability` de um `Place` = 1.0 (±1e-9) (teste "Integridade de probabilidade", §10). Decisão registrada em `docs/adr/0003-normalizacao-score-negativo.md`. |
| `lonlat_type` | string \| null | origem (`resolutions[].lonlat_type`) | `point` \| `center` \| `representative point` \| `settlement` \| `null`. `null` ocorre em ~4% das resoluções reais — tratar como "precisão desconhecida", nunca como erro. Quando `settlement`, indica precisão de área, não ponto exato — sinalizado visualmente (FR-004), nunca tratado como precisão igual a `point`. |
| `precision_meters` | int \| null | origem (`modern.jsonl[].precision.meters`) | Estimativa numérica de quão próxima a coordenada está do lugar pretendido. **Ausente especificamente quando o candidato é uma região/ilha/corpo d'água/via (mismatch ontológico ponto-vs-área), não quando há incerteza posicional genuína** — ver taxonomia em `docs/data-contracts.md`. Nunca inventar um valor quando ausente; `null` é informação (o "tipo Extensão" da taxonomia), não dado faltante a imputar. |

## LocationReason (Motivo de Não-Localização)

Não é uma entidade separada no contrato de saída — é o par `(is_locatable=false, special_reason)` dentro de `Place`. Documentado aqui por clareza semântica, pois é referenciado como conceito próprio no spec.

| `special_reason` | Significado | Tratamento |
|---|---|---|
| `unknown_place` | Localização desconhecida | Mantido, `is_locatable=false` |
| `nonspecific_place` | Lugar simbólico/profético | Mantido, `is_locatable=false` |
| `multiple_locations` | Refere-se a múltiplos locais | Mantido, `is_locatable=false` |
| `no_candidates_resolved` | Sem candidato e sem identificação `special` de origem (caso raro) | Mantido, `is_locatable=false` — razão sintética do pipeline, não existe na origem |
| `not_a_place` / `not_a_proper_name` / `recursive` | Não é de fato um lugar / loop | `Place` inteiro excluído do catálogo (não aparece na saída) — **só quando `candidates` também está vazio**; se houver candidatos reais concorrentes, o lugar é mantido como localizável (ver `docs/adr/0004`) |

## Itinerário Narrativo

Não é uma entidade exportada — é uma sequência derivada usada só pelo cálculo Monte Carlo (`pipeline/s05_uncertainty.py`, métrica "comprimento do itinerário narrativo"). Construída sobre **todas** as menções (`Verse`), ordenadas por `sort`, não sobre a lista deduplicada de `Place`s: um lugar mencionado várias vezes é revisitado no itinerário toda vez que reaparece na leitura (ver `docs/adr/0002-itinerario-narrativo-revisita-lugares.md`). Mesma-lugar-para-mesma-lugar contribui distância zero; retorno após visitar outro lugar contribui distância geodésica cheia.

## Verse (Versículo)

Referência textual a uma menção de lugar.

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `sort` | string (8 chars, BBCCCVVV) | origem | Chave canônica. String, zeros à esquerda significativos (Constitution IV). |
| `osis` | string | origem | Ex. `Acts.1.4`. |
| `chapter` | int | derivado de `sort` | Caracteres 5-6 de `sort`, convertido a inteiro apenas para exibição/filtro — o `sort` original permanece string. |

## CooccurrenceEdge (Conexão de Coocorrência)

Aresta do grafo de lugares.

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `source` | place_id | derivado | — |
| `target` | place_id | derivado | Não-direcionado; `source`/`target` sem ordem semântica. |
| `weight` | int | derivado | Número de capítulos em que os dois lugares coocorrem. |
| `chapters` | int[] | derivado | Lista dos capítulos de coocorrência. |

## Community (Comunidade)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `community_id` | int | derivado (Louvain/Leiden) | — |
| `place_ids` | place_id[] | derivado | — |
| `is_connected` | boolean | derivado | Resultado da verificação de conectividade pós-detecção (Louvain pode produzir comunidades desconexas — validação obrigatória, FR-011). |

Comparação quantitativa (NMI/ARI) contra a partição de referência (caps. 1–7 Jerusalém; 8–12 Judeia e Samaria; 13–28 missão aos gentios) é calculada pelo pipeline e vai para o relatório escrito — **não** faz parte do contrato `graph.json` consumido pela UI (decisão da sessão de clarificação 2026-08-02).

## LinkCandidate (Candidato a Nova Conexão)

Usado apenas no artefato de relatório (`linkpred.json`), não consumido pela UI interativa.

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `from_verse` | string (OSIS) | derivado | Sempre em Atos. |
| `to_verse` | string (OSIS) | derivado | Qualquer lugar do cânon. |
| `score` | float | derivado (modelo) | Saída do melhor modelo. |
| `in_catalog` | boolean | derivado | `true` se já existe como referência cruzada conhecida (não é de fato um "candidato novo"). |
| `model` | string | derivado | Qual dos 6 modelos gerou o score reportado. |
| `negative_sampling` | string | derivado | `random` \| `distance_matched` — qual estratégia foi usada para a avaliação associada a este modelo. |

## Source (Fonte)

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `source_id` | string | origem (`source.jsonl.id`) | — |
| `citation` | string | derivado | `source.jsonl.display_name` (já formatado, ex. `"Abel, Géographie de la Palestine (1967)"`). |
| `locator` | string \| null | origem (`identification_sources[source_id]`) | Localizador opcional dentro da fonte: `title`, `page`, `map` ou `table` (o que existir). Pode ser objeto vazio na origem — nesse caso `locator=null`. |

**Confirmado por inspeção real** (`docs/data-contracts.md`): a Fonte é relacionada ao **`Place` inteiro**, não a um `LocationCandidate` específico — join via `Place.identification_sources` (chaves = `source.jsonl.id`). Não existe, nos dados reais, um vínculo Fonte↔candidato individual. `PlaceDetail.tsx` deve exibir a lista de fontes do lugar de forma agregada (não por candidato).

## Relacionamentos

```
Place 1---N LocationCandidate
Place 1---N Verse (via verses[])
Place N---N Place (via CooccurrenceEdge, quando coocorrem em capítulo)
Place N---1 Community (quando is_locatable ou não — comunidade é sobre coocorrência textual, não localização)
Place N---N Source (via identification_sources — proveniência do lugar, não do candidato individual)
LinkCandidate: Verse (Atos) ---> Verse (qualquer livro)
```

## Invariantes de validação (mapeadas para `tests/`)

1. Toda `LocationCandidate.lon` ∈ [10, 48] e `.lat` ∈ [15, 43] (bbox real do alcance de Atos — Jerusalém a Roma, incl. Malta e Etiópia; corrigido do bbox "Mediterrâneo oriental" original por dados reais, ver `docs/adr/0005`) — `test_coordinates_order.py`.
2. Σ `probability` de candidatos de um `Place` = 1.0 ± 1e-9 — `test_probability_integrity.py`.
3. `Place.candidate_count` = contagem de chaves em `modern_associations` da origem — `test_candidate_preservation.py`.
4. Nenhum `Place` com >1 candidato na origem aparece com exatamente 1 candidato na saída — `test_no_candidate_collapse.py`.
5. `Verse.sort` tem exatamente 8 caracteres e é string — `test_canonical_key.py`.
6. Duas execuções do pipeline com a mesma seed produzem `data/processed/*.json` byte-idênticos — `test_reproducibility.py`.
7. Todo `sort` em `Place.verses` começa com `"44"`; nenhum `chapters`/`mention_count` reflete menção de outro livro — cobrir em `test_candidate_preservation.py` ou teste dedicado.
