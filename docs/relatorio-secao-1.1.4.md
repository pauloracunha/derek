# 1.1.4 Uma taxonomia da indeterminação, não uma hipótese única

A formulação original deste trabalho (H1) partia de uma premissa simples: ferramentas de geolocalização bíblica escondem a incerteza arqueológica ao colapsar múltiplos candidatos de localização em um único ponto no mapa. A correção proposta seria, então, exibir todos os candidatos conhecidos, ponderados por confiança.

Essa premissa está correta, mas incompleta. Ao extrair e normalizar os 107 lugares mencionados no livro de Atos a partir do dataset `openbibleinfo/Bible-Geocoding-Data`, observou-se que **apenas 4,7% dos lugares localizáveis (5 de 107) possuem mais de um candidato de localização concorrente** — abaixo do limiar de 15% que o próprio desenho metodológico do projeto havia estabelecido como critério para considerar H1 sustentada. Medida estritamente pela definição original, a hipótese central do trabalho é fraca para este livro.

O que a extração revelou, no entanto, é que a "incerteza sobre onde um lugar fica" não é um fenômeno único — é uma família de pelo menos quatro fenômenos distintos, com taxas de ocorrência e implicações de representação diferentes entre si. Colapsá-los sob um único rótulo seria repetir, em escala menor, o mesmo erro de simplificação que o projeto se propõe a corrigir.

## Quatro tipos de indeterminação

| Tipo | Pergunta sem resposta | Ocorrência em Atos | Fonte da evidência |
|---|---|---|---|
| **Identificação** | Onde exatamente fica este lugar? | 5 lugares (4,7% dos 107 localizáveis) | `candidate_count ≥ 2` |
| **Extensão** (mismatch ontológico) | Isto é um ponto ou uma área/linha? | 35 candidatos (26,7% dos 131 candidatos) | `lonlat_type = "representative point"` sem `precision.meters` |
| **Precisão posicional** | A quantos metros do lugar pretendido está esta coordenada? | 96 candidatos (73,3%), mediana de 35 m | `precision.meters`, campo numérico de `modern.jsonl` |
| **Ontológica** | Isto é sequer um lugar? | 0 casos dentro de Atos (120 no dataset bíblico completo) | identificação `special` coexistindo com candidatos reais no mesmo registro |

### Identificação

É a forma de indeterminação prevista pela formulação original de H1: um mesmo lugar antigo tem mais de uma hipótese de localização moderna concorrente, cada uma com um grau de confiança próprio. Ocorre em 5 dos 107 lugares de Atos — uma taxa baixa, mas não nula, e cada um desses 5 casos é exibido com todos os seus candidatos simultaneamente, nunca reduzido a um único ponto.

### Extensão: um problema de forma, não de confiança

Trinta e cinco candidatos de localização em Atos (26,7% do total) são classificados na origem como `representative point` e não possuem uma estimativa de precisão em metros associada. A inspeção desses 35 casos mostra que **100% deles correspondem a regiões, ilhas, corpos d'água ou vias** — Galácia, Ásia, Licaônia, Chipre, Creta, o Mar Vermelho, a Rua Direita — sem exceção.

Isto não é incerteza no sentido em que o termo é normalmente empregado. O dataset não está inseguro sobre onde fica a Galácia; simplesmente não existe "o ponto" da Galácia, porque a Galácia é uma região, não um lugar pontual. O problema é de **incompatibilidade entre a ontologia do objeto geográfico e a ontologia do formato de representação**: todo formato de intercâmbio geoespacial de uso corrente — incluindo o GeoJSON subjacente a este dataset — representa lugares como pontos, e uma região forçada nesse formato produz um artefato sem significado geográfico (um "ponto representativo" arbitrário dentro de uma área).

A consequência para a representação visual é mais severa do que a da incerteza de identificação: um erro de identificação desloca um marcador por alguns quilômetros; um erro de extensão transforma uma região em um alfinete, comunicando uma falsidade categórica sobre a natureza do objeto representado. Afeta 26,7% dos candidatos de Atos — mais de cinco vezes a taxa de incerteza de identificação que motivou o desenho original do projeto.

### Precisão posicional: a métrica que faltava

Noventa e seis candidatos de localização em Atos (73,3%) possuem, em `modern.jsonl`, um campo `precision.meters` — uma estimativa numérica, derivada de uma descrição textual da fonte original, de quão distante a coordenada registrada está do local pretendido. A mediana entre os candidatos de Atos é de 35 metros, com máximo de 5.000 metros.

Este campo é a métrica quantitativa real de precisão posicional disponível no dataset, e é estritamente mais defensável do que inferir precisão a partir da categoria `lonlat_type` isoladamente — que, como demonstrado acima, mistura indiscriminadamente precisão posicional genuína com mismatch ontológico. Note-se que 17 dos 52 candidatos originalmente rotulados `representative point` possuem, na verdade, `precision.meters` pequeno (mediana de 5 m) — são pontos precisos mal-classificados pela categoria bruta, não áreas extensas. A separação por presença/ausência de `precision.meters`, e não pela categoria `lonlat_type` per se, é o que permite discriminar corretamente entre as duas primeiras linhas da taxonomia.

### Ontológica: quando a fonte discorda sobre se algo é um lugar

No dataset bíblico completo (não restrito a Atos), 120 registros possuem simultaneamente uma identificação classificada como `special` — isto é, uma fonte ou tradição afirmando que o termo não se refere a um lugar real (nome de pessoa, substantivo comum) — e uma ou mais identificações concorrentes com candidatos de localização reais e coordenadas. Trata-se de uma quarta forma de indeterminação, anterior a qualquer pergunta sobre localização: a própria existência do lugar como referente geográfico é disputada internamente pelas fontes.

Dentro do recorte de Atos, este trabalho não encontrou nenhuma ocorrência desse fenômeno (0 de 107 lugares) — um resultado negativo, reportado como tal, e não uma lacuna metodológica. O fenômeno é real e documentado no dataset (120 casos no total), mas não se manifesta neste livro específico.

## Implicação metodológica

A reformulação proposta não substitui H1; ela a recontextualiza como um caso particular de um problema mais amplo. Em vez de "ferramentas de geolocalização bíblica escondem a incerteza locacional", a formulação mais precisa é: **o formato-padrão de intercâmbio geoespacial — um ponto por lugar — é estruturalmente incapaz de representar pelo menos quatro tipos distintos e não-equivalentes de indeterminação presentes na fonte, e a prática corrente de todas as ferramentas examinadas os colapsa indistintamente no mesmo marcador.**

Sob essa formulação, o resultado de 4,7% deixa de ser uma refutação de H1 e passa a ser um dado substantivo: a forma de indeterminação que a literatura de geolocalização bíblica assume como dominante é, neste livro, a mais rara das quatro identificadas. As outras três — extensão, precisão posicional e ontológica — não estavam no desenho original da pesquisa e emergiram exclusivamente da inspeção direta dos dados brutos.
