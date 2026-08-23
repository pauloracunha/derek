# Relatório da Sprint 3 — Interface e Validação

**Feature**: `specs/004-sprint3-interface-validacao/` · **Período**: 2026-08-17 a 2026-08-23 · **Status**: 34/43 tasks (US1–US4 completas; US5 e Polish parcialmente bloqueados) · **Testes**: 11/11 Vitest passando, lint limpo

Esta sprint fecha a camada visual sobre o pipeline das Sprints 1–2, cobrindo US1–US4 de `specs/004-sprint3-interface-validacao/spec.md`: mapa com todos os candidatos de localização visíveis simultaneamente (Princípio I), painel de lugares não localizáveis (Princípio II), grafo de coocorrência sincronizado com a timeline de capítulos, e publicação pública. US5 (teste de compreensão com usuários reais, H4/SC-003) depende de ação humana e permanece aberta.

---

## 1. Mapa com todos os candidatos visíveis (`Map.tsx`) — US1, Princípio I

Um marcador por `LocationCandidate` de cada lugar localizável — nunca só o candidato de maior score.

- **Peso visual** (`web/src/services/visualWeight.ts`): `opacity = 0.15 + 0.85·probability`, `radius = 4 + 12·probability` — piso mínimo garante que nenhum candidato de baixa probabilidade fique invisível ou inclicável.
- **Vínculo entre candidatos**: linha tracejada + cor compartilhada conecta candidatos do mesmo lugar, exibida só quando esse lugar está selecionado.
- **Forma do marcador**: canal independente de cor — círculo sólido para `'point'`; quadrado/anel pontilhado para `'center' | 'representative point' | 'settlement'` — distinguindo ponto exato de área aproximada (FR-003), sem competir com a cor reservada para comunidade (US3).
- **Regressão testada**: `Map.test.tsx` confirma que, para lugar com 2+ candidatos, todos renderizam e nenhum fica abaixo do piso de opacidade/raio.

---

## 2. Painel de não localizáveis (`UnlocatablePanel.tsx`) — US2, Princípio II

Lista 100% dos lugares `is_locatable: false`, cada um com `special_reason` traduzido para texto legível (`unknown_place`, `nonspecific_place`, `multiple_locations`, `no_candidates_resolved`). `Map.tsx` garante que esses lugares nunca geram marcador — só aparecem no painel.

**Regressão testada**: `UnlocatablePanel.test.tsx` confirma que o número de itens renderizados bate exatamente com `places.filter(p => !p.is_locatable).length` — nenhum lugar descartado silenciosamente.

---

## 3. Grafo sincronizado com a timeline (`NetworkGraph.tsx` + `ChapterTimeline.tsx`) — US3

Layout `d3-force` sobre `graph.json` (107 nós/1.059 arestas, Sprint 2), colorido por comunidade, com força customizada atraindo cada nó a um centroide fixo por `community` (cluster sem lib nova).

- **Timeline**: range slider duplo (capítulos 1–28) ligado a `chapterRange` no store — mesmo estado já usado por `placeInChapterRange` no mapa.
- **Filtro de arestas**: `edge.chapters` interseccionado com `chapterRange`; nós sem aresta na faixa permanecem visíveis, isolados — nunca somem do grafo (Princípio II aplicado a nó de grafo).
- **Comunidade desconexa**: sinalizada visualmente (borda tracejada + texto) quando `community_is_connected === false`, nunca omitida (FR-006).
- **Seleção cruzada**: clique em nó do grafo chama o mesmo `selectPlace()` usado pelo mapa — sem estado novo.

**Regressão testada**: `NetworkGraph.test.tsx` cobre `edgeInChapterRange` diretamente; "nó sempre renderizado" garantido estruturalmente — o componente nunca filtra `layout.nodes`, só `links`.

---

## 4. Legenda, atribuição e publicação (`Legend.tsx`, `Footer.tsx`) — US4

`Legend.tsx` explica opacidade/tamanho = probabilidade (com piso mínimo) e forma do marcador = área vs. ponto exato. `Footer.tsx` traz atribuição de licença das fontes (OpenBible.info Bible-Geocoding-Data e cross-references, CC-BY). Ambos sempre visíveis em `App.tsx`, não atrás de menu.

**Publicação**: repositório dedicado `github.com/pauloracunha/derek` (project site, não user site — `pauloracunha.github.io` estava reservado para outro projeto). `base: '/derek/'` em `vite.config.ts`; `dataLoader.ts` usa `import.meta.env.BASE_URL` em vez de caminho absoluto. Deploy via GitHub Pages, branch `gh-pages` (`web/dist` como orphan branch).

**URL pública confirmada (200, sem login)**: **https://pauloracunha.github.io/derek/**
- `/derek/` → 200
- `/derek/data/places.json` → 200

---

## 5. Teste de compreensão (US5, H4) — bloqueado, ação humana

`docs/usability-test.md` criado com a tabela de campos (`participant_id`, `date`, `explained_correctly`, `justification`, `notes`) e rubrica de `explained_correctly`: `true` se o participante expressar a ideia de múltiplas hipóteses conflitantes de localização, sem exigir termo técnico.

**Não rodado nesta sprint**: prazo (2026-08-17 a 2026-08-23) fechou antes de recrutar e conduzir sessões com participantes reais — publicação (US4) só ficou disponível perto do fim da janela, sem tempo hábil para agendar 3–5 sessões. Fica como pendência explícita para a próxima sprint, não como resultado forçado (Princípio VI).

**Pendente**: conduzir sessões com 3–5 participantes reais sobre a aplicação publicada, sem explicação prévia da equipe; registrar cada sessão conforme conduzida (não em lote, para evitar viés de memória); calcular taxa de acerto agregada frente à meta de 80% (SC-003), reportando como está — sem ajustar amostra ou critério post-hoc (Princípio VI).

---

## 6. Estado de testes e lint

- **Vitest**: 4 arquivos, 11 testes, todos passando (`Map.test.tsx`, `UnlocatablePanel.test.tsx`, `NetworkGraph.test.tsx`, `Legend.test.tsx`).
- **Lint** (`just lint` = `ruff` + `eslint`): 0 erros; 1 warning cosmético de fast-refresh em `NetworkGraph.tsx`, não bloqueante.
- **Build**: `npm run build` sem erro; `web/dist` validado com `base: '/derek/'`.
- **Validação manual**: `curl` confirma 200 em `/derek/`, `/derek/data/places.json` (107 lugares) e `/derek/data/graph.json`; validação visual completa (candidatos coincidindo no mapa) ainda requer sessão de navegador real — não substituída por este check.

---

## 7. Tarefas bloqueadas (ação humana, não automatizável)

- **T036–T038** (US5): conduzir e registrar sessões de teste de compreensão, calcular taxa de acerto.
- **T042**: atualizar `CLAUDE.md` § Estado atual com achados reais do teste de compreensão — depende de T036–T038.
- **T043**: fechar `relatorio.md` § Sprint 3 (R3.1–R3.6) com evidência de cada artefato — depende de T038.

## 8. O que esta sprint não faz (por decisão, não por lacuna)

- `linkpred.json` e comparação NMI/ARI de comunidades (Sprint 2) não aparecem na UI interativa — decisão já registrada em `001-atlas-atos`, não reaberta aqui; permanecem só no relatório escrito.
- Otimização para telas móveis fica fora de escopo, conforme já assumido em `001-atlas-atos`.
- Nenhum dado de `data/raw/` ou schema de `specs/001-atlas-atos/contracts/` foi modificado (Princípio V).
