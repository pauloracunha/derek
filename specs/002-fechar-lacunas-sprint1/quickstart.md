# Quickstart: Fechar Lacunas de Evidência da Sprint 1

## Rodar a Sprint 1 completa com um único comando

```bash
uv run python -m pipeline.sprint1
```

Ao final, devem existir:

- `data/processed/places.json` (catálogo de lugares — já existia)
- `docs/schema.md` (novo — esquema real das tabelas carregadas)
- `docs/candidate-distribution.md` (novo — distribuição de candidatos + indicação do limiar)

Se qualquer etapa falhar (ex.: rede indisponível no download), a execução para nessa etapa com mensagem clara — não segue adiante com dado parcial.

## Verificação manual (mapeada às User Stories do spec)

1. **US1** — Abrir `docs/schema.md` sem rodar nada. Confirmar que lista as 3 tabelas (`ancient`, `modern`, `source`) com campos, tipos e contagem de linhas.
2. **US2** — Abrir `docs/candidate-distribution.md` sem rodar nada. Confirmar que mostra 1/2/3+ candidatos, lugares não-localizáveis, e se o limiar de 15% foi ultrapassado.
3. **US3** — Buscar `test_no_candidate_collapse` no projeto por nome de arquivo (`find tests/ -name "test_no_candidate_collapse.py"` — é um nome de arquivo, `grep` de conteúdo não serve aqui). Confirmar que corresponde a `tests/test_no_candidate_collapse.py`, arquivo real e executável (`uv run pytest tests/test_no_candidate_collapse.py -v`).
4. **US4** — Rodar `rm -rf data/raw data/interim data/processed docs/schema.md docs/candidate-distribution.md` (ambiente limpo) e depois `uv run python -m pipeline.sprint1`. Confirmar que termina sem erro e produz os 3 artefatos numa execução só.

## Reexecução (idempotência — SC-006)

```bash
uv run python -m pipeline.sprint1
uv run python -m pipeline.sprint1
```

Confirmar que `docs/schema.md` e `docs/candidate-distribution.md` têm o mesmo conteúdo após a segunda execução (exceto `generated_at`), sem arquivos duplicados.
