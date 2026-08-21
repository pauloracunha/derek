---

description: "Task list for feature 001-atlas-atos"
---

# Tasks: Atlas de Atos — Visualização de Rede de Lugares com Incerteza Preservada

**Input**: Design documents from `/specs/001-atlas-atos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md, CONTEXT.md (todos presentes)

**Tests**: Incluídas. O documento de origem (`definitions.md` §10) exige explicitamente os 6 testes de invariante do pipeline — não são TDD opcional, são a garantia automatizada de que os princípios da constituição (I–IV) não são violados.

**Organization**: Tarefas agrupadas por user story do spec (US1–US4), mais uma fase de entrega analítica sem UI (FR-010 parcial, FR-015) e uma fase de polimento. Revisado após sessão `/grill-with-docs` de 2026-08-02 (ver `CONTEXT.md` e `docs/adr/`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US4, mapeado a `spec.md`
- Caminhos de arquivo exatos em cada descrição

## Path Conventions

Monorepo de dois componentes, conforme `plan.md`: `pipeline/` (Python), `web/src/` (React/TS), `tests/` (pytest) e `data/` (raw/interim/processed) na raiz.

---

## Phase 1: Setup

**Purpose**: Inicialização do projeto

- [X] T001 Criar estrutura de diretórios per `plan.md` Project Structure: `pipeline/`, `web/`, `data/{raw,interim,processed}`, `tests/`, `docs/`; adicionar `data/raw/` e `data/interim/` ao `.gitignore`
- [X] T002 Inicializar projeto Python com `uv` em `pyproject.toml`: dependências `duckdb`, `polars`, `networkx`, `scikit-learn`, `node2vec`, `pyproj`, `pytest`
- [X] T003 [P] Inicializar projeto web (Vite + React + TypeScript) em `web/package.json`: dependências `maplibre-gl`, `d3-force`, `zustand`
- [X] T004 [P] Configurar lint/format Python (`ruff`) em `pyproject.toml`
- [X] T005 [P] Configurar lint/format web (`eslint` + `prettier`) em `web/`
- [X] T006 [P] Criar `justfile` com alvos `data`, `pipeline`, `test`, `web`
- [X] T007 Criar `pipeline/config.py` com `BOOK_ID=44` e URLs/hashes das fontes: `ancient.jsonl`, `modern.jsonl`, `source.jsonl`, arquivo de referências cruzadas OpenBible.info

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extração de Atos e esqueleto do app — bloqueia todas as user stories

**⚠️ CRITICAL**: Nenhuma user story começa antes desta fase estar completa

- [X] T008 Implementar `pipeline/s01_download.py` — baixa `ancient.jsonl`, `modern.jsonl`, `source.jsonl` e o arquivo de referências cruzadas para `data/raw/`
- [X] T009 Inspecionar estrutura real do arquivo de referências cruzadas (delimitador, cabeçalho, formato de referência — provavelmente OSIS) e documentar em `docs/data-contracts.md` (não presumir — ver `research.md` item 1)
- [X] T010 Inspecionar `source.jsonl` real: achar a chave de join entre `identification`/`resolution` de `ancient.jsonl` e uma entrada de `source.jsonl` (`id_source` é um tipo `ancient`\|`modern`\|`special`, **não** é essa chave); documentar em `docs/data-contracts.md`. Se não houver join confiável, marcar Fonte como atributo opcional por candidato (ver `CONTEXT.md`, termo "Fonte", e `spec.md` Assumptions)
- [X] T011 [P] Implementar `pipeline/s02_load.py` — carrega os 3 `.jsonl` em DuckDB (`data/interim/atlas.duckdb`)
- [X] T012 Implementar `pipeline/s03_extract_acts.py` — filtrar lugares com `verse.sort LIKE '44%'`; normalizar `modern_associations` em candidatos com `probability` (clip-a-zero + fallback uniforme, `docs/adr/0003`); resolver `lon`/`lat` das resoluções (sem precisar join com `modern.jsonl` — já embutido, com fallback pra `modern.jsonl` se ausente); tratar resoluções `special` por `candidates` não-vazio, não por presença de `special` (`docs/adr/0004`). Filtra `verses[]`/`chapters`/`mention_count` só a menções de Atos (depends on T011)
- [X] T013 Em `pipeline/s03_extract_acts.py`, calcular e logar a tabela de distribuição de contagem de candidatos (1 / 2 / 3+) — decide o eixo narrativo do relatório (H1), ver `research.md`/`quickstart.md` (depends on T012)
- [X] T014 [P] Escrever `tests/test_coordinates_order.py` — todo candidato exportado cai no bbox real de Atos (lon 10–48, lat 15–43 — corrigido de "Mediterrâneo oriental", `docs/adr/0005`)
- [X] T015 [P] Escrever `tests/test_probability_integrity.py` — Σ `probability` por lugar = 1.0 (±1e-9)
- [X] T016 [P] Escrever `tests/test_candidate_preservation.py` — `candidate_count` exportado == número de chaves em `modern_associations` da origem; todo `sort` em `verses[]` começa com `"44"` (nenhuma menção de outro livro vaza)
- [X] T017 [P] Escrever `tests/test_no_candidate_collapse.py` — nenhum lugar com >1 candidato na origem sai com exatamente 1 candidato na saída (teste mais importante do projeto — Constitution I)
- [X] T018 [P] Escrever `tests/test_canonical_key.py` — todo `sort`/`verses[]` exportado tem 8 caracteres e é string, nunca inteiro
- [X] T019 Implementar `pipeline/s08_export.py` — exporta `data/processed/places.json` conforme `contracts/places.schema.json` (campo `dispersion_index`, não `uncertainty_index`) (depends on T012, T013)
- [X] T020 [P] Escrever `tests/test_reproducibility.py` — duas execuções de `s03`+`s08` com a mesma seed produzem `places.json` byte-idêntico (seed inteira, reprodutibilidade escopada ao lockfile — ver `docs/adr/0001-reprodutibilidade-escopo-lockfile.md`)
- [X] T021 [P] Implementar `web/src/services/dataLoader.ts` — carrega e tipa `data/processed/*.json` (tipos TS espelhando `contracts/*.schema.json`)
- [X] T022 [P] Implementar `web/src/state/store.ts` — estado global (lugar selecionado, faixa de capítulos) via Zustand/Context; a faixa de capítulos é lida tanto pelo mapa quanto pelo grafo (US1 e US3 compartilham este filtro)
- [X] T023 Implementar `web/src/App.tsx` — layout base per spec §6.1 (header, área de mapa, painel lateral, timeline, painel de grafo), sem conteúdo interativo ainda

**Checkpoint**: `places.json` exportado e validado pelos testes de invariante; app renderiza layout vazio. Início das user stories liberado.

---

## Phase 3: User Story 1 - Explorar lugares no mapa sem perder a incerteza de localização (Priority: P1) 🎯 MVP

**Goal**: Ao selecionar um lugar, o mapa mostra todos os candidatos de localização conhecidos simultaneamente, com peso visual proporcional à confiança.

**Independent Test**: Selecionar um lugar com 2+ candidatos e verificar que todos aparecem no mapa com opacidade+tamanho proporcionais ao score, junto com a fonte.

- [ ] T024 [P] [US1] Implementar `web/src/components/Map.tsx` — mapa MapLibre GL com tiles claros (CARTO Positron)
- [ ] T025 [US1] Em `web/src/components/Map.tsx`, renderizar TODOS os candidatos de um lugar simultaneamente, com opacidade E tamanho do marcador proporcionais a `probability` (FR-002, FR-003 — Constitution I) (depends on T024, T021)
- [ ] T026 [US1] Em `web/src/components/Map.tsx`, desenhar linha tracejada conectando os candidatos do mesmo lugar, com rótulo no candidato modal (depends on T025)
- [ ] T027 [US1] Em `web/src/components/Map.tsx`, renderizar halo difuso para candidatos com `lonlat_type="settlement"`, distinto do marcador de ponto exato (FR-004) (depends on T025)
- [ ] T028 [P] [US1] Implementar `web/src/components/PlaceDetail.tsx` — painel lateral com nome do lugar e lista de candidatos (score, probability, fonte se disponível — ver T010)
- [ ] T029 [US1] Integrar `PlaceDetail.tsx` com `store.ts` para reagir à seleção de lugar feita no mapa (depends on T025, T028, T022)
- [ ] T030 [P] [US1] Implementar `web/src/components/Legend.tsx` — legenda permanente explicando opacidade+tamanho e halo de área (FR-007)
- [ ] T031 [P] [US1] Implementar `web/src/components/UncertaintyExplainer.tsx` — texto explicativo permanente sobre múltiplos pontos por lugar (FR-008)
- [ ] T032 [US1] Em `PlaceDetail.tsx` (ou painel de lista de lugares), ordenar/destacar lugares por `dispersion_index` decrescente ("mais disputados primeiro") (FR-020) (depends on T019, T028)
- [X] T033 [P] [US1] Escrever `tests/test_contracts_places.py` — validar `places.json` contra `contracts/places.schema.json` (incl. `dispersion_index`)

**Checkpoint**: US1 completa e testável de forma independente.

---

## Phase 4: User Story 2 - Consultar lugares sem localização conhecida sem que sejam descartados (Priority: P1)

**Goal**: Lugares sem localização conhecida permanecem visíveis, em painel próprio, com razão explícita; lugares que não são de fato lugares são excluídos por completo.

**Independent Test**: Consultar a lista de "sem localização conhecida" e confirmar razão explícita e legível em cada item.

- [ ] T034 [US2] Em `pipeline/s03_extract_acts.py`, garantir `is_locatable=false` + `special_reason` para `unknown_place`/`nonspecific_place`/`multiple_locations`; exclusão total do catálogo para `not_a_place`/`not_a_proper_name`/`recursive` (extends T012 — Constitution II)
- [ ] T035 [P] [US2] Implementar `web/src/components/UnlocatablePanel.tsx` — painel dedicado listando lugares com `is_locatable=false` e a razão (FR-005)
- [ ] T036 [US2] Em `UnlocatablePanel.tsx`, mapear `special_reason` (código técnico) para texto legível em português (depends on T035)
- [ ] T037 [P] [US2] Escrever `tests/test_unlocatable_reason_required.py` — todo lugar com `is_locatable=false` tem `special_reason` preenchido; nenhum lugar `not_a_place`/`not_a_proper_name`/`recursive` aparece na saída

**Checkpoint**: US1 + US2 completas e testáveis de forma independente.

---

## Phase 5: User Story 3 - Entender como os lugares de Atos se conectam entre si (Priority: P2)

**Goal**: Visualização de rede de coocorrência por capítulo, filtrável por faixa de capítulos (sincronizada com o mapa), com agrupamento visual por comunidade.

**Independent Test**: Selecionar uma faixa de capítulos e verificar que o grafo e o mapa realçam lugares/conexões correspondentes, agrupados por comunidade.

- [ ] T038 [US3] Implementar `pipeline/s04_build_graph.py` — grafo de coocorrência por capítulo (nós=lugares, arestas=coocorrência); calcular `degree`, `weighted_degree`, `betweenness` (depends on T012)
- [ ] T039 [US3] Implementar `pipeline/s06_communities.py` — detecção de comunidades (Louvain, `seed` inteira — ver `docs/adr/0001`); validar conectividade de cada comunidade e sinalizar as desconexas (FR-011) (depends on T038)
- [ ] T040 [US3] Estender `pipeline/s08_export.py` para incluir `graph.json` conforme `contracts/graph.schema.json` (depends on T039)
- [ ] T041 [P] [US3] Escrever `tests/test_community_connectivity.py` — toda comunidade internamente desconexa está marcada `community_is_connected=false`, nunca omitida
- [ ] T042 [P] [US3] Implementar `web/src/components/NetworkGraph.tsx` — renderizar grafo com `d3-force` em painel lateral, separado do mapa (FR-009)
- [ ] T043 [US3] Em `NetworkGraph.tsx`, colorir/agrupar nós por `community` (FR-010) (depends on T042, T040)
- [ ] T044 [P] [US3] Implementar `web/src/components/ChapterTimeline.tsx` — seletor de capítulo/faixa de capítulos
- [ ] T045 [US3] Integrar `ChapterTimeline.tsx` com `store.ts`, `NetworkGraph.tsx` **e `Map.tsx`** — filtrar nós/arestas do grafo E marcadores do mapa pela faixa de capítulos selecionada (spec US3 Acceptance Scenario 3 — mapa e grafo sincronizados pelo mesmo filtro) (depends on T044, T042, T024, T022)

**Checkpoint**: US1 + US2 + US3 completas e testáveis de forma independente.

---

## Phase 6: User Story 4 - Confiar no grau de incerteza agregada da rede (Priority: P3)

**Goal**: Métricas de rede baseadas em distância reportadas com IC 95% e valor determinístico, lado a lado; métricas topológicas nunca variam.

**Independent Test**: Consultar as métricas de distância e verificar presença de média + IC + valor determinístico.

- [ ] T046 Implementar `pipeline/s05_uncertainty.py` — Monte Carlo (N=1000, seed inteira fixa) para as 5 métricas de distância (comprimento total, distância média, fecho convexo, centralidade geográfica, itinerário narrativo), usando distância geodésica WGS84 (`pyproj`). Itinerário narrativo é calculado sobre a sequência de `Verse` (revisita lugares mencionados várias vezes, não deduplica por primeira menção — ver `docs/adr/0002-itinerario-narrativo-revisita-lugares.md`) (depends on T012, T038)
- [ ] T047 [US4] Em `pipeline/s05_uncertainty.py`, calcular `mean`/`ci_low`/`ci_high`/`deterministic` por métrica e `place_rank_stability` (depends on T046)
- [ ] T048 [US4] Estender `pipeline/s08_export.py` para incluir `uncertainty.json` conforme `contracts/uncertainty.schema.json` (depends on T047)
- [ ] T049 [P] [US4] Escrever `tests/test_montecarlo_seed_reproducibility.py` — mesma seed inteira produz `uncertainty.json` byte-idêntico dentro da mesma versão travada em `uv.lock` (ver `docs/adr/0001`)
- [ ] T050 [P] [US4] Escrever `tests/test_topology_unaffected.py` — `degree`/`betweenness`/`community` de `graph.json` não variam entre execuções de Monte Carlo (FR-014 — Constitution VI)
- [ ] T051 [P] [US4] Implementar `web/src/components/UncertaintyPanel.tsx` — exibir métricas de distância com média/IC95%/valor determinístico lado a lado (FR-013)

**Checkpoint**: US1–US4 completas — aplicação interativa (MVP completo) funcional e testável de forma independente.

---

## Phase 7: Predição de Links & Comparação de Comunidades (entrega de relatório, sem UI)

**Goal**: FR-010 (parte quantitativa), FR-015, SC-005, SC-006 — análises documentadas no relatório escrito, não expostas na aplicação (decisão da sessão de clarificação 2026-08-02).

- [ ] T052 Implementar `pipeline/s07_linkpred.py` — construir subgrafo ego (raio 1) de referências cruzadas envolvendo versículos de Atos, não-direcionado (depends on T009)
- [ ] T053 Em `pipeline/s07_linkpred.py`, implementar split treino/teste (80/20) garantindo conectividade do grafo de treino (depends on T052)
- [ ] T054 Em `pipeline/s07_linkpred.py`, implementar amostragem negativa `random` e `distance_matched` (depends on T053)
- [ ] T055 Em `pipeline/s07_linkpred.py`, implementar as 4 heurísticas (Common Neighbors, Jaccard, Adamic-Adar, Preferential Attachment) (depends on T054)
- [ ] T056 Em `pipeline/s07_linkpred.py`, implementar `node2vec` + Regressão Logística e `node2vec` + Gradient Boosting (produto de Hadamard dos embeddings) (depends on T054)
- [ ] T057 Em `pipeline/s07_linkpred.py`, calcular AUC-ROC/AP/Precision@{50,100,500} para os 6 modelos × 2 estratégias e gerar top 100 candidatos fora do catálogo (depends on T055, T056)
- [ ] T058 Em `pipeline/s06_communities.py`, calcular NMI/ARI contra a partição de referência (caps. 1–7 / 8–12 / 13–28) e registrar em `docs/decisions.md` (depends on T039)
- [ ] T059 Estender `pipeline/s08_export.py` para incluir `linkpred.json` conforme `contracts/linkpred.schema.json` (depends on T057)
- [ ] T060 [P] Escrever `tests/test_negative_sampling_both_reported.py` — todo modelo tem entrada para `random` E `distance_matched` em `linkpred.json` (FR-015)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Itens que afetam múltiplas user stories ou fecham requisitos transversais

- [ ] T061 [P] Implementar `web/src/components/Footer.tsx` — atribuição de licença OpenBible.info (CC BY 4.0) e OpenStreetMap (ODbL), sempre visível (FR-016)
- [ ] T062 [P] Registrar ADRs curtos adicionais de `research.md` em `docs/decisions.md` (0001 e 0002 já registrados na sessão de grill)
- [ ] T063 Consolidar tabela final de distribuição de candidatos e achados H1–H5 no relatório/`README.md`
- [ ] T064 Executar o roteiro de verificação manual de `quickstart.md` (US1–US4 + legenda + rodapé + filtro de capítulo sincronizado mapa/grafo)
- [ ] T065 Conduzir teste de compreensão com 3–5 participantes reais (SC-003, meta ≥80% de acerto)
- [ ] T066 [P] Escrever `README.md` com instruções de setup e execução do pipeline e do app

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente
- **Foundational (Phase 2)**: depende do Setup — BLOQUEIA todas as user stories
- **US1 (Phase 3)** e **US2 (Phase 4)**: dependem só do Foundational — podem rodar em paralelo entre si
- **US3 (Phase 5)**: depende do Foundational (usa `places.json` de T012); a integração final (T045) também depende de `Map.tsx` de US1 (T024) — única dependência de US3 sobre US1, além do Foundational
- **US4 (Phase 6)**: depende do Foundational E de `pipeline/s04_build_graph.py` (T038, de US3) — o grafo de coocorrência é insumo do cálculo de itinerário/comprimento de rede
- **Fase 7 (Predição de Links)**: depende do Foundational (T009) e de US3 (T039, para NMI/ARI) — independente de US1/US2/US4
- **Polish (Phase 8)**: depende de todas as fases anteriores desejadas estarem completas

### User Story Dependencies

- **US1 (P1)**: nenhuma dependência de outra user story
- **US2 (P1)**: nenhuma dependência de outra user story (compartilha `s03_extract_acts.py` com US1 via Foundational, não depende do código de US1)
- **US3 (P2)**: depende do Foundational; a task final de integração (T045) depende de `Map.tsx` de US1 — documentado explicitamente após a decisão de filtro de capítulo sincronizado (grill 2026-08-02, Q6)
- **US4 (P3)**: depende do grafo de US3 (T038) para as métricas de itinerário/comprimento de rede — exceção à independência entre stories, documentada explicitamente

### Parallel Opportunities

- Todas as tarefas `[P]` do Setup (T003–T006) em paralelo
- T014–T018 e T020 (testes de invariante) em paralelo entre si, após T012/T019
- Após o Foundational: US1 e US2 podem ser implementadas em paralelo por pessoas/agentes diferentes
- Dentro de cada story, tarefas `[P]` (componentes de arquivos distintos) em paralelo

---

## Parallel Example: User Story 1

```bash
# Componentes de UI independentes de US1 em paralelo:
Task: "Implementar web/src/components/Map.tsx — mapa MapLibre GL"
Task: "Implementar web/src/components/PlaceDetail.tsx — painel de detalhe"
Task: "Implementar web/src/components/Legend.tsx — legenda"
Task: "Implementar web/src/components/UncertaintyExplainer.tsx — texto explicativo"
Task: "Escrever tests/test_contracts_places.py — validação de schema"
```

---

## Implementation Strategy

### MVP First (User Story 1 apenas)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO — bloqueia todas as stories)
3. Completar Phase 3: US1
4. **PARAR e VALIDAR**: testar US1 de forma independente (mapa com múltiplos candidatos)
5. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → fundação pronta (`places.json` exportado e validado)
2. + US1 → testar independentemente → demo (MVP visual)
3. + US2 → testar independentemente → demo (integridade "nada desaparece")
4. + US3 → testar independentemente → demo (dimensão relacional, mapa+grafo sincronizados)
5. + US4 → testar independentemente → demo (incerteza agregada)
6. + Fase 7 → achados de relatório (predição de links, NMI/ARI)
7. + Polish → publicação final

### Notes

- `[P]` = arquivos diferentes, sem dependência pendente
- Verificar que os testes de invariante (T014–T018, T020, T033, T037, T041, T049, T050, T060) falham antes da implementação correspondente, quando escritos antes do código
- Commit após cada tarefa ou grupo lógico
- Parar em qualquer checkpoint para validar a story isoladamente
- T038 (grafo de US3) é pré-requisito de T046 (Monte Carlo de US4); T024 (Map de US1) é pré-requisito de T045 (integração de US3) — duas dependências cruzadas entre stories, mantenha-as explícitas ao paralelizar equipes
