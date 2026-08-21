"""Carrega os 3 .jsonl brutos em DuckDB (data/interim/atlas.duckdb). Nunca escreve em data/raw/."""

from datetime import UTC, datetime
from pathlib import Path

import duckdb

from pipeline import config

SCHEMA_ARTIFACT_PATH = Path("docs/schema.md")
TABLES = ("ancient", "modern", "source")


def write_schema_artifact(con: duckdb.DuckDBPyConnection) -> None:
    """Esquema real das tabelas carregadas, gerado por introspecção (nunca escrito à mão) —
    fecha a lacuna de evidência R1.3 (specs/002-fechar-lacunas-sprint1)."""
    generated_at = datetime.now(UTC).isoformat()
    lines = [
        "# Esquema das tabelas carregadas",
        "",
        (
            f"Gerado automaticamente por `pipeline/s02_load.py` em {generated_at}. "
            "Não editar à mão — reflete sempre a execução mais recente de `s02_load.py`."
        ),
        "",
    ]
    for table in TABLES:
        row_count = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        columns = con.execute(f"PRAGMA table_info('{table}')").fetchall()
        lines.append(f"## `{table}` ({row_count} linhas)")
        lines.append("")
        lines.append("| Campo | Tipo |")
        lines.append("|---|---|")
        for _cid, name, col_type, *_rest in columns:
            lines.append(f"| `{name}` | `{col_type}` |")
        lines.append("")

    SCHEMA_ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_ARTIFACT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Esquema gravado em {SCHEMA_ARTIFACT_PATH}")


def load() -> None:
    config.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(config.DUCKDB_PATH))
    try:
        con.execute("DROP TABLE IF EXISTS ancient")
        con.execute("DROP TABLE IF EXISTS modern")
        con.execute("DROP TABLE IF EXISTS source")

        con.execute(
            f"CREATE TABLE ancient AS SELECT * FROM read_ndjson_auto('{config.RAW_DIR / 'ancient.jsonl'}', maximum_object_size=20000000)"
        )
        con.execute(
            f"CREATE TABLE modern AS SELECT * FROM read_ndjson_auto('{config.RAW_DIR / 'modern.jsonl'}', maximum_object_size=20000000)"
        )
        con.execute(
            f"CREATE TABLE source AS SELECT * FROM read_ndjson_auto('{config.RAW_DIR / 'source.jsonl'}', maximum_object_size=20000000)"
        )

        counts = {
            table: con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in TABLES
        }
        print(f"  Carregado: {counts}")

        write_schema_artifact(con)
    finally:
        con.close()


def main() -> None:
    load()


if __name__ == "__main__":
    main()
