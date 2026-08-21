# 1.2 Solução

> **Legenda:** trechos marcados com `[PREENCHER]` dependem do calendário do curso ou de evidência que só você pode produzir. Não os deixe no documento final.
>
> **Nota sobre a numeração:** o sumário do template indica "1.2.2 Premissas e Restrições" e "1.2.3 Backlog de Produto", enquanto o corpo indica "1.2.2 Escopo do Projeto" e "1.2.3 Cronograma de Ações Planejadas". Este documento adota os títulos do corpo e contempla o conteúdo de ambas as versões. Confirmar com o orientador qual numeração vale.

---

## 1.2.1 Objetivo SMART

### Objetivo principal

> Desenvolver e publicar, até o encerramento do prazo do Projeto Aplicado, um pipeline de dados reprodutível e uma aplicação web estática que catalogam os lugares mencionados no livro de Atos dos Apóstolos a partir de fontes abertas licenciadas em CC BY, **preservando 100% dos candidatos de localização registrados na fonte** — verificado por teste automatizado que falha se qualquer lugar for reduzido a um único candidato — e quantificando, por validação estatística, a cobertura do catálogo aberto de referências cruzadas por meio de um modelo de predição de links avaliado contra no mínimo quatro heurísticas de referência.

### Decomposição SMART

| Critério | Aplicação ao objetivo |
|---|---|
| **S — Específico** | O resultado é um artefato definido: pipeline em Python + aplicação web estática, restritos ao livro de Atos, consumindo `ancient.jsonl`, `modern.jsonl` e o catálogo de referências cruzadas do OpenBible.info. Não há ambiguidade sobre o que será entregue nem sobre o recorte. |
| **M — Mensurável** | Cinco critérios objetivos e verificáveis, listados abaixo. Nenhum depende de julgamento subjetivo. |
| **A — Atingível** | Todas as fontes são abertas e já obtidas; a escala é pequena (aproximadamente uma centena de lugares); o stack é o de domínio do autor (Python, SQL, React); não há dependência de terceiros, aprovação institucional, custo de licença ou infraestrutura servidora. |
| **R — Relevante** | Ataca uma falha de representação documentada na seção 1.1, que afeta desenvolvedores, produtores de material didático e leitores finais. O artefato é reaproveitável por terceiros sob licença aberta, e o método é agnóstico ao recorte. |
| **T — Temporal** | Três sprints, encerrando em `[PREENCHER: data limite de entrega]`. Cada sprint tem escopo e critério de aceite próprios, definidos em 1.2.3. |

### Critérios de aceite mensuráveis

| # | Critério | Forma de verificação | Meta |
|---|---|---|---|
| CA1 | Nenhum lugar com múltiplos candidatos é exportado com apenas um | Teste automatizado `test_no_candidate_collapse` | 0 ocorrências |
| CA2 | Pipeline executável do zero em um único comando | `uv run python -m pipeline.sprint1` (`just sprint1`), execução em ambiente limpo, do download à exportação — validado por `tests/test_sprint1_evidence_artifacts.py` | 1 comando |
| CA3 | Reprodutibilidade determinística | Duas execuções com a mesma seed produzem saídas idênticas | 100% |
| CA4 | Comparação honesta de modelos de predição de links | Mínimo de 4 heurísticas + 2 modelos aprendidos, com duas estratégias de amostragem negativa | 6 modelos, 2 estratégias |
| CA5 | Compreensão da representação de incerteza | Teste com usuários sem treinamento prévio, medindo se identificam corretamente o significado de múltiplos pontos | ≥ 3 participantes |

> **Nota de construção do objetivo.** Os critérios acima medem **entrega e método**, não a confirmação das hipóteses da seção 1.1. Essa separação é deliberada: um objetivo que dependesse de uma hipótese se confirmar seria, por definição, um objetivo cujo fracasso estaria fora do controle do executor. As hipóteses são testadas e reportadas com o resultado que apresentarem; o objetivo é atingido pela qualidade do teste, não pelo seu sinal.

### Objetivos secundários

| # | Objetivo | Métrica |
|---|---|---|
| OS1 | Publicar dataset derivado versionado, com procedência e licença declaradas | Repositório público com `LICENSE` e `docs/data-contracts.md` |
| OS2 | Registrar decisões arquiteturais que divergiram da especificação inicial | ADRs em `docs/adr/` |
| OS3 | Reduzir o custo de entrada para reuso por terceiros | Tempo entre clonar o repositório e obter os dados processados, medido e documentado |

---

## 1.2.2 Escopo do Projeto

### Premissas

Sentenças assumidas como verdadeiras, cuja comprovação depende de fatores externos ao projeto.

| # | Premissa | Impacto se falsa | Mitigação |
|---|---|---|---|
| P1 | Os datasets do OpenBible.info permanecem disponíveis no GitHub e sob CC BY durante a execução | **Alto** — inviabilizaria a fonte primária | Congelar cópia local dos arquivos brutos no início da Sprint 1, com registro do commit hash |
| P2 | O campo `modern_associations` contém candidatos concorrentes em volume suficiente para sustentar o eixo de incerteza de identificação | **Alto** — a premissa central do projeto perderia lastro | Gatilho de pivô definido: se a proporção ficar abaixo de 15%, adotar a incerteza de **precisão** (`lonlat_type`, `precision.meters`) como eixo principal, sem alteração de código |
| P3 | Os scores de confiança do dataset são normalizáveis em uma distribuição de probabilidade | **Médio** — exigiria formulação alternativa | Verificar o domínio real dos valores antes de aplicar a fórmula; documentar o tratamento adotado em ADR |
| P4 | A estrutura documentada no readme do dataset corresponde ao conteúdo real dos arquivos | **Médio** — retrabalho de parser | Sessão de inspeção obrigatória antes de escrever código de análise; formatos observados registrados em `docs/data-contracts.md` |
| P5 | O grafo de referências cruzadas restrito a Atos tem densidade suficiente para treinar e avaliar predição de links | **Médio** — o componente de ML perderia validade estatística | Expandir para a rede ego de raio 1 (Atos + alvos diretos); se ainda insuficiente, reportar a limitação em vez de forçar o resultado |
| P6 | O autor dispõe da carga horária semanal necessária para as três sprints | **Alto** — comprometeria o prazo | Escopo dimensionado com folga; itens de prioridade 6 a 8 já classificados como descartáveis na seção 1.1.4 |

### Restrições

| Tipo | Restrição | Origem |
|---|---|---|
| Prazo | Três sprints, encerramento em `[PREENCHER]` | Calendário do curso |
| Recurso humano | Execução individual, sem equipe | Natureza do Projeto Aplicado |
| Disponibilidade | Projeto conduzido em paralelo a atividade profissional em tempo integral | Contexto do autor |
| Jurídica | Uso restrito a fontes em domínio público ou CC BY; obrigatoriedade de atribuição visível | Licenciamento das fontes |
| Jurídica | Traduções bíblicas modernas em português são proprietárias e não podem ser redistribuídas | Direito autoral das editoras |
| Técnica | Arquitetura estática, sem backend em runtime | Ausência de orçamento para infraestrutura |
| Técnica | Sem uso de serviços de mapa que exijam chave de API paga | Custo |
| Escopo | Recorte limitado ao livro de Atos | Viabilidade dentro do prazo |
| Metodológica | Ausência de validação por especialista em arqueologia ou geografia histórica | Indisponibilidade de acesso a especialista |

### Escopo incluído

- Ingestão reprodutível de `ancient.jsonl`, `modern.jsonl` e do catálogo de referências cruzadas
- Filtragem e normalização dos lugares mencionados em Atos
- Preservação integral dos candidatos de localização, com probabilidade normalizada
- Classificação e exibição dos lugares não localizáveis, com a razão explícita
- Grafo de coocorrência de lugares por capítulo, com métricas topológicas
- Propagação de incerteza por simulação de Monte Carlo sobre métricas de distância
- Detecção de comunidades no grafo, comparada a uma partição narrativa de referência
- Predição de links sobre a rede de referências cruzadas, com heurísticas e modelos aprendidos
- Aplicação web estática com mapa interativo e representação visual da incerteza
- Documentação de contratos de dados, decisões arquiteturais e licenciamento

### Escopo excluído (declarado explicitamente)

- Exibição de texto bíblico integral
- Suporte a livros além de Atos
- Análise morfossintática ou de línguas originais
- Renderização de geometrias complexas (rios, regiões, polígonos)
- Autenticação, persistência de sessão ou backend em runtime
- Qualquer juízo sobre qual candidato de localização é o correto
- Produção de conhecimento teológico, histórico ou arqueológico original

> A última exclusão é a mais importante de declarar. O projeto **expõe** a incerteza produzida por terceiros; não a resolve, não a arbitra e não substitui julgamento especializado.

### Recursos necessários

| Categoria | Item | Custo |
|---|---|---|
| Dados | `ancient.jsonl`, `modern.jsonl`, `source.jsonl` (OpenBible.info, CC BY 4.0) | Gratuito |
| Dados | Catálogo de referências cruzadas (OpenBible.info, CC BY) | Gratuito |
| Computacional | Notebook pessoal; escala não exige GPU nem processamento distribuído | Já disponível |
| Software | Python 3.11+, DuckDB, networkx, scikit-learn, node2vec, pyproj | Código aberto |
| Software | Node.js, Vite, React, TypeScript, MapLibre GL JS | Código aberto |
| Serviços | Basemap de tiles sem chave de API | Gratuito |
| Serviços | Hospedagem estática (Vercel, Netlify ou GitHub Pages) | Camada gratuita |
| Serviços | Repositório Git público | Gratuito |
| Ferramenta | Assistente de codificação para execução assistida | Assinatura já existente |

**Custo financeiro total do projeto: zero.** Isso é consequência direta da restrição jurídica adotada — trabalhar apenas com fontes abertas eliminou a única despesa plausível, que seria o licenciamento de conteúdo bíblico.

### Habilidades e conhecimentos

| Domínio | Nível atual | Origem | Lacuna |
|---|---|---|---|
| Engenharia de dados e SQL | Consolidado | Experiência profissional em desenvolvimento fullstack | — |
| Python para análise | Intermediário | Curso de Data Science e Machine Learning | — |
| Ciência de redes | Básico a intermediário | Curso; leitura dirigida | Métricas de rede e validação por modelo nulo exigem estudo dirigido |
| Machine learning aplicado | Intermediário | Curso | Predição de links e amostragem negativa exigem estudo específico |
| Geoprocessamento | Básico | Autodidata | Sistemas de coordenadas e cálculo geodésico exigem estudo dirigido |
| Frontend (React, TypeScript) | Consolidado | Experiência profissional | — |
| Visualização cartográfica | Básico | Autodidata | Camadas, projeções e representação de incerteza exigem estudo dirigido |
| Arqueologia e geografia histórica | Nulo | — | **Lacuna assumida e não mitigável.** Tratada por decisão de projeto: o sistema não emite juízo sobre identificações, apenas transporta e exibe o julgamento registrado na fonte |

> A última linha é uma decisão de arquitetura, não uma omissão. A ausência de competência arqueológica foi convertida em restrição de escopo: nenhuma funcionalidade do sistema exige que o autor avalie a plausibilidade de uma identificação.

---

## 1.2.3 Cronograma de Ações Planejadas

### Backlog de produto

Requisitos organizados em três sprints. O template exige **um artefato de evidência por requisito**; a numeração abaixo é a referência para o capítulo 2.

#### Sprint 1 — Fundação de dados

| ID | Requisito | Artefato de evidência |
|---|---|---|
| R1.1 | Inspecionar a estrutura real das três fontes antes de escrever qualquer parser | `docs/data-contracts.md` |
| R1.2 | Implementar download reprodutível com registro de versão da fonte | `pipeline/s01_download.py` + log de execução |
| R1.3 | Carregar os JSONL em DuckDB e modelar as tabelas de trabalho | `pipeline/s02_load.py` + `docs/schema.md` (esquema real, gerado por introspecção) |
| R1.4 | Extrair os lugares de Atos, normalizar candidatos e calcular probabilidades | `pipeline/s03_extract_acts.py` |
| R1.5 | Produzir a tabela de distribuição de contagem de candidatos | `docs/candidate-distribution.md` (persistido, com indicação explícita do lado do limiar) |
| R1.6 | Implementar a suíte de testes de integridade | `tests/` — seis testes da especificação, incl. `test_no_candidate_collapse.py` (CA1) |

**Critério de aceite da sprint:** `uv run python -m pipeline.sprint1` (ou `just sprint1`) executa download→carga→extração→exportação em um comando único, sem depender de estágios de sprints futuras; a distribuição de candidatos está quantificada e persistida; a decisão sobre o gatilho de pivô está registrada em `docs/candidate-distribution.md` e discutida em `docs/relatorio-secao-1.1.4.md`. Evidência completa em `specs/002-fechar-lacunas-sprint1/`.

#### Sprint 2 — Análise e modelagem

| ID | Requisito | Artefato de evidência |
|---|---|---|
| R2.1 | Construir o grafo de coocorrência de lugares por capítulo | `pipeline/s04_build_graph.py` + `graph.json` (107 nós, 1059 arestas, 0 isolados) |
| R2.2 | Calcular métricas topológicas (grau, grau ponderado, intermediação) | `graph.json.nodes[]` |
| R2.3 | Implementar Monte Carlo sobre métricas de distância, com IC de 95% | `pipeline/s05_uncertainty.py` + `uncertainty.json` (4 escalares + ranking de centralidade geográfica em `place_rank_stability[]`) |
| R2.4 | Detectar comunidades e comparar com a partição narrativa de referência | `pipeline/s06_communities.py` + `docs/community-comparison.md` (5 comunidades, 0 desconexas, NMI=0,24, ARI=0,11) |
| R2.5 | Implementar predição de links com 4 heurísticas e 2 modelos aprendidos | `pipeline/s07_linkpred.py` — rede ego de Atos: 7.821 nós, 38.766 arestas |
| R2.6 | Avaliar com duas estratégias de amostragem negativa e comparar | `linkpred.json.results[]` (12 combinações) — `random` favorece consistentemente `distance_matched` (ex. preferential_attachment: AUC 0,819→0,768; node2vec_lr: 0,876→0,846), heurísticas locais (common_neighbors/jaccard/adamic_adar) quase não mudam entre estratégias |

**Critério de aceite da sprint:** todas as métricas calculadas com seed fixa (42); resultados de predição de links reportados para ambas as estratégias de amostragem, independentemente do sinal. Tempo medido do início de `s04_build_graph.py` até os 4 artefatos prontos (`graph.json`, `uncertainty.json`, `docs/community-comparison.md`, `linkpred.json`): **~105s** (`uv run python -m pipeline.s08_export`, maior parte no treinamento node2vec de `s07_linkpred.py`).

#### Sprint 3 — Interface e validação

| ID | Requisito | Artefato de evidência |
|---|---|---|
| R3.1 | Exportar os quatro contratos JSON de saída | `pipeline/s08_export.py` + arquivos gerados |
| R3.2 | Implementar a aplicação base com mapa e camada de lugares | Repositório `web/` + captura de tela |
| R3.3 | Implementar a representação visual da incerteza locacional | Captura de tela + trecho de código da camada |
| R3.4 | Implementar o painel de lugares não localizáveis, com a razão explícita | Captura de tela |
| R3.5 | Implementar legenda, texto explicativo e atribuição de licença | Captura de tela |
| R3.6 | Publicar a aplicação e conduzir teste de compreensão com usuários | URL pública + registro das sessões de teste |

**Critério de aceite da sprint:** aplicação publicada e acessível; camada de incerteza funcional; teste de compreensão conduzido com no mínimo três participantes e resultados registrados.

### Linha do tempo

| Marco | Sprint | Período | Entrega |
|---|---|---|---|
| M1 | 1 | `[PREENCHER]` | Dados extraídos, distribuição de candidatos quantificada |
| M2 | 2 | `[PREENCHER]` | Análises concluídas, modelos avaliados |
| M3 | 3 | `[PREENCHER]` | Aplicação publicada, hipóteses reportadas |
| M4 | — | `[PREENCHER]` | Relatório final consolidado |

> **Ferramenta de acompanhamento:** `[PREENCHER — Trello, Planner ou GitHub Projects]`. Anexar captura de tela do quadro, conforme exigido pelo template.

### Rastreabilidade entre hipóteses, requisitos e sprints

| Hipótese | Requisitos que a testam | Sprint |
|---|---|---|
| H1 — multiplicidade de candidatos | R1.4, R1.5 | 1 |
| H2 — impacto da incerteza em métricas | R2.3 | 2 |
| H3 — recuperação de ligações omitidas | R2.5, R2.6 | 2 |
| H4 — compreensão da representação visual | R3.3, R3.6 | 3 |
| H5 — redução do custo de entrada | R1.2, R1.3, R3.1 | 1 e 3 |

### Gestão de risco do cronograma

| Risco | Probabilidade | Impacto | Resposta |
|---|---|---|---|
| Estrutura da fonte mais complexa que o previsto | Alta | Médio | R1.1 existe justamente para absorver isso na Sprint 1, antes de qualquer código dependente |
| Gatilho de pivô acionado na Sprint 1 | Média | Baixo no código, médio na narrativa | Ambos os eixos de incerteza já são suportados pelos campos exportados; o pivô altera o texto do relatório, não a implementação |
| Grafo de referências cruzadas insuficiente para ML | Média | Médio | Expandir para rede ego; se persistir, reportar a limitação |
| Indisponibilidade de participantes para o teste de compreensão | Média | Baixo | Reduzir para três participantes; conduzir remotamente |
| Estouro de prazo na Sprint 3 | Média | Alto | Itens de prioridade 6 a 8 da seção 1.1.4 já classificados como descartáveis |