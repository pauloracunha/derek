"""O teste mais importante do projeto (Constitution I): nenhum lugar com >1 candidato
na origem sai com exatamente 1 candidato na saída."""

import json

from pipeline import config


def test_no_place_with_multiple_origin_candidates_is_collapsed_to_one(places):
    ancient = {}
    with (config.RAW_DIR / "ancient.jsonl").open() as f:
        for line in f:
            d = json.loads(line)
            ancient[d["id"]] = d

    offenders = []
    for p in places:
        origin_count = len(ancient[p["place_id"]].get("modern_associations", {}))
        if origin_count > 1 and p["candidate_count"] == 1:
            offenders.append((p["place_id"], p["name"], origin_count))

    assert not offenders, f"Lugares colapsados para 1 candidato: {offenders}"


def test_multi_candidate_places_render_all_candidates(places):
    for p in places:
        origin_count = p["candidate_count"]
        if origin_count > 1:
            assert len(p["candidates"]) == origin_count
