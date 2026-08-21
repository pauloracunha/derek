# Data Model: Fechar Lacunas de Evidência da Sprint 1

Esta feature não introduz entidades de domínio novas (não toca `Place`, `LocationCandidate` etc. de `001-atlas-atos/data-model.md`). Os "dados" aqui são dois artefatos de documentação gerada.

## SchemaArtifact (`docs/schema.md`)

Gerado ao final de `pipeline/s02_load.py`. Uma seção por tabela carregada.

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `generated_at` | string (ISO 8601) | derivado (timestamp da execução) | Cabeçalho do arquivo — indica que o conteúdo é gerado, não editado à mão |
| `tables[].name` | string | `PRAGMA table_info` / `information_schema` | Uma entrada por tabela (`ancient`, `modern`, `source`) |
| `tables[].columns[].name` | string | idem | — |
| `tables[].columns[].type` | string | idem | Tipo real inferido pelo DuckDB no momento da carga — não um tipo presumido |
| `tables[].row_count` | int | `SELECT count(*)` | Confere com a contagem já validada em `docs/data-contracts.md` (1342/1596/442) |

**Regra de sobrescrita**: toda execução de `s02_load.py` sobrescreve `docs/schema.md` inteiro — nunca acrescenta a um arquivo anterior (Edge Case do spec: sem arquivos órfãos).

## CandidateDistributionArtifact (`docs/candidate-distribution.md`)

Gerado ao final de `pipeline/s03_extract_acts.py`. Mesmo cálculo que já existe em `report_candidate_distribution()` — só ganha um segundo destino de escrita.

| Campo | Tipo | Origem | Regra |
|---|---|---|---|
| `generated_at` | string (ISO 8601) | derivado | Idem acima |
| `locatable_count` | int | `report_candidate_distribution()` | Total de lugares localizáveis |
| `with_1_candidate` / `with_2_candidates` / `with_3plus_candidates` | int + % | idem | Mesmos números já impressos hoje no terminal |
| `unlocatable_count` | int | idem | — |
| `threshold_pct` | float (15.0) | constante do projeto | Limiar de decisão citado em `definitions.md` §5.1 e `relatorio.md` P2 |
| `threshold_crossed` | boolean | derivado (`multi_candidate_pct >= threshold_pct`) | FR-004 — indicação explícita de qual lado do limiar, nunca implícita |

**Regra de sobrescrita**: mesma regra do artefato de esquema — sempre reflete a execução mais recente (Edge Case do spec).

## Relacionamentos

```
s02_load.py  --gera-->  SchemaArtifact (docs/schema.md)
s03_extract_acts.py  --gera-->  CandidateDistributionArtifact (docs/candidate-distribution.md)
pipeline/sprint1.py  --orquestra-->  s01_download → s02_load → s03_extract_acts → s08_export.export_places
```

Nenhum dos dois artefatos é lido de volta por código — são terminais (consumidos por humanos avaliando o projeto), diferente de `places.json`/`graph.json`, que são contratos programáticos consumidos pelo frontend.

## Invariantes de validação (mapeadas para `tests/`)

1. Após rodar `pipeline/sprint1.py` (ou `s02_load.py` isoladamente), `docs/schema.md` existe e lista exatamente as 3 tabelas (`ancient`, `modern`, `source`) com `row_count` > 0 — `tests/test_sprint1_evidence_artifacts.py`.
2. Após rodar `pipeline/sprint1.py` (ou `s03_extract_acts.py` isoladamente), `docs/candidate-distribution.md` existe, contém os 4 números (1/2/3+/não-localizáveis) e o campo `threshold_crossed` — `tests/test_sprint1_evidence_artifacts.py`.
3. `tests/test_no_candidate_collapse.py` existe com esse nome exato e contém o teste que verifica a garantia de não-colapso (Constitution I) — verificável por busca textual direta (SC-003 do spec).
4. `uv run python -m pipeline.sprint1` executado em ambiente limpo termina com sucesso e produz `data/processed/places.json`, `docs/schema.md`, `docs/candidate-distribution.md` numa única invocação — `tests/test_sprint1_evidence_artifacts.py` (marcado como teste de integração, mais lento).
