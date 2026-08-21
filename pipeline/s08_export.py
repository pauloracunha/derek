"""Exporta os artefatos finais para data/processed/. Saída determinística (chaves ordenadas,
sem espaços supérfluos) para permitir comparação byte-a-byte entre execuções (FR-018)."""

import json

from pipeline import config
from pipeline.s03_extract_acts import run as extract_places
from pipeline.s04_build_graph import build_graph_export
from pipeline.s05_uncertainty import run as compute_uncertainty
from pipeline.s06_communities import run as compute_communities
from pipeline.s06_communities import write_community_comparison_artifact
from pipeline.s07_linkpred import run as compute_linkpred


def _write_json(name: str, data) -> None:
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = config.PROCESSED_DIR / name
    with dest.open("w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"  {name}: {dest.stat().st_size:,} bytes")


def export_places() -> None:
    places = extract_places()
    _write_json("places.json", places)


def export_graph() -> None:
    """Requer places.json já exportado (export_places()) — s04_build_graph.py lê do disco.
    Inclui comunidades reais (s06_communities.py), não o placeholder community=0."""
    communities = compute_communities()
    write_community_comparison_artifact(communities)
    export = build_graph_export(
        community_by_place=communities["community_by_place"],
        connectivity_by_community=communities["connectivity_by_community"],
    )
    _write_json("graph.json", export)


def export_uncertainty() -> None:
    """Requer graph.json já exportado (export_graph()) — s05_uncertainty.py lê arestas do disco."""
    _write_json("uncertainty.json", compute_uncertainty())


def export_linkpred() -> None:
    """Independente das demais — usa cross-references.txt (data/raw/) e places.json."""
    _write_json("linkpred.json", compute_linkpred())


def main() -> None:
    print("Exportando places.json...")
    export_places()
    print("Exportando graph.json...")
    export_graph()
    print("Exportando uncertainty.json...")
    export_uncertainty()
    print("Exportando linkpred.json...")
    export_linkpred()


if __name__ == "__main__":
    main()
