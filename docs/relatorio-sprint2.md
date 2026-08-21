# Relatório da Sprint 2 — Análise de Rede e Modelagem

**Feature**: `specs/003-sprint2-analise-modelagem/` · **Status**: implementada e testada (31/31 tasks) · **Testes-Constitution**: 25/25 passando (22 rápidos + 3 lentos)

Esta sprint implementou os quatro módulos de análise do pipeline (`s04`–`s07`), respondendo às hipóteses H2 (a incerteza de localização importa em agregado?) e H3 (é possível prever conexões bíblicas ainda não catalogadas?). Não inclui interface — é análise pura, consumida pelo relatório escrito e, no caso de grafo/incerteza, pelos contratos que a aplicação web da Sprint 3 vai ler.

---

## 1. Grafo de coocorrência e métricas topológicas (`s04_build_graph.py`)

Grafo não-direcionado: nós são os 107 lugares localizáveis de Atos (Sprint 1); duas arestas conectam lugares que aparecem no mesmo capítulo, com peso igual ao número de capítulos coocorrentes.

| Métrica | Valor |
|---|---|
| Nós | 107 |
| Arestas | 1.059 |
| Nós isolados | **0** |

**Achado**: nenhum dos 107 lugares de Atos está isolado na rede de coocorrência — todo lugar mencionado compartilha ao menos um capítulo com outro. Isso é evidência indireta de uma narrativa espacialmente densa: Atos não introduz lugares "de passagem" que nunca mais se cruzam com o resto da história.

Grau, grau ponderado e intermediação (`betweenness`) são calculados aqui e **nunca recalculados** nas etapas seguintes — são invariantes topológicos, não dependem de coordenada (Constitution VI). Isso é verificado automaticamente por `tests/test_topology_unaffected.py`, que roda a simulação de incerteza (seção 2) e confirma que os três valores não mudam nem em uma casa decimal.

---

## 2. Propagação de incerteza via Monte Carlo (`s05_uncertainty.py`) — H2

1.000 simulações, seed fixa (42). A cada rodada, cada lugar sorteia um candidato de localização proporcional à sua `probability` (Sprint 1). Quatro métricas escalares de rede + um ranking por lugar (centralidade geográfica — corrigido durante o `/grill-with-docs` desta sprint para não ser tratado como escalar, ver §5).

| Métrica | Média | IC 95% | Determinístico |
|---|---|---|---|
| Comprimento total da rede (km) | 666.637,3 | [665.608,9 — 667.109,6] | 667.093,0 |
| Distância média por aresta (km) | 629,50 | [628,53 — 629,94] | 629,93 |
| Área do fecho convexo (km²) | 4.843.277,7 | [4.843.277,7 — 4.843.277,7] | 4.843.277,7 |
| Itinerário narrativo (km) | 153.737,0 | [153.321,9 — 154.145,4] | 153.859,5 |

### Leitura honesta do resultado (Constitution VI)

**O intervalo de confiança é estreito em todas as quatro métricas** — a maior variação relativa é de ~0,2% (comprimento total da rede). Isso **não é falha de implementação**: é consequência direta do achado já registrado na Sprint 1 — só 4,7% dos lugares de Atos têm mais de um candidato de localização. Com 95,3% dos lugares fixos entre simulações, a rede como um todo mal se move.

**Achado adicional, não previsto no desenho original**: a área do fecho convexo tem variância **zero** — média, IC baixo, IC alto e valor determinístico são exatamente o mesmo número. Isso acontece porque os pontos que definem o perímetro do fecho convexo (Roma, Etiópia/Meroe, os extremos geográficos da narrativa) são todos lugares com um único candidato — os poucos lugares com candidatos concorrentes ficam geograficamente "no meio" da rede, nunca nas bordas que determinam a área. A forma geral do alcance geográfico de Atos é, portanto, completamente determinada pelos lugares menos disputados, não pelos mais disputados — um achado conceitualmente interessante que reforça a reformulação da Sprint 1 (a incerteza que existe não é a que move a leitura agregada).

**Resposta a H2, como está**: a incerteza de identificação de localização, na escala em que ocorre em Atos, **tem impacto agregado pequeno** sobre a rede. A hipótese não é confirmada no sentido forte (H2 previa que o intervalo seria largo o suficiente para mudar a leitura); é reportada como está, não forçada.

### Ranking de centralidade geográfica

Por lugar, `modal_rank` (posição mais frequente no ranking de distância ao centroide ponderado por `mention_count`) e `rank_ci` (faixa de posições observada nas 1.000 simulações). Para a maioria dos 102 lugares com candidato único, `rank_ci` é um intervalo degenerado (`[r, r]` — a posição nunca muda). Só os 5 lugares com múltiplos candidatos têm faixa de posição não-trivial — efeito concentrado exatamente onde a Sprint 1 previu.

---

## 3. Comunidades vs. partição narrativa de referência (`s06_communities.py`)

Detecção via Louvain sobre o mesmo grafo de coocorrência, seed fixa. Partição de referência: três blocos tradicionais de Atos (Jerusalém, caps. 1–7; Judeia e Samaria, caps. 8–12; missão aos gentios, caps. 13–28), atribuídos pelo primeiro capítulo de menção de cada lugar.

| Métrica | Valor |
|---|---|
| Comunidades detectadas | 5 |
| Comunidades internamente desconexas | 0 |
| NMI (normalized mutual information) | 0,2367 |
| ARI (adjusted Rand index) | 0,1136 |

### Leitura honesta do resultado

Concordância **baixa** entre os agrupamentos automáticos e a divisão narrativa tradicional (NMI/ARI perto de 0, que é o valor esperado sob partições independentes; 1,0 seria concordância perfeita). Isso é reportado como está — não é um resultado "ruim", é informação: a estrutura de coocorrência que emerge da leitura pura de "quem aparece com quem por capítulo" **não replica** a divisão teológica/geográfica tradicional em três fases. As 5 comunidades detectadas provavelmente refletem agrupamentos de proximidade geográfica de curto prazo (uma viagem específica, uma cidade e seus arredores imediatos) em vez da macroestrutura narrativa de longo prazo que a tradição exegética usa. Nenhuma comunidade saiu desconexa — o algoritmo produziu grupos topologicamente coerentes, só não alinhados à partição de referência.

---

## 4. Predição de links (`s07_linkpred.py`) — H3

Rede ego de raio 1 em torno dos versículos de Atos, construída a partir do catálogo de referências cruzadas do OpenBible.info (Sprint 1).

| Métrica | Valor |
|---|---|
| Nós | 7.821 |
| Arestas | 38.759 |
| Densidade | 0,00127 |

Split treino/teste 80/20, garantindo grau mínimo 1 em treino. Seis modelos — quatro heurísticas estruturais e dois aprendidos (`node2vec` + Regressão Logística / Gradient Boosting, combinados por produto de Hadamard) — cada um avaliado sob duas estratégias de amostragem negativa.

| Modelo | `random` (AUC / AP) | `distance_matched` (AUC / AP) | Δ AUC |
|---|---|---|---|
| Common Neighbors | 0,805 / 0,803 | 0,801 / 0,797 | −0,004 |
| Jaccard | 0,805 / 0,804 | 0,800 / 0,792 | −0,005 |
| Adamic-Adar | 0,805 / 0,806 | 0,801 / 0,802 | −0,004 |
| Preferential Attachment | 0,814 / 0,805 | 0,781 / 0,765 | **−0,033** |
| node2vec + Regressão Logística | 0,874 / 0,887 | 0,849 / 0,856 | **−0,025** |
| node2vec + Gradient Boosting | 0,855 / 0,870 | 0,822 / 0,831 | **−0,033** |

### Leitura honesta do resultado

**A estratégia `distance_matched` é sistematicamente mais difícil que `random`, mas o tamanho do efeito varia por modelo** — este é o achado mais defensável desta sprint (era esperado pelo desenho original e se confirmou):

- **Heurísticas estruturais locais** (Common Neighbors, Jaccard, Adamic-Adar) quase não mudam entre as duas estratégias (Δ AUC entre −0,004 e −0,005). Fazem sentido: essas heurísticas olham só a vizinhança imediata dos dois versículos, não a distância no cânon — não têm "atalho" de distância pra explorar, e portanto não perdem quando esse atalho é removido.
- **Preferential Attachment e os dois modelos aprendidos perdem de 2,5 a 3,3 pontos de AUC** ao trocar para `distance_matched`. Isso indica que parte do desempenho desses modelos sob amostragem aleatória vinha de aprender "versículos próximos no cânon tendem a se referenciar" — um atalho estatístico real, mas não o mesmo que entender a estrutura da rede de referências em si. `distance_matched` neutraliza esse atalho ao forçar os negativos a terem a mesma distância canônica dos positivos.
- **Nenhuma heurística superou os modelos aprendidos** nesta rede — `node2vec + Regressão Logística` foi o melhor modelo sob as duas estratégias (AUC 0,874 e 0,849). Isso diverge da "expectativa calibrada" do desenho original do projeto (que heurísticas simples costumam empatar ou superar embeddings em grafos pequenos e esparsos) — reportado como está, sem ajustar o experimento para forçar esse resultado.

**Resposta a H3, como está**: é possível prever conexões plausíveis com desempenho consistentemente acima do acaso (AUC ~0,78–0,87 mesmo na avaliação mais rigorosa), mas a diferença entre as duas estratégias de amostragem negativa mostra que parte do sinal aprendido é proximidade no cânon, não necessariamente relação de conteúdo — distinção que só a comparação das duas estratégias, lado a lado, torna visível.

---

## 5. Dois bugs reais achados e corrigidos durante a implementação

Registrados aqui porque ambos mudaram o resultado numérico, não só o código — e porque a forma como foram encontrados (teste automatizado, não inspeção visual) é evidência do rigor metodológico do processo.

### 5.1 `distance_matched` estava, na prática, indistinguível de `random`

Implementação inicial buscava um par de amostragem negativa com a distância canônica desejada por até 50 tentativas aleatórias. Num espaço de 7.821 nós, a chance de acertar uma distância específica por sorteio é baixa — a busca caía no fallback aleatório na maioria das vezes, produzindo resultados de `distance_matched` quase idênticos a `random` (AUC 0,798 vs. 0,798 na primeira execução). Substituída por busca direcionada (`bisect` sobre os nós ordenados por posição canônica), que sempre encontra um candidato próximo da distância-alvo. Depois da correção, o efeito esperado (§4) apareceu.

### 5.2 Voto negativo "ressuscitava" como aresta positiva pela direção oposta

O catálogo de referências cruzadas lista as duas direções de um par com votos **possivelmente diferentes** — achado real: `Acts.3.19→Acts.3.21` tem voto 4, mas `Acts.3.21→Acts.3.19` tem voto **−1**, no mesmo catálogo. Como o grafo desta sprint é não-direcionado, a implementação inicial aceitava a aresta se qualquer uma das duas direções tivesse voto ≥ 0 — deixando pares com voto rejeitado numa direção entrarem pela porta dos fundos da direção oposta. Corrigido para somar o voto das duas direções antes de aplicar o filtro (mesmo critério já usado para `score` negativo de candidato de localização, Sprint 1, ADR 0003) — o voto relevante é o líquido do par, não de uma direção isolada.

---

## 6. Tempo de execução

Do início de `s04_build_graph.py` até os quatro artefatos prontos (`graph.json`, `uncertainty.json`, `docs/community-comparison.md`, `linkpred.json`): **~105 segundos**, via `uv run python -m pipeline.s08_export`. A maior parte do tempo é o treinamento `node2vec` em `s07_linkpred.py` (rede de ~7.800 nós); os outros três módulos rodam em poucos segundos.

## 7. O que esta sprint não faz (por decisão, não por lacuna)

- Não tem interface interativa — `graph.json`/`uncertainty.json` alimentam a UI da Sprint 3; comunidades (NMI/ARI) e predição de links são só relatório, decisão já registrada na sessão de clarificação da Sprint 1.
- Não usa o catálogo bíblico inteiro de referências cruzadas (344.789 pares) — só a vizinhança ego de raio 1 em torno de Atos (7.821 nós), por escopo deliberado do projeto.
- Não força nenhum resultado — os três achados "fracos" desta sprint (IC estreito, NMI/ARI baixo, heurísticas não superando ML) são reportados exatamente como saíram, por exigência da Constitution (Princípio VI).
