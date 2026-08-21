# Implementation Plan: Sprint 3 — Interface e Validação

**Branch**: `004-sprint3-interface-validacao` | **Date**: 2026-08-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-sprint3-interface-validacao/spec.md`

## Summary

Fechar as User Stories US1–US5 desta feature (que herdam US1–US4 de
`specs/001-atlas-atos/spec.md`) sobre a base já existente em `web/` (Vite + React 19 +
Zustand, `store.ts` com `chapterRange` compartilhado, `dataLoader.ts` carregando
`places.json`). Implementar componentes de mapa (MapLibre GL), painel de detalhe/incerteza,
painel de não-localizáveis, grafo de coocorrência (d3-force) com filtro por capítulo,
legenda/atribuição fixas, publicar a build estática, e conduzir teste de compreensão com
3–5 participantes.

## Technical Context

**Language/Version**: TypeScript ~6.0 / React 19.2, Node.js (via Vite 8)

**Primary Dependencies**: `maplibre-gl` (mapa), `d3-force` (layout de grafo), `zustand`
(estado compartilhado mapa↔grafo↔timeline), React 19

**Storage**: N/A — dados estáticos pré-processados em `web/public/data/*.json`, copiados
de `data/processed/` pelo pipeline (`s08_export.py`)

**Testing**: Vitest/Testing Library para componentes (a confirmar em research.md — projeto
`web/` ainda não tem test runner configurado); Playwright ou teste manual para fluxo E2E
do teste de compreensão

**Target Platform**: navegador (site estático), sem otimização mobile (fora de escopo,
herdado de 001-atlas-atos)

**Project Type**: web — frontend único (`web/`), sem backend em runtime (site estático);
dados vêm de arquivos JSON versionados/gerados pelo pipeline Python em `pipeline/`

**Performance Goals**: carregamento inicial utilizável em conexão padrão (SC-005); sem
meta numérica de fps/latência — escala é ~107 lugares / ~1059 arestas (grafo já
dimensionado em `003-sprint2-analise-modelagem`), não exige otimização de grandes volumes

**Constraints**: sem backend em runtime (constituição, "Restrições de escopo"); nunca
colapsar candidatos (Princípio I); nunca esconder lugar não-localizável (Princípio II);
`lonlat` é `lon,lat` (Princípio III) — `dataLoader.ts` já expõe `lon`/`lat` separados,
must-preserve essa ordem em qualquer novo consumo de `lonlat`

**Scale/Scope**: 107 lugares, ~1059 arestas de coocorrência, 5 comunidades — dataset
pequeno, sem paginação/virtualização necessária

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Como esta feature cumpre |
|---|---|
| I. Incerteza nunca colapsa | US1/FR-002: todos os candidatos de um lugar renderizados simultaneamente, peso visual (opacidade+tamanho) proporcional a `probability`. Nenhum componente planejado seleciona "o melhor candidato" para exibição isolada. |
| II. Lugar não-localizável nunca desaparece | US2/FR-004: painel dedicado itera 100% dos lugares com `is_locatable: false`, exibindo `special_reason` traduzido para texto legível. Nenhum filtro de UI remove esses lugares da lista, só do mapa. |
| III. `lonlat` é `lon,lat` | Camada de mapa consome `candidate.lon`/`candidate.lat` já separados por `dataLoader.ts` — nenhuma leitura direta de string `lonlat` na feature web. |
| IV. `sort` é string | Não aplicável a esta feature (não há ordenação por `sort` na UI planejada; ordenação de lugares usa `dispersion_index`, numérico por natureza). |
| V. Dados de origem imutáveis | Feature só consome `web/public/data/*.json`, artefatos derivados já gerados por `s08_export.py`; nenhuma escrita em `data/raw/`. |
| VI. Resultado fraco é válido | Aplica-se ao teste de compreensão (US5): resultado abaixo de 80% é reportado como está no relatório (FR-011), sem ajustar critério ou amostra pós-hoc. |
| Restrição de escopo (analytics avançado fora da UI) | `linkpred.json` e comparação NMI/ARI permanecem fora do escopo desta feature (Assumptions), conforme decisão já registrada em 001-atlas-atos. |
| Deploy estático | FR-001/FR-009: aplicação consome JSON estático e é publicada sem backend em runtime. |

Nenhuma violação identificada. Gate PASSA sem necessidade de Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/004-sprint3-interface-validacao/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/            # Phase 1 output — referencia contratos já publicados em
│                          # specs/001-atlas-atos/contracts/*.schema.json (não duplicados)
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
web/
├── public/
│   └── data/                    # places.json, graph.json, uncertainty.json, linkpred.json
│                                 # (copiados de data/processed/ pelo pipeline)
├── src/
│   ├── components/
│   │   ├── Map.tsx               # US1 — MapLibre GL, candidatos com opacidade/tamanho
│   │   ├── PlaceDetail.tsx       # US1 — painel de detalhe do lugar selecionado
│   │   ├── UnlocatablePanel.tsx  # US2 — lugares sem localização + razão
│   │   ├── ChapterTimeline.tsx   # US3 — seletor de faixa de capítulos
│   │   ├── NetworkGraph.tsx      # US3 — grafo d3-force, agrupado por comunidade
│   │   ├── Legend.tsx            # US4 — legenda permanente da codificação visual
│   │   └── Footer.tsx            # US4 — texto explicativo + atribuição de licença
│   ├── services/
│   │   └── dataLoader.ts         # já existe — extender para graph.json/uncertainty.json
│   ├── state/
│   │   └── store.ts              # já existe — chapterRange compartilhado
│   ├── App.tsx                    # já existe — placeholders a substituir pelos componentes acima
│   └── App.css / index.css
└── tests/
    └── components/                # testes de componente (US1/US2/US3/US4)

docs/
└── usability-test.md             # US5 — registro das sessões de teste de compreensão
                                    # (3–5 participantes, acerto/erro + justificativa)
```

**Structure Decision**: projeto frontend único (`web/`), sem diretório `backend/` — a
aplicação é site estático que só lê os quatro JSONs pré-processados. Novos componentes
entram em `web/src/components/`, substituindo os placeholders já marcados em `App.tsx`
com comentários `US1`/`US2`/`US3`. Registro do teste de compreensão (US5) fica fora de
`web/`, em `docs/`, por ser evidência de processo, não código de produto.

## Complexity Tracking

*Sem violações de constituição a justificar — seção não aplicável.*
