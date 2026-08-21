# Feature Specification: Fechar Lacunas de Evidência da Sprint 1

**Feature Branch**: `002-fechar-lacunas-sprint1`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "Fechar as lacunas de evidência da Sprint 1 do Atlas de Atos, sem mexer no registro de commit hash da fonte (fora de escopo). Precisa: (1) persistir o esquema real das tabelas carregadas como artefato em disco, não só inspeção ad-hoc; (2) persistir a tabela de distribuição de contagem de candidatos (1/2/3+) como artefato em disco, não só stdout, para servir de evidência de sprint; (3) corrigir a rastreabilidade entre o teste de preservação de candidatos e o nome citado no relatório do projeto (CA1); (4) um comando único que execute a Sprint 1 completa (download → carga → extração → exportação) sem depender de estágios de sprints futuras que ainda não existem, resolvendo a falha atual do comando de pipeline completo e a dependência de uma ferramenta não garantidamente instalada no ambiente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auditar o esquema de dados carregado sem reexecutar nada (Priority: P1)

Um avaliador do projeto (orientador, banca, revisor) quer conferir a estrutura das tabelas de dados carregadas na Sprint 1 — quais tabelas existem, quais colunas e tipos cada uma tem — sem precisar instalar o projeto, rodar código ou ter acesso ao ambiente de desenvolvimento.

**Why this priority**: É evidência formal exigida pelo critério de aceite da Sprint 1 (R1.3 do cronograma do projeto). Sem um artefato persistido, a evidência não existe de forma auditável — hoje só existiu de forma transitória no terminal durante o desenvolvimento.

**Independent Test**: Abrir o arquivo de esquema gerado e verificar que ele lista as tabelas carregadas com seus campos e tipos, sem executar nenhum comando.

**Acceptance Scenarios**:

1. **Given** a etapa de carga de dados já foi executada, **When** o avaliador abre o artefato de esquema, **Then** ele vê a lista completa de tabelas, campos e tipos carregados, datada da execução mais recente.
2. **Given** a etapa de carga é executada novamente (ex.: dado de origem atualizado), **When** o artefato de esquema é regenerado, **Then** ele reflete o estado mais recente, sem misturar informação de execuções antigas.

---

### User Story 2 - Auditar a distribuição de candidatos sem reexecutar nada (Priority: P1)

Um avaliador quer conferir a tabela de distribuição de lugares por número de candidatos de localização (1 / 2 / 3+) — o número que decide se a hipótese central do projeto é sustentada ou se o eixo de análise deve ser outro — sem rodar código.

**Why this priority**: É o critério de aceite mais citado da Sprint 1 (R1.5): "a distribuição de candidatos está quantificada". Essa tabela também é a evidência-chave usada para justificar decisões de framing no relatório final — precisa ser conferível de forma independente e permanente, não reconstruída de memória a cada consulta.

**Independent Test**: Abrir o artefato de distribuição e verificar que ele mostra a contagem de lugares por faixa de candidatos e indica claramente se o limiar de decisão foi ultrapassado.

**Acceptance Scenarios**:

1. **Given** a etapa de extração já foi executada, **When** o avaliador abre o artefato de distribuição, **Then** ele vê quantos lugares têm 1, 2 e 3+ candidatos, o total de lugares localizáveis, e uma indicação explícita de qual lado do limiar de decisão o resultado caiu.
2. **Given** o artefato de distribuição já existe de uma execução anterior, **When** a etapa de extração roda de novo, **Then** o artefato é sobrescrito de forma determinística — nunca acumula versões conflitantes lado a lado.

---

### User Story 3 - Rastrear o teste de preservação de candidatos pelo nome citado no relatório (Priority: P2)

Um avaliador lê o critério de aceite CA1 no relatório do projeto, que cita o nome de um teste automatizado responsável por garantir que nenhum lugar com múltiplos candidatos é reduzido a um só. Ele quer localizar esse teste no projeto pelo nome exato citado, sem precisar adivinhar ou vasculhar arquivos.

**Why this priority**: É uma inconsistência de rastreabilidade documental — de baixo risco técnico, mas gera atrito real numa avaliação formal (um avaliador que busca pelo nome citado e não encontra o arquivo correspondente levanta dúvida sobre se o teste existe de verdade). Prioridade menor que US1/US2 porque não bloqueia nenhuma evidência de estar disponível, só a torna mais difícil de localizar.

**Independent Test**: Buscar, no projeto, pelo nome do teste exatamente como citado no relatório e confirmar que ele corresponde a um teste real e executável.

**Acceptance Scenarios**:

1. **Given** o relatório do projeto cita o nome de um teste de preservação de candidatos, **When** esse nome é buscado no projeto, **Then** ele corresponde exatamente a um teste automatizado existente e executável (não a um nome parecido, nem a um teste ausente).

---

### User Story 4 - Rodar a Sprint 1 completa com um único comando (Priority: P1)

Alguém validando o projeto do zero (avaliador reproduzindo o trabalho, ou o próprio autor num ambiente limpo) quer executar toda a Sprint 1 — download das fontes, carga, extração e exportação do catálogo de lugares — com uma única invocação, sem precisar saber a ordem manual das etapas nem depender de uma ferramenta que pode não estar instalada.

**Why this priority**: É o critério de aceite CA2 do projeto ("pipeline executável do zero em um único comando") e hoje falha: o comando existente tenta rodar etapas de sprints futuras que ainda não existem, e depende de uma ferramenta de linha de comando não garantidamente presente no ambiente de quem for validar.

**Independent Test**: Em um ambiente limpo (sem execução anterior), rodar o comando único da Sprint 1 e verificar que ele produz o catálogo de lugares final e os artefatos de evidência, do início ao fim, sem falhar e sem exigir nenhuma etapa manual extra.

**Acceptance Scenarios**:

1. **Given** um ambiente limpo, sem dados baixados nem processados, **When** o comando único de Sprint 1 é executado, **Then** ao final existem: os dados brutos baixados, o catálogo de lugares exportado, o artefato de esquema e o artefato de distribuição — todos gerados nessa única invocação.
2. **Given** o comando único de Sprint 1, **When** executado, **Then** ele não aciona nenhuma etapa pertencente a sprints futuras (que ainda não foram implementadas) e não requer nenhuma ferramenta além das já usadas no restante do projeto.
3. **Given** uma falha em qualquer etapa do comando único (ex.: fonte de dados indisponível), **When** a falha ocorre, **Then** a execução para imediatamente com uma mensagem clara indicando qual etapa falhou — nunca segue adiante silenciosamente com dado parcial ou desatualizado.

---

### Edge Cases

- Comando único de Sprint 1 executado duas vezes seguidas: os artefatos de evidência (esquema, distribuição, catálogo) devem ser sobrescritos de forma limpa, sem deixar arquivos órfãos de execuções anteriores.
- Etapa de download falha por indisponibilidade de rede durante o comando único: a execução para nessa etapa, com mensagem clara — não deve prosseguir usando dado bruto potencialmente desatualizado de uma execução anterior sem avisar.
- Distribuição de candidatos muda de execução para execução (porque o dado de origem foi atualizado): o artefato de distribuição sempre reflete a execução mais recente; nenhuma referência antiga fica implicitamente válida.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE gerar, após a etapa de carga de dados, um artefato em arquivo contendo o esquema completo das tabelas carregadas (nomes de tabela, campos e tipos).
- **FR-002**: O artefato de esquema DEVE ser gerado automaticamente como parte da execução da etapa de carga — não é um passo manual separado.
- **FR-003**: O sistema DEVE gerar, após a etapa de extração, um artefato em arquivo contendo a tabela de distribuição de lugares por número de candidatos (1 / 2 / 3+).
- **FR-004**: O artefato de distribuição DEVE indicar explicitamente se o resultado ficou abaixo ou acima do limiar de decisão que determina o eixo de análise do projeto.
- **FR-005**: O nome do teste automatizado responsável por garantir que nenhum lugar com múltiplos candidatos é reduzido a um só DEVE corresponder exatamente ao nome citado como evidência desse critério no relatório do projeto.
- **FR-006**: DEVE existir um único comando executável que realize toda a sequência da Sprint 1 — download das fontes, carga, extração, exportação do catálogo de lugares — do início ao fim.
- **FR-007**: Esse comando único NÃO DEVE depender de nenhuma etapa pertencente a uma sprint futura ainda não implementada.
- **FR-008**: Esse comando único NÃO DEVE depender de nenhuma ferramenta externa que não esteja já em uso e disponível no restante do projeto.
- **FR-009**: O comando único DEVE poder ser executado em um ambiente limpo (sem execução anterior) e produzir, numa única invocação, todos os artefatos de evidência da Sprint 1 (esquema, distribuição, catálogo de lugares).
- **FR-010**: Uma falha em qualquer etapa do comando único DEVE interromper a execução imediatamente com uma mensagem que identifique claramente a etapa que falhou — nunca deve prosseguir silenciosamente com resultado parcial.
- **FR-011**: O registro de qual versão/commit da fonte de dados foi usado permanece fora do escopo desta feature — não deve ser adicionado como efeito colateral de nenhum dos requisitos acima.

### Key Entities

- **Artefato de Esquema**: representação persistida em arquivo da estrutura das tabelas carregadas — tabela, campo, tipo. Gerado a cada execução da etapa de carga, sempre refletindo o estado mais recente.
- **Artefato de Distribuição de Candidatos**: representação persistida em arquivo da contagem de lugares por faixa de número de candidatos, incluindo a indicação de qual lado do limiar de decisão foi alcançado. Gerado a cada execução da etapa de extração.
- **Comando de Sprint 1**: procedimento único e executável que encadeia download, carga, extração e exportação, produzindo todos os artefatos de evidência da Sprint 1 numa só invocação, sem depender de etapas de sprints futuras nem de ferramentas externas não garantidas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Um avaliador consegue abrir um único arquivo e ver o esquema completo das tabelas carregadas, sem executar nenhum comando ou código.
- **SC-002**: Um avaliador consegue abrir um único arquivo e ver a distribuição de candidatos por lugar, incluindo a indicação do limiar de decisão, sem executar nenhum comando ou código.
- **SC-003**: Buscar, no projeto, pelo nome do teste de preservação de candidatos exatamente como citado no relatório retorna um teste real, existente e executável — 100% de correspondência.
- **SC-004**: A Sprint 1 completa executa do zero até a exportação final numa única invocação de comando, sem falha, em um ambiente limpo.
- **SC-005**: A execução do comando de Sprint 1 não exige a instalação de nenhuma ferramenta além das já usadas no restante do projeto.
- **SC-006**: Executar o comando de Sprint 1 duas vezes seguidas produz os mesmos três artefatos de evidência, sem arquivos duplicados ou órfãos de execuções anteriores.

## Assumptions

- O registro de commit/versão da fonte de dados está fora de escopo por decisão explícita — nenhum requisito acima deve introduzir esse comportamento como efeito colateral.
- A lógica de negócio da Sprint 1 (extração, normalização, cálculo de probabilidade) já foi validada em trabalho anterior e não é alterada por esta feature — o escopo aqui é exclusivamente persistência de evidência, correção de nome de teste, e consolidação de execução em um único comando.
- "Ferramenta externa não garantidamente disponível" refere-se a qualquer binário de terceiros que precise ser instalado separadamente do ambiente já em uso pelo restante do projeto; o comando único deve usar apenas o que já está estabelecido como dependência nas fases anteriores.
- Os artefatos de evidência (esquema, distribuição) são material de apoio à avaliação e ao relatório — não são consumidos pela aplicação web nem fazem parte dos contratos de dados já publicados para o frontend.
