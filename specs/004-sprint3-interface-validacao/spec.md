# Feature Specification: Sprint 3 — Interface e Validação

**Feature Branch**: `004-sprint3-interface-validacao`

**Created**: 2026-08-19

**Status**: Draft

**Input**: User description: "famos seguir para a sprint 3"

**Relação com 001-atlas-atos**: esta feature fecha as User Stories US1–US4 e os requisitos
FR-002 a FR-011, FR-016, FR-019, FR-020 já definidos em `specs/001-atlas-atos/spec.md`,
que permanecem a fonte de verdade para comportamento visual e critérios de aceite. Este
documento escopa o que falta implementar sobre a base já existente em `web/`
(layout, roteamento de dados, `store.ts` com `chapterRange` compartilhado) para fechar a
Sprint 3 do relatório (R3.1–R3.6), publicar a aplicação e conduzir o teste de compreensão.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver todos os candidatos de um lugar no mapa, com peso visual proporcional à confiança (Priority: P1)

Usuário seleciona um lugar de Atos no mapa ou em uma lista e vê, simultaneamente, todos
os candidatos de localização conhecidos daquele lugar — nunca apenas o mais provável —
cada um com opacidade e tamanho de marcador proporcionais à probabilidade relativa.

**Why this priority**: é a contribuição central do projeto (princípio não negociável 1 do
CLAUDE.md); sem isso não há produto demonstrável.

**Independent Test**: carregar `places.json` real, selecionar um lugar com 2+ candidatos
(ex.: identificado em `docs/candidate-distribution.md`) e confirmar visualmente que todos
aparecem ao mesmo tempo, com peso visual diferenciado e fonte de cada identificação
acessível.

**Acceptance Scenarios**:

1. **Given** um lugar com múltiplos candidatos, **When** selecionado, **Then** todos os
   candidatos aparecem no mapa ligados visualmente entre si, com opacidade e tamanho de
   marcador proporcionais à probabilidade de cada um.
2. **Given** um lugar com um único candidato de alta confiança, **When** selecionado,
   **Then** o mapa mostra um único marcador sólido.
3. **Given** um lugar cuja melhor localização é uma área aproximada (não ponto exato),
   **When** exibido, **Then** aparece com indicador visual de imprecisão de área,
   distinto do marcador de ponto exato.

---

### User Story 2 - Consultar o painel de lugares não localizáveis com razão explícita (Priority: P1)

Usuário abre um painel dedicado listando todo lugar de Atos sem localização geográfica
conhecida, cada um com a razão explícita em linguagem legível (não código técnico).

**Why this priority**: segundo princípio não negociável do projeto (CLAUDE.md); descartar
esses lugares silenciosamente repete a falha que o projeto corrige.

**Independent Test**: abrir o painel e confirmar que 100% dos lugares com
`localizable: false` em `places.json` aparecem, cada um com texto de razão legível, e que
nenhum aparece como ponto no mapa.

**Acceptance Scenarios**:

1. **Given** um lugar sem localização conhecida ou simbólico, **When** o usuário consulta
   o painel, **Then** o lugar aparece com a razão da não-localização, e não aparece como
   ponto no mapa.
2. **Given** o conjunto completo de lugares não localizáveis do dataset exportado,
   **When** contado, **Then** o número exibido no painel bate exatamente com o número de
   lugares `localizable: false` em `places.json`.

---

### User Story 3 - Explorar o grafo de coocorrência filtrado por capítulo, sincronizado com o mapa (Priority: P2)

Usuário navega pelo grafo de rede (`graph.json`), agrupado por comunidade detectada, e ao
selecionar uma faixa de capítulos na timeline, tanto o grafo quanto o mapa (US1) passam a
exibir apenas os lugares e conexões daquele intervalo.

**Why this priority**: transforma o mapa de pontos em rede narrativa; depende de US1 já
renderizar lugares, por isso vem depois.

**Independent Test**: selecionar uma faixa de capítulos na timeline e verificar que grafo
e mapa atualizam simultaneamente para o mesmo subconjunto de lugares, via o
`chapterRange` já compartilhado em `store.ts`.

**Acceptance Scenarios**:

1. **Given** a aplicação carregada, **When** o usuário seleciona um intervalo de
   capítulos, **Then** o grafo exibe somente os lugares e conexões daquele intervalo.
2. **Given** o grafo completo, **When** exibido, **Then** os lugares aparecem agrupados
   por comunidade detectada (`docs/community-comparison.md` — 5 comunidades).
3. **Given** um intervalo de capítulos selecionado, **When** aplicado, **Then** o mapa
   também passa a exibir só os lugares daquele intervalo (estado compartilhado,
   `placeInChapterRange` já implementado).
4. **Given** uma comunidade detectada internamente desconexa, **When** exibida, **Then**
   o sistema sinaliza essa inconsistência em vez de apresentá-la sem ressalva.

---

### User Story 4 - Confiar na legenda, atribuição e publicação pública da aplicação (Priority: P2)

Usuário abre a aplicação publicada (link público, sem cadastro) e encontra legenda
permanente da codificação visual de incerteza, texto explicativo de por que um lugar pode
ter múltiplos pontos, e atribuição de licença das fontes de dados sempre visível.

**Why this priority**: sem publicação e legibilidade da codificação visual, o teste de
compreensão (US5) e o critério de aceite da Sprint 3 não são alcançáveis; é pré-requisito
para validar US1–US3 com usuários reais.

**Independent Test**: acessar a URL pública sem login, confirmar que legenda, texto
explicativo e atribuição de licença estão visíveis sem interação adicional.

**Acceptance Scenarios**:

1. **Given** a aplicação publicada, **When** acessada por link direto, **Then** carrega
   sem exigir instalação, cadastro ou autenticação.
2. **Given** a aplicação carregada, **When** exibida, **Then** legenda da codificação de
   incerteza, texto explicativo sobre múltiplos pontos, e atribuição de licença das fontes
   aparecem sempre visíveis (não escondidos atrás de menu).

---

### User Story 5 - Validar a compreensão da codificação visual com usuários reais (Priority: P3)

Equipe do projeto conduz sessão de teste de compreensão com participantes reais, medindo
se conseguem explicar, sem explicação prévia, por que alguns lugares aparecem com
múltiplos pontos no mapa.

**Why this priority**: valida H4 (compreensão da representação visual) e o critério de
aceite formal da Sprint 3; depende de US1 e US4 estarem prontos e publicados.

**Independent Test**: conduzir sessão com 3–5 participantes, registrar se cada um
consegue explicar corretamente a codificação visual após uso livre da aplicação, sem
receber explicação prévia da equipe.

**Acceptance Scenarios**:

1. **Given** a aplicação publicada, **When** 3 a 5 participantes reais a exploram sem
   explicação prévia, **Then** o resultado (acerto/erro por participante, com
   justificativa) é registrado em documento persistido.
2. **Given** os resultados registrados, **When** consolidados, **Then** pelo menos 80%
   dos participantes explica corretamente por que um lugar aparece com múltiplos pontos
   (SC-003 de 001-atlas-atos).

---

### Edge Cases

- Lugar com dois ou mais candidatos de score praticamente empatado: todos aparecem, sem
  escolha arbitrária de "vencedor" único no mapa.
- Faixa de capítulos selecionada não contém nenhum lugar: grafo e mapa exibem estado
  vazio explícito, não erro nem tela em branco sem explicação.
- Participante do teste de compreensão não consegue completar a tarefa: registrado como
  falha, sem excluir da amostra nem ajustar critério post-hoc (princípio 6 do CLAUDE.md).
- Menos de 3 participantes disponíveis até o fim do prazo da sprint: risco já mapeado no
  relatório (seção "Gestão de risco do cronograma") — reduzir para 3 e conduzir
  remotamente, nunca reportar SC-003 com amostra abaixo de 3.
- Dados de `linkpred.json`/comparação NMI/ARI: não aparecem na UI interativa por decisão
  já registrada em 001-atlas-atos (Clarifications, sessão 2026-08-02) — só no relatório
  escrito.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE carregar os quatro contratos JSON exportados
  (`places.json`, `graph.json`, `uncertainty.json`, `linkpred.json`) diretamente do
  build estático publicado, sem backend em tempo de execução.
- **FR-002**: O sistema DEVE exibir todos os candidatos de localização de um lugar
  selecionado simultaneamente, com opacidade e tamanho de marcador proporcionais à
  probabilidade relativa de cada candidato (herda FR-002/FR-003 de 001-atlas-atos).
- **FR-003**: O sistema DEVE distinguir visualmente marcador de ponto exato de indicador
  de área aproximada (herda FR-004 de 001-atlas-atos).
- **FR-004**: O sistema DEVE exibir painel dedicado com 100% dos lugares não
  localizáveis, cada um com razão explícita legível (herda FR-005 de 001-atlas-atos).
- **FR-005**: O sistema DEVE exibir grafo de coocorrência filtrável por faixa de
  capítulos, agrupado por comunidade detectada, sincronizado com o filtro do mapa via
  estado compartilhado (herda FR-009/FR-010 de 001-atlas-atos).
- **FR-006**: O sistema DEVE sinalizar explicitamente qualquer comunidade detectada
  internamente desconexa (herda FR-011 de 001-atlas-atos).
- **FR-007**: O sistema DEVE exibir legenda permanente da codificação visual de
  incerteza, texto explicativo sobre múltiplos pontos por lugar, e atribuição de licença
  das fontes de dados, todos visíveis sem interação adicional (herda FR-007/FR-008/FR-016
  de 001-atlas-atos).
- **FR-008**: O sistema DEVE permitir ordenar ou destacar lugares pelo índice de
  dispersão de candidatos (herda FR-020 de 001-atlas-atos).
- **FR-009**: A aplicação DEVE ser publicada em URL pública, acessível sem instalação,
  cadastro ou autenticação.
- **FR-010**: A equipe DEVE conduzir teste de compreensão com 3 a 5 participantes reais
  e registrar os resultados (acerto/erro por participante) em documento persistido no
  repositório.
- **FR-011**: O relatório DEVE reportar a taxa de acerto do teste de compreensão frente
  à meta de 80% (SC-003 de 001-atlas-atos), independentemente do resultado (princípio 6
  do CLAUDE.md).

### Key Entities *(include if feature involves data)*

- **Sessão de teste de compreensão**: registro de um participante, com timestamp, se
  explicou corretamente a codificação visual, e a justificativa dada.
- **Lugar / Candidato de Localização / Motivo de Não-Localização / Comunidade**: entidades
  já definidas em `specs/001-atlas-atos/spec.md#key-entities`, reutilizadas sem alteração
  de forma.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Ao selecionar qualquer lugar localizável na aplicação publicada, o usuário
  vê todos os candidatos e a confiança relativa de cada um em uma única tela.
- **SC-002**: 100% dos lugares sem localização conhecida aparecem no painel dedicado com
  razão explícita.
- **SC-003**: Em teste de compreensão com 3–5 participantes reais, pelo menos 80%
  explica corretamente por que alguns lugares têm múltiplos pontos, após uso livre da
  aplicação publicada.
- **SC-004**: Selecionar uma faixa de capítulos atualiza mapa e grafo para o mesmo
  subconjunto de lugares em uma única interação, sem recarregar a página.
- **SC-005**: A aplicação publicada carrega e fica utilizável (mapa e painéis visíveis)
  em conexão de internet padrão, sem exigir login.

## Assumptions

- Base técnica de `web/` (Vite + React + Zustand, `store.ts` com `chapterRange`) já
  existe e é reutilizada; esta feature completa a camada visual sobre ela, não a
  reescreve.
- Hospedagem estática (ex. GitHub Pages, Netlify ou Vercel) é suficiente — decisão de
  qual serviço usar fica para o plano técnico, não é requisito de produto.
- Teste de compreensão conduzido de forma informal (chamada remota ou presencial),
  registrado em markdown no repositório — sem ferramenta de pesquisa dedicada.
- Otimização para telas móveis permanece fora de escopo, conforme já assumido em
  001-atlas-atos.
- Resultados de link prediction (`linkpred.json`) e comparação NMI/ARI de comunidades
  continuam fora da UI interativa, apenas no relatório escrito — decisão já tomada em
  001-atlas-atos e não reaberta aqui.
