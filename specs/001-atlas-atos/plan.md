# Implementation Plan: Atlas de Atos — Visualização de Rede de Lugares com Incerteza Preservada

**Branch**: `001-atlas-atos` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-atlas-atos/spec.md`

## Summary

Pipeline reprodutível (Python) que extrai os lugares mencionados no livro de Atos a partir do dataset `openbibleinfo/Bible-Geocoding-Data`, normaliza cada candidato de localização em `modern_associations` como uma probabilidade explícita (nunca colapsando para um único ponto), constrói o grafo de coocorrência por capítulo, propaga a incerteza locacional via Monte Carlo apenas nas métricas que dependem de distância, detecta comunidades, avalia predição de links sobre a rede de referências cruzadas com duas estratégias de amostragem negativa, e exporta quatro artefatos JSON estáticos. Uma aplicação web estática (mapa + grafo + painéis) consome esses artefatos para permitir a exploração interativa do núcleo do produto (User Stories 1–4 do spec); análises avançadas (link prediction, NMI/ARI) ficam documentadas apenas no relatório escrito, por decisão registrada na sessão de clarificação.

## Technical Context

**Language/Version**: Python 3.11+ (pipeline) e TypeScript (frontend, via Vite)

**Primary Dependencies**: `uv` (gerenciador Python), DuckDB (armazenamento intermediário/joins), Polars ou pandas (manipulação tabular), `networkx` (grafo e Louvain), `python-igraph`+`leidenalg` (alternativa Leiden, opcional), `scikit-learn` + `node2vec` (link prediction), `pyproj`/`geopy` (distância geodésica WGS84); React + MapLibre GL JS (mapa), `d3-force` (grafo em painel lateral), Zustand ou Context (estado)

**Storage**: Arquivos — DuckDB local (`data/interim/`, não versionado) para processamento intermediário; JSON estático versionado em `data/processed/` como saída final consumida pelo frontend. Sem banco de dados servidor.

**Testing**: `pytest` para o pipeline (testes da seção 10 do documento de definição: ordem de coordenadas, integridade de probabilidade, preservação de candidatos, sem colapso, chave canônica, reprodutibilidade). Testes de frontend a definir na fase de tasks (não bloqueiam este plano).

**Target Platform**: Site estático (deploy em Vercel, Netlify ou GitHub Pages); pipeline roda localmente/CI, não em runtime de produção.

**Project Type**: Web application (pipeline de dados Python + frontend estático React/TypeScript) — projeto de dois componentes (`pipeline/` e `web/`) compartilhando artefatos JSON como contrato.

**Performance Goals**: Não há meta de alta concorrência (Constitution: uso de baixa concorrência, não produção em larga escala). Meta qualitativa: interação no mapa/grafo responsiva o suficiente para não atrapalhar o teste de compreensão (SC-003) — sem alvo numérico formal de latência, pois a escala de dados é pequena (~100 lugares, dataset estático pré-processado).

**Constraints**: Sem backend em runtime (FR não-negocial); dados de origem imutáveis (Constitution V); toda simulação estocástica usa seed fixa e é byte-reprodutível (Constitution VI / testes §10); Monte Carlo restrito a métricas dependentes de distância (Constitution, spec FR-014).

**Scale/Scope**: Escopo fixo ao livro de Atos (~28 capítulos, ordem de grandeza de ~100 lugares e algumas centenas de versículos); grafo ego de referências cruzadas de raio 1 a partir de Atos (ordem de grandeza de milhares de arestas, conforme `linkpred.json` de referência: ~1200 nós, ~9000 arestas).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Status |
|---|---|---|
| I. Incerteza nunca colapsa | Contratos `places.json`/`data-model.md` preservam array `candidates` completo por lugar; FR-002 exige exibição de todos os candidatos | PASS |
| II. Lugar não-localizável nunca desaparece | `is_locatable=false` + `special_reason` no contrato de dados; FR-005/FR-006 distinguem "mantém com razão" de "exclui de fato" | PASS |
| III. Ordem `lon,lat` | Documentado explicitamente em `data-model.md` e testado (teste de bbox do Mediterrâneo oriental) | PASS |
| IV. Chaves canônicas são string | `sort` tipado como string em todo contrato de dados | PASS |
| V. Dados de origem imutáveis | `data/raw/` somente leitura; pipeline em estágios numerados (`s01`..`s08`) sempre reprocessa do bruto | PASS |
| VI. Resultado fraco é resultado válido | `research.md` e contratos de saída incluem explicitamente o caminho de reporte de resultado fraco (ex.: `<15%` multi-candidato, heurística vencendo embedding) sem gate de "sucesso" artificial | PASS |

Nenhuma violação. Sem necessidade de `Complexity Tracking`.

**Re-check pós-Fase 1** (após `data-model.md` e `contracts/`): schemas de `places.json` e `graph.json` exigem estruturalmente os campos que sustentam os Princípios I–IV (`candidates` array completo, `special_reason` obrigatório quando `is_locatable=false`, `lon`/`lat` como pares nomeados explícitos, `sort`/`verses` tipados como string). `linkpred.json` exige as duas estratégias de amostragem negativa por modelo. Nenhuma violação introduzida pelo design. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-atlas-atos/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── places.schema.json
│   ├── graph.schema.json
│   ├── uncertainty.schema.json
│   └── linkpred.schema.json
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
atlas-atos/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── justfile
├── data/
│   ├── raw/                   # .gitignore — downloads brutos (ancient.jsonl, modern.jsonl, source.jsonl, cross-refs)
│   ├── interim/                # .gitignore — duckdb
│   └── processed/              # versionado — places.json, graph.json, uncertainty.json, linkpred.json
├── pipeline/
│   ├── __init__.py
│   ├── config.py               # BOOK_ID=44, URLs, hashes
│   ├── s01_download.py
│   ├── s02_load.py              # jsonl → duckdb
│   ├── s03_extract_acts.py      # filtro + normalização (valida H1)
│   ├── s04_build_graph.py
│   ├── s05_uncertainty.py       # Monte Carlo espacial
│   ├── s06_communities.py
│   ├── s07_linkpred.py
│   └── s08_export.py            # → data/processed/*.json
├── tests/
│   ├── test_coordinates_order.py
│   ├── test_probability_integrity.py
│   ├── test_candidate_preservation.py
│   ├── test_no_candidate_collapse.py
│   ├── test_canonical_key.py
│   └── test_reproducibility.py
├── docs/
│   ├── data-contracts.md        # formatos observados, não presumidos
│   └── decisions.md             # ADRs curtos
└── web/
    ├── package.json
    ├── vite.config.ts
    ├── public/data/              # cópia/symlink de data/processed
    └── src/
        ├── components/           # Map, NetworkGraph, PlaceDetail, UnlocatablePanel, Legend, ChapterTimeline
        ├── state/                # store (Zustand/Context)
        └── services/             # carregamento e parsing dos JSON de data/processed
```

**Structure Decision**: Monorepo de dois componentes (`pipeline/` Python + `web/` TypeScript/React) unidos pelo contrato de arquivos JSON em `data/processed/`, servido estaticamente em `web/public/data/`. Corresponde à Opção "Web application" do template, adaptada: aqui "backend" é substituído por um pipeline batch offline (sem servidor em runtime), e "frontend" consome artefatos pré-computados em vez de uma API.

## Complexity Tracking

*Sem violações de constituição a justificar.*
