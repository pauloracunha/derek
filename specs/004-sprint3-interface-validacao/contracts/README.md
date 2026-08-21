# Contratos consumidos por esta feature

Esta feature não define contratos novos — consome os quatro contratos já publicados e
congelados em `specs/001-atlas-atos/contracts/`:

| Contrato | Consumido por | Uso |
|---|---|---|
| [`places.schema.json`](../../001-atlas-atos/contracts/places.schema.json) | US1, US2, US4 | mapa, painel de detalhe, painel de não-localizáveis, legenda de dispersão |
| [`graph.schema.json`](../../001-atlas-atos/contracts/graph.schema.json) | US3 | grafo de coocorrência, agrupamento por comunidade, sinalização `community_is_connected` |
| [`uncertainty.schema.json`](../../001-atlas-atos/contracts/uncertainty.schema.json) | Fora da UI interativa (relatório) — citado aqui só por completude do pipeline | não consumido por componente novo desta feature |
| [`linkpred.schema.json`](../../001-atlas-atos/contracts/linkpred.schema.json) | Fora de escopo — decisão já registrada (001-atlas-atos, Clarifications) | não consumido pela UI |

Qualquer alteração de forma nesses contratos é uma mudança de escopo em
`001-atlas-atos`, não desta feature — se necessária, deve ser proposta lá primeiro.

`web/src/services/dataLoader.ts` já espelha `places.schema.json` em `LocationCandidate`
e `Place`. Esta feature estende `dataLoader.ts` para carregar também `graph.json`
(tipos `GraphNode`/`GraphEdge`, ainda não definidos — ver `data-model.md`).
