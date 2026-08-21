# Feature Specification: Atlas de Atos — Visualização de Rede de Lugares com Incerteza Preservada

**Feature Branch**: `001-atlas-atos`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "Pipeline reprodutível + aplicação web que visualiza a rede de lugares mencionados no livro de Atos dos Apóstolos, preservando e exibindo a incerteza arqueológica sobre a localização de cada lugar, em vez de colapsá-la para um ponto único."

## Clarifications

### Session 2026-08-02

- Q: Quais análises avançadas (predição de novas conexões, comparação de comunidades NMI/ARI) devem ser navegáveis dentro do app web, versus aparecer só no relatório escrito? → A: Nenhum na UI — só no relatório escrito; app mostra apenas mapa, grafo de coocorrência e painel de incerteza.
- Q: Codificação de incerteza pode depender só de opacidade, ou precisa reforço não-dependente de opacidade/cor? → A: Opacidade + tamanho do marcador proporcional à probabilidade (reforço redundante simples).
- Q: Qual o alvo objetivo do teste de compreensão (SC-003) — % mínimo de acerto pra considerar sucesso? → A: 80% (confirmado).

### Sessão de grill 2026-08-02 (contra CONTEXT.md e data-model.md)

- Q: O índice de dispersão de candidatos por lugar (`dispersion_index`) deve ser um recurso real de UI? → A: Sim — usado para ordenar/destacar lugares mais disputados no painel de US1 (ver FR-020).
- Q: Selecionar uma faixa de capítulos filtra só o grafo, ou também o mapa? → A: Os dois, via estado compartilhado — ver Acceptance Scenario 3 de US3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar lugares no mapa sem perder a incerteza de localização (Priority: P1)

Um leitor do relatório (ou visitante da aplicação) seleciona um lugar mencionado em Atos e vê, no mapa, todas as localizações candidatas conhecidas para aquele lugar — não apenas a mais provável — cada uma com peso visual proporcional à confiança na identificação.

**Why this priority**: Esta é a contribuição central do projeto. Toda ferramenta existente colapsa a incerteza em um ponto único; corrigir isso é a razão de existir do sistema. Sem esta funcionalidade não há produto.

**Independent Test**: Selecionar um lugar com 2+ candidatos conhecidos (ex.: um lugar em disputa arqueológica) e verificar que todos os candidatos aparecem simultaneamente no mapa, com opacidade/peso proporcional ao score de cada um, junto com a fonte de cada identificação.

**Acceptance Scenarios**:

1. **Given** um lugar de Atos com múltiplos candidatos de localização, **When** o usuário o seleciona, **Then** todos os candidatos aparecem no mapa, ligados visualmente entre si, com opacidade e tamanho do marcador proporcionais à probabilidade de cada um.
2. **Given** um lugar com um único candidato de alta confiança, **When** o usuário o seleciona, **Then** o mapa mostra um único marcador sólido para aquele lugar.
3. **Given** um lugar cuja melhor localização conhecida é apenas "algum ponto dentro de um assentamento" (não um ponto exato), **When** exibido no mapa, **Then** o lugar aparece com um indicador visual de imprecisão de área, distinto de um marcador de ponto exato.

---

### User Story 2 - Consultar lugares sem localização conhecida sem que sejam descartados (Priority: P1)

Um usuário quer saber quais lugares mencionados em Atos não têm localização geográfica conhecida (nomes simbólicos, referências proféticas, lugares não identificáveis) e por quê, em vez de vê-los simplesmente desaparecerem do sistema.

**Why this priority**: É um dos dois princípios inegociáveis do projeto (junto com o P1 acima): descartar silenciosamente esses lugares repete exatamente a falha que o projeto denuncia nas ferramentas existentes. Sem isso, a integridade da narrativa de dados fica comprometida.

**Independent Test**: Consultar a lista de "lugares mencionados sem localização conhecida" e confirmar que cada item traz uma razão explícita e legível (não um código técnico opaco).

**Acceptance Scenarios**:

1. **Given** um lugar de Atos classificado como sem localização conhecida ou simbólico, **When** o usuário consulta a aplicação, **Then** o lugar aparece em um painel dedicado com a razão da não-localização, e não aparece como ponto no mapa.
2. **Given** um lugar que na verdade é um nome de pessoa ou substantivo comum mal-identificado como lugar, **When** os dados são processados, **Then** esse item é excluído completamente da aplicação (não aparece em nenhum painel).

---

### User Story 3 - Entender como os lugares de Atos se conectam entre si (Priority: P2)

Um usuário navega por uma visualização de rede que mostra quais lugares aparecem juntos nos mesmos capítulos de Atos, podendo identificar agrupamentos (ex.: fase em Jerusalém, fase de expansão à Judeia e Samaria, fase da missão aos gentios) e os lugares mais centrais na narrativa.

**Why this priority**: Complementa a visualização geográfica com a dimensão relacional/estrutural da narrativa — é o que transforma um mapa de pontos em um "atlas" de rede. Depende de P1 estar funcional (lugares já precisam existir e estar catalogados), por isso vem em segundo lugar.

**Independent Test**: Selecionar um capítulo (ou faixa de capítulos) na linha do tempo e verificar que o grafo de rede realça os lugares e conexões correspondentes, com lugares agrupados por comunidade detectada.

**Acceptance Scenarios**:

1. **Given** a aplicação carregada, **When** o usuário seleciona um intervalo de capítulos, **Then** o grafo de rede exibe somente os lugares e conexões relevantes àquele intervalo.
2. **Given** o grafo completo, **When** exibido, **Then** os lugares aparecem agrupados por comunidade detectada, permitindo comparação visual com os três blocos narrativos de Atos (Jerusalém; Judeia e Samaria; missão aos gentios).
3. **Given** um intervalo de capítulos selecionado na timeline, **When** aplicado, **Then** o mapa (US1) também passa a exibir só os lugares mencionados naquele intervalo, mantendo mapa e grafo sincronizados pelo mesmo filtro.

---

### User Story 4 - Confiar no grau de incerteza agregada da rede (Priority: P3)

Um leitor do relatório quer saber se a incerteza de localização dos lugares individuais realmente muda a leitura agregada da rede (ex.: comprimento total do itinerário, distância média entre lugares) ou se o efeito é desprezível.

**Why this priority**: Responde a uma pergunta analítica de apoio ao relatório (o quanto a incerteza importa em agregado), não bloqueia o uso exploratório básico da aplicação, por isso é priorizada por último.

**Independent Test**: Consultar as métricas de distância da rede e verificar que cada uma vem acompanhada de intervalo de confiança e do valor determinístico de referência, permitindo comparar os dois.

**Acceptance Scenarios**:

1. **Given** as métricas baseadas em distância da rede, **When** exibidas ou reportadas, **Then** cada uma mostra média, intervalo de confiança e o valor obtido usando apenas o candidato de maior confiança.
2. **Given** uma métrica puramente estrutural (grau, intermediação, comunidade), **When** exibida, **Then** ela não varia entre simulações — pois não depende da incerteza de localização.

---

### Edge Cases

- Lugar com dois ou mais candidatos de score praticamente empatado: todos devem aparecer, sem escolha arbitrária de um "vencedor" como único candidato exibido.
- Lugar cuja resolução é do tipo "múltiplos locais" (ex.: um objeto móvel referenciado em vários lugares): permanece no catálogo, marcado como não-localizável, sem ponto único forçado no mapa.
- Lugar com referência circular de identificação: excluído da aplicação.
- Texto descritivo de uma identificação contém marcação de referência a outro lugar embutida: o texto exibido ao usuário deve ser legível, sem tags técnicas aparentes.
- Comunidade detectada na rede resulta em um subgrupo geograficamente ou narrativamente desconectado: o sistema deve sinalizar essa inconsistência em vez de apresentá-la como uma comunidade coesa.
- A proporção de lugares com múltiplos candidatos é baixa (abaixo de ~15%): o eixo de incerteza reportado no relatório se desloca de "incerteza de identificação" para "incerteza de precisão" (marcadores de área vs. ponto exato), sem forçar uma narrativa que os dados não sustentam.
- Estratégias diferentes de avaliação de candidatos a novas conexões (referências cruzadas) produzem resultados de qualidade muito diferentes entre si: ambas devem ser reportadas lado a lado, e a diferença discutida, não escondida.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE restringir seu escopo aos lugares mencionados no livro de Atos dos Apóstolos; nenhum outro livro é processado ou exibido.
- **FR-002**: Para cada lugar localizável, o sistema DEVE exibir todas as localizações candidatas conhecidas simultaneamente, nunca apenas a de maior confiança.
- **FR-003**: O sistema DEVE representar visualmente o grau de confiança de cada candidato por dois canais redundantes — opacidade e tamanho do marcador — ambos proporcionais à probabilidade relativa daquele candidato frente aos demais do mesmo lugar, garantindo leitura mesmo quando um dos dois canais não é perceptível (ex.: baixo contraste, daltonismo).
- **FR-004**: O sistema DEVE distinguir visualmente uma localização pontual precisa de uma localização aproximada (área/assentamento), evitando comunicar falsa precisão.
- **FR-005**: O sistema DEVE listar, em painel próprio, todos os lugares mencionados em Atos que não possuem localização geográfica conhecida, cada um com a razão explícita da não-localização em linguagem legível.
- **FR-006**: O sistema DEVE excluir completamente do catálogo os lugares que, após processamento, se revelam não serem de fato lugares (nomes de pessoas mal-identificados, substantivos comuns, referências circulares).
- **FR-007**: O sistema DEVE exibir uma legenda permanente e sempre visível explicando a codificação visual da incerteza.
- **FR-008**: O sistema DEVE exibir um texto explicativo permanente descrevendo por que um mesmo lugar pode aparecer com múltiplos pontos no mapa.
- **FR-009**: O sistema DEVE exibir uma visualização de rede mostrando quais lugares de Atos coocorrem nos mesmos capítulos, incluindo a possibilidade de filtrar por capítulo ou faixa de capítulos.
- **FR-010**: O sistema DEVE agrupar visualmente os lugares da rede exibida no app por comunidade detectada automaticamente. A comparação quantitativa dessas comunidades com os três blocos narrativos de referência de Atos (Jerusalém; Judeia e Samaria; missão aos gentios) é calculada e documentada apenas no relatório escrito, não exibida interativamente no app.
- **FR-011**: O sistema DEVE sinalizar explicitamente qualquer comunidade detectada que seja internamente desconexa, em vez de apresentá-la sem ressalvas.
- **FR-012**: O sistema DEVE calcular e reportar a distribuição de lugares por número de candidatos de localização (1, 2, 3+) como evidência quantitativa central do grau de incerteza de identificação presente nos dados.
- **FR-013**: O sistema DEVE reportar métricas de rede baseadas em distância (ex.: comprimento total da rede, distância média, itinerário narrativo) acompanhadas de intervalo de confiança que reflete a incerteza de localização, e do valor obtido usando somente o candidato de maior confiança, para comparação.
- **FR-014**: O sistema NÃO DEVE variar métricas puramente estruturais da rede (grau, intermediação, comunidade) em função da incerteza de localização, pois essas métricas não dependem de coordenadas.
- **FR-015**: O sistema DEVE avaliar candidatos a novas conexões entre versículos de Atos e o restante do texto bíblico, usando ao menos duas estratégias de avaliação com níveis de rigor diferentes, e documentar os resultados de ambas lado a lado no relatório escrito, sem favorecer a que produz números mais favoráveis. Esta análise não é exibida interativamente no app.
- **FR-016**: O sistema DEVE exibir a atribuição de licença das fontes de dados geográficos e de referências cruzadas de forma permanente e visível.
- **FR-017**: O sistema NÃO DEVE modificar os dados de origem; toda informação exibida deve ser derivada e reprodutível a partir dos dados brutos originais.
- **FR-018**: O processo de geração dos dados exibidos DEVE ser reprodutível: executá-lo novamente com os mesmos parâmetros produz o mesmo resultado.
- **FR-019**: O sistema DEVE incluir um teste de compreensão com um pequeno grupo de usuários reais para verificar se a codificação visual da incerteza é entendida sem explicação prévia.
- **FR-020**: O sistema DEVE permitir ordenar ou destacar lugares pelo grau de dispersão entre seus candidatos de localização (lugares mais disputados primeiro), usando o índice de dispersão calculado por lugar.

### Key Entities

- **Lugar (Place)**: um local mencionado no texto de Atos; possui nome, tipo, lista de versículos onde é mencionado, e um indicador de se é localizável ou não.
- **Candidato de Localização**: uma hipótese de localização geográfica para um lugar, com coordenadas, grau de confiança (score) e probabilidade relativa frente aos demais candidatos do mesmo lugar.
- **Motivo de Não-Localização**: razão explícita pela qual um lugar não pode ser posicionado no mapa (ex.: localização desconhecida, lugar simbólico/profético, referência a múltiplos locais).
- **Versículo**: unidade textual de referência de uma menção a um lugar, associada a um capítulo do livro de Atos.
- **Conexão de Coocorrência**: relação entre dois lugares que aparecem no mesmo capítulo, com peso proporcional à frequência de coocorrência.
- **Comunidade**: agrupamento de lugares detectado a partir da estrutura de coocorrência.
- **Candidato a Nova Conexão**: par de versículos (um em Atos, outro em qualquer lugar da Bíblia) sugerido como referência cruzada plausível, ainda não presente no catálogo de referências conhecidas.
- **Fonte**: referência bibliográfica que embasa uma identificação ou localização de um lugar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Ao selecionar qualquer lugar localizável, o usuário consegue ver todos os seus candidatos de localização e o grau de confiança relativo de cada um em uma única tela, sem navegação adicional.
- **SC-002**: 100% dos lugares mencionados em Atos sem localização conhecida aparecem listados com razão explícita — nenhum é descartado silenciosamente.
- **SC-003**: Em um teste de compreensão com 3 a 5 participantes reais, ao menos 80% consegue explicar corretamente, após usar a aplicação, por que alguns lugares aparecem com múltiplos pontos no mapa.
- **SC-004**: O relatório final apresenta a distribuição de lugares por número de candidatos (1 / 2 / 3+) com destaque, permitindo avaliar diretamente se a hipótese de incerteza de identificação se sustenta nos dados.
- **SC-005**: Todas as métricas de rede baseadas em distância são reportadas com intervalo de confiança e comparadas ao valor determinístico equivalente, permitindo julgar se a incerteza de localização tem impacto agregado relevante.
- **SC-006**: A comparação entre estratégias de avaliação de novas conexões é reportada lado a lado, com a diferença entre elas discutida explicitamente no relatório, independentemente de qual resultado for mais favorável.
- **SC-007**: A aplicação publicada é acessível publicamente via link, sem exigir instalação, cadastro ou autenticação por parte do usuário.

## Assumptions

- Escopo restrito ao livro de Atos (livro 44); demais livros bíblicos não são processados nem exibidos, mesmo quando referenciados como alvo de uma conexão cruzada.
- Fontes de dados: repositório aberto de geolocalização bíblica (licença CC BY 4.0) e conjunto de referências cruzadas do mesmo projeto (licença CC BY); o formato exato do arquivo de referências cruzadas será inspecionado e documentado antes de qualquer suposição sobre sua estrutura.
- Não há autenticação de usuário, conta, nem persistência de dados por usuário — a aplicação é somente leitura/exploração.
- Não há backend em tempo de execução; a aplicação é publicada como site estático, com todos os dados pré-processados incluídos.
- Público-alvo: leitores do relatório acadêmico do projeto e visitantes interessados na exploração da rede de lugares — uso de baixa concorrência, não uma aplicação de produção em larga escala.
- O teste de compreensão da interface é feito com uma amostra pequena (3 a 5 pessoas), suficiente para validar a legibilidade da codificação visual, não para generalização estatística.
- Otimização específica para telas móveis não é requisito desta versão.
- Resultados de candidatos a novas conexões (referências cruzadas) e a comparação quantitativa de comunidades (NMI/ARI) são apresentados apenas no relatório escrito; não fazem parte da aplicação web interativa desta versão.
- Texto bíblico completo não é exibido em nenhum momento — apenas referências (livro, capítulo, versículo) e metadados de lugares.
- Atribuição de fonte bibliográfica por candidato individual é best-effort: depende de uma chave de join com `source.jsonl` ainda não confirmada na documentação de origem. Se não existir, a atribuição de licença permanece garantida via rodapé genérico (FR-016), sem bloquear nenhuma user story.
