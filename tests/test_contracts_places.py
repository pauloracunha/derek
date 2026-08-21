"""Valida data/processed/places.json contra specs/001-atlas-atos/contracts/places.schema.json."""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path("specs/001-atlas-atos/contracts/places.schema.json")
PLACES_PATH = Path("data/processed/places.json")


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_places_json_matches_schema(schema):
    if not PLACES_PATH.exists():
        pytest.skip("data/processed/places.json ainda não exportado (rode pipeline.s08_export)")
    data = json.loads(PLACES_PATH.read_text())
    jsonschema.validate(instance=data, schema=schema)
