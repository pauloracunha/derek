# Atlas de Atos

Pipeline de dados + web app que visualiza a rede de lugares do livro de Atos
preservando a incerteza arqueológica de localização.

## Princípios não negociáveis

1. NUNCA colapsar múltiplos candidatos de localização em um ponto único.
   Isso é precisamente a falha que o projeto existe para corrigir.
2. NUNCA descartar silenciosamente lugares não localizáveis. Eles aparecem
   na UI com a razão explícita.
3. `lonlat` no dataset de origem é "longitude,latitude" — NESTA ORDEM.
4. `sort` (BBCCCVVV) é STRING. Nunca converter para inteiro.
5. Nenhum dado de origem é modificado. Toda transformação é derivada e
   reprodutível a partir do bruto.
6. Se um resultado de análise for fraco ou contrariar a hipótese, reportar
   como está. Não ajustar o experimento até obter o resultado desejado.

Ver constituição completa em `.specify/memory/constitution.md`.

## Comandos

- `just sprint1`    — Sprint 1 completa num comando só (download→carga→extração→exportação)
- `just data`       — baixa fontes brutas
- `just test`       — pytest (rápido, sem rede — exclui `slow`)
- `just test-slow`  — pytest com rede real/ambiente limpo (`@pytest.mark.slow`)
- `just web`        — dev server do frontend
- `just pipeline`   — comentado (reativar quando Sprint 3/UI decidir o fluxo completo)

## Estado atual

<!-- atualizar a cada sessão -->
`001-atlas-atos`: Setup + Foundational implementados e testados (24/66 tasks) — pipeline real (s01-s03+s08 parcial), web renderiza layout base com dados reais. US1-US4 + Fase 7 + Polish ainda não implementados.

`002-fechar-lacunas-sprint1`: implementado e testado (17/18 tasks — T017 é verificação manual). Sprint 1 roda de ponta a ponta com `just sprint1`, evidência persistida em `docs/schema.md`/`docs/candidate-distribution.md`, teste renomeado para `test_no_candidate_collapse.py`. 16 testes rápidos + 2 lentos, todos passando.

`003-sprint2-analise-modelagem`: implementado e testado (27/31 tasks — T028-T031 são polish/verificação). `pipeline/s04-s07` completos: grafo (107 nós/1059 arestas/0 isolados), Monte Carlo (4 métricas escalares + ranking de centralidade), comunidades (5, NMI=0,24/ARI=0,11 vs. partição narrativa), link prediction (rede ego 7.821 nós/38.766 arestas, 12 combinações modelo×amostragem — `distance_matched` sistematicamente mais difícil que `random`). `s08_export.py` gera os 4 artefatos (`places.json`, `graph.json`, `uncertainty.json`, `linkpred.json`) em ~105s. 25 testes (22 rápidos + 3 lentos), todos passando.

## Decisões arquiteturais

Ver `docs/decisions.md` e `docs/adr/` (5 ADRs registrados durante a implementação de `001-atlas-atos`).

<!-- SPECKIT START -->
Plano ativo: [specs/004-sprint3-interface-validacao/plan.md](specs/004-sprint3-interface-validacao/plan.md)
<!-- SPECKIT END -->
