---
description: "Task list for Sprint 3 — Interface e Validação"
---

# Tasks: Sprint 3 — Interface e Validação

**Input**: Design documents from `/specs/004-sprint3-interface-validacao/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/README.md, quickstart.md, CONTEXT.md (decisões de grill 2026-08-19)

**Tests**: não exigidos explicitamente na spec (US1–US4 não pedem TDD). Incluídos como
tarefas de implementação por story, não como fase TDD separada, porque verificar os
Princípios I/II (incerteza nunca colapsa / não-localizável nunca desaparece) na prática
é parte do critério de aceite de cada story, não um extra.

**Organization**: tarefas agrupadas por user story (US1–US5), seguindo prioridade de
`spec.md`. Todo caminho é relativo à raiz do repositório.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1–US5, mapeando para `spec.md`

## Path Conventions

Projeto frontend único em `web/` (sem `backend/`) — ver `plan.md` § Project Structure.
Registro do teste de compreensão (US5) fica em `docs/`, fora de `web/`.

---

## Phase 1: Setup

**Purpose**: preparar dados e ferramentas de teste antes de qualquer componente

- [X] T001 Rodar pipeline e copiar os 4 JSONs gerados para `web/public/data/`: `uv run python -m pipeline.s08_export && cp data/processed/*.json web/public/data/`
- [X] T002 [P] Instalar e configurar Vitest + @testing-library/react em `web/` (`package.json`, `vite.config.ts` — decisão em `research.md` #1)
- [X] T003 [P] Importar CSS base do MapLibre GL em `web/src/main.tsx` ou `web/src/index.css` (`maplibre-gl/dist/maplibre-gl.css`)

**Checkpoint**: `npm run dev` em `web/` carrega `places.json` real (já funciona hoje) e `npm run test` roda sem erro de config.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: infraestrutura de dados e tipos compartilhada por US1–US4 — nenhuma story começa sem isto

**⚠️ CRITICAL**: bloqueia todas as user stories

- [X] T004 Adicionar tipos `GraphNode`, `GraphEdge`, `Graph` e função `loadGraph()` em `web/src/services/dataLoader.ts`, espelhando `specs/001-atlas-atos/contracts/graph.schema.json` (ver `data-model.md`)
- [X] T005 Estender `web/src/App.tsx` para carregar `graph.json` via `loadGraph()` junto de `places.json`, guardando resultado em novo estado local ou no store (guardado em `store.ts` via `graph`/`setGraph`)
- [X] T006 [P] Criar diretório `web/src/components/` com arquivos stub para `Map.tsx`, `PlaceDetail.tsx`, `UnlocatablePanel.tsx`, `ChapterTimeline.tsx`, `NetworkGraph.tsx`, `Legend.tsx`, `Footer.tsx` (substituindo os placeholders comentados em `App.tsx`)

Nenhum campo novo é necessário em `web/src/state/store.ts` — `chapterRange` e
`selectedPlaceId` já existentes cobrem US1/US3, incluindo seleção cruzada mapa↔grafo
(ver `data-model.md` § Extensão de estado, grill 2026-08-19 Q9).

**Checkpoint**: `dataLoader.ts` expõe `Place` e `Graph` tipados; `App.tsx` carrega ambos os JSONs sem erro; stubs de componente existem para todas as stories.

---

## Phase 3: User Story 1 - Ver todos os candidatos de um lugar no mapa (Priority: P1) 🎯 MVP

**Goal**: selecionar um lugar no mapa e ver todos os candidatos de localização simultaneamente, com peso visual (opacidade + tamanho) proporcional à probabilidade — Princípio I.

**Independent Test**: carregar `places.json` real, selecionar lugar com `candidate_count >= 2` (ver `quickstart.md`), confirmar que todos os candidatos aparecem ao mesmo tempo.

### Implementation for User Story 1

- [X] T007 [US1] Implementar `Map.tsx` em `web/src/components/Map.tsx`: inicializar MapLibre GL, renderizar um marcador por `LocationCandidate` de todos os lugares localizáveis carregados
- [X] T008 [US1] Em `Map.tsx`, aplicar peso visual linear com piso mínimo: `opacity = 0.15 + 0.85·candidate.probability`, `radius = 4 + 12·candidate.probability` — nunca exibir só o candidato de maior score, nunca deixar candidato de baixa probabilidade invisível/inclicável (Princípio I / FR-002; ver CONTEXT.md § Peso Visual, grill Q1) — extraído para `web/src/services/visualWeight.ts`
- [X] T009 [US1] Em `Map.tsx`, ligar candidatos do mesmo `place_id` com linha tracejada + cor compartilhada, exibida somente quando esse lugar está selecionado (CONTEXT.md § Vínculo Visual, grill Q2)
- [X] T010 [US1] Em `Map.tsx`, distinguir forma do marcador por `lonlat_type`: círculo sólido para `'point'`; quadrado/losango ou anel pontilhado para `'center' | 'representative point' | 'settlement'` — canal independente de cor (reservada para Comunidade em US3) (CONTEXT.md § Forma do Marcador, grill Q3; FR-003)
- [X] T011 [US1] Implementar `PlaceDetail.tsx` em `web/src/components/PlaceDetail.tsx`: exibir nome, candidatos (com score/probabilidade) e fontes (`sources[]`) do `selectedPlaceId` atual do store
- [X] T012 [US1] Ligar clique em marcador do mapa a `useAtlasStore().selectPlace(placeId)`, e clique fora/em lugar sem candidatos a `selectPlace(null)`
- [X] T013 [US1] Substituir placeholders de `map-area` e parte de `side-panel` em `web/src/App.tsx` pelos componentes `Map.tsx` e `PlaceDetail.tsx`
- [X] T014 [P] [US1] Teste de componente em `web/tests/components/Map.test.tsx`: dado um lugar com 2+ candidatos, todos aparecem renderizados, nenhum com opacidade/raio abaixo do piso mínimo (regressão do Princípio I) — testa `visualWeight.ts` diretamente (maplibre-gl exige WebGL real, indisponível em jsdom)

**Checkpoint**: US1 funcional e testável isoladamente — selecionar qualquer lugar localizável mostra todos os candidatos com peso visual diferenciado.

---

## Phase 4: User Story 2 - Painel de lugares não localizáveis com razão explícita (Priority: P1)

**Goal**: painel dedicado lista 100% dos lugares `is_locatable: false`, cada um com `special_reason` traduzido para texto legível — Princípio II.

**Independent Test**: contar `is_locatable == false` em `places.json` (ver `quickstart.md`) e confirmar que o painel lista exatamente esse número, nenhum a menos.

### Implementation for User Story 2

- [X] T015 [US2] Criar mapa de tradução `SpecialReason → texto legível` em `web/src/services/dataLoader.ts` ou novo `web/src/services/reasonLabels.ts` (`unknown_place`, `nonspecific_place`, `multiple_locations`, `no_candidates_resolved`)
- [X] T016 [US2] Implementar `UnlocatablePanel.tsx` em `web/src/components/UnlocatablePanel.tsx`: filtrar `places` do store por `is_locatable === false`, renderizar nome + razão traduzida para cada um
- [X] T017 [US2] Garantir em `Map.tsx` (T007) que lugares com `is_locatable === false` nunca geram marcador no mapa (só aparecem em `UnlocatablePanel.tsx`)
- [X] T018 [US2] Substituir placeholder restante de `side-panel` em `web/src/App.tsx` por `UnlocatablePanel.tsx` (aba ou seção separada de `PlaceDetail.tsx`)
- [X] T019 [P] [US2] Teste de componente em `web/tests/components/UnlocatablePanel.test.tsx`: número de itens renderizados bate com `places.filter(p => !p.is_locatable).length` (regressão do Princípio II)

**Checkpoint**: US1 e US2 funcionam juntas e independentemente — nenhum lugar desaparece silenciosamente, nenhum candidato colapsa.

---

## Phase 5: User Story 3 - Grafo de coocorrência filtrado por capítulo, sincronizado com o mapa (Priority: P2)

**Goal**: grafo `graph.json` agrupado por comunidade, filtrável por faixa de capítulo, com mapa e grafo sincronizados pelo mesmo `chapterRange` e por seleção cruzada de lugar.

**Independent Test**: selecionar faixa de capítulos na timeline e verificar que grafo e mapa atualizam para o mesmo subconjunto de lugares (`quickstart.md`).

### Implementation for User Story 3

- [X] T020 [US3] Implementar `ChapterTimeline.tsx` em `web/src/components/ChapterTimeline.tsx`: range slider duplo (alças from/to) cobrindo capítulos 1–28, ligado a `useAtlasStore().setChapterRange` (grill Q7)
- [X] T021 [US3] Implementar `NetworkGraph.tsx` em `web/src/components/NetworkGraph.tsx`: layout `d3-force` sobre `nodes`/`edges` de `graph.json`, coloração por `community`; adicionar força customizada que atrai cada nó a um centroide fixo por `community` (círculo de centros), além de `forceManyBody`/`forceLink`/`forceCollide` padrão — cluster sem lib nova (`research.md` #3, grill Q4)
- [X] T022 [US3] Em `NetworkGraph.tsx`, filtrar arestas exibidas por `edge.chapters` interseção com `chapterRange` do store (mesmo padrão de `placeInChapterRange` em `store.ts`); nós sem aresta na faixa permanecem visíveis, isolados — nunca somem do grafo (Princípio II aplicado a nó de grafo, grill Q5)
- [X] T023 [US3] Em `Map.tsx`, aplicar `placeInChapterRange(place, chapterRange)` (já existe em `store.ts`) para esconder marcadores fora da faixa selecionada
- [X] T024 [US3] Em `NetworkGraph.tsx`, sinalizar visualmente nós com `community_is_connected === false` (ex. borda tracejada + texto), nunca omitir a inconsistência (FR-006)
- [X] T025 [US3] Em `NetworkGraph.tsx`, ligar clique em nó a `useAtlasStore().selectPlace(node.place_id)` — seleção cruzada mapa↔grafo reusando o `selectPlace` de T012, sem estado novo (grill Q9)
- [X] T026 [US3] Substituir placeholders de `timeline-area` e `graph-area` em `web/src/App.tsx` por `ChapterTimeline.tsx` e `NetworkGraph.tsx`
- [X] T027 [P] [US3] Teste de componente em `web/tests/components/NetworkGraph.test.tsx`: alterar `chapterRange` no store filtra arestas exibidas conforme esperado, nós sem aresta na faixa continuam renderizados isolados — filtro (`edgeInChapterRange`) testado diretamente; "nó sempre renderizado" garantido estruturalmente (componente nunca filtra `layout.nodes`, só `links`)

**Checkpoint**: US1–US3 funcionam juntas — selecionar faixa de capítulos atualiza mapa e grafo simultaneamente, sem recarregar página (SC-004); clicar nó do grafo seleciona o lugar no mapa/painel.

---

## Phase 6: User Story 4 - Legenda, atribuição e publicação pública (Priority: P2)

**Goal**: legenda permanente da codificação visual, texto explicativo e atribuição de licença sempre visíveis; aplicação publicada em URL pública sem login.

**Independent Test**: acessar URL pública sem login e confirmar legenda/texto/atribuição visíveis sem interação adicional (`quickstart.md`).

### Implementation for User Story 4

- [X] T028 [P] [US4] Implementar `Legend.tsx` em `web/src/components/Legend.tsx`: explicar opacidade/tamanho = probabilidade (com piso mínimo), forma do marcador = área vs. ponto exato (espelha T008/T010)
- [X] T029 [P] [US4] Implementar `Footer.tsx` em `web/src/components/Footer.tsx`: texto explicativo sobre múltiplos pontos por lugar + atribuição de licença das fontes — OpenBible.info Bible-Geocoding-Data (geolocalização) e OpenBible.info cross-references (CC-BY), conforme `docs/data-contracts.md`
- [X] T030 [US4] Adicionar `Legend.tsx` e `Footer.tsx` em `web/src/App.tsx`, sempre visíveis (não atrás de menu/modal)
- [ ] T031 [US4] **BLOQUEADO (ação humana)** Confirmar nome do repositório GitHub (preferência: `<usuário>.github.io` para servir na raiz, `base: '/'`); se project site em vez disso, setar `base: '/<nome-do-repo>/'` em `web/vite.config.ts` antes do build (`research.md` #4, grill Q8) — projeto ainda não é repositório git
- [X] T032 [US4] Build de produção: `cd web && npm run build`, validar `web/dist` gerado sem erro e assets carregando com o `base` correto — validado com `base` padrão (`/`); revisitar se T031 resolver para project site
- [ ] T033 [US4] **BLOQUEADO (ação humana)** Publicar `web/dist` via GitHub Pages (`research.md` #4) e confirmar URL pública acessível sem cadastro/login — depende de T031
- [X] T034 [P] [US4] Teste de componente em `web/tests/components/Legend.test.tsx`: legenda renderiza sem depender de seleção de lugar

**Checkpoint**: aplicação publicada e acessível publicamente; US1–US4 completas e demonstráveis via URL pública (R3.2–R3.6 do relatório).

---

## Phase 7: User Story 5 - Teste de compreensão com usuários reais (Priority: P3)

**Goal**: validar H4 — 3 a 5 participantes reais explicam corretamente, sem explicação prévia, por que lugares aparecem com múltiplos pontos.

**Independent Test**: conduzir sessão com 3–5 participantes e registrar resultado em documento persistido (`quickstart.md` § Teste de compreensão).

### Implementation for User Story 5

- [X] T035 [US5] Criar `docs/usability-test.md` com a tabela de campos definida em `data-model.md` § Sessão de teste de compreensão (`participant_id`, `date`, `explained_correctly`, `justification`, `notes`) e a rubrica de `explained_correctly` (grill Q6)
- [ ] T036 [US5] **BLOQUEADO (ação humana)** Conduzir sessões com 3 a 5 participantes reais sobre a aplicação publicada (T033), sem explicação prévia da equipe, perguntando por que alguns lugares têm múltiplos pontos — depende de T033
- [ ] T037 [US5] **BLOQUEADO (ação humana)** Registrar cada sessão em `docs/usability-test.md` conforme conduzida (não em lote ao final, para evitar viés de memória), aplicando a rubrica: `true` se o participante expressar a ideia de múltiplas hipóteses conflitantes de localização, sem exigir termo técnico
- [ ] T038 [US5] **BLOQUEADO (ação humana)** Calcular taxa de acerto agregada e reportar em `relatorio.md` (seção Sprint 3 / H4), independentemente de atingir os 80% de SC-003 (Princípio VI — nunca ajustar amostra ou critério pós-hoc)

**Checkpoint**: SC-003 avaliado e reportado; critério de aceite formal da Sprint 3 (`relatorio.md`) fechado.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: consistência final entre stories e evidência para o relatório

- [X] T039 [P] Rodar `just lint` (`ruff` + `eslint` de `web/`) e corrigir violações introduzidas por esta feature — 0 erros (1 warning cosmético de fast-refresh em `NetworkGraph.tsx`, não bloqueante)
- [X] T040 [P] Rodar todos os testes de componente (`npm run test` em `web/`) e confirmar suíte verde — 4 arquivos, 11 testes, todos passando
- [ ] T041 **BLOQUEADO (ação humana)** Validar manualmente os passos de `quickstart.md` (Princípio I e II) na build publicada, não só em dev local — depende de T033
- [ ] T042 **BLOQUEADO (ação humana)** Atualizar `CLAUDE.md` § Estado atual com o resultado real desta feature (tasks concluídas, achados do teste de compreensão) — depende de T036–T038
- [ ] T043 **BLOQUEADO (ação humana)** Atualizar `relatorio.md` § Sprint 3 (R3.1–R3.6) com evidência de cada artefato (capturas de tela, URL pública, link para `docs/usability-test.md`) — depende de T033/T038

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — pode começar imediatamente
- **Foundational (Phase 2)**: depende de Setup — bloqueia todas as user stories
- **US1 (Phase 3)**: depende só de Foundational
- **US2 (Phase 4)**: depende só de Foundational; T017 depende de `Map.tsx` existir (T007, US1) mas US2 é testável isoladamente via `UnlocatablePanel.tsx` sem esperar US1 terminar
- **US3 (Phase 5)**: depende de Foundational; T023/T025 tocam `Map.tsx` (US1), então na prática roda melhor depois de US1 concluída, mesmo sem dependência de dados
- **US4 (Phase 6)**: depende de Foundational; T028/T029 são independentes, mas T033 (publicação) só faz sentido depois de US1–US3 completas o suficiente para demo
- **US5 (Phase 7)**: depende de US4 (T033 — precisa de URL pública) estar concluída
- **Polish (Phase 8)**: depende de todas as stories desejadas estarem completas

### Parallel Opportunities

- T002/T003 (Setup) em paralelo
- Dentro de Foundational: T006 em paralelo, após T004/T005
- Dentro de US1: T014 (teste) em paralelo com implementação de T011–T013 depois de T007–T010 prontos
- US1 e US2 podem ser desenvolvidas em paralelo por pessoas diferentes assim que Foundational termina (T017 é o único ponto de integração)
- T028/T029/T034 (US4) em paralelo entre si

---

## Parallel Example: User Story 1

```bash
Task: "Implementar Map.tsx com marcadores por candidato (web/src/components/Map.tsx)"
Task: "Teste de componente Map.test.tsx cobrindo lugar com 2+ candidatos (web/tests/components/Map.test.tsx)"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Completar Setup + Foundational
2. Completar US1 (mapa com candidatos) — **valida Princípio I**
3. Completar US2 (painel de não-localizáveis) — **valida Princípio II**
4. **PARAR e VALIDAR**: os dois princípios não negociáveis do projeto (CLAUDE.md) estão demonstráveis
5. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → base pronta
2. US1 → validar Princípio I → demo
3. US2 → validar Princípio II → demo
4. US3 → grafo + sincronização → demo
5. US4 → legenda + publicação pública → app publicado
6. US5 → teste de compreensão sobre app publicado → fecha critério de aceite da Sprint 3

---

## Notes

- [P] = arquivos diferentes, sem dependência pendente
- Nenhuma tarefa desta lista modifica `data/raw/` ou os schemas de `specs/001-atlas-atos/contracts/` (Princípio V / escopo desta feature)
- T008/T010/T017/T024 são as tarefas mais diretamente ligadas aos gates de constituição (I, II, restrição de escopo) — não pular ao revisar
- Decisões de peso visual, forma de marcador, cluster de grafo, rubrica de teste de compreensão e publicação vêm da sessão de grill 2026-08-19 — ver `CONTEXT.md` e `research.md` para o racional completo
- Commitar após cada tarefa ou grupo lógico
- Parar em qualquer checkpoint para validar a story isoladamente
