"""Propagação de incerteza via Monte Carlo — só nas métricas que dependem de distância
geográfica (Constitution VI). Métricas topológicas (grau, intermediação, comunidade) nunca
são recalculadas aqui.

5 métricas (spec 003, FR-003):
- 4 escalares de rede: comprimento total, distância média por aresta, área do fecho convexo,
  itinerário narrativo — cada uma com mean/ci_low/ci_high/deterministic.
- 1 ranking por lugar: centralidade geográfica (distância ao centroide ponderado por
  mention_count) — modal_rank/rank_ci por lugar (grill 2026-08-11 Q1).

Itinerário narrativo revisita lugares mencionados várias vezes (ADR 0002), não deduplica.
"""

import json
import random
import statistics
from collections import Counter
from itertools import pairwise

from pyproj import Geod
from scipy.spatial import ConvexHull

from pipeline import config
from pipeline.s04_build_graph import load_locatable_places

GEOD = Geod(ellps="WGS84")


def _load_graph_edges() -> list[tuple[str, str]]:
    with open(config.PROCESSED_DIR / "graph.json") as f:
        graph = json.load(f)
    return [(e["source"], e["target"]) for e in graph["edges"]]


def _sample_coords(places: list[dict], rng: random.Random) -> dict[str, tuple[float, float]]:
    """Um candidato por lugar, amostrado proporcional a `probability` (uniforme em empate,
    já garantido pela normalização de s03_extract_acts.py)."""
    coords = {}
    for p in places:
        candidates = p["candidates"]
        weights = [c["probability"] for c in candidates]
        chosen = rng.choices(candidates, weights=weights, k=1)[0]
        coords[p["place_id"]] = (chosen["lon"], chosen["lat"])
    return coords


def _deterministic_coords(places: list[dict]) -> dict[str, tuple[float, float]]:
    coords = {}
    for p in places:
        best = max(p["candidates"], key=lambda c: c["probability"])
        coords[p["place_id"]] = (best["lon"], best["lat"])
    return coords


def _geod_distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    _, _, dist_m = GEOD.inv(a[0], a[1], b[0], b[1])
    return dist_m / 1000.0


def _total_and_mean_edge_distance(
    edges: list[tuple[str, str]], coords: dict[str, tuple[float, float]]
) -> tuple[float, float]:
    if not edges:
        return 0.0, 0.0
    total = sum(_geod_distance_km(coords[a], coords[b]) for a, b in edges)
    return total, total / len(edges)


def _convex_hull_area_km2(coords: dict[str, tuple[float, float]]) -> float:
    points = list(coords.values())
    if len(points) < 3:
        return 0.0
    hull = ConvexHull(points)
    ring_lons = [points[i][0] for i in hull.vertices]
    ring_lats = [points[i][1] for i in hull.vertices]
    area_m2, _ = GEOD.polygon_area_perimeter(ring_lons, ring_lats)
    return abs(area_m2) / 1_000_000.0


def _weighted_centroid(
    places: list[dict], coords: dict[str, tuple[float, float]]
) -> tuple[float, float]:
    total_weight = sum(p["mention_count"] for p in places) or 1
    lon = sum(coords[p["place_id"]][0] * p["mention_count"] for p in places) / total_weight
    lat = sum(coords[p["place_id"]][1] * p["mention_count"] for p in places) / total_weight
    return lon, lat


def _centrality_ranking(
    places: list[dict], coords: dict[str, tuple[float, float]]
) -> list[str]:
    """place_id ordenado do mais central (menor distância ao centroide) ao menos central."""
    centroid = _weighted_centroid(places, coords)
    dist = {p["place_id"]: _geod_distance_km(coords[p["place_id"]], centroid) for p in places}
    return sorted(dist, key=dist.get)


def _narrative_itinerary_sequence(places: list[dict]) -> list[str]:
    """Sequência de place_id por Verse, ordenada por sort — revisita lugares (ADR 0002)."""
    entries = []
    for p in places:
        for sort in p["verses"]:
            entries.append((sort, p["place_id"]))
    entries.sort(key=lambda e: e[0])
    return [place_id for _, place_id in entries]


def _itinerary_length_km(sequence: list[str], coords: dict[str, tuple[float, float]]) -> float:
    total = 0.0
    for prev, curr in pairwise(sequence):
        if prev == curr:
            continue
        total += _geod_distance_km(coords[prev], coords[curr])
    return total


def _percentile(values: list[float], pct: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    k = (len(values) - 1) * pct / 100
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def run() -> dict:
    places = load_locatable_places()
    edges = _load_graph_edges()
    itinerary_sequence = _narrative_itinerary_sequence(places)

    deterministic_coords = _deterministic_coords(places)
    det_total, det_mean = _total_and_mean_edge_distance(edges, deterministic_coords)
    det_hull = _convex_hull_area_km2(deterministic_coords)
    det_itin = _itinerary_length_km(itinerary_sequence, deterministic_coords)

    rng = random.Random(config.SEED)
    totals, means, hulls, itins = [], [], [], []
    rank_history: dict[str, list[int]] = {p["place_id"]: [] for p in places}

    for _ in range(config.N_SIMULATIONS):
        coords = _sample_coords(places, rng)
        total, mean = _total_and_mean_edge_distance(edges, coords)
        totals.append(total)
        means.append(mean)
        hulls.append(_convex_hull_area_km2(coords))
        itins.append(_itinerary_length_km(itinerary_sequence, coords))

        ranking = _centrality_ranking(places, coords)
        for rank, place_id in enumerate(ranking, start=1):
            rank_history[place_id].append(rank)

    def metric_entry(values: list[float], deterministic: float) -> dict:
        return {
            "mean": statistics.mean(values),
            "ci_low": _percentile(values, 2.5),
            "ci_high": _percentile(values, 97.5),
            "deterministic": deterministic,
        }

    metrics = {
        "total_network_length_km": metric_entry(totals, det_total),
        "mean_edge_distance_km": metric_entry(means, det_mean),
        "convex_hull_area_km2": metric_entry(hulls, det_hull),
        "narrative_itinerary_length_km": metric_entry(itins, det_itin),
    }

    place_rank_stability = []
    for place_id, ranks in rank_history.items():
        modal_rank = Counter(ranks).most_common(1)[0][0]
        place_rank_stability.append({
            "place_id": place_id,
            "modal_rank": modal_rank,
            "rank_ci": [min(ranks), max(ranks)],
        })
    place_rank_stability.sort(key=lambda r: r["place_id"])

    return {
        "n_simulations": config.N_SIMULATIONS,
        "seed": config.SEED,
        "metrics": metrics,
        "place_rank_stability": place_rank_stability,
    }


def main() -> None:
    result = run()
    m = result["metrics"]
    print(f"  Comprimento total: {m['total_network_length_km']['mean']:.1f} km "
          f"[{m['total_network_length_km']['ci_low']:.1f}, {m['total_network_length_km']['ci_high']:.1f}] "
          f"(determinístico: {m['total_network_length_km']['deterministic']:.1f})")
    print(f"  Distância média/aresta: {m['mean_edge_distance_km']['mean']:.2f} km")
    print(f"  Área do fecho convexo: {m['convex_hull_area_km2']['mean']:,.0f} km²")
    print(f"  Itinerário narrativo: {m['narrative_itinerary_length_km']['mean']:.1f} km")


if __name__ == "__main__":
    main()
