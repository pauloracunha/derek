"""ADR 0001: mesma seed produz uncertainty.json byte-idêntico (dentro da mesma versão travada)."""

import json

from pipeline.s05_uncertainty import run as run_uncertainty


def test_two_runs_same_seed_produce_identical_uncertainty():
    result1 = run_uncertainty()
    result2 = run_uncertainty()
    assert json.dumps(result1, sort_keys=True) == json.dumps(result2, sort_keys=True)
