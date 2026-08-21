"""FR-008: toda comunidade internamente desconexa é sinalizada, nunca omitida."""

import networkx as nx

from pipeline.s04_build_graph import build_graph, load_locatable_places
from pipeline.s06_communities import run as run_communities


def test_every_disconnected_community_is_flagged():
    result = run_communities()
    places = load_locatable_places()
    g = build_graph(places)

    nodes_by_community: dict[int, list[str]] = {}
    for place_id, community_id in result["community_by_place"].items():
        nodes_by_community.setdefault(community_id, []).append(place_id)

    for community_id, nodes in nodes_by_community.items():
        actually_connected = len(nodes) <= 1 or nx.is_connected(g.subgraph(nodes))
        recorded_connected = result["connectivity_by_community"][community_id]
        assert actually_connected == recorded_connected, (
            f"comunidade {community_id}: conectividade real={actually_connected}, "
            f"registrada={recorded_connected}"
        )

    assert set(result["disconnected_communities"]) == {
        cid for cid, connected in result["connectivity_by_community"].items() if not connected
    }
