"""probability soma 1.0 por lugar, mesmo com score negativo na origem (docs/adr/0003)."""


def test_probabilities_sum_to_one_per_place(places):
    for p in places:
        if not p["candidates"]:
            continue
        total = sum(c["probability"] for c in p["candidates"])
        assert abs(total - 1.0) < 1e-9, f"{p['place_id']}: soma={total}"


def test_probabilities_never_negative(places):
    for p in places:
        for c in p["candidates"]:
            assert c["probability"] >= 0, f"{p['place_id']}/{c['modern_id']}: probability={c['probability']}"


def test_negative_score_candidate_gets_near_zero_probability(places):
    """Um candidato com score negativo nunca deve dominar a distribuição (ADR 0003)."""
    found_negative = False
    for p in places:
        scores = [c["score"] for c in p["candidates"]]
        if any(s < 0 for s in scores) and any(s > 0 for s in scores):
            found_negative = True
            for c in p["candidates"]:
                if c["score"] < 0:
                    assert c["probability"] == 0.0
    assert found_negative, "Nenhum lugar de teste com score negativo+positivo misturado encontrado nos dados reais"
