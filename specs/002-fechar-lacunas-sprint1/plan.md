# Implementation Plan: Fechar Lacunas de Evidência da Sprint 1

**Branch**: `002-fechar-lacunas-sprint1` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-fechar-lacunas-sprint1/spec.md`

## Summary

Feature de fechamento: persiste dois artefatos de evidência que hoje só existem transitoriamente no terminal (esquema das tabelas DuckDB, distribuição de contagem de candidatos), corrige a divergência de nome entre `tests/test_no_collapse.py` e o nome `test_no_candidate_collapse` citado em `relatorio.md` (CA1), e cria um comando único (`pipeline/sprint1.py`, executável via `uv run python -m pipeline.sprint1`) que roda download→carga→extração→exportação sem depender de estágios de sprints futuras (s04-s07, ainda inexistentes) nem do binário `just` (não garantido no ambiente). Não altera nenhuma lógica de negócio já validada em `001-atlas-atos` — é só persistência de evidência + correção de nome + orquestração.

## Technical Context

**Language/Version**: Python 3.11+ (mesmo ambiente de `001-atlas-atos`, sem dependência nova)

**Primary Dependencies**: Nenhuma nova. Reusa `duckdb` (introspecção de esquema via `information_schema`/`PRAGMA table_info`) e a lógica já existente em `pipeline/s01_download.py`, `s02_load.py`, `s03_extract_acts.py`, `s08_export.py`.

**Storage**: Artefatos de evidência (`docs/schema.md`, `docs/candidate-distribution.md`) são arquivos markdown versionados em `docs/` — nunca em `data/interim/` (gitignored, Constitution V) nem em `data/processed/` (reservado a contratos de dados consumidos pela UI, não a documentação de evidência).

**Testing**: `pytest` — teste renomeado (`tests/test_no_candidate_collapse.py`), mais um teste novo que verifica a existência e o formato mínimo dos dois artefatos após a execução do comando de Sprint 1.

**Target Platform**: Mesmo ambiente local/CI já usado pelo pipeline — sem infraestrutura nova.

**Project Type**: Extensão do pipeline Python existente (não introduz frontend nem contratos de API novos).

**Performance Goals**: Sem meta formal — a Sprint 1 completa já roda em poucos segundos com os dados atuais (~1300 registros brutos); nenhuma mudança nesta feature afeta a ordem de grandeza.

**Constraints**: FR-007/FR-008 (spec) — o comando único não pode invocar `s04`-`s07` (inexistentes) nem depender de `just` (não instalado neste ambiente, confirmado durante a validação da Sprint 1). FR-011 — não introduzir registro de commit/versão da fonte como efeito colateral.

**Scale/Scope**: Escopo mínimo — 2 artefatos novos, 1 arquivo de teste renomeado, 1 módulo novo de orquestração (`pipeline/sprint1.py`), sem mudança de schema de dados consumidos pela aplicação web.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Verificação | Status |
|---|---|---|
| I. Incerteza nunca colapsa | Não aplicável — feature não toca lógica de candidatos/probabilidade | N/A (sem violação) |
| II. Lugar não-localizável nunca desaparece | Não aplicável — mesma razão | N/A (sem violação) |
| III. Ordem `lon,lat` | Não aplicável | N/A (sem violação) |
| IV. Chaves canônicas são string | Não aplicável | N/A (sem violação) |
| V. Dados de origem imutáveis | `pipeline/sprint1.py` só invoca `s01`-`s03`+`s08` já existentes; nenhuma escrita nova em `data/raw/` | PASS |
| VI. Resultado fraco é resultado válido | FR-004 exige que o artefato de distribuição indique o lado do limiar sem suavizar — nenhum ajuste de threshold pra "melhorar" o resultado | PASS |

Nenhuma violação. Sem necessidade de `Complexity Tracking`.

**Re-check pós-Fase 1**: `data-model.md` define os dois artefatos como saída determinística e sobrescrita (nunca acumulativa) — consistente com Constitution V/VI. `pipeline/sprint1.py` reusa as funções existentes de `s01`-`s03`/`s08` sem duplicar lógica de negócio. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/002-fechar-lacunas-sprint1/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

Sem `contracts/`: esta feature não expõe nem consome nenhuma interface de API/UI nova — os dois artefatos são documentação markdown lida por humanos, não dado estruturado consumido por código (diferente de `places.json`/`graph.json` em `001-atlas-atos`, que têm JSON Schema formal porque são contratos programáticos com o frontend).

### Source Code (repository root, alterações sobre a estrutura de `001-atlas-atos`)

```text
pipeline/
├── s02_load.py            # MODIFICADO: gera docs/schema.md ao final da carga
├── s03_extract_acts.py    # MODIFICADO: gera docs/candidate-distribution.md
└── sprint1.py              # NOVO: orquestra s01→s02→s03→s08 num comando único

docs/
├── schema.md                    # NOVO — gerado, não editado à mão
└── candidate-distribution.md    # NOVO — gerado, não editado à mão

tests/
├── test_no_candidate_collapse.py   # RENOMEADO de test_no_collapse.py (mesmo conteúdo)
└── test_sprint1_evidence_artifacts.py  # NOVO: verifica existência/formato dos 2 artefatos

justfile   # MODIFICADO: alvo `sprint1` chamando `uv run python -m pipeline.sprint1`
           # (conveniência opcional — o comando canônico continua sendo o uv run direto,
           # que não depende do binário `just`, ver research.md)
```

**Structure Decision**: Nenhuma estrutura nova de projeto — só extensão pontual do `pipeline/` e `tests/` já existentes de `001-atlas-atos`, mais dois artefatos de documentação gerados em `docs/`.

## Complexity Tracking

*Sem violações de constituição a justificar.*
