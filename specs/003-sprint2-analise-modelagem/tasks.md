---

description: "Task list for feature 003-sprint2-analise-modelagem"
---

# Tasks: Sprint 2 — Análise de Rede e Modelagem

**Input**: Design documents from `/specs/003-sprint2-analise-modelagem/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (todos presentes; contratos reusados de `001-atlas-atos/contracts/`)

**Tests**: Incluídos. As 5 invariantes de `data-model.md` são o critério de aceite desta sprint (Constitution VI/FR-004, FR-008, ADR 0001, FR-013/FR-014).

**Organization**: Tarefas agrupadas por user story, na ordem de prioridade do spec (US1, US2 — P1 — depois US3, US4 — P2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1-US4, mapeado a `spec.md`

## Setup / Foundational

Não aplicável — todas as dependências (`networkx`, `scikit-learn`, `node2vec`, `pyproj`) já foram declaradas e instaladas em `001-atlas-atos`. Nenhuma tarefa bloqueante nova além das dependências entre stories descritas abaixo.

---

## Phase 1: User Story 1 - Ver como os lugares de Atos se relacionam estruturalmente (Priority: P1)

**Goal**: Grafo de coocorrência com métricas topológicas, incluindo nós isolados, exportado em `graph.json`.

**Independent Test**: Consultar `graph.json` e verificar grau/grau ponderado/intermediação por lugar, incluindo lugares sem nenhuma coocorrência.

- [X] T001 [US1] Implementar `pipeline/s04_build_graph.py` — construir grafo de coocorrência a partir de `data/processed/places.json` (só lugares `is_locatable=true`): nós = lugares, arestas = coocorrência em capítulo, peso = nº de capítulos coocorrentes; lugares sem coocorrência entram como nó isolado (FR-001; spec Edge Case 1)
- [X] T002 [US1] Em `pipeline/s04_build_graph.py`, calcular `degree`, `weighted_degree`, `betweenness` por lugar via `networkx` (FR-002) (depends on T001)
- [X] T003 [US1] Estender `pipeline/s08_export.py` para incluir `graph.json` conforme `specs/001-atlas-atos/contracts/graph.schema.json` (`community`/`community_is_connected` preenchidos como placeholder até US3) (depends on T002)
- [X] T004 [P] [US1] Escrever `tests/test_graph_isolated_nodes.py` — lugar mencionado 1x sem coocorrência aparece como nó isolado em `graph.json`, nunca excluído (spec Edge Case 1)

**Checkpoint**: US1 completa e testável de forma independente.

---

## Phase 2: User Story 2 - Saber se a incerteza de localização muda a leitura agregada da rede (Priority: P1)

**Goal**: Monte Carlo (N=1000, seed fixa) sobre as 4 métricas escalares de distância + ranking de centralidade geográfica, exportado em `uncertainty.json`; métricas topológicas de US1 nunca variam.

**Independent Test**: Consultar `uncertainty.json` e verificar mean/ci_low/ci_high/deterministic nas 4 métricas escalares e modal_rank/rank_ci por lugar em `place_rank_stability`.

- [X] T005 [US2] Implementar `pipeline/s05_uncertainty.py` — Monte Carlo com N=1000 e seed inteira fixa (`config.SEED`); a cada rodada, amostrar 1 candidato por lugar proporcional a `probability` (amostragem uniforme em caso de empate — spec Edge Case 2) (depends on T001 — usa as arestas do grafo para comprimento total/distância média)
- [X] T006 [US2] Em `pipeline/s05_uncertainty.py`, calcular as 4 métricas escalares (comprimento total da rede, distância média por conexão, área do fecho convexo, comprimento do itinerário narrativo) com `mean`/`ci_low`/`ci_high` (percentis 2.5/97.5) e `deterministic` (candidato de maior `probability`, nunca maior `score` bruto — ADR 0003) (FR-003, FR-006; data-model.md `DistanceMetricSimulation`) (depends on T005)
- [X] T007 [US2] Em `pipeline/s05_uncertainty.py`, implementar o itinerário narrativo sobre a sequência de `Verse` (`places.json[].verses`, ordenados por `sort`), revisitando lugares mencionados várias vezes — nunca deduplicando pela primeira menção (ADR 0002; FR-005) (depends on T005)
- [X] T008 [US2] Em `pipeline/s05_uncertainty.py`, calcular o ranking de centralidade geográfica (distância ao centroide ponderado) a cada simulação, agregando `modal_rank`/`rank_ci` por lugar em `place_rank_stability` (FR-003, FR-006; data-model.md `PlaceRankStability`; grill 2026-08-11 Q1) (depends on T005)
- [X] T009 [US2] Estender `pipeline/s08_export.py` para incluir `uncertainty.json` conforme `uncertainty.schema.json` (depends on T006, T007, T008)
- [X] T010 [P] [US2] Escrever `tests/test_topology_unaffected.py` — `degree`/`weighted_degree`/`betweenness` de `graph.json` são idênticos antes e depois de rodar `s05_uncertainty.py` (Constitution VI; FR-004; data-model.md invariante 1) (depends on T002, T009)
- [X] T011 [P] [US2] Escrever `tests/test_montecarlo_seed_reproducibility.py` — duas execuções de `s05_uncertainty.py` com a mesma seed produzem `uncertainty.json` byte-idêntico (ADR 0001; data-model.md invariante 3) (depends on T009)

**Checkpoint**: US1 + US2 completas e testáveis de forma independente.

---

## Phase 3: User Story 3 - Comparar os agrupamentos automáticos com a divisão narrativa tradicional (Priority: P2)

**Goal**: Comunidades detectadas (com conectividade validada) comparadas à partição narrativa de referência via NMI/ARI, em `docs/community-comparison.md`.

**Independent Test**: Consultar `docs/community-comparison.md` e verificar NMI, ARI e contagem de comunidades desconexas (mesmo que zero).

- [X] T012 [US3] Implementar `pipeline/s06_communities.py` — detecção de comunidades (Louvain, `networkx`, seed inteira) sobre o grafo de coocorrência de `s04_build_graph.py` (FR-007) (depends on T001)
- [X] T013 [US3] Em `pipeline/s06_communities.py`, validar a conectividade interna de cada comunidade (busca em largura no subgrafo induzido) e marcar `is_connected`; nenhuma comunidade desconexa é omitida (FR-008; spec Edge Case "comunidade desconexa") (depends on T012)
- [X] T014 [US3] Em `pipeline/s06_communities.py`, definir a partição narrativa de referência (3 blocos por faixa de capítulo: 1-7 Jerusalém, 8-12 Judeia e Samaria, 13-28 missão aos gentios) e calcular NMI (`sklearn.metrics.normalized_mutual_info_score`) e ARI (`adjusted_rand_score`) contra as comunidades detectadas — reportar mesmo se ARI for negativo (FR-009; data-model.md `ReferencePartition`/`CommunityComparisonResult`) (depends on T013)
- [X] T015 [US3] Gerar `docs/community-comparison.md` com NMI, ARI e contagem de comunidades desconexas, seguindo o padrão de artefato gerado (cabeçalho "não editar à mão", `generated_at`) já estabelecido em `002-fechar-lacunas-sprint1` (depends on T014)
- [X] T016 [US3] Atualizar `pipeline/s08_export.py` para preencher `community`/`community_is_connected` em `graph.json` a partir de `s06_communities.py` (substituindo o placeholder de T003) (depends on T003, T013)
- [X] T017 [P] [US3] Escrever `tests/test_community_connectivity.py` — toda comunidade marcada `is_connected=false` está de fato desconexa por verificação independente; nenhuma comunidade desconexa passa sem sinalização (data-model.md invariante 2) (depends on T016)
- [X] T018 [P] [US3] Escrever `tests/test_community_singleton_is_valid.py` — comunidade com um único lugar é aceita como resultado válido, não gera erro nem é filtrada (spec Edge Case "singleton")

**Checkpoint**: US1 + US2 + US3 completas e testáveis de forma independente.

---

## Phase 4: User Story 4 - Saber se é possível prever novas conexões bíblicas plausíveis (Priority: P2)

**Goal**: 6 modelos (4 heurísticas + 2 aprendidos) × 2 estratégias de amostragem negativa, avaliados sobre a rede de referências cruzadas em torno de Atos, exportados em `linkpred.json`.

**Independent Test**: Consultar `linkpred.json` e verificar 12 combinações modelo×estratégia em `results[]`, nenhum par com voto negativo entre as arestas positivas.

- [X] T019 [US4] Implementar `pipeline/s07_linkpred.py` — parsear `data/raw/cross-references.txt` (TSV, já documentado em `docs/data-contracts.md`); construir o subgrafo ego de raio 1 a partir dos versículos de Atos (research.md item 2); excluir pares com `Votes < 0` do conjunto de arestas positivas, manter pares com `Votes = 0` (research.md item 1; grill 2026-08-11 Q2; FR-014; spec Edge Cases de voto negativo/zero)
- [X] T020 [US4] Em `pipeline/s07_linkpred.py`, implementar split treino/teste (80/20) garantindo conectividade do grafo de treino (depends on T019)
- [X] T021 [US4] Em `pipeline/s07_linkpred.py`, implementar as duas estratégias de amostragem negativa: `random` (pares uniformemente aleatórios) e `distance_matched` (pares com distância no cânone pareada à distribuição dos positivos) (FR-013) (depends on T020)
- [X] T022 [US4] Em `pipeline/s07_linkpred.py`, implementar as 4 heurísticas — Common Neighbors, Jaccard, Adamic-Adar, Preferential Attachment — avaliadas antes de qualquer modelo aprendido (FR-011) (depends on T021)
- [X] T023 [US4] Em `pipeline/s07_linkpred.py`, implementar `node2vec` + Regressão Logística e `node2vec` + Gradient Boosting (produto de Hadamard dos embeddings) (FR-012) (depends on T021)
- [X] T024 [US4] Em `pipeline/s07_linkpred.py`, calcular AUC-ROC/AP/Precision@{50,100,500} para os 6 modelos × 2 estratégias (12 combinações) e gerar as 100 arestas de maior score fora do catálogo (`top_candidates[]`) (FR-013, FR-015 — reportar mesmo se heurística superar modelo aprendido) (depends on T022, T023)
- [X] T025 [US4] Estender `pipeline/s08_export.py` para incluir `linkpred.json` conforme `linkpred.schema.json` (depends on T024)
- [X] T026 [P] [US4] Escrever `tests/test_negative_sampling_both_reported.py` — todo modelo em `linkpred.json.results[]` tem exatamente uma entrada `negative_sampling="random"` e uma `negative_sampling="distance_matched"` (12 no total) (data-model.md invariante 4) (depends on T025)
- [X] T027 [P] [US4] Escrever `tests/test_no_negative_vote_as_positive_edge.py` — nenhum par com `Votes < 0` do catálogo original aparece como aresta positiva em `linkpred.json`; pares com `Votes = 0` continuam presentes (data-model.md invariante 5; grill 2026-08-11 Q2) (depends on T025)

**Checkpoint**: Todas as 4 user stories completas e testáveis de forma independente.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T028 [P] Medir o tempo entre iniciar `s04_build_graph.py` e ter os 4 artefatos prontos (SC-007), registrar em `docs/community-comparison.md` ou `relatorio.md`
- [X] T029 [P] Atualizar `relatorio.md` §1.2.3 (Sprint 2) para citar os artefatos reais (`graph.json`, `uncertainty.json`, `docs/community-comparison.md`, `linkpred.json`) como evidência de R2.1-R2.6
- [X] T030 [P] Atualizar `CLAUDE.md` "Estado atual" para refletir a conclusão de `003-sprint2-analise-modelagem`
- [X] T031 Executar o roteiro de verificação manual de `quickstart.md` por completo (as 4 user stories) e confirmar que todos os passos passam

---

## Dependencies & Execution Order

### Story Dependencies

- **US1 (P1)**: sem dependência de outra story — só depende de `places.json` (Sprint 1)
- **US2 (P1)**: depende de US1 (T001 — usa as arestas do grafo para comprimento total/distância média da rede)
- **US3 (P2)**: depende de US1 (T001 — comunidades são detectadas sobre o mesmo grafo de coocorrência); independente de US2
- **US4 (P2)**: totalmente independente de US1/US2/US3 — usa só `places.json` e `cross-references.txt`, pode ser feita em paralelo com qualquer uma das outras três

### Parallel Opportunities

- US4 inteira pode rodar em paralelo com US1+US2+US3 (nenhuma dependência de arquivo em comum além de `pipeline/s08_export.py`, que é tocado por várias tasks de forma sequencial — ver abaixo)
- `pipeline/s08_export.py` é tocado por T003 (US1), T009 (US2), T016 (US3) e T025 (US4) — sequenciais entre si independente da story, mesmo arquivo
- T004, T010, T011 (US1/US2), T017, T018 (US3), T026, T027 (US4) são testes em arquivos próprios — paralelos entre si dentro da mesma story quando não competem por dependência

### Notes

- Nenhuma task desta sprint modifica a lógica de extração já validada em `001-atlas-atos`/`002-fechar-lacunas-sprint1` (Constitution I-V inalteradas) — só adiciona os 4 módulos de análise previstos desde o plano original.
- `T001` (grafo de US1) é pré-requisito de `T005` (Monte Carlo de US2) e `T012` (comunidades de US3) — duas dependências cruzadas de US1 sobre as outras stories P1/P2, mantenha-as explícitas ao paralelizar.
