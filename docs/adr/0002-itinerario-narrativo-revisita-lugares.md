---
status: accepted
---

# Itinerário narrativo revisita lugares, não deduplica por primeira menção

A métrica "comprimento do itinerário narrativo" (Monte Carlo, `FR-013`) precisa de uma posição narrativa única por ponto do caminho. A opção óbvia — deduplicar por Lugar usando a primeira menção — foi cogitada e rejeitada: o itinerário é construído sobre a sequência de **versículos** (`Verse`), não sobre a lista deduplicada de `Place`s. Um lugar mencionado várias vezes (ex. Jerusalém, `mention_count: 59`) é revisitado no itinerário toda vez que reaparece, mesmo que a narrativa já tenha "saído" dele e voltado.

Consequência: a métrica fica mais fiel à leitura literal do texto (revisitas custam distância real), mas o cálculo é sobre a sequência de versículos, não sobre uma lista simples de lugares únicos ordenados — impacta diretamente `pipeline/s05_uncertainty.py` (T044/T045) e deve ser refletido em `data-model.md`.

Alternativa rejeitada: itinerário como sequência de `Place`s únicos por primeira menção — mais simples de implementar, mas descartaria o custo real de "ir e voltar" a um lugar, subestimando a distância total percorrida.
