# Data Model: Sprint 3 — Interface e Validação

## Entidades já existentes (reutilizadas sem alteração)

`Place`, `LocationCandidate`, `Source`, `SpecialReason`, `LonLatType` — definidas em
`web/src/services/dataLoader.ts`, espelhando `specs/001-atlas-atos/contracts/places.schema.json`.
Esta feature não altera esses tipos.

## Tipos novos a adicionar em `dataLoader.ts`

Espelham `specs/001-atlas-atos/contracts/graph.schema.json`, ainda não consumido pela UI.

```ts
export interface GraphNode {
  place_id: string
  degree: number
  weighted_degree: number
  betweenness: number
  community: number
  community_is_connected?: boolean
}

export interface GraphEdge {
  source: string
  target: string
  weight: number
  chapters: number[]
}

export interface Graph {
  unit: 'chapter'
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export function loadGraph(): Promise<Graph> {
  return fetchJson<Graph>('/data/graph.json')
}
```

## Entidade nova: Sessão de teste de compreensão (US5)

Não é um tipo TypeScript — vive como registro em markdown (`docs/usability-test.md`,
decisão em `research.md` #5), não em `web/src`.

| Campo | Descrição |
|---|---|
| `participant_id` | identificador anônimo sequencial (P1, P2, ...) |
| `date` | data da sessão |
| `explained_correctly` | booleano — ver rubrica abaixo |
| `justification` | transcrição resumida da explicação dada pelo participante |
| `notes` | observações livres (dificuldades de navegação, confusões de UI) |

**Rubrica de `explained_correctly`**: marcar `true` se o participante expressar, em suas
próprias palavras, a ideia de que existem **múltiplas hipóteses conflitantes** sobre a
localização real de um lugar (ex. "os pesquisadores não têm certeza de qual é o lugar
certo", "há mais de um lugar candidato para o mesmo nome"). Não é necessário citar termos
técnicos ("probabilidade", "score", "candidato de localização") nem mencionar o
significado do peso visual (opacidade/tamanho) — SC-003 avalia só a compreensão do
"porquê" dos múltiplos pontos, não a leitura completa da codificação visual (grill
2026-08-19, Q6). Marcar `false` para respostas que atribuam os múltiplos pontos a causas
não relacionadas à incerteza de identificação (ex. "são lugares diferentes com nome
parecido", "é um erro do mapa").

Regra de negócio (FR-011 / Princípio VI): a taxa de acerto agregada (`explained_correctly`
= true / total) é reportada no relatório final independentemente de atingir os 80% de
SC-003.

## Extensão de estado (`store.ts`)

Nenhum campo novo — `chapterRange` e `selectedPlaceId` já cobrem US1/US3. Seleção cruzada
mapa↔grafo (grill 2026-08-19, Q9) reutiliza `selectPlace`/`selectedPlaceId` existentes:
clicar um nó do grafo chama `selectPlace(node.place_id)`, mesma função usada pelo clique
de marcador no mapa (T013) — nenhum estado novo necessário.

## Relações

```text
Place 1---N LocationCandidate   (candidates[])
Place 1---N Source              (sources[])
GraphNode 1---1 Place           (place_id compartilhado — join client-side)
GraphEdge N---2 GraphNode       (source/target referenciam place_id)
Sessão de teste N---1 Aplicação publicada (avaliada, não modelada em código)
```
