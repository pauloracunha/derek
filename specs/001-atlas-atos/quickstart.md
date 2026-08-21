# Quickstart: Atlas de Atos

Guia mínimo para rodar o pipeline e a aplicação web localmente. Detalhes de setup real (comandos exatos de `justfile`/`pyproject.toml`) são definidos na fase de tasks — este documento fixa a sequência esperada.

## 1. Pipeline (Python)

```bash
just data       # baixa ancient.jsonl, modern.jsonl, source.jsonl e o arquivo de referências cruzadas
just pipeline    # executa s01..s08 em sequência
just test        # pytest — valida os 6 invariantes de data-model.md
```

Saída esperada em `data/processed/`:

- `places.json` — conforme `contracts/places.schema.json`
- `graph.json` — conforme `contracts/graph.schema.json`
- `uncertainty.json` — conforme `contracts/uncertainty.schema.json`
- `linkpred.json` — conforme `contracts/linkpred.schema.json` (artefato de relatório, não é lido pela UI)

**Checagem manual crítica após `s03_extract_acts.py`**: a tabela de distribuição de contagem de candidatos (1 / 2 / 3+) DEVE ser inspecionada antes de prosseguir — ela decide se o eixo narrativo principal do relatório é "incerteza de identificação" (H1 sustentada, ≥15% multi-candidato) ou "incerteza de precisão" (H1 fraca, pivotar para `lonlat_type`/precisão). Ver `research.md` item 1 e Edge Cases do spec.

## 2. Aplicação web

```bash
cd web
npm install
just web          # ou: npm run dev
```

Pré-requisito: `data/processed/*.json` já existir (copiado/symlinkado para `web/public/data/`). A UI não funciona com dados vazios/ausentes — não há fallback para dados sintéticos.

## 3. Roteiro de verificação manual (mapeado às User Stories do spec)

1. **US1 (P1)** — Selecionar um lugar com 2+ candidatos (ex.: um lugar em disputa arqueológica conhecida). Confirmar que todos os candidatos aparecem no mapa simultaneamente, com opacidade E tamanho proporcionais à probabilidade (FR-003, clarificação Q2).
2. **US2 (P1)** — Abrir o painel de lugares não-localizáveis. Confirmar que cada item tem uma razão legível (não um código como `unknown_place` cru) e que nenhum lugar sem localização conhecida está ausente do painel.
3. **US3 (P2)** — Selecionar uma faixa de capítulos na timeline. Confirmar que o grafo lateral filtra para os lugares/conexões relevantes e mostra agrupamento visual por comunidade.
4. **US4 (P3)** — Consultar as métricas de distância (no relatório ou painel de incerteza, conforme escopo definido em tasks). Confirmar presença de média + IC 95% + valor determinístico lado a lado.
5. **Legenda e texto explicativo (FR-007, FR-008)** — Confirmar que ambos estão sempre visíveis, sem exigir clique/hover para aparecer.
6. **Atribuição de licença (FR-016)** — Confirmar rodapé com atribuição OpenBible.info (CC BY 4.0) e OpenStreetMap (ODbL).

## 4. Teste de compreensão (SC-003)

Com 3 a 5 participantes reais que não conhecem o projeto: pedir para explorar livremente por ~5 min, depois perguntar "por que alguns lugares no mapa têm mais de um ponto?". Meta: ≥80% explica corretamente sem consultar a legenda/texto explicativo durante a pergunta.
