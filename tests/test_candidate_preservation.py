"""candidate_count na saída == contagem de modern_associations na origem; verses só de Atos."""

import json

from pipeline import config


def _ancient_by_id():
    result = {}
    with (config.RAW_DIR / "ancient.jsonl").open() as f:
        for line in f:
            d = json.loads(line)
            result[d["id"]] = d
    return result


def test_candidate_count_matches_origin_modern_associations(places):
    ancient = _ancient_by_id()
    for p in places:
        origin = ancient[p["place_id"]]
        expected = len(origin.get("modern_associations", {}))
        assert p["candidate_count"] == expected, (
            f"{p['place_id']}: saída tem {p['candidate_count']}, origem tem {expected}"
        )


def test_verses_scope_restricted_to_acts(places):
    for p in places:
        for sort in p["verses"]:
            assert sort.startswith(config.BOOK_ID), f"{p['place_id']}: sort {sort} não é de Atos"
            assert len(sort) == 8 and isinstance(sort, str)
