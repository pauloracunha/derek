---

description: "Task list for feature 002-fechar-lacunas-sprint1"
---

# Tasks: Fechar Lacunas de Evidência da Sprint 1

**Input**: Design documents from `/specs/002-fechar-lacunas-sprint1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (todos presentes; sem `contracts/` — ver `plan.md`)

**Tests**: Incluídos. As 4 invariantes de `data-model.md` são a evidência de que a feature realmente fecha as lacunas identificadas — não são TDD opcional aqui, são o critério de aceite.

**Organization**: Tarefas agrupadas por user story (US1, US2, US4 — todas P1 — depois US3, P2, na ordem de prioridade do spec).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependência pendente)
- **[Story]**: US1/US2/US3/US4, mapeado a `spec.md`

## Setup / Foundational

Não aplicável — esta feature reusa integralmente a infraestrutura Python já estabelecida em `001-atlas-atos` (sem dependência nova, sem estrutura de projeto nova). Nenhuma tarefa bloqueante compartilhada entre as user stories abaixo.

---

## Phase 1: User Story 1 - Auditar o esquema de dados sem reexecutar nada (Priority: P1)

**Goal**: `docs/schema.md` existe, é gerado automaticamente pela carga de dados, e mostra o esquema real das 3 tabelas.

**Independent Test**: Rodar `pipeline/s02_load.py` isoladamente e abrir `docs/schema.md` sem executar mais nada.

- [X] T001 [US1] Adicionar `write_schema_artifact()` em `pipeline/s02_load.py` — introspecciona as 3 tabelas via `PRAGMA table_info`/`information_schema` do DuckDB e escreve `docs/schema.md` (nome da tabela, campos, tipos, `row_count`, `generated_at`), sempre sobrescrevendo o arquivo inteiro (FR-001, FR-002; data-model.md `SchemaArtifact`)
- [X] T002 [US1] Chamar `write_schema_artifact()` ao final de `load()`/`main()` em `pipeline/s02_load.py`, para que a geração seja automática, não um passo manual (depends on T001)
- [X] T003 [P] [US1] Escrever `tests/test_sprint1_evidence_artifacts.py::test_schema_artifact_exists_and_lists_tables` — roda a carga e verifica que `docs/schema.md` existe e lista `ancient`/`modern`/`source` com `row_count > 0` (data-model.md invariante 1)

**Checkpoint**: US1 completa e testável de forma independente.

---

## Phase 2: User Story 2 - Auditar a distribuição de candidatos sem reexecutar nada (Priority: P1)

**Goal**: `docs/candidate-distribution.md` existe, reflete os mesmos números já calculados por `report_candidate_distribution()`, e indica explicitamente se o limiar de 15% foi ultrapassado.

**Independent Test**: Rodar `pipeline/s03_extract_acts.py` isoladamente e abrir `docs/candidate-distribution.md` sem executar mais nada.

- [X] T004 [US2] Dividir `report_candidate_distribution()` em `pipeline/s03_extract_acts.py` em duas funções: `compute_candidate_distribution(places) -> dict` (cálculo puro — contagens 1/2/3+/não-localizáveis + `threshold_crossed`, sem print nem write) e `print_candidate_distribution(result)` (só imprime, mesmo texto de hoje). Remover a função antiga (research.md item 3; grill 2026-08-02 Q1)
- [X] T005 [US2] Adicionar `write_distribution_artifact(result)` em `pipeline/s03_extract_acts.py` — escreve `docs/candidate-distribution.md` a partir do dict de `compute_candidate_distribution()`, com `generated_at`, sempre sobrescrevendo (FR-003, FR-004; data-model.md `CandidateDistributionArtifact`) (depends on T004)
- [X] T006 [US2] Em `main()` de `pipeline/s03_extract_acts.py`, chamar `compute_candidate_distribution()` uma vez e passar o resultado pra `print_candidate_distribution()` e `write_distribution_artifact()` (depends on T005)
- [X] T007 [US2] Estender `tests/test_sprint1_evidence_artifacts.py` com `test_distribution_artifact_exists_and_matches_counts` — chama `compute_candidate_distribution()` diretamente (sem rodar o pipeline inteiro nem capturar stdout) e verifica que `write_distribution_artifact()` produz um `docs/candidate-distribution.md` com os 4 números e `threshold_crossed` batendo com o dict (data-model.md invariante 2) (depends on T003 — mesmo arquivo de teste, não paralelizável com T003)

**Checkpoint**: US1 + US2 completas e testáveis de forma independente.

---

## Phase 3: User Story 4 - Rodar a Sprint 1 completa com um único comando (Priority: P1)

**Goal**: `uv run python -m pipeline.sprint1` executa download→carga→extração→exportação do zero, numa invocação só, sem depender de `s04`-`s07` nem de `just`.

**Independent Test**: Em ambiente limpo, rodar `uv run python -m pipeline.sprint1` e verificar que produz `places.json` + os dois artefatos de evidência sem falhar.

- [X] T008 [US4] Criar `pipeline/sprint1.py` — chama em sequência `s01_download.main()`, `s02_load.load()`, `s03_extract_acts.run()`, `s08_export.export_places()`, imprimindo `"Etapa N/4: <nome>"` antes de cada uma; SEM `try/except` — deixa a exceção original propagar com traceback completo, satisfazendo FR-010 (identificar a etapa) sem esconder o erro real por trás de uma exceção customizada (FR-006, FR-007, FR-008; research.md item 4; grill 2026-08-02 Q4) (depends on T002, T006 — precisa que os dois artefatos já sejam gerados pelas etapas que orquestra)
- [X] T009 [US4] Adicionar alvo `sprint1` no `justfile` chamando `uv run python -m pipeline.sprint1` — conveniência opcional para quem tiver `just`; o comando canônico continua sendo o `uv run` direto (depends on T008)
- [X] T010 [US4] Registrar marcador `slow` em `pyproject.toml` (`[tool.pytest.ini_options] markers`) e atualizar `justfile`/`just test` para rodar `pytest -m "not slow"` por padrão — testes de rede real ficam fora do `pytest` do dia a dia (grill 2026-08-02 Q2)
- [X] T011 [US4] Estender `tests/test_sprint1_evidence_artifacts.py` com `test_sprint1_command_produces_all_artifacts_in_clean_environment`, marcado `@pytest.mark.slow` — remove `data/raw`, `data/interim`, `data/processed`, os dois artefatos de evidência; roda `pipeline.sprint1` (baixa da rede de verdade); verifica que os 3 artefatos existem ao final de uma única invocação (data-model.md invariante 4; FR-009) (depends on T008, T007, T010 — mesmo arquivo de teste)
- [X] T012 [US4] Estender `tests/test_sprint1_evidence_artifacts.py` com `test_sprint1_rerun_is_idempotent`, marcado `@pytest.mark.slow` (roda `sprint1.py` duas vezes = 2 downloads reais) — compara `docs/schema.md`/`docs/candidate-distribution.md` ignorando o campo `generated_at`; confirma que não sobram arquivos duplicados (SC-006; Edge Case do spec) (depends on T011 — mesmo arquivo de teste)

**Checkpoint**: US1 + US2 + US4 completas — a Sprint 1 roda do zero com um comando só e produz evidência auditável.

---

## Phase 4: User Story 3 - Rastrear o teste de preservação de candidatos pelo nome citado no relatório (Priority: P2)

**Goal**: `tests/test_no_candidate_collapse.py` existe com esse nome exato, batendo com CA1 de `relatorio.md`.

**Independent Test**: Buscar `test_no_candidate_collapse` no projeto e confirmar que corresponde a um arquivo de teste real e executável.

- [X] T013 [US3] Renomear `tests/test_no_collapse.py` para `tests/test_no_candidate_collapse.py`, mantendo as duas funções de teste existentes sem alteração de conteúdo (FR-005; research.md item 5)
- [X] T014 [US3] Atualizar toda referência ao nome antigo `test_no_collapse` em `specs/001-atlas-atos/tasks.md`, `specs/001-atlas-atos/data-model.md` (invariante de validação #4) e `specs/001-atlas-atos/plan.md` (árvore de `tests/`) para o novo nome `test_no_candidate_collapse`, mantendo a documentação consistente com o código real (depends on T013)

**Checkpoint**: Todas as 4 user stories completas e testáveis de forma independente.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T015 [P] Atualizar `CLAUDE.md` "Estado atual" para refletir a conclusão de `002-fechar-lacunas-sprint1`
- [X] T016 [P] Atualizar `relatorio.md` para citar `docs/schema.md` e `docs/candidate-distribution.md` como artefato de evidência de R1.3/R1.5, e `tests/test_no_candidate_collapse.py` (já correto após T013/T014) como evidência de CA1
- [X] T017 Executar o roteiro de verificação manual de `quickstart.md` por completo (as 4 user stories + idempotência) e confirmar que todos os passos passam
- [X] T018 [P] Comentar o alvo `pipeline` no `justfile` com nota `# TODO: reativar quando s04-s07 existirem — Sprint 2` — hoje falha porque esses estágios não existem; evita que avaliador confunda com bug ativo (grill 2026-08-02 Q3)

---

## Dependencies & Execution Order

### Story Dependencies

- **US1 (P1)**: sem dependência de outra story — só toca `s02_load.py`
- **US2 (P1)**: sem dependência de outra story — só toca `s03_extract_acts.py`; compartilha o arquivo `tests/test_sprint1_evidence_artifacts.py` com US1 (T007 depende de T003 só por causa disso, não por lógica)
- **US4 (P1)**: depende de US1 (T002) e US2 (T006) estarem implementadas — o orquestrador só produz os 3 artefatos completos se as duas gerações já existirem nas etapas que ele chama
- **US3 (P2)**: totalmente independente das outras três — pode ser feita a qualquer momento, inclusive em paralelo

### Parallel Opportunities

- T001-T003 (US1) podem ser feitas em paralelo com T013-T014 (US3) — arquivos completamente diferentes
- T003, T007, T011, T012 tocam o mesmo arquivo de teste — sequenciais entre si, apesar de pertencerem a stories "independentes"
- T015/T016 (Polish) em paralelo entre si

---

## Implementation Strategy

### MVP (fechar as 2 lacunas de maior prioridade primeiro)

1. US1 (schema.md) e US2 (candidate-distribution.md) — as duas lacunas de evidência mais citadas no critério de aceite da Sprint 1 (R1.3/R1.5)
2. US4 (comando único) — depende das duas anteriores, fecha CA2
3. US3 (rename do teste) — independente, pode entrar em qualquer ponto, inclusive em paralelo com 1-2

### Notes

- Nenhuma task desta feature toca a lógica de extração/normalização já validada em `001-atlas-atos` (Constitution I-IV inalteradas) — só adiciona persistência de evidência, um orquestrador fino, e um rename.
- `T008` é o único ponto que precisa saber a ordem correta das 4 etapas (`s01→s02→s03→s08`) — mantê-la sincronizada com o `justfile` existente de `001-atlas-atos` se este for alterado no futuro.
