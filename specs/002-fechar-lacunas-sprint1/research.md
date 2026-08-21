# Research: Fechar Lacunas de Evidência da Sprint 1

Sem NEEDS CLARIFICATION pendente no Technical Context — as decisões abaixo resolvem os únicos pontos de ambiguidade real.

## 1. Onde persistir os artefatos de evidência

- **Decision**: `docs/schema.md` e `docs/candidate-distribution.md`, versionados no repositório.
- **Rationale**: `data/interim/` é gitignored (Constitution V — área de trabalho intermediária, não evidência auditável). `data/processed/` é reservado a contratos de dados consumidos pela aplicação web (`places.json` etc.), com JSON Schema formal — misturar documentação de evidência ali confundiria o propósito do diretório. `docs/` já é o lugar dos outros artefatos de evidência da Sprint 1 (`docs/data-contracts.md`, `docs/adr/`), e é versionado por padrão.
- **Alternatives considered**: `data/processed/schema.json` (formato estruturado) — rejeitado porque nada no projeto consome esse esquema programaticamente; é documentação pra humano, markdown é o formato certo. Anexar ao `docs/data-contracts.md` existente — rejeitado porque esse arquivo documenta a *fonte* (dados brutos observados), enquanto os novos artefatos documentam a *saída do pipeline* (tabelas carregadas, distribuição calculada); são momentos diferentes do processo e merecem arquivos próprios para não sobrecarregar um documento já longo.

## 2. Como extrair o esquema real das tabelas DuckDB

- **Decision**: usar `PRAGMA table_info(<tabela>)` (ou `information_schema.columns`) do próprio DuckDB, ao final de `s02_load.py`, e formatar o resultado como markdown.
- **Rationale**: é a fonte de verdade do que foi de fato carregado — não uma suposição de schema mantida manualmente que pode divergir do código real (esse é exatamente o tipo de "suposição não verificada" que já causou 5 dos achados registrados em `docs/adr/` durante `001-atlas-atos`). Gerar automaticamente elimina o risco de o artefato ficar desatualizado.
- **Alternatives considered**: documentar o esquema manualmente com base na leitura do código — rejeitado pela mesma razão que motivou esta feature: documentação escrita à mão diverge do sistema real com o tempo.

## 3. Como persistir a distribuição de candidatos sem duplicar lógica

- **Decision**: `s03_extract_acts.py` ganha uma função que escreve em arquivo o mesmo resultado que `report_candidate_distribution()` já calcula e imprime — a função de cálculo não muda, só ganha um segundo destino de saída (arquivo, além do stdout).
- **Rationale**: evita duplicar a lógica de contagem/limiar em dois lugares (um bug clássico é a versão em arquivo divergir da versão impressa). Uma função calcula, duas saídas (print + write) consomem o mesmo resultado.
- **Alternatives considered**: script separado que reprocessa `places.json` já exportado para recalcular a distribuição — rejeitado por introduzir uma segunda fonte de verdade para o mesmo número.

## 4. Comando único sem depender de `just`

- **Decision**: `pipeline/sprint1.py`, um módulo Python executável via `uv run python -m pipeline.sprint1`, que chama em sequência as funções `main()`/`run()` já existentes de `s01_download`, `s02_load`, `s03_extract_acts`, `s08_export.export_places` — nessa ordem, parando no primeiro erro com uma mensagem indicando a etapa. O `justfile` ganha um alvo `sprint1` que só chama esse comando, como conveniência opcional para quem tiver `just` instalado — mas o comando canônico (o que satisfaz FR-008 e SC-005) é o `uv run python -m pipeline.sprint1` direto, porque `uv` já é dependência obrigatória do projeto desde `001-atlas-atos`, enquanto `just` foi confirmado ausente no ambiente de validação.
- **Rationale**: resolve FR-007 (não chama s04-s07, que não existem) e FR-008 (não introduz dependência de ferramenta não garantida) ao mesmo tempo, sem reescrever a lógica de cada estágio — só orquestra o que já existe e já está testado.
- **Alternatives considered**: consertar o `justfile` existente comentando os estágios futuros — rejeitado porque não resolve a falha de fundo (dependência de um binário não instalado) e exigiria descomentar manualmente a cada nova sprint, um passo manual fácil de esquecer. Um script shell (`sprint1.sh`) — rejeitado por introduzir uma segunda linguagem de orquestração quando Python já orquestra tudo o resto do projeto.

## 5. Nome do teste de preservação de candidatos

- **Decision**: renomear `tests/test_no_collapse.py` → `tests/test_no_candidate_collapse.py`, mantendo as duas funções de teste existentes (`test_no_place_with_multiple_origin_candidates_is_collapsed_to_one`, `test_multi_candidate_places_render_all_candidates`) inalteradas — só o nome do arquivo muda, para bater com o citado em `relatorio.md` (CA1).
- **Rationale**: CA1 do relatório busca pelo nome do arquivo/teste como identificador de evidência; a correspondência exata elimina a ambiguidade sem exigir que o relatório seja reescrito (o relatório é o documento de avaliação formal, mais caro de alterar do que um nome de arquivo interno).
- **Alternatives considered**: atualizar `relatorio.md` para citar `test_no_collapse.py` em vez de renomear o código — rejeitado porque o nome atual do arquivo (`test_no_collapse`) é menos específico que o nome citado no relatório (`test_no_candidate_collapse`, que deixa claro que é sobre *candidatos*, não sobre qualquer colapso genérico); a correção na direção do nome mais específico é a melhoria, não só uma sincronização arbitrária.
