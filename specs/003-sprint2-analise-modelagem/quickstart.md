# Quickstart: Sprint 2 — Análise de Rede e Modelagem

Pré-requisito: Sprint 1 completa (`uv run python -m pipeline.sprint1` ou `just sprint1`), `data/processed/places.json` existente.

## Rodar os módulos desta sprint

```bash
uv run python -m pipeline.s04_build_graph
uv run python -m pipeline.s05_uncertainty
uv run python -m pipeline.s06_communities
uv run python -m pipeline.s07_linkpred
uv run python -m pipeline.s08_export
```

Ao final, devem existir (além dos artefatos da Sprint 1):

- `data/processed/graph.json` (conforme `specs/001-atlas-atos/contracts/graph.schema.json`)
- `data/processed/uncertainty.json` (conforme `uncertainty.schema.json`)
- `data/processed/linkpred.json` (conforme `linkpred.schema.json`)
- `docs/community-comparison.md` (NMI/ARI vs partição narrativa — artefato de relatório, não contrato de UI)

## Verificação manual (mapeada às User Stories do spec)

1. **US1** — Abrir `graph.json`. Confirmar que todo lugar de `places.json` (localizável) aparece como nó, mesmo os isolados (sem aresta). Confirmar `degree`/`betweenness` presentes.
2. **US2** — Abrir `uncertainty.json`. Confirmar que as 5 métricas de distância têm `mean`/`ci_low`/`ci_high`/`deterministic`. Rodar `s05_uncertainty` duas vezes e confirmar saída idêntica (mesma seed).
3. **US3** — Abrir `docs/community-comparison.md`. Confirmar presença de NMI, ARI, e contagem de comunidades desconexas (mesmo que zero).
4. **US4** — Abrir `linkpred.json`. Confirmar 6 modelos × 2 estratégias = 12 entradas em `results[]`. Conferir que nenhum par com voto negativo do catálogo original aparece em `top_candidates[]` como `in_catalog=false` com origem espúria.

## Tempo (SC-007)

```bash
time (uv run python -m pipeline.s04_build_graph && \
      uv run python -m pipeline.s05_uncertainty && \
      uv run python -m pipeline.s06_communities && \
      uv run python -m pipeline.s07_linkpred && \
      uv run python -m pipeline.s08_export)
```

Registrar o tempo total no relatório (SC-007) — sem meta fixa, só medição honesta.
