# Feature Specification: Sprint 2 — Análise de Rede e Modelagem

**Feature Branch**: `003-sprint2-analise-modelagem`

**Created**: 2026-08-11

**Status**: Draft

**Input**: User description: "agora sigamos para a sprint 2 considerando todos os achados da sprint 1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver como os lugares de Atos se relacionam estruturalmente (Priority: P1)

Um leitor do relatório quer saber quais lugares de Atos aparecem juntos na narrativa (mesmo capítulo) e quais são estruturalmente mais centrais — sem que essa leitura dependa de onde cada lugar fica no mapa.

**Why this priority**: É a base de tudo que vem depois nesta sprint — comunidades e a métrica de itinerário narrativo dependem do grafo existir primeiro. Sem isso, não há Sprint 2.

**Independent Test**: Consultar o grafo de coocorrência exportado e verificar que cada lugar tem grau, grau ponderado e intermediação calculados, e que esses valores não mudam entre execuções (não dependem de simulação nenhuma).

**Acceptance Scenarios**:

1. **Given** o catálogo de lugares de Atos já extraído (Sprint 1), **When** o grafo de coocorrência é construído, **Then** cada par de lugares que aparece no mesmo capítulo gera uma conexão, com peso proporcional a quantos capítulos coocorrem.
2. **Given** um lugar mencionado só uma vez, sem coocorrer com nenhum outro, **When** o grafo é construído, **Then** esse lugar aparece como nó isolado — não é excluído do grafo.
3. **Given** o grafo construído, **When** as métricas topológicas são calculadas, **Then** grau, grau ponderado e intermediação são os mesmos em qualquer execução — nunca variam por causa de incerteza de localização.

---

### User Story 2 - Saber se a incerteza de localização muda a leitura agregada da rede (Priority: P1)

Um leitor do relatório quer saber se a existência de múltiplos candidatos de localização por lugar realmente afeta métricas agregadas da rede (distância total percorrida, distância média, etc.) ou se o efeito é desprezível — respondendo à pergunta central que motivou o projeto, mesmo sabendo que a taxa de multiplicidade de candidatos em Atos é baixa (achado real da Sprint 1: 4,7%).

**Why this priority**: É o resultado central de H2 — a comparação entre o valor "se a gente soubesse a localização exata" (determinístico) e o intervalo real de incerteza. Prioridade P1 porque é a pergunta que dá sentido ao projeto, independente da taxa de multiplicidade ser alta ou baixa.

**Independent Test**: Consultar as métricas de distância simuladas e verificar que cada uma vem com média, intervalo de 95% de confiança e o valor determinístico de referência, lado a lado.

**Acceptance Scenarios**:

1. **Given** o grafo de coocorrência e o catálogo de candidatos de localização, **When** a simulação de incerteza é executada, **Then** cada métrica escalar que depende de distância (comprimento total da rede, distância média por conexão, área do fecho convexo, comprimento do itinerário narrativo) é reportada com média, IC 95% e valor determinístico; a centralidade geográfica, por ser um ranking por lugar e não um número único de rede, é reportada como a posição mais frequente de cada lugar nesse ranking e a faixa de posições observada entre as simulações.
2. **Given** o itinerário narrativo, **When** calculado, **Then** ele revisita um lugar toda vez que a narrativa volta a mencioná-lo — não é deduplicado pela primeira menção.
3. **Given** as métricas puramente topológicas (grau, intermediação, comunidade) da User Story 1, **When** a simulação de incerteza é executada, **Then** essas métricas permanecem idênticas em toda simulação — a simulação nunca as recalcula.
4. **Given** o intervalo de confiança calculado, **When** reportado, **Then** o resultado é apresentado como está — seja o intervalo largo (incerteza importa em agregado) ou estreito (incerteza tem impacto agregado pequeno) — sem ajuste até "melhorar" o resultado.

---

### User Story 3 - Comparar os agrupamentos automáticos com a divisão narrativa tradicional (Priority: P2)

Um leitor do relatório quer saber se os agrupamentos de lugares que emergem automaticamente da estrutura de coocorrência correspondem à divisão narrativa tradicional de Atos (fase em Jerusalém; fase de expansão à Judeia e Samaria; fase da missão aos gentios).

**Why this priority**: Enriquece a leitura estrutural da User Story 1 com uma validação externa (a tradição narrativa), mas não é pré-requisito para nenhuma outra parte da sprint — por isso vem depois das duas prioridades P1.

**Independent Test**: Consultar a comparação entre as comunidades detectadas e a partição narrativa de referência e verificar que existe uma métrica de concordância reportada, e que nenhuma comunidade internamente desconexa passa sem aviso.

**Acceptance Scenarios**:

1. **Given** o grafo de coocorrência, **When** a detecção de comunidades é executada, **Then** cada lugar recebe uma comunidade, e toda comunidade internamente desconexa é sinalizada explicitamente, nunca apresentada como coesa sem ressalva.
2. **Given** as comunidades detectadas e a partição narrativa de referência (3 blocos), **When** comparadas, **Then** uma métrica padrão de concordância entre partições é calculada e reportada, independente de o resultado ser alto ou baixo.

---

### User Story 4 - Saber se é possível prever novas conexões bíblicas plausíveis (Priority: P2)

Um leitor do relatório quer saber se, a partir da estrutura de referências cruzadas já conhecida envolvendo Atos, é possível prever conexões plausíveis ainda não catalogadas — e quer essa avaliação feita de forma honesta, sem inflar artificialmente o resultado.

**Why this priority**: Responde a H3, mas depende de infraestrutura de avaliação (heurísticas, modelos, duas estratégias de amostragem negativa) mais pesada que as demais stories — e seu resultado, seja qual for, não bloqueia a leitura de rede das outras três stories. Por isso é P2, junto da User Story 3.

**Independent Test**: Consultar a tabela de resultados dos modelos de predição de links e verificar que as duas estratégias de amostragem negativa aparecem lado a lado para cada modelo, com a diferença entre elas discutida.

**Acceptance Scenarios**:

1. **Given** o catálogo de referências cruzadas já baixado na Sprint 1, **When** a rede em torno de Atos é construída, **Then** ao menos 4 heurísticas estruturais simples são avaliadas antes de qualquer modelo aprendido.
2. **Given** as heurísticas avaliadas, **When** os modelos aprendidos são avaliados, **Then** ao menos 2 modelos aprendidos são incluídos, e cada um dos 6 modelos é avaliado sob as 2 estratégias de amostragem negativa (aleatória e pareada por distância no cânone).
3. **Given** os 12 resultados (6 modelos × 2 estratégias), **When** reportados, **Then** a diferença de desempenho entre as duas estratégias é discutida explicitamente — inclusive se uma heurística simples superar um modelo aprendido.
4. **Given** um par de referência cruzada com voto líquido negativo (a comunidade rejeitou esse par), **When** processado, **Then** ele não é contado como conexão positiva de treino nem de avaliação — a mesma disciplina já aplicada a candidatos de localização com score negativo.

---

### Edge Cases

- Lugar mencionado uma única vez, sem coocorrer com nenhum outro: aparece como nó isolado no grafo, nunca excluído.
- Todos os candidatos de um lugar têm probabilidade igual (empate perfeito): a simulação de incerteza amostra uniformemente entre eles, sem preferência arbitrária por ordem ou índice.
- Par de referência cruzada com voto líquido negativo: nunca tratado como conexão positiva válida (ver User Story 4, Acceptance Scenario 4).
- Par de referência cruzada com voto líquido exatamente zero: permanece como conexão positiva válida — é uma referência catalogada e real, só sem sinal extra de confiança; só voto negativo (rejeição ativa) é excluído.
- Comunidade detectada com um único lugar (singleton): é resultado válido, reportado como está, não é erro.
- Rede de referências cruzadas em torno de Atos insuficiente em volume para treinar/avaliar os modelos com significância: a limitação é reportada explicitamente, o resultado não é forçado nem escondido.
- Comunidade detectada internamente desconexa: sinalizada explicitamente, nunca apresentada como grupo coeso.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE construir um grafo de coocorrência de lugares de Atos, onde dois lugares se conectam se aparecem no mesmo capítulo, com peso proporcional ao número de capítulos em que coocorrem.
- **FR-002**: O sistema DEVE calcular, para cada lugar, grau, grau ponderado e intermediação dentro do grafo de coocorrência.
- **FR-003**: O sistema DEVE simular, via método de amostragem repetida (mínimo 1000 simulações, semente fixa), apenas as métricas que dependem de distância geográfica: quatro escalares de rede (comprimento total da rede, distância média por conexão, área do fecho convexo, comprimento do itinerário narrativo) e um ranking por lugar (centralidade geográfica — distância ao centroide ponderado).
- **FR-004**: O sistema NÃO DEVE recalcular ou variar métricas puramente topológicas (grau, intermediação, comunidade) em função da simulação de incerteza — essas métricas não dependem de coordenadas.
- **FR-005**: O comprimento do itinerário narrativo DEVE ser calculado revisitando um lugar toda vez que a narrativa volta a mencioná-lo, nunca deduplicando pela primeira menção.
- **FR-006**: Toda métrica escalar simulada DEVE ser reportada com média, intervalo de 95% de confiança, e o valor obtido usando somente o candidato de localização de maior confiança (valor determinístico), lado a lado. O ranking de centralidade geográfica DEVE ser reportado, por lugar, com a posição mais frequente e a faixa de posições observada entre as simulações.
- **FR-007**: O sistema DEVE detectar comunidades de lugares a partir da estrutura do grafo de coocorrência.
- **FR-008**: Toda comunidade detectada que seja internamente desconexa DEVE ser sinalizada explicitamente, nunca apresentada sem essa ressalva.
- **FR-009**: O sistema DEVE comparar as comunidades detectadas com uma partição narrativa de referência de três blocos (fase em Jerusalém; fase de expansão à Judeia e Samaria; fase da missão aos gentios), usando uma métrica padrão de concordância entre partições.
- **FR-010**: O sistema DEVE construir, a partir do catálogo de referências cruzadas já obtido, a rede de referências em torno dos versículos de Atos.
- **FR-011**: O sistema DEVE avaliar candidatos a novas conexões bíblicas usando no mínimo 4 heurísticas estruturais simples, avaliadas antes de qualquer modelo aprendido.
- **FR-012**: O sistema DEVE avaliar também no mínimo 2 modelos aprendidos a partir da estrutura da rede.
- **FR-013**: Cada um dos modelos (heurísticos e aprendidos) DEVE ser avaliado sob duas estratégias de amostragem negativa — pares aleatórios e pares pareados por distância no cânone — e os resultados de ambas DEVEM ser reportados lado a lado, sem favorecer a estratégia que produz números mais favoráveis.
- **FR-014**: Um par de referência cruzada com voto líquido negativo NÃO DEVE ser tratado como conexão positiva válida em nenhuma etapa de treino ou avaliação.
- **FR-015**: Todo resultado desta sprint — inclusive fraco, nulo ou contrário à expectativa (ex.: heurística simples superando modelo aprendido, intervalo de confiança estreito, rede insuficiente para avaliação significativa) — DEVE ser reportado como está, sem ajuste do método até obter o resultado desejado.
- **FR-016**: Os resultados de grafo e de incerteza agregada DEVEM ser exportados em formato consumível pela aplicação web (contratos já definidos); os resultados de comunidades (comparação quantitativa) e de predição de links são destinados exclusivamente ao relatório escrito, não à interface interativa.

### Key Entities

- **Grafo de Coocorrência**: rede de lugares de Atos, onde arestas representam coocorrência em capítulo, com peso e lista de capítulos.
- **Métricas Topológicas**: grau, grau ponderado, intermediação — por lugar, invariantes à incerteza de localização.
- **Simulação de Incerteza**: conjunto de execuções repetidas (semente fixa) que amostram um candidato de localização por lugar a cada rodada, usadas só para métricas de distância.
- **Comunidade**: agrupamento de lugares detectado a partir do grafo de coocorrência, com indicação de conectividade interna.
- **Partição Narrativa de Referência**: divisão de Atos em três blocos narrativos tradicionais, usada como comparação externa às comunidades detectadas.
- **Par de Referência Cruzada**: par de versículos (um em Atos) com voto líquido da comunidade que embasa o catálogo de referências cruzadas — já obtido e caracterizado na Sprint 1.
- **Candidato a Nova Conexão**: par de versículos sugerido por um modelo de predição como referência cruzada plausível, ainda ausente do catálogo conhecido.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: As métricas topológicas de todo lugar são idênticas em qualquer execução, independente da simulação de incerteza rodar antes ou depois.
- **SC-002**: 100% das 4 métricas escalares de distância são reportadas com média, IC 95% e valor determinístico lado a lado; 100% dos lugares têm posição modal e faixa de posições reportadas no ranking de centralidade geográfica.
- **SC-003**: 100% das comunidades detectadas internamente desconexas aparecem sinalizadas — nenhuma passa sem aviso.
- **SC-004**: A comparação entre comunidades detectadas e a partição narrativa de referência é reportada com uma métrica de concordância padrão, qualquer que seja o valor obtido.
- **SC-005**: Os 6 modelos de predição de links são avaliados sob as 2 estratégias de amostragem negativa, resultando em 12 combinações reportadas lado a lado.
- **SC-006**: A diferença de desempenho entre as duas estratégias de amostragem negativa é discutida explicitamente no relatório, com a direção e a magnitude da diferença citadas.
- **SC-007**: O tempo entre iniciar a construção do grafo e ter os quatro artefatos desta sprint prontos (grafo, incerteza, comunidades, predição de links) é medido e reportado.

## Assumptions

- Os contratos de saída para grafo, incerteza agregada e predição de links já foram definidos na Sprint 1 (`specs/001-atlas-atos/contracts/`) — esta sprint implementa a geração desses dados, não redefine o formato.
- O catálogo de referências cruzadas já foi baixado e seu formato real (TSV, referências em OSIS, votos que podem ser negativos) já foi documentado na Sprint 1 (`docs/data-contracts.md`) — esta sprint parte de um formato já conhecido, não precisa de nova inspeção.
- A taxa real de lugares com múltiplos candidatos de localização em Atos (4,7%, achado da Sprint 1) não impede esta sprint: construção de grafo, detecção de comunidades e predição de links não dependem dessa taxa ser alta.
- Reprodutibilidade (semente fixa) segue o mesmo critério já estabelecido na Sprint 1: garantida dentro da mesma versão de dependências travada, não necessariamente através de atualizações futuras de bibliotecas.
- O comprimento do itinerário narrativo revisita lugares mencionados várias vezes, em vez de deduplicar pela primeira menção — decisão já tomada na Sprint 1.
- Esta sprint não inclui interface interativa — os artefatos de grafo e incerteza alimentam a aplicação web a ser construída na Sprint 3; os artefatos de comunidades (comparação quantitativa) e de predição de links alimentam só o relatório escrito, por decisão já registrada na especificação da Sprint 1.
- A rede de referências cruzadas usada para predição de links é a vizinhança direta de Atos dentro do catálogo completo (não o catálogo bíblico inteiro), para manter volume de computação tratável.
