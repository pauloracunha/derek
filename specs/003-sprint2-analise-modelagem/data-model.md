# Data Model: Sprint 2 — Análise de Rede e Modelagem

As entidades `Place`, `LocationCandidate`, `CooccurrenceEdge`, `Community`, `LinkCandidate` e `Source` já estão definidas em `specs/001-atlas-atos/data-model.md` — este documento não as redefine, só detalha os campos que esta sprint efetivamente calcula e onde antes só havia a intenção de contrato.

## CooccurrenceEdge (implementação — já definida em `001-atlas-atos/data-model.md`)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `source` / `target` | place_id | derivado | Par de lugares que coocorrem em ≥1 capítulo de `places.json` (Sprint 1). Não-direcionado. |
| `weight` | int | derivado | Número de capítulos em que os dois lugares coocorrem. |
| `chapters` | int[] | derivado | Lista dos capítulos de coocorrência. |

## TopologicalMetrics (por nó do grafo, campo de `graph.json.nodes[]`)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `degree` | int | derivado (`networkx`) | Nunca varia entre execuções de Monte Carlo (Constitution VI, FR-004). |
| `weighted_degree` | int | derivado | Soma dos pesos das arestas do lugar. |
| `betweenness` | float | derivado | Intermediação — mesma invariância acima. |

## DistanceMetricSimulation (`uncertainty.json`, campo `metrics{}` — já contratado em `001`)

**Só 4 métricas são escalares de rede** — centralidade geográfica é um ranking por lugar, não um escalar (grill 2026-08-11 Q1; corrigido em `001-atlas-atos/contracts/uncertainty.schema.json` e `research.md`).

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| métrica (chave) | string | derivado | Uma das 4: `total_network_length_km`, `mean_edge_distance_km`, `convex_hull_area_km2`, `narrative_itinerary_length_km`. Nunca inclui métrica topológica (FR-003/FR-004) nem centralidade (é ranking, ver `PlaceRankStability` abaixo). |
| `mean` / `ci_low` / `ci_high` | float | derivado (Monte Carlo, N=1000, seed fixa) | Percentis 2.5/97.5 do IC 95%. |
| `deterministic` | float | derivado | Valor usando só o candidato de maior `probability` por lugar — nunca o candidato de maior `score` bruto (que pode divergir sob score negativo, ADR 0003). |

Itinerário narrativo (`narrative_itinerary_length_km`) é calculado sobre a sequência de `Verse` revisitando lugares (ADR 0002), não sobre a lista deduplicada de `Place`.

## PlaceRankStability (`uncertainty.json`, campo `place_rank_stability[]` — já contratado em `001`)

Destino real da centralidade geográfica: um ranking por lugar (distância ao centroide ponderado da rede), cuja estabilidade é medida através das 1000 simulações.

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `place_id` | place_id | derivado | — |
| `modal_rank` | int | derivado | Posição mais frequente do lugar no ranking de centralidade, entre as 1000 simulações. |
| `rank_ci` | [int, int] | derivado | Intervalo de posições (não IC estatístico clássico — faixa de ranks observada). |

## Community (implementação — já definida em `001-atlas-atos/data-model.md`)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `community_id` | int | derivado (Louvain) | — |
| `place_ids` | place_id[] | derivado | — |
| `is_connected` | boolean | derivado | Verificação de conectividade pós-Louvain (FR-008) — Louvain pode gerar comunidade internamente desconexa. |

## ReferencePartition (não exportada — usada só no cálculo de NMI/ARI)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `block` | string | constante do projeto | `jerusalem` (caps. 1-7) \| `judeia_samaria` (caps. 8-12) \| `missao_gentios` (caps. 13-28) |
| `chapters` | int[] | constante | Faixa de capítulos de cada bloco. |

## CommunityComparisonResult (artefato de relatório, `docs/community-comparison.md` — não é contrato de UI)

| Campo | Tipo | Origem/Derivado | Regra |
|---|---|---|---|
| `nmi` | float [0,1] | derivado (`sklearn.metrics.normalized_mutual_info_score`) | — |
| `ari` | float [-1,1] | derivado (`sklearn.metrics.adjusted_rand_score`) | ARI pode ser negativo (concordância pior que acaso) — reportar como está (Constitution VI). |
| `disconnected_communities` | int | derivado | Contagem de comunidades com `is_connected=false` — nunca omitido. |

## LinkCandidate (implementação — já definida em `001-atlas-atos/data-model.md`)

Campos já contratados (`from_verse`, `to_verse`, `score`, `in_catalog`, `model`, `negative_sampling`). Esta sprint adiciona a regra de exclusão:

**Regra nova**: pares de `cross-references.txt` com `Votes < 0` (voto líquido negativo — rejeição ativa) são excluídos do conjunto de arestas positivas antes de qualquer split treino/teste ou avaliação. Pares com `Votes = 0` permanecem incluídos (research.md item 1; FR-014; grill 2026-08-11 Q2).

## Relacionamentos

```
Place (001) --coocorrência--> CooccurrenceEdge --agrega--> TopologicalMetrics
CooccurrenceEdge --amostra Monte Carlo--> DistanceMetricSimulation (usa LocationCandidate.lon/lat de 001)
CooccurrenceEdge --Louvain--> Community --compara--> ReferencePartition --produz--> CommunityComparisonResult
cross-references.txt (filtrado: Votes >= 0) --ego raio 1 de Atos--> grafo de referências --6 modelos x 2 amostragens--> LinkCandidate
```

## Invariantes de validação (mapeadas para `tests/`)

1. `degree`/`weighted_degree`/`betweenness` de um lugar são idênticos antes e depois de rodar a simulação de Monte Carlo — `test_topology_unaffected.py` (FR-004, Constitution VI).
2. Toda `Community` com `is_connected=false` está de fato desconexa quando verificada por busca em largura dentro do subgrafo induzido — `test_community_connectivity.py` (FR-008).
3. Duas execuções de `s05_uncertainty.py` com a mesma seed produzem `uncertainty.json` byte-idêntico — `test_montecarlo_seed_reproducibility.py` (ADR 0001).
4. Todo modelo em `linkpred.json.results[]` tem exatamente uma entrada com `negative_sampling="random"` e uma com `negative_sampling="distance_matched"` — `test_negative_sampling_both_reported.py` (FR-013).
5. Nenhum par com `Votes < 0` do catálogo original aparece como aresta positiva em `linkpred.json` — teste dedicado ou incluído em `test_negative_sampling_both_reported.py` (FR-014).
