"""Predição de links sobre a rede de referências cruzadas em torno de Atos.

- Rede: subgrafo ego de raio 1 a partir dos versículos de Atos em cross-references.txt
  (research.md item 2).
- Pares com Votes < 0 são excluídos das arestas positivas; Votes = 0 permanecem
  (research.md item 1; grill 2026-08-11 Q2; FR-014).
- 4 heurísticas + 2 modelos aprendidos (node2vec + LR / GBM), cada um avaliado sob 2
  estratégias de amostragem negativa (random, distance_matched) — FR-011/FR-012/FR-013.
"""

import bisect
import csv
import random

import networkx as nx
import numpy as np
from node2vec import Node2Vec
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from pipeline import config

# Ordem canônica dos 66 livros do cânon protestante (para distância no cânone).
BOOK_ORDER = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph",
    "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb",
    "Jas", "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev",
]
BOOK_INDEX = {book: i for i, book in enumerate(BOOK_ORDER)}

HEURISTICS = ["common_neighbors", "jaccard", "adamic_adar", "preferential_attachment"]
LEARNED_MODELS = ["node2vec_lr", "node2vec_gbm"]
ALL_MODELS = HEURISTICS + LEARNED_MODELS
NEGATIVE_STRATEGIES = ["random", "distance_matched"]


def _canonical_rank(verse_ref: str) -> int:
    """Proxy monotônico de posição no cânone. Refs de intervalo (ex. Col.1.16-Col.1.17)
    usam a primeira referência."""
    ref = verse_ref.split("-")[0]
    parts = ref.split(".")
    book, chapter, verse = parts[0], int(parts[1]), int(parts[2])
    book_idx = BOOK_INDEX.get(book, len(BOOK_ORDER))
    return book_idx * 100_000 + chapter * 1_000 + verse


def parse_cross_references(path=None) -> list[tuple[str, str, int]]:
    path = path or (config.RAW_DIR / "cross-references.txt")
    rows = []
    with open(path) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # cabeçalho
        for row in reader:
            if len(row) < 3:
                continue
            frm, to, votes = row[0], row[1], row[2]
            try:
                rows.append((frm, to, int(votes)))
            except ValueError:
                continue
    return rows


def build_ego_network(rows: list[tuple[str, str, int]]) -> nx.Graph:
    """Ego de raio 1: versículos de Atos + seus alvos diretos; arestas com voto líquido
    negativo excluídas do conjunto positivo (Votes=0 permanece — grill Q2, FR-014).

    O catálogo lista as duas direções de um par com votos POTENCIALMENTE DIFERENTES
    (ex.: Acts.3.19->Acts.3.21 = 4, Acts.3.21->Acts.3.19 = -1 — achado real). Como o grafo
    aqui é não-direcionado, o voto líquido do par é a SOMA das duas direções (mesmo
    espírito do ADR 0003: usar o sinal líquido, não uma direção isolada)."""
    acts_verses = {frm for frm, _, _ in rows if frm.startswith("Acts.")}
    node_set = set(acts_verses)
    for frm, to, _ in rows:
        if frm in acts_verses:
            node_set.add(to)

    net_votes: dict[tuple[str, str], int] = {}
    for frm, to, votes in rows:
        if frm not in node_set or to not in node_set:
            continue
        pair = (frm, to) if frm <= to else (to, frm)
        net_votes[pair] = net_votes.get(pair, 0) + votes

    g = nx.Graph()
    g.add_nodes_from(node_set)
    for (a, b), net in net_votes.items():
        if net >= 0:
            g.add_edge(a, b)
    return g


def split_train_test(g: nx.Graph, seed: int, test_fraction: float = 0.2) -> tuple[nx.Graph, list]:
    rng = random.Random(seed)
    edges = list(g.edges())
    rng.shuffle(edges)
    n_test = int(len(edges) * test_fraction)
    test_edges = edges[:n_test]

    train_g = g.copy()
    train_g.remove_edges_from(test_edges)
    # garante conectividade do treino: devolve ao treino qualquer aresta de teste cuja
    # remoção isole um nó (grau zero) — sem isso o nó fica sem representação nenhuma.
    kept_test = []
    for a, b in test_edges:
        if train_g.degree(a) == 0 or train_g.degree(b) == 0:
            train_g.add_edge(a, b)
        else:
            kept_test.append((a, b))
    return train_g, kept_test


def _non_edges_sample(g: nx.Graph, n: int, rng: random.Random) -> list[tuple[str, str]]:
    nodes = list(g.nodes())
    samples = []
    attempts = 0
    max_attempts = n * 50
    while len(samples) < n and attempts < max_attempts:
        a, b = rng.sample(nodes, 2)
        attempts += 1
        if not g.has_edge(a, b):
            samples.append((a, b))
    return samples


def sample_negatives(
    g: nx.Graph, positive_pairs: list[tuple[str, str]], strategy: str, seed: int
) -> list[tuple[str, str]]:
    rng = random.Random(seed)
    n = len(positive_pairs)
    if strategy == "random":
        return _non_edges_sample(g, n, rng)

    # distance_matched: pareia a distribuição de distância canônica dos positivos.
    # Busca direcionada (bisect) em vez de tentativa aleatória — num espaço de milhares de
    # nós, tentativa aleatória raramente acerta uma distância específica (achado real: a
    # primeira versão, com 50 tentativas aleatórias, caía quase sempre no fallback e
    # produzia resultado indistinguível de `random`, mascarando o efeito que a estratégia
    # deveria demonstrar).
    pos_distances = [abs(_canonical_rank(a) - _canonical_rank(b)) for a, b in positive_pairs]
    nodes = list(g.nodes())
    ranks = {node: _canonical_rank(node) for node in nodes}
    sorted_nodes = sorted(nodes, key=lambda n: ranks[n])
    sorted_ranks = [ranks[n] for n in sorted_nodes]

    negatives = []
    for target_dist in pos_distances:
        found = None
        for _ in range(10):
            anchor = rng.choice(nodes)
            sign = rng.choice([1, -1])
            desired = ranks[anchor] + sign * target_dist
            pos = bisect.bisect_left(sorted_ranks, desired)
            for candidate_idx in (pos, pos - 1, min(pos + 1, len(sorted_nodes) - 1)):
                if 0 <= candidate_idx < len(sorted_nodes):
                    candidate = sorted_nodes[candidate_idx]
                    if candidate != anchor and not g.has_edge(anchor, candidate):
                        found = (anchor, candidate)
                        break
            if found:
                break
        negatives.append(found or _non_edges_sample(g, 1, rng)[0])
    return negatives


def _heuristic_scores(g: nx.Graph, pairs: list[tuple[str, str]], model: str) -> list[float]:
    if model == "common_neighbors":
        return [len(list(nx.common_neighbors(g, a, b))) for a, b in pairs]
    if model == "jaccard":
        return [s for _, _, s in nx.jaccard_coefficient(g, pairs)]
    if model == "adamic_adar":
        return [s for _, _, s in nx.adamic_adar_index(g, pairs)]
    if model == "preferential_attachment":
        return [s for _, _, s in nx.preferential_attachment(g, pairs)]
    raise ValueError(model)


def _node2vec_embeddings(g: nx.Graph, seed: int) -> dict:
    n2v = Node2Vec(
        g, dimensions=32, walk_length=15, num_walks=10, workers=1, seed=seed, quiet=True
    )
    model = n2v.fit(window=5, min_count=1, seed=seed)
    return {node: model.wv[str(node)] for node in g.nodes() if str(node) in model.wv}


def _hadamard(embeddings: dict, a: str, b: str) -> np.ndarray | None:
    if a not in embeddings or b not in embeddings:
        return None
    return embeddings[a] * embeddings[b]


def evaluate_model(
    model: str,
    train_g: nx.Graph,
    test_positive: list[tuple[str, str]],
    negatives: list[tuple[str, str]],
    embeddings: dict | None = None,
    classifier=None,
) -> dict:
    pairs = test_positive + negatives
    labels = [1] * len(test_positive) + [0] * len(negatives)

    if model in HEURISTICS:
        scores = _heuristic_scores(train_g, pairs, model)
    else:
        vecs, valid_labels, valid_idx = [], [], []
        for i, (a, b) in enumerate(pairs):
            h = _hadamard(embeddings, a, b)
            if h is not None:
                vecs.append(h)
                valid_labels.append(labels[i])
                valid_idx.append(i)
        if len(set(valid_labels)) < 2 or not vecs:
            scores = [0.0] * len(pairs)
        else:
            proba = classifier.predict_proba(np.array(vecs))[:, 1]
            scores = [0.0] * len(pairs)
            for idx, p in zip(valid_idx, proba):
                scores[idx] = p

    auc = roc_auc_score(labels, scores) if len(set(labels)) > 1 else 0.5
    ap = average_precision_score(labels, scores)
    ranked = sorted(zip(scores, labels), key=lambda x: -x[0])
    precision_at_k = {}
    for k in (50, 100, 500):
        top_k = ranked[:k]
        precision_at_k[str(k)] = sum(label for _, label in top_k) / len(top_k) if top_k else 0.0

    return {"auc": auc, "ap": ap, "precision_at_k": precision_at_k}


def run() -> dict:
    rows = parse_cross_references()
    g = build_ego_network(rows)
    train_g, test_edges = split_train_test(g, seed=config.SEED)

    results = []
    embeddings = _node2vec_embeddings(train_g, seed=config.SEED)
    train_vecs, train_labels = [], []
    train_negatives = sample_negatives(train_g, list(train_g.edges()), "random", config.SEED)
    for a, b in list(train_g.edges())[: len(train_negatives)]:
        h = _hadamard(embeddings, a, b)
        if h is not None:
            train_vecs.append(h)
            train_labels.append(1)
    for a, b in train_negatives:
        h = _hadamard(embeddings, a, b)
        if h is not None:
            train_vecs.append(h)
            train_labels.append(0)

    classifiers = {}
    if len(set(train_labels)) > 1:
        classifiers["node2vec_lr"] = LogisticRegression(max_iter=1000).fit(train_vecs, train_labels)
        classifiers["node2vec_gbm"] = GradientBoostingClassifier(random_state=config.SEED).fit(
            train_vecs, train_labels
        )

    for strategy in NEGATIVE_STRATEGIES:
        negatives = sample_negatives(g, test_edges, strategy, config.SEED)
        for model in ALL_MODELS:
            clf = classifiers.get(model)
            if model in LEARNED_MODELS and clf is None:
                continue
            metrics = evaluate_model(
                model, train_g, test_edges, negatives, embeddings=embeddings, classifier=clf
            )
            results.append({
                "model": model,
                "negative_sampling": strategy,
                "auc": metrics["auc"],
                "ap": metrics["ap"],
                "precision_at_k": metrics["precision_at_k"],
            })

    top_candidates = _top_candidates(g, train_g, embeddings, classifiers.get("node2vec_lr"))

    n_nodes = g.number_of_nodes()
    n_edges = g.number_of_edges()
    density = (2 * n_edges) / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0.0

    return {
        "graph_stats": {"nodes": n_nodes, "edges": n_edges, "density": density},
        "results": results,
        "top_candidates": top_candidates,
    }


def _top_candidates(
    g: nx.Graph, train_g: nx.Graph, embeddings: dict, classifier, limit: int = 100
) -> list[dict]:
    if classifier is None:
        return []
    acts_nodes = [n for n in g.nodes() if str(n).startswith("Acts.")]
    scored = []
    rng = random.Random(config.SEED)
    sample_targets = rng.sample(list(g.nodes()), min(300, g.number_of_nodes()))
    for a in acts_nodes[:100]:
        for b in sample_targets:
            if a == b or g.has_edge(a, b):
                continue
            h = _hadamard(embeddings, a, b)
            if h is None:
                continue
            score = float(classifier.predict_proba(h.reshape(1, -1))[0, 1])
            scored.append((score, a, b))
    scored.sort(key=lambda x: -x[0])
    return [
        {"from": a, "to": b, "score": score, "in_catalog": g.has_edge(a, b)}
        for score, a, b in scored[:limit]
    ]


def main() -> None:
    result = run()
    print(f"  Rede ego de Atos: {result['graph_stats']['nodes']} nós, "
          f"{result['graph_stats']['edges']} arestas (densidade {result['graph_stats']['density']:.5f})")
    for r in result["results"]:
        print(f"  {r['model']:25s} {r['negative_sampling']:16s} AUC={r['auc']:.3f} AP={r['ap']:.3f}")


if __name__ == "__main__":
    main()
