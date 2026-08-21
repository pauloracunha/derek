"""Evidência persistida da Sprint 1 (specs/002-fechar-lacunas-sprint1).

Testes rápidos/offline (usam data/raw/ já baixado, reusado entre sessões pytest via fixture
de sessão em conftest.py) ficam aqui sem marcador. Testes que exigem ambiente limpo/rede real
são marcados @pytest.mark.slow e ficam fora do `pytest` padrão (ver pyproject.toml)."""

from pathlib import Path

import duckdb
import pytest

from pipeline import config
from pipeline.s02_load import load
from pipeline.s03_extract_acts import (
    compute_candidate_distribution,
    write_distribution_artifact,
)

SCHEMA_PATH = Path("docs/schema.md")
DISTRIBUTION_PATH = Path("docs/candidate-distribution.md")


def test_schema_artifact_exists_and_lists_tables():
    load()
    assert SCHEMA_PATH.exists()
    content = SCHEMA_PATH.read_text(encoding="utf-8")
    for table in ("ancient", "modern", "source"):
        assert f"## `{table}`" in content, f"tabela {table} ausente de {SCHEMA_PATH}"

    con = duckdb.connect(str(config.DUCKDB_PATH))
    try:
        for table in ("ancient", "modern", "source"):
            row_count = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            assert row_count > 0
            assert f"({row_count} linhas)" in content
    finally:
        con.close()


def test_distribution_artifact_exists_and_matches_counts(places):
    result = compute_candidate_distribution(places)
    write_distribution_artifact(result)

    assert DISTRIBUTION_PATH.exists()
    content = DISTRIBUTION_PATH.read_text(encoding="utf-8")

    assert str(result["with_1_candidate"]) in content
    assert str(result["with_2_candidates"]) in content
    assert str(result["with_3plus_candidates"]) in content
    assert str(result["unlocatable_count"]) in content
    assert "threshold_crossed" in content.lower() or (
        "abaixo do limiar" in content.lower() or "acima do limiar" in content.lower()
    )


@pytest.mark.slow
def test_sprint1_command_produces_all_artifacts_in_clean_environment(tmp_path, monkeypatch):
    import shutil
    import subprocess
    import sys

    for p in (config.RAW_DIR, config.INTERIM_DIR, config.PROCESSED_DIR, SCHEMA_PATH, DISTRIBUTION_PATH):
        if Path(p).is_dir():
            shutil.rmtree(p)
        elif Path(p).exists():
            Path(p).unlink()

    result = subprocess.run(
        [sys.executable, "-m", "pipeline.sprint1"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    assert (config.PROCESSED_DIR / "places.json").exists()
    assert SCHEMA_PATH.exists()
    assert DISTRIBUTION_PATH.exists()


@pytest.mark.slow
def test_sprint1_rerun_is_idempotent():
    import re
    import subprocess
    import sys

    def run_and_read():
        result = subprocess.run(
            [sys.executable, "-m", "pipeline.sprint1"],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        schema = re.sub(r"em .*Z?\d*\+\d\d:\d\d", "", SCHEMA_PATH.read_text(encoding="utf-8"))
        dist = re.sub(r"em .*Z?\d*\+\d\d:\d\d", "", DISTRIBUTION_PATH.read_text(encoding="utf-8"))
        return schema, dist

    schema1, dist1 = run_and_read()
    schema2, dist2 = run_and_read()
    assert schema1 == schema2
    assert dist1 == dist2
