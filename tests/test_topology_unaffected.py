"""Constitution VI / FR-004: métricas topológicas nunca variam com a simulação de incerteza."""

import json

from pipeline.s04_build_graph import build_graph_export
from pipeline.s05_uncertainty import run as run_uncertainty


def test_topology_identical_before_and_after_montecarlo():
    before = build_graph_export()

    run_uncertainty()  # roda a simulação de incerteza — não deve tocar a topologia

    after = build_graph_export()

    before_by_id = {n["place_id"]: n for n in before["nodes"]}
    after_by_id = {n["place_id"]: n for n in after["nodes"]}
    assert before_by_id.keys() == after_by_id.keys()
    for place_id, node_before in before_by_id.items():
        node_after = after_by_id[place_id]
        assert node_before["degree"] == node_after["degree"]
        assert node_before["weighted_degree"] == node_after["weighted_degree"]
        assert node_before["betweenness"] == node_after["betweenness"]


def test_graph_json_on_disk_matches_topology_after_uncertainty_run():
    run_uncertainty()
    fresh = build_graph_export()
    with open("data/processed/graph.json") as f:
        on_disk = json.load(f)
    on_disk_by_id = {n["place_id"]: n for n in on_disk["nodes"]}
    for node in fresh["nodes"]:
        d = on_disk_by_id[node["place_id"]]
        assert d["degree"] == node["degree"]
        assert d["betweenness"] == node["betweenness"]
