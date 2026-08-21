---
status: accepted
---

# Normalização de probabilidade com score negativo: clip-a-zero + fallback uniforme

`definitions.md` §1.2 define `probability_i = score_i / Σscore_j`, assumindo score sempre positivo. A inspeção real de `ancient.jsonl` (`docs/data-contracts.md`) mostrou que **20,5% dos lugares com múltiplos candidatos têm ao menos um candidato com score negativo** — `score` é um voto líquido da comunidade (pode ser predominantemente contrário a um candidato), não uma confiança sempre-positiva. A fórmula ingênua produz probabilidade negativa, >1, ou divide por um Σ próximo de zero.

Decidimos: para cada `Place`, calcular `score'_i = max(score_i, 0)` (clipar negativos a zero) antes de normalizar. `probability_i = score'_i / Σscore'_j`. Se **todos** os candidatos de um lugar tiverem `score' = 0` (Σ=0), usar distribuição uniforme (`probability_i = 1/N`) como fallback explícito — nunca dividir por zero, nunca descartar o candidato (Constitution I).

Um candidato com score negativo continua **presente** em `candidates[]` (nunca removido — a comunidade "votar contra" não é o mesmo que "não é candidato"), mas com `probability = 0`, ficando visualmente quase invisível (opacidade/tamanho mínimos) — o que é uma leitura honesta: o público de fato rejeitou essa hipótese.

Alternativa rejeitada: softmax sobre os scores brutos. Rejeitada porque daria probabilidade não-nula a candidatos que a comunidade rejeitou ativamente (score muito negativo), distorcendo o sinal na direção oposta à intenção dos votantes — contradiz o princípio de honestidade de dados do projeto (Constitution VI).

Alternativa rejeitada: shift por `min(score)` do lugar antes de normalizar. Rejeitada por ser uma transformação arbitrária sem significado no domínio (o deslocamento muda dependendo de quão negativo é o pior candidato daquele lugar específico, tornando `probability` não comparável entre lugares diferentes).

**Por que clip é a única opção que não fabrica confiança**: um candidato com voto líquido negativo não tem "probabilidade baixa" — tem **evidência contrária** registrada pela comunidade. Softmax e o deslocamento por `min(score)` atribuem massa de probabilidade positiva a essa hipótese mesmo assim, inventando confiança que a fonte nunca expressou. Clip-a-zero é a única das três transformações que respeita literalmente o que os votantes disseram: "não sabemos o suficiente pra dar confiança positiva a isso" vira probabilidade zero, não um valor pequeno arbitrário. O candidato continua visível em `candidates[]` (peso ≈0, nunca removido) porque a ausência de confiança positiva não é o mesmo que ausência do próprio candidato — são dois fatos diferentes e a Constitution I proíbe colapsar um no outro.
