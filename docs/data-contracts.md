# Contratos de dados observados (não presumidos)

Inspeção real dos 4 arquivos brutos em `data/raw/`, feita em 2026-08-02 durante `/speckit-implement` (T009/T010). Onde este documento diverge de `definitions.md` ou de `specs/001-atlas-atos/data-model.md`, **este documento é a fonte de verdade** — os outros foram escritos antes da inspeção real e continham suposições incorretas.

## Taxonomia de indeterminação observada em Atos (não é uma hipótese só — são quatro)

A hipótese original do projeto (H1: "muitos lugares têm múltiplos candidatos") mede só uma fatia da indeterminação real presente nos dados. Rodando o pipeline contra os 107 lugares de Atos e cruzando `candidates[].lonlat_type` com `modern.jsonl[].precision.meters` (ver seção `precision{}` abaixo), aparecem **quatro tipos distintos e não-equivalentes** de indeterminação, cada um exigindo tratamento diferente na UI e no relatório — colapsá-los todos em "incerteza de precisão" seria tão impreciso quanto o problema original que o projeto denuncia.

| Tipo | Pergunta sem resposta | Ocorrência em Atos | Evidência |
|---|---|---|---|
| **Identificação** | Onde exatamente fica este lugar? (múltiplos candidatos concorrentes) | 5 lugares (4,7% dos 107 localizáveis) | `candidate_count >= 2` |
| **Extensão** (mismatch ontológico) | Isto é um ponto ou uma área/linha? | 35 candidatos (~27% dos 131 candidatos) | `lonlat_type == "representative point"` **e** `modern.precision.meters` ausente. 100% desses 35 são `region`\|`island`\|`body of water`\|`promontory`\|`road` (Galácia, Ásia, Creta, Chipre, Mar Vermelho, Rua Direita etc.) — nenhuma exceção. Não é incerteza: o dataset não está inseguro sobre onde fica o Mar Adriático, só não existe "o ponto" de uma região. |
| **Precisão posicional** | Onde dentro deste assentamento/ponto? | 96 candidatos com `precision.meters` real (mediana 35m; inclui os 79 `point`/`settlement` + 17 `representative point` mal-rotulados mas pontuais) | `modern.jsonl[].precision.meters` — campo quantitativo real, derivado de `precision.description`, nunca antes usado no relatório |
| **Ontológica** | Isto é sequer um lugar? | 0 lugares dentro do escopo de Atos (120 no dataset bíblico inteiro — nenhum caiu no filtro de Atos) | `identifications[].id_source == "special"` coexistindo com `modern_associations` não-vazio no mesmo `Place` — ver `docs/adr/0004` |

**Por que separar Extensão de Precisão posicional importa**: um app que mostra dois sítios candidatos pra Jerusalém erra por poucos quilômetros — é o tipo de incerteza que a hipótese original antecipava. Um app que mostra a Judeia (uma região) ou o Mar Adriático (um corpo d'água) como um alfinete de GPS comunica algo categoricamente falso: transforma uma região em um lugar pontual. Isso não é "menos preciso" — é uma categoria de erro diferente, e afeta ~27% dos candidatos de Atos, mais que o triplo da taxa de incerteza de identificação (4,7%) que motivou o projeto originalmente.

**`precision.meters` incorporado ao contrato de exportação** (`contracts/places.schema.json`, campo `candidates[].precision_meters`) — decisão tomada em 2026-08-02, ver conversa de revisão dos achados.

## Contagens reais

| Arquivo | Registros |
|---|---|
| `ancient.jsonl` | 1342 |
| `modern.jsonl` | 1596 |
| `source.jsonl` | 442 |
| `cross-references.txt` | 344799 pares (+ 1 linha de cabeçalho) |

(Os arquivos `.jsonl` não terminam com newline final — `wc -l` subconta em 1; contagem real confirmada via `duckdb.read_ndjson_auto`.)

## `cross-references.txt` (OpenBible.info)

- Formato: **TSV** (tab-separated), com cabeçalho: `From Verse\tTo Verse\tVotes\t#www.openbible.info CC-BY 2026-07-27` — a 4ª "coluna" do cabeçalho é só atribuição, não dado real; só as 3 primeiras colunas têm valor por linha.
- URL real: `https://a.openbible.info/data/cross-references.zip` (contém `cross_references.txt`; a URL "óbvia" `.txt` direta dá 403 — o arquivo só existe dentro do zip).
- Referências em formato OSIS abreviado (`Gen.1.1`, `Acts.1.8`), compatível com o campo `osis` de `ancient.jsonl`.
- Ranges dentro de um campo usam `-`: `Col.1.16-Col.1.17` (referência composta, não um intervalo de dois campos separados).
- `Votes` é inteiro e **pode ser negativo** (ex. `Gen.1.1 → Exod.31.18 = -38`) — voto líquido da comunidade, não uma contagem de votos positivos.
- **As duas direções de um par podem ter votos diferentes** (achado real, `pipeline/s07_linkpred.py`): `Acts.3.19→Acts.3.21 = 4` e `Acts.3.21→Acts.3.19 = -1` coexistem no catálogo. Ao construir um grafo não-direcionado a partir desses pares, o voto relevante é a **soma das duas direções**, nunca uma direção isolada — do contrário um par com voto líquido negativo pode "ressuscitar" como aresta positiva pela direção oposta.
- 13.319 linhas têm `Acts.*` como `From Verse`.

## `ancient.jsonl` — estrutura real (bem mais rica que o exemplo truncado de `definitions.md`)

Chaves de topo: `id`, `friendly_id`, `url_slug`, `preceding_article`, `types`, `verses`, `identifications`, `modern_associations`, `identification_sources`, `extra`, `geojson_file`, `kml_file`, `geometry_credit`, `linked_data`, `media`, `translation_name_counts`.

### `identifications[]`

Cada identificação tem: `id`, `id_source` (`"ancient"`\|`"modern"`\|`"special"`), `class`, `types`, `description`, `score` (objeto: `time_total`, `time_values`, `time_best_fits`, `time_intercept`, `time_slope`, `time_r_squared`, `vote_total`, `vote_average`, `vote_count`), `resolutions[]`, `media` (opcional).

Quando `id_source == "special"`, a identificação tem também um campo **`special`** direto nela (não só dentro de `resolutions[]`) com o valor da razão (`not_a_place`, `unknown_place`, etc.) — confirmado no exemplo real abaixo. Ler `identification.special` como fonte primária.

### `resolutions[]`

Campos confirmados: `lonlat`, `lonlat_type`, `type`, `class`, `description`, `modern_basis_id`, `best_path_score`, `ancient_geometry`, `land_or_water`, `local_geometry_id`, `geojson_roles`, `paths` (cadeia de `ancient_id`→`modern_id`/`special` usada para montar a resolução).

**`lonlat_type` pode ser `null`** (200 ocorrências no dataset) — além de `point`/`center`/`representative point`/`settlement`. Tratar `null` como "tipo de precisão desconhecido", nunca como erro. Distribuição real: `point`=3474, `representative point`=679, `center`=579, `null`=200, `settlement`=74.

### `modern_associations{}` — ⚠️ `score` pode ser negativo ou zero

Amostra real (`Abel-keramim`, 6 candidatos): scores observados = `236, 106, 38, 16, -37, -46`. Levantamento no dataset inteiro:

- 1335 lugares têm `modern_associations` não-vazio
- **274 lugares (20,5%) têm pelo menos 1 candidato com score negativo**
- Do total de 4314 entradas candidato: 3536 positivas, 368 zero, **410 negativas**

Isso quebra a fórmula ingênua `probability = score / Σscore` do `definitions.md` §1.2 (pode gerar probabilidade negativa, >1, ou divisão por Σ≈0). **Decisão registrada em `docs/adr/0003-normalizacao-score-negativo.md`.**

### `identification_sources{}` — a Fonte é por LUGAR, não por candidato

```json
{
  "s0592d6": {"title": "Josh 19:28"},
  "s3f220c": {"title": "Abdon (place)"},
  "sc3c58f": {"table": "22"},
  "sf6c174": {"map": "3"},
  "s7eb9df": {}
}
```

Chave = `source.jsonl[].id`. Valor = localizador opcional dentro da fonte — chaves observadas: `title`/`titles`, `page`/`pages`, `map`, `table` (singular = string, plural = lista de strings, ex. `{"pages": ["112","185"]}`), podem vir vazios `{}`. Pipeline normaliza qualquer valor (string ou lista) para uma string única (join por `", "`). **Isto substitui a suposição de `data-model.md` de que `LocationCandidate N---1 Source`** — na verdade é `Place N---N Source`, sem vínculo direto com qual candidato específico usa qual fonte. Corrigido em `data-model.md`.

## `modern.jsonl` — estrutura real

Chaves de topo incluem: `id`, `friendly_id`, `url_slug`, `lonlat`, `geometry`, `class`, `type`, `land_or_water`, `precision`, `ancient_associations`, `coordinates_source`, `secondary_sources`, `media`, `names`, `geojson_roles`.

### `coordinates_source{}` e `secondary_sources[]` — join real com `source.jsonl`

```json
"coordinates_source": {"id": "Q337141", "source_id": "s7cc8b2", "type": "wikidata"}
"secondary_sources": [
  {"source_id": "sfec0af", "type": "osm", "url": "..."},
  {"source_id": "sd62f5f", "type": "geonames", "url": "..."}
]
```

`source_id` referencia `source.jsonl[].id`. Este é o join de proveniência das **coordenadas** (de onde veio o lon/lat), diferente do `identification_sources` de `ancient.jsonl` (que é proveniência da **identificação** do lugar antigo). São dois relacionamentos Fonte distintos, ambos reais, nenhum por-candidato.

### `precision{}` — sinal de precisão mais rico que `lonlat_type`

```json
"precision": {"description": "point in mountain range", "type": "terrain"}
```

`precision.type` tem 8 valores observados: `distance` (395), `settlement` (378), `tel` (272), `visible` (193), `water` (137), `region` (128), `terrain` (88), `path` (5). Mais granular que `lonlat_type`, mas fora do escopo mínimo de FR-004 (que já usa `lonlat_type`) — registrado aqui como enriquecimento futuro possível, não implementado nesta versão.

## `source.jsonl` — estrutura real

Campos: `id` (string, prefixo `s`), `friendly_id`, `display_name`, `contributors[]`, `type` (`book`\|`article`\|...), `year`, mais campos opcionais por tipo (`url`, `amazon_id`/`amazon_url`, `google_books_id`/`google_books_url`, `worldcat_id`/`worldcat_url`). `display_name` é o texto pronto para exibição (ex. `"Abel, Géographie de la Palestine (1967)"`).

## Correções aplicadas a `data-model.md` / `contracts/` a partir desta inspeção

1. `Place N---N Source` via `identification_sources` (não `LocationCandidate N---1 Source`)
2. Normalização de `probability` corrigida para tratar score negativo/zero — ver ADR 0003
3. `lonlat_type` aceita `null` no schema
4. `identification.special` lido diretamente da identificação quando `id_source == "special"`
