# Atlas de Atos Constitution

## Core Principles

### I. Incerteza nunca colapsa
NUNCA colapsar múltiplos candidatos de localização de um lugar em um ponto único. Todo lugar localizável com N candidatos DEVE exibir os N candidatos, com peso visual proporcional à probabilidade de cada um. Colapsar para "o candidato de maior score" é precisamente a falha que este projeto existe para corrigir — qualquer código, teste ou visualização que faça isso é um bug de prioridade máxima, não um detalhe de implementação.

### II. Lugar não-localizável nunca desaparece
NUNCA descartar silenciosamente um lugar sem localização conhecida. Lugares com resolução `unknown_place`, `nonspecific_place` ou `multiple_locations` permanecem no catálogo e aparecem na interface com a razão explícita. Só são excluídos de fato os que não são lugares reais (`not_a_place`, `not_a_proper_name`, `recursive`).

### III. Ordem de coordenadas é `lon,lat`
O campo `lonlat` de origem é `"longitude,latitude"`, nesta ordem. Toda leitura, teste e visualização DEVE respeitar essa ordem explicitamente — nunca assumir `lat,lon` por convenção de outra biblioteca sem conversão deliberada e testada.

### IV. Chaves canônicas são strings
`sort` (formato `BBCCCVVV`) é string, nunca inteiro. Zeros à esquerda são significativos para a ordenação canônica. Qualquer conversão para número quebra a ordenação e é proibida.

### V. Dados de origem são imutáveis
Nenhum arquivo em `data/raw/` é modificado. Toda transformação é derivada e reprodutível a partir do bruto — o pipeline pode ser apagado e reexecutado a qualquer momento sem perda de informação.

### VI. Resultado fraco é resultado válido
Se uma métrica, hipótese ou modelo produzir resultado fraco, nulo ou contrário à expectativa (ex.: proporção de multi-candidatos abaixo de 15%, heurística simples superando embedding, intervalo de confiança estreito), o resultado é reportado como está. Ajustar o experimento, a amostra ou o modelo até obter o resultado desejado é proibido.

## Restrições de escopo

Fora de escopo, não implementar: exibição de texto bíblico completo, suporte a livros além de Atos (livro 44), autenticação, banco de dados servidor, backend em runtime, análise morfossintática/línguas originais, geometrias complexas (apenas pontos).

Deploy é estático (sem backend em runtime). Toda análise avançada (predição de links, comparação de comunidades NMI/ARI) é documentada no relatório escrito, não exposta interativamente na aplicação web (decisão registrada em `specs/001-atlas-atos/spec.md`, sessão de clarificação 2026-08-02).

## Qualidade e reprodutibilidade

- Seed fixa em toda simulação estocástica (Monte Carlo, split de link prediction, amostragem negativa). Duas execuções com a mesma seed produzem saída byte-idêntica.
- Distância geográfica usa geodésica real (WGS84), nunca euclidiana sobre lat/lon bruto.
- Monte Carlo aplica-se somente a métricas que dependem de coordenadas (comprimento de rede, distância média, fecho convexo, centralidade geográfica, itinerário narrativo). Métricas topológicas puras (grau, intermediação, comunidade) NUNCA são simuladas — não dependem de localização.
- Amostragem negativa de link prediction reporta obrigatoriamente as duas estratégias (`random` e `distance_matched`) lado a lado; a diferença entre elas é discutida, nunca omitida.

## Governance

Esta constituição rege as decisões de implementação do pipeline e da aplicação web do Atlas de Atos. Qualquer plano ou tarefa que viole um princípio da seção Core Principles precisa de justificativa explícita registrada em `Complexity Tracking` do plano correspondente, ou ser redesenhada para cumprir o princípio.

**Version**: 1.0.0 | **Ratified**: 2026-08-02 | **Last Amended**: 2026-08-02
