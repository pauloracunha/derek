"""spec.md US1 Edge Case 1: lugar sem coocorrência aparece como nó isolado, nunca excluído.

A rede real de Atos não tem nenhum nó isolado (107/107 lugares coocorrem com algo — achado
real, ver s04_build_graph.py), então este teste usa um dado sintético mínimo para provar o
invariante independente da densidade real."""

from pipeline.s04_build_graph import build_graph_export


def _place(place_id, chapters):
    return {"place_id": place_id, "chapters": chapters}


def test_place_with_no_cooccurrence_appears_as_isolated_node():
    places = [
        _place("a1", [1, 2]),
        _place("a2", [1]),
        _place("a3", [9]),  # nunca coocorre com a1/a2 — capítulo exclusivo
    ]
    export = build_graph_export(places)
    node_ids = {n["place_id"] for n in export["nodes"]}
    assert node_ids == {"a1", "a2", "a3"}, "lugar sem coocorrência foi excluído do grafo"

    a3 = next(n for n in export["nodes"] if n["place_id"] == "a3")
    assert a3["degree"] == 0
    assert a3["weighted_degree"] == 0

    edge_pairs = {(e["source"], e["target"]) for e in export["edges"]}
    assert ("a1", "a3") not in edge_pairs
    assert ("a3", "a1") not in edge_pairs
    assert ("a1", "a2") in edge_pairs
