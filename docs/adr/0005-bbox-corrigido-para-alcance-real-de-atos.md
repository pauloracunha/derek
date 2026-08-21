---
status: accepted
---

# Bbox de validação corrigido: Atos alcança Roma e a Etiópia, não só o "Mediterrâneo oriental"

`definitions.md` §10 e a Constitution (Princípio III) fixavam o bbox de validação de coordenadas em lon 20–50, lat 25–45 ("Mediterrâneo oriental"). Rodando `test_coordinates_order.py` contra os dados reais extraídos de Atos, 11 candidatos falharam — todos lugares genuínos e corretos da narrativa: Roma, Fórum de Ápio, Três Vendas, Putéoli, Régio, Siracusa, Malta (viagem de Paulo a Roma, Atos 27–28, lon ~12–15) e Etiópia/Meroe (Atos 8:27, lat ~16,9).

O bbox original estava errado, não os dados. Atos narra uma jornada que vai de Jerusalém a Roma e menciona a Etiópia — sai do "Mediterrâneo oriental" estrito por definição.

Corrigido para lon [10, 48], lat [15, 43] (intervalo real observado lon [12.49, 46.10], lat [16.94, 41.89], com margem). Atualizado em `pipeline/config.py`, `tests/test_coordinates_order.py` e `data-model.md`. `plan.md`/`research.md`/`tasks.md` mantêm o número antigo em prosa histórica — não corrigidos por serem documentos de fase já concluída; este ADR é a referência atual.

Alternativa rejeitada: manter bbox estrito e tratar Roma/Malta/Etiópia como outliers a excluir do teste. Rejeitada por esconder dados geográficos corretos atrás de uma suposição de escopo errada — exatamente o tipo de "ajustar o teste até passar" que a Constitution VI proíbe.
