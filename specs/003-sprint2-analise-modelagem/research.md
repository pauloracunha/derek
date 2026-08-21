# Research: Sprint 2 — Análise de Rede e Modelagem

A maior parte das decisões de stack já foi tomada em `specs/001-atlas-atos/research.md` (itens 4-9: networkx/Louvain, node2vec+heurísticas, amostragem negativa dupla, geodésica WGS84, Monte Carlo restrito, MapLibre — este último não se aplica aqui). Este documento cobre só as decisões **novas**, específicas desta sprint.

## 1. Pares de referência cruzada com voto líquido negativo ou zero

- **Decision**: um par `(from_verse, to_verse)` é excluído do conjunto de arestas positivas **só** quando o voto líquido é negativo (rejeição ativa da comunidade). Pares com voto líquido zero **permanecem** como positivos válidos — continuam sendo referências cruzadas catalogadas e reais, só sem sinal de confiança extra; excluí-los jogaria fora conexões conhecidas sem motivo (contagem real em Atos: 59 negativos, 102 zero, 13.158 positivos — excluir os 102 descartaria ~0,8% do catálogo de Atos sem razão). Um par excluído (voto negativo) não é reaproveitado como negativo automático de treino — é simplesmente removido do grafo de referências (grill 2026-08-11 Q2).
  **Correção de implementação (achado real)**: como o grafo é não-direcionado mas o catálogo lista as duas direções de um par com votos possivelmente diferentes (`Acts.3.19→Acts.3.21=4` vs. `Acts.3.21→Acts.3.19=-1`), "voto líquido" significa a **soma das duas direções**, calculada antes do filtro — nunca o voto de uma direção isolada (`pipeline/s07_linkpred.py::build_ego_network`).
- **Rationale**: mesma disciplina já registrada em `docs/adr/0003-normalizacao-score-negativo.md` — um voto líquido negativo é evidência de que a comunidade rejeitou aquele par, não uma conexão fraca-mas-válida. Tratá-lo como positivo fabricaria confiança que a fonte não expressa; tratá-lo como negativo de treino introduziria um viés não solicitado pela especificação. Exclusão simples é a opção mais neutra.
- **Alternatives considered**: usar o voto como peso de aresta (permitindo negativo) — rejeitado porque a maioria dos algoritmos de grafo (incluindo os de `networkx` usados aqui) não têm semântica bem definida para peso negativo; manter como positivo com peso baixo — rejeitado pela mesma razão do ADR 0003 (fabricaria confiança inexistente).

## 2. Rede de referências cruzadas em torno de Atos

- **Decision**: subgrafo ego de raio 1 a partir dos versículos de Atos presentes em `cross-references.txt` — todos os pares onde Atos aparece de um lado, mais os vizinhos diretos desses alvos (já previsto em `definitions.md` §5.4 e herdado por `001-atlas-atos`).
- **Rationale**: mantém o volume computacional tratável nesta escala (~13.300 pares com Atos como origem, ver `docs/data-contracts.md`) sem exigir o catálogo bíblico inteiro (344.790 pares), que introduziria ruído de domínios totalmente alheios a Atos.
- **Alternatives considered**: catálogo completo — rejeitado por escopo (o projeto é recortado a Atos, Constitution/spec `001`); só arestas onde Atos é a origem, sem vizinhos diretos — rejeitado por reduzir demais o volume de treino, arriscando a limitação de P5 (`relatorio.md`) se ainda insuficiente.

## 3. Métrica de concordância entre comunidades e partição narrativa

- **Decision**: NMI (normalized mutual information) e ARI (adjusted Rand index), calculados via `scikit-learn` (`sklearn.metrics.normalized_mutual_info_score`, `sklearn.metrics.adjusted_rand_score`) — já previstas nominalmente em `definitions.md`/`001-atlas-atos`, aqui só confirmada a biblioteca (já é dependência do projeto, sem adição nova).
- **Rationale**: são as duas métricas padrão da literatura de detecção de comunidades para comparar partições, com implementação madura já disponível na dependência já instalada — nenhuma escolha nova de fato, só a confirmação de que não precisa de biblioteca adicional.
- **Alternatives considered**: nenhuma — é escolha já resolvida no planejamento original, sem ambiguidade a resolver aqui.

## 4. Quando reportar rede insuficiente para predição de links (Edge Case do spec)

- **Decision**: não existe um limiar numérico fixo de "insuficiente" — a decisão é qualitativa e feita na redação do relatório, comparando o volume de arestas positivas obtidas (após excluir votos negativos, decisão 1 acima) com a ordem de grandeza mínima citada em `definitions.md`/`relatorio.md` P5 (grafo ego de raio 1, ~alguns milhares de arestas esperadas). Se os resultados de AUC/AP para as heurísticas ficarem próximos de 0.5 (equivalente a chute aleatório) mesmo na estratégia `distance_matched`, isso é reportado como sinal de rede insuficiente, não escondido.
- **Rationale**: um limiar numérico arbitrário definido agora (antes de ver o dado real) correria o risco de ser ele mesmo um ajuste pós-hoc disfarçado — indo contra a Constitution VI. Melhor deixar o próprio resultado (AUC próximo do acaso) ser o sinal, e descrever isso na redação, do que inventar um número de corte sem base.
- **Alternatives considered**: fixar um limiar (ex. "menos de 500 arestas positivas = insuficiente") — rejeitado por ser arbitrário e não rastreável a nenhuma fonte; a Sprint 1 já mostrou (achado do bbox, achado do H1 fraco) que compromissos numéricos fixados antes de ver o dado real tendem a precisar de correção depois.
