"""FR-013: todo modelo tem entrada para as 2 estratégias de amostragem negativa.

Marcado slow: uma execução completa de s07_linkpred.py (node2vec incluso) leva ~2min,
fora do orçamento da suíte rápida do dia a dia."""

import pytest

from pipeline.s07_linkpred import ALL_MODELS, NEGATIVE_STRATEGIES, run


@pytest.mark.slow
def test_every_model_has_both_negative_sampling_strategies():
    result = run()
    seen = {(r["model"], r["negative_sampling"]) for r in result["results"]}
    expected = {(m, s) for m in ALL_MODELS for s in NEGATIVE_STRATEGIES}
    assert seen == expected, f"faltando: {expected - seen}"
    assert len(result["results"]) == len(ALL_MODELS) * len(NEGATIVE_STRATEGIES) == 12
