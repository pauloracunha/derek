"""Gera curvas ROC dos 6 modelos de link prediction sob as 2 estratégias de
amostragem negativa (random, distance_matched). Reexecuta s07_linkpred para
capturar scores/labels brutos (linkpred.json guarda só AUC/AP agregados).

Uso: uv run python scripts/plot_roc_linkpred.py
Saída: docs/figures/roc_linkpred.png
"""

import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve

from pathlib import Path

from pipeline import config, s07_linkpred as lp


def _scores_and_labels(model, train_g, test_positive, negatives, embeddings=None, classifier=None):
    pairs = test_positive + negatives
    labels = [1] * len(test_positive) + [0] * len(negatives)

    if model in lp.HEURISTICS:
        scores = lp._heuristic_scores(train_g, pairs, model)
        return scores, labels

    vecs, valid_labels, valid_idx = [], [], []
    for i, (a, b) in enumerate(pairs):
        h = lp._hadamard(embeddings, a, b)
        if h is not None:
            vecs.append(h)
            valid_labels.append(labels[i])
            valid_idx.append(i)
    scores = [0.0] * len(pairs)
    if len(set(valid_labels)) >= 2 and vecs:
        import numpy as np
        proba = classifier.predict_proba(np.array(vecs))[:, 1]
        for idx, p in zip(valid_idx, proba):
            scores[idx] = p
    return scores, labels


def main():
    rows = lp.parse_cross_references()
    g = lp.build_ego_network(rows)
    train_g, test_edges = lp.split_train_test(g, seed=config.SEED)

    embeddings = lp._node2vec_embeddings(train_g, seed=config.SEED)
    train_vecs, train_labels = [], []
    train_negatives = lp.sample_negatives(train_g, list(train_g.edges()), "random", config.SEED)
    for a, b in list(train_g.edges())[: len(train_negatives)]:
        h = lp._hadamard(embeddings, a, b)
        if h is not None:
            train_vecs.append(h)
            train_labels.append(1)
    for a, b in train_negatives:
        h = lp._hadamard(embeddings, a, b)
        if h is not None:
            train_vecs.append(h)
            train_labels.append(0)

    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression

    classifiers = {
        "node2vec_lr": LogisticRegression(max_iter=1000).fit(train_vecs, train_labels),
        "node2vec_gbm": GradientBoostingClassifier(random_state=config.SEED).fit(train_vecs, train_labels),
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    colors = plt.cm.tab10.colors

    for ax, strategy in zip(axes, lp.NEGATIVE_STRATEGIES):
        negatives = lp.sample_negatives(g, test_edges, strategy, config.SEED)
        for i, model in enumerate(lp.ALL_MODELS):
            clf = classifiers.get(model)
            if model in lp.LEARNED_MODELS and clf is None:
                continue
            scores, labels = _scores_and_labels(
                model, train_g, test_edges, negatives, embeddings=embeddings, classifier=clf
            )
            fpr, tpr, _ = roc_curve(labels, scores)
            auc = roc_auc_score(labels, scores)
            ax.plot(fpr, tpr, color=colors[i % 10], label=f"{model} (AUC={auc:.3f})")
        ax.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
        ax.set_title(f"Amostragem negativa: {strategy}")
        ax.set_xlabel("Taxa de falsos positivos")
        ax.legend(fontsize=8, loc="lower right")

    axes[0].set_ylabel("Taxa de verdadeiros positivos")
    fig.suptitle("Curvas ROC — predição de links (rede ego de Atos)")
    fig.tight_layout()

    out_dir = Path("docs") / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "roc_linkpred.png"
    fig.savefig(out_path, dpi=150)
    print(f"Salvo em {out_path}")


if __name__ == "__main__":
    main()
