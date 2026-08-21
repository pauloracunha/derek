# Atlas de Atos

Pipeline de dados + web app que visualiza a rede de lugares mencionados no livro de Atos dos Apóstolos, preservando a incerteza arqueológica de localização em vez de colapsá-la para um ponto único.

## Language

**Lugar**:
Um lugar mencionado no livro de Atos. A origem (`ancient.jsonl`) guarda TODAS as menções bíblicas de um lugar (ex. Jerusalém aparece também em Gênesis, Salmos, Apocalipse); um `Lugar` deste projeto só existe se tiver >=1 menção em Atos, e seus dados derivados (`verses`, `mention_count`, `chapters`, candidatos ligados via `identification_ids`) são **sempre filtrados a menções de Atos only** — nunca carregam dado de outro livro, mesmo que a origem os inclua.
_Avoid_: copiar `verses[]` da origem sem filtrar por `sort` começando em `"44"`.

**Candidato de Localização**:
Uma hipótese de localização geográfica para um Lugar, com coordenadas, `score` bruto de origem e `probability` normalizada frente aos demais candidatos do mesmo lugar.
_Avoid_: "candidato" sozinho, sem qualificador — colide com Candidato a Nova Conexão.

**Candidato a Nova Conexão**:
Um par de versículos (um em Atos, outro em qualquer lugar do cânon) sugerido por predição de links como referência cruzada plausível, ainda ausente do catálogo conhecido.
_Avoid_: "candidato" sozinho; "link candidate" (manter em português no texto corrido).

**Incerteza** (termo guarda-chuva):
O tema central do projeto — a existência de múltiplas hipóteses plausíveis e não-equivalentes sobre onde um Lugar fica, em vez de um ponto único e certo. Nunca é o nome de um campo específico — sempre um conceito, nunca um valor numérico isolado.
_Avoid_: usar "incerteza" como nome de campo/variável (ver Índice de Dispersão e IC 95% de `uncertainty.json`, que são medições concretas *da* incerteza, não a incerteza em si).

**Índice de Dispersão** (`dispersion_index` por Lugar):
Métrica derivada por Lugar (0–1) que resume o quão espalhada é a distribuição de probabilidade entre seus Candidatos de Localização — próximo de 0 quando um candidato domina, próximo de 1 quando os candidatos são igualmente prováveis. Usado na UI para ordenar/destacar lugares mais disputados no US1.
_Avoid_: "uncertainty_index" (nome de campo antigo, renomear para `dispersion_index` no contrato); "incerteza" sozinho para se referir a este campo.

**Fonte**:
Referência bibliográfica de `source.jsonl` que embasa a identificação de um Lugar. Relação confirmada por inspeção real (`docs/data-contracts.md`): é `Place N---N Source`, via `identification_sources` — no nível do Lugar inteiro, não por Candidato de Localização individual (não existe, nos dados reais, join Fonte↔candidato específico).
_Avoid_: assumir que existe uma Fonte por candidato — a granularidade real é por Lugar.

**Itinerário Narrativo**:
Sequência ordenada por `sort` de **todas** as menções de Lugar em Atos (uma entrada por versículo, não deduplicada por Lugar) — usada para acumular a distância geodésica percorrida "seguindo a leitura". Um Lugar mencionado várias vezes é revisitado múltiplas vezes no itinerário; mesma-lugar-para-mesma-lugar contribui distância zero, mas retornos após visitar outro lugar contribuem distância cheia.
_Avoid_: confundir com a lista de `Lugar`s únicos (deduplicados) — o Itinerário Narrativo é sobre `Verse`s, não sobre `Place`s.

**Centralidade Geográfica**:
Ranking dos Lugares por distância ao centroide ponderado da rede — uma métrica de **distância** (simulada via Monte Carlo, `place_rank_stability[]` em `uncertainty.json`: `modal_rank` + faixa de posições por Lugar). Não é um número único de rede.
_Avoid_: confundir com **Intermediação** (`betweenness`), que também é chamada de "centralidade" na literatura de grafos mas é puramente topológica (nunca simulada — Constitution VI) e vive em `graph.json`, não em `uncertainty.json`. No projeto, "centralidade" sozinha é ambíguo entre as duas — sempre qualificar como "centralidade geográfica" ou "intermediação".

**Peso Visual** (de um Candidato de Localização no mapa):
Combinação de opacidade e raio do marcador, ambos derivados de `probability` por
mapeamento linear com piso mínimo — nunca 0 — para que nenhum candidato fique invisível
ou inclicável (`opacity = 0.15 + 0.85·probability`, `radius = 4 + 12·probability`, valores
de referência; ajuste fino em implementação). Garante que o Princípio I (nenhum candidato
colapsado/escondido) se sustente mesmo para candidatos de baixa probabilidade relativa.
_Avoid_: opacidade/raio proporcional linear puro sem piso — candidato de prob. baixa
ficaria efetivamente invisível, o que é indistinguível de tê-lo descartado.

**Vínculo Visual** (entre Candidatos de Localização do mesmo Lugar):
Linha tracejada + cor compartilhada conectando os marcadores de todos os Candidatos de
Localização de um mesmo Lugar, exibida somente quando esse Lugar está selecionado (não
para todos os lugares simultaneamente, para não poluir o mapa completo). Comunica que os
pontos são hipóteses concorrentes do mesmo Lugar, não lugares distintos.
_Avoid_: exibir o vínculo permanentemente para todo lugar multi-candidato ao mesmo tempo
— decisão explícita de não fazer isso (poluição visual), rediscutir se usuários do teste
de compreensão (US5) não perceberem a relação sem seleção prévia.

**Forma do Marcador** (codificação de `lonlat_type`):
Círculo sólido = candidato de ponto exato (`lonlat_type: 'point'`); quadrado/losango ou
anel pontilhado = candidato de área aproximada (`'center' | 'representative point' |
'settlement'`). Canal visual independente de opacidade/tamanho (que codificam
`probability`) — evita comunicar falsa precisão sem depender só de cor, que já está
reservada para Comunidade no grafo (US3).
_Avoid_: usar cor para distinguir ponto vs. área — colide com o canal de cor já usado
para Comunidade em `NetworkGraph.tsx`.

## Flagged ambiguities

- **"Candidato"** usado sem qualificador em `spec.md` (ex. FR-002, FR-015) mistura dois conceitos não relacionados (localização geográfica vs. referência cruzada). Resolução: sempre qualificar — "candidato de localização" ou "candidato a nova conexão" — em spec, código e UI.
- **"Incerteza"** era usado tanto como tema geral quanto como nome de campo (`uncertainty_index`). Resolução: campo renomeado para Índice de Dispersão; "incerteza" reservado como termo guarda-chuva.
- ~~Chave de join `LocationCandidate` → Fonte~~ **Resolvida** (2026-08-02, durante implementação de `001-atlas-atos`): é `Place N---N Source` via `identification_sources`, não por candidato. Ver termo "Fonte" acima e `docs/adr/`.
