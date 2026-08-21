# Implementation Plan: Sprint 2 — Análise de Rede e Modelagem

**Branch**: `003-sprint2-analise-modelagem` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-sprint2-analise-modelagem/spec.md`

## Summary

Implementa os módulos `s04_build_graph.py`, `s05_uncertainty.py`, `s06_communities.py` e `s07_linkpred.py` do pipeline — construção do grafo de coocorrência de lugares por capítulo, métricas topológicas, propagação de incerteza via Monte Carlo restrita a métricas de distância, detecção de comunidades comparada a uma partição narrativa de referência, e predição de links sobre a rede de referências cruzadas com 6 modelos × 2 estratégias de amostragem negativa. Os contratos de saída (`graph.json`, `uncertainty.json`, `linkpred.json`) já foram definidos em `001-atlas-atos/contracts/` — esta feature os implementa, não os redefine. Não inclui UI (Sprint 3).

## Technical Context

**Language/Version**: Python 3.11+ (mesmo ambiente de `001`/`002`)

**Primary Dependencies**: `networkx` (grafo, Louvain, métricas topológicas — já instalado), `scikit-learn` + `node2vec` (link prediction — já instalado), `pyproj` (distância geodésica WGS84 — já instalado). Nenhuma dependência nova além das já declaradas em `001-atlas-atos/plan.md`.

**Storage**: Lê `data/processed/places.json` (saída de `001`) e `data/raw/cross-references.txt` (já baixado por `s01_download.py`). Escreve `data/processed/graph.json`, `uncertainty.json`, `linkpred.json` (contratos já definidos), mais um artefato de relatório para NMI/ARI (mesmo padrão de `docs/*.md` gerado, estabelecido em `002-fechar-lacunas-sprint1`).

**Testing**: `pytest` — testes de invariante por módulo (conectividade de comunidade, invariância topológica sob Monte Carlo, presença das 2 estratégias de amostragem negativa por modelo), seguindo o padrão já estabelecido (`tests/test_*.py`, marcador `slow` para o que precisar da rede de referências cruzadas completa).

**Target Platform**: Mesmo ambiente local/CI do restante do pipeline.

**Project Type**: Extensão do pipeline Python existente (`pipeline/`) — sem frontend novo.

**Performance Goals**: Monte Carlo com 1000 simulações deve rodar em segundos a poucos minutos nesta escala (~100 lugares, grafo de coocorrência pequeno) — sem meta formal de latência, mesma postura de `001-atlas-atos/plan.md`.

**Constraints**: Constitution VI (Monte Carlo só em métricas de distância, nunca topológicas); ADR 0002 (itinerário narrativo revisita lugares); ADR 0001 (reprodutibilidade escopada ao lockfile, seed inteira); FR-014 desta spec (votos negativos de referência cruzada nunca contam como conexão positiva — mesma disciplina do ADR 0003).

**Scale/Scope**: Grafo de coocorrência ~107 lugares localizáveis (Sprint 1). Rede de referências cruzadas em torno de Atos: ego de raio 1 a partir dos versículos de Atos dentro de `cross-references.txt` (344.790 pares no catálogo completo, subconjunto bem menor restrito à vizinhança de Atos).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Status |
|---|---|---|
| I. Incerteza nunca colapsa | Não aplicável diretamente — esta sprint não toca `candidates[]`; consome `places.json` já correto | N/A |
| II. Lugar não-localizável nunca desaparece | Grafo de coocorrência inclui só lugares localizáveis (spec FR-001 usa o catálogo já filtrado); lugares não-localizáveis continuam intactos em `places.json`, não tocados aqui | N/A |
| III. Ordem `lon,lat` | Reusa `lon`/`lat` já corretos de `places.json` para distância geodésica | PASS |
| IV. Chaves canônicas são string | `sort`/`verses` já vêm como string de `places.json`; nenhuma conversão nova | PASS |
| V. Dados de origem imutáveis | `cross-references.txt` em `data/raw/` só é lido, nunca escrito | PASS |
| VI. Resultado fraco é resultado válido | FR-015 exige reportar resultado fraco/nulo como está (heurística vencendo ML, rede insuficiente, IC estreito) — sem gate de "sucesso" artificial | PASS |

Nenhuma violação. Sem necessidade de `Complexity Tracking`.

**Re-check pós-Fase 1**: `data-model.md` mantém `CooccurrenceEdge`/`Community`/`LinkCandidate` consistentes com `001-atlas-atos/data-model.md` (mesmas entidades, sem redefinição divergente); `graph.schema.json`/`uncertainty.schema.json`/`linkpred.schema.json` de `001` continuam a fonte de verdade do contrato — nenhum campo novo introduzido sem necessidade. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/003-sprint2-analise-modelagem/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output — referencia 001-atlas-atos/data-model.md, não duplica
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

Sem `contracts/` própria: os contratos (`graph.schema.json`, `uncertainty.schema.json`, `linkpred.schema.json`) já existem em `specs/001-atlas-atos/contracts/` e são reusados como estão — criar uma cópia aqui duplicaria a fonte de verdade.

### Source Code (repository root, alterações sobre `001-atlas-atos`)

```text
pipeline/
├── s04_build_graph.py      # NOVO — grafo de coocorrência + métricas topológicas
├── s05_uncertainty.py      # NOVO — Monte Carlo sobre métricas de distância
├── s06_communities.py      # NOVO — detecção de comunidades + NMI/ARI vs partição de referência
├── s07_linkpred.py         # NOVO — predição de links (6 modelos × 2 amostragens negativas)
└── s08_export.py           # MODIFICADO — estende para incluir graph.json/uncertainty.json/linkpred.json

tests/
├── test_topology_unaffected.py              # NOVO
├── test_community_connectivity.py           # NOVO
├── test_montecarlo_seed_reproducibility.py  # NOVO
└── test_negative_sampling_both_reported.py  # NOVO

docs/
└── community-comparison.md  # NOVO — NMI/ARI vs partição narrativa, mesmo padrão de docs/*.md gerado
```

**Structure Decision**: Mesma estrutura monorepo de `001-atlas-atos` — só adiciona os 4 módulos de pipeline previstos desde o planejamento original (`001-atlas-atos/plan.md` já continha essa árvore) mais os testes correspondentes, hoje ainda não implementados.

## Complexity Tracking

*Sem violações de constituição a justificar.*
