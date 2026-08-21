"""Grafo de coocorrência de lugares de Atos por capítulo.

- Nós: todo Place com is_locatable=true (mesmo sem nenhuma coocorrência — nunca excluído).
- Arestas: dois lugares coocorrem se aparecem no mesmo capítulo; peso = nº de capítulos coocorrentes.
- Métricas topológicas (degree/weighted_degree/betweenness) nunca dependem de coordenadas —
  não variam com a simulação de incerteza (Constitution VI, s05_uncertainty.py).
"""

import itertools
import json
from collections import defaultdict

import networkx as nx

from pipeline import config


def load_locatable_places() -> list[dict]:
    with open(config.PROCESSED_DIR / "places.json") as f:
        places = json.load(f)
    return [p for p in places if p["is_locatable"]]


def build_graph(places: list[dict]) -> nx.Graph:
    g = nx.Graph()
    for p in places:
        g.add_node(p["place_id"])

    chapter_to_places = defaultdict(set)
    for p in places:
        for ch in p["chapters"]:
            chapter_to_places[ch].add(p["place_id"])

    edge_chapters = defaultdict(set)
    for ch, place_ids in chapter_to_places.items():
        for a, b in itertools.combinations(sorted(place_ids), 2):
            edge_chapters[(a, b)].add(ch)

    for (a, b), chapters in edge_chapters.items():
        g.add_edge(a, b, weight=len(chapters), chapters=sorted(chapters))

    return g


def compute_topology(g: nx.Graph) -> dict:
    betweenness = nx.betweenness_centrality(g, weight=None)
    topology = {}
    for node in g.nodes:
        weighted_degree = sum(data["weight"] for _, _, data in g.edges(node, data=True))
        topology[node] = {
            "degree": g.degree(node),
            "weighted_degree": weighted_degree,
            "betweenness": betweenness[node],
        }
    return topology


def build_graph_export(
    places: list[dict] | None = None,
    community_by_place: dict[str, int] | None = None,
    connectivity_by_community: dict[int, bool] | None = None,
) -> dict:
    places = places if places is not None else load_locatable_places()
    g = build_graph(places)
    topology = compute_topology(g)
    community_by_place = community_by_place or {}
    connectivity_by_community = connectivity_by_community or {}

    nodes = []
    for node in sorted(g.nodes):
        community_id = community_by_place.get(node, 0)
        entry = {
            "place_id": node,
            "degree": topology[node]["degree"],
            "weighted_degree": topology[node]["weighted_degree"],
            "betweenness": topology[node]["betweenness"],
            "community": community_id,
        }
        if community_id in connectivity_by_community:
            entry["community_is_connected"] = connectivity_by_community[community_id]
        nodes.append(entry)
    edges = [
        {
            "source": a,
            "target": b,
            "weight": data["weight"],
            "chapters": data["chapters"],
        }
        for a, b, data in sorted(g.edges(data=True), key=lambda e: (e[0], e[1]))
    ]

    return {"unit": "chapter", "nodes": nodes, "edges": edges}


def main() -> None:
    export = build_graph_export()
    isolated = sum(1 for n in export["nodes"] if n["degree"] == 0)
    print(f"  Grafo: {len(export['nodes'])} nós ({isolated} isolados), {len(export['edges'])} arestas")


if __name__ == "__main__":
    main()
