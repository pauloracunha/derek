"""spec.md Edge Case: comunidade com um único lugar é resultado válido, não é erro."""

import networkx as nx

from pipeline.s06_communities import _is_connected


def test_singleton_community_is_treated_as_connected():
    g = nx.Graph()
    g.add_node("a1")
    assert _is_connected(g, {"a1"}) is True


def test_real_communities_may_include_singletons_without_crashing():
    from pipeline.s06_communities import run as run_communities

    result = run_communities()
    sizes = {}
    for community_id in result["community_by_place"].values():
        sizes[community_id] = sizes.get(community_id, 0) + 1
    # não afirma que existe singleton nos dados reais — só que, se existir, é aceito sem erro
    for community_id, size in sizes.items():
        if size == 1:
            assert result["connectivity_by_community"][community_id] is True
