"""FR-018 / Constitution VI: duas execuções produzem places.json byte-idêntico.

Escopo de "byte-idêntico" é a versão travada em uv.lock, não upgrades futuros
(docs/adr/0001-reprodutibilidade-escopo-lockfile.md)."""

import json

from pipeline.s03_extract_acts import run


def test_two_runs_produce_identical_places_json():
    run1 = run()
    run2 = run()
    encoded1 = json.dumps(run1, sort_keys=True)
    encoded2 = json.dumps(run2, sort_keys=True)
    assert encoded1 == encoded2
