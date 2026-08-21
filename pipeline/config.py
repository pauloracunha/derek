"""Constantes do pipeline. Ver docs/data-contracts.md para o formato observado das fontes."""

from pathlib import Path

BOOK_ID = "44"  # Atos dos Apóstolos, numeração canônica do dataset (sort = BBCCCVVV)
SEED = 42  # ver docs/adr/0001-reprodutibilidade-escopo-lockfile.md
N_SIMULATIONS = 1000

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")
DUCKDB_PATH = INTERIM_DIR / "atlas.duckdb"

GEOCODING_BASE_URL = "https://raw.githubusercontent.com/openbibleinfo/Bible-Geocoding-Data/main/data"
SOURCES = {
    "ancient.jsonl": f"{GEOCODING_BASE_URL}/ancient.jsonl",
    "modern.jsonl": f"{GEOCODING_BASE_URL}/modern.jsonl",
    "source.jsonl": f"{GEOCODING_BASE_URL}/source.jsonl",
}
CROSS_REFERENCES_ZIP_URL = "https://a.openbible.info/data/cross-references.zip"
CROSS_REFERENCES_ZIP_MEMBER = "cross_references.txt"
CROSS_REFERENCES_FILENAME = "cross-references.txt"

# Bbox do alcance real da narrativa de Atos (Jerusalém a Roma, incl. Malta e Etiópia) —
# usado para validar ordem lon/lat (Constitution III). Ver docs/adr/0005.
BBOX_LON = (10.0, 48.0)
BBOX_LAT = (15.0, 43.0)

# Tratamento de resoluções "special" (definitions.md §2.3 + docs/data-contracts.md)
KEPT_UNLOCATABLE_REASONS = {"unknown_place", "nonspecific_place", "multiple_locations"}
EXCLUDED_REASONS = {"not_a_place", "not_a_proper_name", "recursive"}
