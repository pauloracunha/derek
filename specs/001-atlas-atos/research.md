# Research: Atlas de Atos

Todas as decisões de stack já vinham fixadas no documento de definição técnica (`definitions.md`) fornecido pelo usuário; este documento consolida a justificativa (Decision/Rationale/Alternatives) e resolve os poucos pontos deixados como inspeção empírica em vez de suposição.

## 1. Formato do arquivo de referências cruzadas (OpenBible.info Cross References)

- **Decision**: Não presumir formato. Antes de escrever qualquer parser, inspecionar o arquivo bruto (`head -5`, contagem de linhas, delimitador, presença de cabeçalho, formato das referências — provavelmente OSIS, ex. `Acts.1.8`) e documentar o observado em `docs/data-contracts.md`.
- **Rationale**: O próprio documento de definição marca isso explicitamente como não verificado ("o formato exato deste arquivo deve ser inspecionado antes de escrever o parser. Não assumir colunas."). Presumir um formato errado quebra o parser silenciosamente ou, pior, produz pares de referência incorretos sem erro visível.
- **Alternatives considered**: Assumir CSV com cabeçalho OSIS-OSIS (comum em distribuições do TSK) — rejeitado porque o documento de origem exige verificação, não suposição; é tratado como tarefa da Sessão 1 do pipeline (`s01_download.py`/inspeção), não como decisão de arquitetura.

## 2. Armazenamento intermediário: DuckDB

- **Decision**: DuckDB como camada intermediária entre os `.jsonl` brutos e as saídas processadas.
- **Rationale**: Lê JSONL nativamente sem ETL customizado, executa os joins (`ancient` × `modern` × `source`) em SQL declarativo, é um arquivo único sem servidor — compatível com o requisito "sem backend em runtime" e com reprodutibilidade (pode ser apagado e recriado do zero).
- **Alternatives considered**: SQLite (sem leitura nativa de JSONL, exigiria ETL manual); pandas/Polars puro sem camada SQL (viável na escala do projeto, mas perde a clareza declarativa do filtro `WHERE sort LIKE '44%'` usado para validar H1); Postgres (servidor de banco de dados — viola o não-objetivo de backend em runtime).

## 3. Manipulação tabular: Polars ou pandas

- **Decision**: Indiferente — escolha livre na fase de tasks, ambos compatíveis com a escala (~100 lugares, milhares de versículos/arestas).
- **Rationale**: Volume de dados pequeno o suficiente para que a diferença de desempenho entre as duas bibliotecas seja irrelevante para os objetivos do projeto.
- **Alternatives considered**: N/A — decisão de baixo impacto, deferida à implementação.

## 4. Grafo e comunidades: networkx (Louvain) com opção de igraph/leidenalg (Leiden)

- **Decision**: `networkx` para construção de grafo e métricas topológicas (grau, intermediação); `networkx.community.louvain_communities` para detecção de comunidades, com `python-igraph` + `leidenalg` como alternativa caso Louvain produza comunidades internamente desconexas de forma persistente.
- **Rationale**: Escala do grafo (~100 nós de lugares) é trivial para `networkx`; usar `igraph` como padrão seria complexidade desnecessária. Louvain é suficiente nessa escala, mas tem falha conhecida (comunidades desconexas), por isso o pipeline valida conectividade após a detecção (Constitution não exige Leiden, mas exige a verificação).
- **Alternatives considered**: `igraph`/Leiden como padrão — rejeitado por overkill na escala do projeto; usado apenas como fallback documentado se a verificação de conectividade falhar.

## 5. Predição de links: heurísticas + node2vec

- **Decision**: Seis modelos em ordem crescente de complexidade — Vizinhos Comuns, Jaccard, Adamic-Adar, Preferential Attachment (heurísticas, sem dependência externa além de `networkx`), depois `node2vec` + Regressão Logística e `node2vec` + Gradient Boosting (via `scikit-learn`), combinando embeddings por produto de Hadamard.
- **Rationale**: Ordem heurística-antes-de-aprendizado é deliberada — expõe explicitamente se um modelo complexo supera uma baseline simples (achado relevante e esperado em grafos pequenos e esparsos, conforme Constitution VI: resultado fraco/contra-intuitivo é reportado, não escondido).
- **Alternatives considered**: Deep learning (GNN) — explicitamente fora de escopo (documento de definição: "ML: scikit-learn + node2vec — sem deep learning"), desproporcional à escala do grafo.

## 6. Amostragem negativa para avaliação de link prediction

- **Decision**: Duas estratégias obrigatórias, reportadas lado a lado — `random` (baseline ingênua, pares uniformemente aleatórios) e `distance_matched` (negativos com distribuição de distância canônica pareada aos positivos).
- **Rationale**: Amostragem puramente aleatória infla artificialmente o AUC (pares distantes no cânon são triviais de distinguir) e não mede a capacidade real do modelo. A comparação entre as duas estratégias é, pelo próprio documento de definição, "um dos achados mais defensáveis do trabalho" — por isso ambas são obrigatórias, não uma escolha de conveniência.
- **Alternatives considered**: Somente `random` — rejeitado por produzir avaliação inflada e não-diagnóstica; somente `distance_matched` — rejeitado por remover a evidência comparativa que demonstra o problema.

## 7. Distância geodésica: pyproj/geopy sobre WGS84

- **Decision**: Distância geodésica real (WGS84) via `pyproj` ou `geopy`, nunca distância euclidiana sobre lat/lon bruto.
- **Rationale**: Lat/lon não é um plano cartesiano; distância euclidiana sobre graus produz erro sistemático crescente com a latitude e a extensão da área (relevante na escala do Mediterrâneo oriental, ~20° de longitude). Métrica exigida em toda a análise baseada em distância (Constitution, seção "Qualidade e reprodutibilidade").
- **Alternatives considered**: Distância euclidiana simples — rejeitada por introduzir erro sistemático sem necessidade, já que bibliotecas de distância geodésica são triviais de usar em Python.

## 8. Simulação de incerteza: Monte Carlo restrito a métricas de distância

- **Decision**: Simular apenas as métricas de distância listadas no documento de definição, com N=1000, seed fixa. Quatro são escalares de rede (comprimento total da rede, distância média por aresta, área do fecho convexo, comprimento do itinerário narrativo), reportadas com média + IC 95% (percentis 2.5/97.5) e valor determinístico. A quinta — centralidade geográfica — é um **ranking por lugar** (distância ao centroide ponderado), não um escalar de rede; reportada como estabilidade de ranking (`modal_rank`/`rank_ci`) por lugar através das simulações, não como média/IC de um número único (corrigido em `contracts/uncertainty.schema.json`, grill 2026-08-11 Q1). Métricas topológicas puras nunca são simuladas.
- **Rationale**: Métricas topológicas dependem só de quem coocorre com quem — não mudam se um ponto se desloca no mapa. Simulá-las seria, nas palavras do próprio documento de definição, "teatro estatístico": custo computacional e cognitivo sem ganho de informação.
- **Alternatives considered**: Simular todas as métricas indiscriminadamente por uniformidade de processo — rejeitado por violar a correção conceitual explícita da fonte e a Constitution (Princípio VI / seção de qualidade).

## 9. Frontend: MapLibre GL JS + d3-force em painel lateral

- **Decision**: MapLibre GL JS para o mapa (sem chave de API, sem custo, open source) com tiles CARTO Positron ou Stadia; `d3-force` sobre SVG para a rede, em painel lateral separado do mapa — não sobreposto a ele.
- **Rationale**: MapLibre evita dependência de serviço pago (ex. Mapbox com chave). Manter a rede em painel separado evita a complexidade e a poluição visual de sobrepor um force-directed graph diretamente sobre um mapa geográfico, que tornaria as duas camadas de informação (localização vs. relação estrutural) difíceis de ler simultaneamente.
- **Alternatives considered**: Renderizar o grafo como camada sobre o mapa (nós nas posições geográficas reais) — rejeitado explicitamente pelo documento de definição ("Não tentar desenhar force-graph sobre o mapa").

## 10. Estado do frontend: Zustand ou Context

- **Decision**: Indiferente — Zustand ou Context API, decisão de baixo impacto para uma aplicação pequena (poucas telas, sem fluxo de autenticação ou formulários complexos).
- **Rationale**: Escala da aplicação não justifica uma escolha de gerenciamento de estado mais robusta (Redux, etc.); qualquer uma das duas resolve o compartilhamento de estado entre mapa, painel de detalhe e grafo.
- **Alternatives considered**: N/A — deferido à implementação.

## 11. Deploy: site estático

- **Decision**: Vercel, Netlify ou GitHub Pages — qualquer hospedagem estática, sem servidor em runtime.
- **Rationale**: Não-objetivo explícito do projeto é "autenticação, banco de dados servidor, backend em runtime". Todos os dados são pré-computados pelo pipeline e servidos como arquivos estáticos.
- **Alternatives considered**: N/A — restrição de escopo já fixada na especificação, não uma escolha em aberto.

## Resumo de riscos conhecidos (carregados para `data-model.md` e testes)

- Ordem de coordenadas `lonlat` = `"longitude,latitude"` — risco de inversão silenciosa se não testado.
- `friendly_id` único apenas dentro de `ancient.jsonl`, não no dataset inteiro — risco de colisão de chave em joins com `modern.jsonl`.
- `description` de identificação contém XML embutido (`<modern id="...">`) — precisa de limpeza antes de exibir na UI.
- `lonlat_type = "settlement"` comunica precisão de área, não ponto exato — precisa de sinalização visual distinta (já capturado em FR-004).
- `time_values`/`time_best_fits` vêm como array vazio quando não há disputa (`time_total = 1000`) — tratar como caso normal, não erro.
- `sort` é string de 8 caracteres com zeros à esquerda — nunca converter para inteiro (Constitution IV).
