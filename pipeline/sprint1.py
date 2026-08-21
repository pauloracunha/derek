"""Comando único da Sprint 1: download -> carga -> extração -> exportação.

Não chama s04-s07 (não existem ainda — Sprint 2) nem depende de `just` (não garantido no
ambiente). Comando canônico: `uv run python -m pipeline.sprint1`
(specs/002-fechar-lacunas-sprint1, FR-006/FR-007/FR-008).

Sem try/except: a exceção original propaga com traceback completo. O print de cada etapa já
satisfaz FR-010 (identificar qual etapa falhou) sem esconder o erro real (grill 2026-08-02 Q4).
"""

from pipeline import s01_download, s02_load, s03_extract_acts, s08_export

STAGES = [
    ("1/4: download", s01_download.main),
    ("2/4: carga", s02_load.load),
    ("3/4: extração", s03_extract_acts.main),
    ("4/4: exportação", s08_export.export_places),
]


def main() -> None:
    for label, stage in STAGES:
        print(f"\n=== Etapa {label} ===")
        stage()
    print("\nSprint 1 completa: places.json, docs/schema.md e docs/candidate-distribution.md gerados.")


if __name__ == "__main__":
    main()
