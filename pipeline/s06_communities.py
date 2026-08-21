"""Detecção de comunidades no grafo de coocorrência + comparação com a partição narrativa
de referência de Atos (Jerusalém; Judeia e Samaria; missão aos gentios).

Louvain pode gerar comunidade internamente desconexa — validado explicitamente (FR-008),
nunca omitido silenciosamente (Constitution II, por analogia).
"""

import networkx as nx
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from pipeline import config
from pipeline.s04_build_graph import build_graph, load_locatable_places

REFERENCE_BLOCKS = [
    ("jerusalem", range(1, 8)),
    ("judeia_samaria", range(8, 13)),
    ("missao_gentios", range(13, 29)),
]


def _reference_block(chapters: list[int]) -> str:
    first_chapter = min(chapters)
    for name, chapter_range in REFERENCE_BLOCKS:
        if first_chapter in chapter_range:
            return name
    return "missao_gentios"  # fallback para capítulos além de 28, não deveria ocorrer em Atos


def detect_communities(g: nx.Graph) -> list[set]:
    return nx.community.louvain_communities(g, seed=config.SEED)


def _is_connected(g: nx.Graph, nodes: set) -> bool:
    if len(nodes) <= 1:
        return True
    subgraph = g.subgraph(nodes)
    return nx.is_connected(subgraph)


def run() -> dict:
    places = load_locatable_places()
    g = build_graph(places)
    communities = detect_communities(g)

    community_by_place = {}
    connectivity_by_community = {}
    for community_id, nodes in enumerate(communities):
        connectivity_by_community[community_id] = _is_connected(g, nodes)
        for node in nodes:
            community_by_place[node] = community_id

    place_by_id = {p["place_id"]: p for p in places}
    detected_labels = []
    reference_labels = []
    for place_id in sorted(community_by_place):
        detected_labels.append(community_by_place[place_id])
        reference_labels.append(_reference_block(place_by_id[place_id]["chapters"]))

    nmi = normalized_mutual_info_score(reference_labels, detected_labels)
    ari = adjusted_rand_score(reference_labels, detected_labels)
    disconnected = [cid for cid, connected in connectivity_by_community.items() if not connected]

    return {
        "community_by_place": community_by_place,
        "connectivity_by_community": connectivity_by_community,
        "n_communities": len(communities),
        "disconnected_communities": disconnected,
        "nmi": nmi,
        "ari": ari,
    }


def write_community_comparison_artifact(result: dict) -> None:
    from datetime import UTC, datetime

    generated_at = datetime.now(UTC).isoformat()
    lines = [
        "# Comparação de comunidades detectadas com a partição narrativa de referência",
        "",
        (
            f"Gerado automaticamente por `pipeline/s06_communities.py` em {generated_at}. "
            "Não editar à mão — reflete sempre a execução mais recente."
        ),
        "",
        f"- Comunidades detectadas (Louvain): {result['n_communities']}",
        (
            f"- Comunidades internamente desconexas: {len(result['disconnected_communities'])} "
            f"{result['disconnected_communities'] if result['disconnected_communities'] else '(nenhuma)'}"
        ),
        "",
        f"- NMI (normalized mutual information) vs. partição narrativa de referência: {result['nmi']:.4f}",
        f"- ARI (adjusted Rand index) vs. partição narrativa de referência: {result['ari']:.4f}",
        "",
        (
            "Partição narrativa de referência: Jerusalém (caps. 1-7), Judeia e Samaria (caps. 8-12), "
            "missão aos gentios (caps. 13-28) — atribuída pelo primeiro capítulo de menção de cada lugar."
        ),
    ]
    from pathlib import Path

    path = Path("docs/community-comparison.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Comparação de comunidades gravada em {path}")


def main() -> None:
    result = run()
    print(f"  {result['n_communities']} comunidades detectadas "
          f"({len(result['disconnected_communities'])} desconexas)")
    print(f"  NMI={result['nmi']:.4f}  ARI={result['ari']:.4f}")
    write_community_comparison_artifact(result)


if __name__ == "__main__":
    main()
