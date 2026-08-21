"""FR-014 / grill 2026-08-11 Q2: par com voto líquido negativo nunca vira aresta positiva;
voto líquido zero permanece.

Testa build_ego_network() diretamente (sem node2vec) — rápido, não precisa do marcador slow.
O catálogo lista as duas direções de um par com votos possivelmente diferentes (achado real:
Acts.3.19->Acts.3.21=4, Acts.3.21->Acts.3.19=-1) — o voto relevante é a SOMA das duas
direções, não uma direção isolada."""

from pipeline.s07_linkpred import build_ego_network, parse_cross_references


def _net_votes_by_pair(rows, node_set):
    net = {}
    for frm, to, votes in rows:
        if frm not in node_set or to not in node_set:
            continue
        pair = (frm, to) if frm <= to else (to, frm)
        net[pair] = net.get(pair, 0) + votes
    return net


def test_negative_net_vote_pairs_excluded_zero_net_vote_pairs_kept():
    rows = parse_cross_references()
    g = build_ego_network(rows)
    node_set = set(g.nodes())

    net = _net_votes_by_pair(rows, node_set)
    negative_pairs = [pair for pair, v in net.items() if v < 0]
    zero_pairs = [pair for pair, v in net.items() if v == 0]

    assert negative_pairs, "nenhum par com voto líquido negativo no escopo — teste não cobre o caso real"
    for a, b in negative_pairs:
        assert not g.has_edge(a, b), f"par com voto líquido negativo virou aresta: {a}-{b}"

    assert zero_pairs, "nenhum par com voto líquido zero no escopo — teste não cobre o caso real"
    kept = sum(1 for a, b in zero_pairs if g.has_edge(a, b))
    assert kept == len(zero_pairs), (
        f"{len(zero_pairs) - kept} pares de voto líquido zero foram excluídos indevidamente"
    )
