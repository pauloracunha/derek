# Atlas de Atos — Especificação Técnica de Implementação

Documento de referência para execução assistida por Claude Code.
Versão 1.0.

---

## 0. Contexto mínimo para o agente

**Objetivo do sistema:** pipeline reprodutível + aplicação web que visualiza a rede de lugares mencionados no livro de Atos dos Apóstolos, preservando e exibindo a incerteza arqueológica sobre a localização de cada lugar, em vez de colapsá-la para um ponto único.

**Recorte:** livro de Atos (livro 44 na numeração canônica do dataset).

**Não-objetivos (fora de escopo, não implementar):**
- Exibição de texto bíblico completo
- Suporte a outros livros além de Atos
- Autenticação, banco de dados servidor, backend em runtime
- Análise morfossintática ou de línguas originais
- Renderização de geometrias complexas (rios, regiões, polígonos) — apenas pontos

---

## 1. Fontes de dados

### 1.1 Geolocalização — `openbibleinfo/Bible-Geocoding-Data`

Licença CC BY 4.0. Formato JSON Lines (um objeto JSON completo por linha).

Arquivos necessários (diretório `data/` do repositório):

| Arquivo | Uso no projeto |
|---|---|
| `ancient.jsonl` | **Principal.** Lugares antigos, versículos, identificações, candidatos |
| `modern.jsonl` | Coordenadas e metadados das localizações modernas |
| `source.jsonl` | Procedência bibliográfica (usado apenas para exibir fontes na UI) |

Ignorar: `geometry.jsonl`, `image.jsonl`, `all.kml`, thumbnails (180 MB), diretório `geometry/`.

### 1.2 Referências cruzadas — OpenBible.info Cross References

Licença CC BY. Aproximadamente 340 mil pares de versículos derivados do *Treasury of Scripture Knowledge*.

> **Instrução ao agente:** o formato exato deste arquivo deve ser inspecionado antes de escrever o parser. Não assumir colunas. Executar `head -5` e verificar delimitador, presença de cabeçalho e formato das referências (provavelmente OSIS, ex.: `Acts.1.8`). Documentar o formato observado em `docs/data-contracts.md`.

---

## 2. Estrutura de dados de origem (verificada)

### 2.1 `ancient.jsonl` — campos relevantes

```jsonc
{
  "id": "a15257a",                    // string de 7 caracteres iniciada por "a"
  "friendly_id": "Jerusalem",         // único dentro de ancient.jsonl
  "url_slug": "jerusalem",
  "type": "settlement",               // ~40 valores possíveis
  "preceding_article": "",            // "the" ou ""

  "verses": [                         // ordenado por "sort"
    {
      "sort": "44001004",             // BBCCCVVV — chave primária canônica
      "osis": "Acts.1.4",
      "usx": "ACT 1:4",
      "readable": "Acts 1:4",
      "alternate_verses": {           // opcional: divergência de versificação
        "kjv": "Acts.4.6"
      },
      "translations": [ /* ... */ ]
    }
  ],

  "identifications": [                // hipóteses de identificação
    {
      "id_source": "modern",          // "ancient" | "modern" | "special"
      "class": "human",
      "modifier": "near",             // "<" | "along" | "near" | "on" | ">"
      "types": ["settlement"],
      "description": "along the <modern id=\"m664b51\">Wadi el Esh</modern>",
      "score": {
        "time_total": 462,            // confiança atual (0-1000)
        "vote_total": 456,
        "vote_count": 19
      },
      "resolutions": [
        {
          "lonlat": "44.402874,14.213898",   // LONGITUDE,LATITUDE (nesta ordem)
          "lonlat_type": "point",            // point|center|representative point|settlement
          "modern_basis_id": "m9f98b7",
          "best_time_score": 133,
          "best_path_score": 44,
          "type": "settlement"
        }
      ]
    }
  ],

  "modern_associations": {            // *** CAMPO CENTRAL DO PROJETO ***
    "m7d8664": {
      "name": "Tel el Beida",
      "url_slug": "tel-el-beida",
      "score": 349,                   // confiança agregada
      "identification_ids": [[0, 0]]
    },
    "mec0b4d": {
      "name": "Ain Kezbeh",
      "score": 52,
      "identification_ids": [[1, 1]]
    }
  }
}
```

### 2.2 Por que `modern_associations` é o campo central

Este objeto **já é a incerteza quantificada**. Cada chave é um candidato de localização moderno, e `score` é uma medida agregada de confiança que combina a confiança na identificação com a confiança na resolução.

Consequência de projeto: **não é necessário inventar um modelo de incerteza.** Basta normalizar os scores para uma distribuição de probabilidade:

```
P(candidato_i) = score_i / Σ score_j
```

Esta é a diferença entre este projeto e todas as ferramentas de consumo existentes, que descartam `modern_associations` e usam apenas a primeira resolução.

### 2.3 Resoluções especiais — tratamento obrigatório

Nem todo lugar resolve para coordenadas. Quando `id_source` é `"special"`, a resolução tem uma propriedade `special` com um destes valores:

| Valor | Significado | Tratamento |
|---|---|---|
| `unknown_place` | Localização desconhecida | **Manter no grafo, excluir do mapa.** Marcar `is_locatable = false` |
| `nonspecific_place` | Lugar simbólico ou profético | Idem |
| `not_a_place` | Nome pessoal tratado como lugar por alguma tradução | **Excluir completamente** |
| `not_a_proper_name` | Substantivo comum (ex.: "floresta") | **Excluir completamente** |
| `multiple_locations` | Refere-se a múltiplos locais (ex.: tabernáculo) | Manter, marcar `is_locatable = false` |
| `recursive` | Loop de referência | Excluir |

> **Atenção:** o descarte silencioso de lugares não-localizáveis é exatamente a falha que o projeto denuncia. Eles devem aparecer na interface, em painel separado, com a razão explícita.

### 2.4 Armadilhas conhecidas

| Armadilha | Consequência se ignorada |
|---|---|
| `lonlat` é `"longitude,latitude"` — ordem invertida em relação ao senso comum | Todos os pontos aparecem no lugar errado do mundo |
| `friendly_id` é único em `ancient.jsonl` mas **não** no dataset inteiro (existe "Jerusalem" ancient e "Jerusalem" modern) | Colisão de chave em joins |
| `description` contém XML embutido (`<modern id="...">`, `<ancient id="...">`) | Tags aparecem literalmente na interface |
| `lonlat_type` = `"settlement"` significa "em algum ponto dentro daquele assentamento", não "exatamente aqui" | Falsa precisão — deve ser sinalizado na UI |
| Quando não há disputa, `time_values` e `time_best_fits` vêm como **arrays vazios** e `time_total` = 1000 | Erro de índice ao processar séries temporais |
| `sort` é string, não inteiro — zeros à esquerda são significativos | Ordenação canônica quebra se convertido para int |

---

## 3. Arquitetura

```
atlas-atos/
├── CLAUDE.md                  # contexto persistente do agente
├── README.md
├── pyproject.toml
├── justfile                   # ou Makefile — orquestração
├── data/
│   ├── raw/                   # .gitignore — downloads brutos
│   ├── interim/               # .gitignore — duckdb
│   └── processed/             # versionado — saídas finais (JSON)
├── pipeline/
│   ├── __init__.py
│   ├── config.py              # constantes: BOOK_ID=44, URLs, hashes
│   ├── s01_download.py
│   ├── s02_load.py            # jsonl → duckdb
│   ├── s03_extract_acts.py    # filtro + normalização
│   ├── s04_build_graph.py
│   ├── s05_uncertainty.py     # Monte Carlo espacial
│   ├── s06_communities.py
│   ├── s07_linkpred.py
│   └── s08_export.py          # → data/processed/*.json
├── notebooks/                 # exploração e figuras do relatório
├── tests/
├── docs/
│   ├── data-contracts.md      # formatos observados, não presumidos
│   └── decisions.md           # ADRs curtos
└── web/
    ├── package.json
    ├── vite.config.ts
    ├── public/data/           # symlink ou cópia de data/processed
    └── src/
```

### 3.1 Stack

**Pipeline (Python 3.11+)**

| Componente | Escolha | Justificativa |
|---|---|---|
| Gerenciador | `uv` | Rápido, lockfile determinístico |
| Armazenamento intermediário | DuckDB | Lê JSONL nativamente, faz os joins em SQL, arquivo único, sem servidor |
| Manipulação | Polars ou pandas | Indiferente nesta escala |
| Grafos | `networkx` | Escala trivial (~100 nós). `igraph` seria overkill |
| Comunidades | `networkx.community.louvain_communities` ou `python-igraph` para Leiden | Ver §5.3 |
| ML | `scikit-learn` + `node2vec` | Sem deep learning |
| Geodésica | `pyproj` ou `geopy` | Distâncias em metros, não em graus |

**Web**

| Componente | Escolha | Justificativa |
|---|---|---|
| Build | Vite + React + TypeScript | Já é seu stack |
| Mapa | MapLibre GL JS | Open source, sem chave de API, sem custo |
| Tiles | CARTO Positron ou Stadia (basemap claro) | Contraste com as camadas de dados |
| Rede | `d3-force` sobre SVG, em painel lateral | Não tentar desenhar force-graph sobre o mapa |
| Estado | Zustand ou Context | Aplicação pequena |

**Deploy:** estático. Vercel, Netlify ou GitHub Pages. Sem backend em runtime.

---

## 4. Contratos de saída

Estes são os artefatos que o pipeline produz e o frontend consome. **Definir antes de escrever código.**

### 4.1 `places.json`

```jsonc
[
  {
    "place_id": "a15257a",
    "name": "Jerusalem",
    "slug": "jerusalem",
    "type": "settlement",
    "is_locatable": true,
    "special_reason": null,          // preenchido se is_locatable=false
    "verses": ["44001004", "44001008"],
    "mention_count": 59,
    "chapters": [1, 2, 3, 4],
    "candidates": [
      {
        "modern_id": "m7d8664",
        "name": "Tel el Beida",
        "lon": 35.2137,
        "lat": 31.7683,
        "score": 349,
        "probability": 0.87,          // score normalizado
        "lonlat_type": "point"
      }
    ],
    "candidate_count": 2,
    "uncertainty_index": 0.39         // ver §5.2
  }
]
```

### 4.2 `graph.json`

```jsonc
{
  "unit": "chapter",                  // granularidade da coocorrência
  "nodes": [
    {
      "place_id": "a15257a",
      "degree": 14,
      "weighted_degree": 31,
      "betweenness": 0.284,
      "community": 0
    }
  ],
  "edges": [
    { "source": "a15257a", "target": "a3b91c2", "weight": 4, "chapters": [1, 8] }
  ]
}
```

### 4.3 `uncertainty.json`

```jsonc
{
  "n_simulations": 1000,
  "seed": 42,
  "metrics": {
    "total_network_length_km": {
      "mean": 4821.3,
      "ci_low": 4655.1,
      "ci_high": 5013.7,
      "deterministic": 4790.2      // valor usando apenas o melhor candidato
    }
  },
  "place_rank_stability": [
    {
      "place_id": "a15257a",
      "modal_rank": 1,
      "rank_ci": [1, 1]
    }
  ]
}
```

### 4.4 `linkpred.json`

```jsonc
{
  "graph_stats": { "nodes": 1240, "edges": 8930, "density": 0.0116 },
  "negative_sampling": "distance_matched",
  "results": [
    { "model": "common_neighbors", "auc": 0.812, "ap": 0.788, "precision_at_100": 0.64 },
    { "model": "adamic_adar",      "auc": 0.839, "ap": 0.801, "precision_at_100": 0.71 },
    { "model": "node2vec_lr",      "auc": 0.856, "ap": 0.823, "precision_at_100": 0.69 }
  ],
  "top_candidates": [
    { "from": "Acts.2.17", "to": "Joel.2.28", "score": 0.981, "in_catalog": false }
  ]
}
```

---

## 5. Especificação dos módulos

### 5.1 `s03_extract_acts.py` — extração e normalização

**Filtro:** um lugar entra no conjunto se possuir ao menos um item em `verses` cujo `sort` comece com `"44"`.

```sql
-- Exemplo em DuckDB
SELECT * FROM ancient
WHERE EXISTS (
  SELECT 1 FROM UNNEST(verses) AS v
  WHERE v.sort LIKE '44%'
);
```

**Normalização de candidatos:** para cada lugar, iterar `modern_associations`, resolver `lonlat` via join com `modern.jsonl` pelo `modern_id`, e calcular `probability = score / Σ scores`.

**Saída obrigatória — este é o resultado que valida H1 e preenche o "How much" do relatório:**

```
Lugares de Atos localizáveis:        N
Com 1 candidato:                     N1  (X%)
Com 2 candidatos:                    N2  (Y%)
Com 3+ candidatos:                   N3  (Z%)
Não localizáveis (special):          NS
```

> **Ponto de decisão de projeto.** Se a proporção de lugares com múltiplos candidatos for muito baixa (digamos, abaixo de 15%), H1 está enfraquecida e o eixo de incerteza perde força. Neste caso, **não force a narrativa**: reporte o número, e pivote o eixo principal para a incerteza *de precisão* (`lonlat_type = "settlement"` e `precision.meters` em `modern.jsonl`), que é uma forma diferente e igualmente real de incerteza. Executar este módulo **primeiro**, antes de qualquer outro trabalho.

### 5.2 `s05_uncertainty.py` — propagação por Monte Carlo

**Correção conceitual importante:** a incerteza locacional **não** afeta métricas puramente topológicas. Grau, intermediação e comunidades dependem só de quem coocorre com quem, e isso não muda se o ponto se desloca no mapa. Aplicar Monte Carlo a essas métricas seria teatro estatístico.

A incerteza afeta apenas **métricas que envolvem distância**. Portanto, simular somente estas:

| Métrica | Definição |
|---|---|
| Comprimento geográfico total da rede | Σ distância geodésica sobre todas as arestas |
| Distância média por aresta | Média das distâncias geodésicas |
| Área do fecho convexo | Extensão espacial coberta pela narrativa |
| Centralidade geográfica | Ranking de lugares por distância ao centroide ponderado |
| Comprimento do itinerário narrativo | Distância acumulada seguindo a ordem canônica das menções |

**Algoritmo:**

```
para i em 1..N (N = 1000):
    para cada lugar localizável p:
        amostrar candidato c ~ Categorical(probabilities de p)
        atribuir coordenadas de c a p
    calcular todas as métricas de distância
    armazenar

reportar média, IC 95% (percentis 2.5 e 97.5), e o valor determinístico
   (obtido usando sempre o candidato de maior score) para comparação
```

Fixar `seed`. Usar distância geodésica real (WGS84), não euclidiana sobre lat/lon.

**H2 é confirmada se** o intervalo de credibilidade for largo o suficiente para que a escolha de candidato altere materialmente a leitura. Se for estreito, **reporte assim mesmo** — "a incerteza existe mas tem impacto agregado pequeno" é um resultado legítimo e publicável.

### 5.3 `s06_communities.py`

Grafo de coocorrência de lugares por capítulo. Executar detecção de comunidades e comparar com uma partição de referência.

Louvain (disponível em `networkx`) é suficiente nesta escala. Se optar por Leiden, usar `python-igraph` + `leidenalg`.

**Verificação obrigatória:** Louvain pode produzir comunidades internamente desconexas. Após a detecção, validar conectividade de cada comunidade e reportar se houver violação.

**Baseline de comparação:** partição por bloco narrativo de Atos (caps. 1–7 Jerusalém, 8–12 Judeia e Samaria, 13–28 missão aos gentios). Reportar NMI e ARI contra essa partição.

### 5.4 `s07_linkpred.py` — o componente de aprendizado de máquina

Este é o módulo mais delicado. É onde é fácil produzir um AUC inflado e sem significado.

**Construção do grafo:** subgrafo induzido das referências cruzadas envolvendo versículos de Atos e seus alvos diretos (rede ego de raio 1). Nós = versículos, arestas = referência cruzada. Não direcionado.

**Split:** remover aleatoriamente 20% das arestas para teste, garantindo que o grafo de treino permaneça conexo (ou tratando componentes isolados explicitamente).

**Amostragem negativa — o ponto crítico:**

Se os negativos forem pares aleatórios de versículos, a tarefa fica trivial: qualquer modelo distingue "Atos 2:17 ↔ Joel 2:28" de "Atos 2:17 ↔ Levítico 13:44". O AUC vai para 0.95 e não significa nada.

Implementar **duas** estratégias e reportar ambas:

1. `random` — negativos amostrados uniformemente entre pares não-conectados. É a baseline ingênua, incluída para demonstrar o problema.
2. `distance_matched` — negativos amostrados de forma a reproduzir a distribuição de distância canônica dos positivos. Se um par positivo tem seus versículos separados por 12 mil versículos no cânon, o negativo pareado deve ter separação similar. Esta é a avaliação honesta.

A diferença de AUC entre as duas estratégias deve ser explicitamente discutida no relatório. É um dos achados mais defensáveis do trabalho.

**Modelos, nesta ordem:**

| # | Modelo | Tipo |
|---|---|---|
| 1 | Vizinhos Comuns | Heurística |
| 2 | Jaccard | Heurística |
| 3 | Adamic-Adar | Heurística |
| 4 | Preferential Attachment | Heurística |
| 5 | node2vec + Regressão Logística | Aprendizado |
| 6 | node2vec + Gradient Boosting | Aprendizado |

Para 5 e 6, combinar os embeddings dos dois nós por produto de Hadamard (padrão da literatura). Documentar dimensão, `p`, `q`, comprimento e número de caminhadas.

**Métricas:** AUC-ROC, Average Precision, Precision@k (k = 50, 100, 500).

> **Expectativa calibrada:** é comum que Adamic-Adar iguale ou supere embeddings em grafos pequenos e esparsos. Se isso ocorrer, **reporte sem constrangimento.** Baseline simples vencendo modelo complexo é resultado válido e demonstra competência em avaliação. Ajustar o modelo até ele "ganhar" é má prática e será percebido.

**Saída interpretável:** as 100 arestas de maior score que não estão no catálogo, com referências legíveis. Esta lista é a evidência de resultado da sprint.

---

## 6. Especificação da interface

### 6.1 Layout

```
┌────────────────────────────────────────────────┐
│  Header: título + seletor de capítulo/faixa    │
├──────────────────────────────┬─────────────────┤
│                              │  Painel lateral │
│         MAPA (MapLibre)      │  ─────────────  │
│                              │  Detalhe do     │
│                              │  lugar          │
│                              │  ─────────────  │
│                              │  Candidatos +   │
│                              │  scores +       │
│                              │  fontes         │
├──────────────────────────────┼─────────────────┤
│  Timeline de capítulos       │  Grafo (d3)     │
└──────────────────────────────┴─────────────────┘
```

### 6.2 Representação visual da incerteza — requisito central

Esta é a contribuição do projeto. Não simplificar.

| Situação | Representação |
|---|---|
| Candidato único, alta confiança | Círculo sólido, borda contínua |
| Múltiplos candidatos | **Todos** renderizados. Opacidade proporcional à probabilidade. Linha tracejada conectando os candidatos do mesmo lugar. Rótulo posicionado no candidato modal |
| `lonlat_type = "settlement"` | Halo difuso indicando "em algum ponto desta área", não ponto preciso |
| Não localizável | **Não desaparece.** Aparece em lista lateral "Mencionados sem localização conhecida", com a razão (`unknown_place`, `nonspecific_place`, etc.) |

**Legenda obrigatória e sempre visível.** Um mapa com pontos translúcidos sem legenda é pior que um mapa de ponto único, porque comunica incerteza sem explicá-la.

### 6.3 Acessibilidade da mensagem

Incluir um texto curto e permanente na interface explicando por que existem múltiplos pontos. Sem isso, o usuário interpreta a multiplicidade como erro de dado. Isso também alimenta o teste de compreensão de H4.

### 6.4 Atribuição de licença

Rodapé obrigatório, com link:

> Dados geográficos e de referências cruzadas: OpenBible.info (CC BY 4.0). Dados do OpenStreetMap sob ODbL.

---

## 7. Mapeamento para as sprints do relatório

| Sprint | Módulos | Requisitos (evidência exigida) | Hipótese testada |
|---|---|---|---|
| **1** | s01–s03 | Download reprodutível; carga em DuckDB; extração de Atos; **tabela de contagem de candidatos**; `docs/data-contracts.md` | **H1** |
| **2** | s04–s07 | Grafo construído; métricas topológicas; Monte Carlo com IC; comunidades + NMI; link prediction com 6 modelos e 2 estratégias de amostragem negativa | **H2, H3** |
| **3** | s08 + web | Exportação dos JSON; aplicação publicada; camada de incerteza; teste de compreensão com 3–5 pessoas | **H4, H5** |

Cada requisito precisa de um artefato correspondente — o template exige paridade entre número de requisitos planejados e artefatos apresentados.

---

## 8. `CLAUDE.md` sugerido

Colocar na raiz do repositório:

```markdown
# Atlas de Atos

Pipeline de dados + web app que visualiza a rede de lugares do livro de Atos
preservando a incerteza arqueológica de localização.

## Princípios não negociáveis

1. NUNCA colapsar múltiplos candidatos de localização em um ponto único.
   Isso é precisamente a falha que o projeto existe para corrigir.
2. NUNCA descartar silenciosamente lugares não localizáveis. Eles aparecem
   na UI com a razão explícita.
3. `lonlat` no dataset de origem é "longitude,latitude" — NESTA ORDEM.
4. `sort` (BBCCCVVV) é STRING. Nunca converter para inteiro.
5. Nenhum dado de origem é modificado. Toda transformação é derivada e
   reprodutível a partir do bruto.
6. Se um resultado de análise for fraco ou contrariar a hipótese, reportar
   como está. Não ajustar o experimento até obter o resultado desejado.

## Comandos

- `just data`      — baixa fontes brutas
- `just pipeline`  — executa s01..s08
- `just test`      — pytest
- `just web`       — dev server do frontend

## Estado atual

<!-- atualizar a cada sessão -->

## Decisões arquiteturais

Ver `docs/decisions.md`.
```

---

## 9. Sequência de prompts para o Claude Code

Executar em sessões separadas. Não pedir tudo de uma vez.

**Sessão 1 — reconhecimento (não escrever código de análise ainda)**
> Baixe `ancient.jsonl` e `modern.jsonl` do repositório openbibleinfo/Bible-Geocoding-Data e o arquivo de referências cruzadas do OpenBible.info. Antes de qualquer processamento, inspecione a estrutura real dos três arquivos: contagem de linhas, campos presentes, tipos, e o formato exato do arquivo de referências cruzadas (delimitador, cabeçalho, formato das referências). Escreva o que observou em `docs/data-contracts.md`. Não presuma nenhum formato — verifique.

**Sessão 2 — extração e teste de H1**
> Carregue os JSONL em DuckDB e extraia todos os lugares com ao menos um versículo cujo `sort` comece com "44". Para cada lugar, normalize `modern_associations` em uma lista de candidatos com coordenadas resolvidas e probabilidade proporcional ao score. Trate resoluções `special` conforme a tabela da especificação. Produza a tabela de distribuição de contagem de candidatos. Este número decide o rumo do projeto — reporte-o com destaque.

**Sessão 3 — grafo e métricas**
> Construa o grafo de coocorrência de lugares por capítulo e calcule grau, grau ponderado e intermediação. Depois implemente a simulação de Monte Carlo apenas para as métricas baseadas em distância listadas na especificação, com 1000 iterações, seed fixa e distância geodésica WGS84. Não aplique Monte Carlo a métricas topológicas — elas não dependem das coordenadas.

**Sessão 4 — link prediction**
> Implemente o pipeline de predição de links conforme a seção 5.4. Implemente as duas estratégias de amostragem negativa e reporte os resultados de ambas lado a lado. Inclua as quatro heurísticas antes de qualquer modelo aprendido. Se as heurísticas superarem os embeddings, reporte o resultado como está.

**Sessão 5 — exportação e frontend**
> Exporte os quatro arquivos JSON conforme os contratos da seção 4. Depois monte a aplicação Vite + React + MapLibre. A camada de incerteza da seção 6.2 é o requisito central — implemente-a primeiro, antes de qualquer refinamento visual.

---

## 10. Testes mínimos

| Teste | Verifica |
|---|---|
| Ordem de coordenadas | Todos os pontos caem em bbox plausível do Mediterrâneo oriental (lon 20–50, lat 25–45) |
| Integridade de probabilidade | Σ probabilidades = 1.0 (±1e-9) para todo lugar localizável |
| Preservação de candidatos | Contagem de candidatos na saída = contagem em `modern_associations` |
| Sem colapso | Nenhum lugar com múltiplos candidatos aparece com apenas um no `places.json` |
| Chave canônica | Todo `sort` tem exatamente 8 caracteres e é string |
| Reprodutibilidade | Duas execuções com a mesma seed produzem saídas byte-idênticas |

O quarto teste é o mais importante do projeto: é a asserção automatizada de que a falha central não foi reintroduzida.