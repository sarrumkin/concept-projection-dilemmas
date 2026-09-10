"""Exploratory conflict retrieval over the frozen corpus, outside its protocol."""
from __future__ import annotations

import numpy as np
import pandas as pd


def binary_ndcg(relevance: np.ndarray, scores: np.ndarray, k: int) -> float:
    """nDCG@k for one query; higher scores rank first, exact ties are averaged.

    Every permutation within a tied score group is equally likely, including
    groups crossing k. No relevant candidates yields zero; k is capped at the
    candidate count. Binary gains equal both rel and 2**rel - 1.
    """
    relevance = np.asarray(relevance, dtype=np.float64)
    scores = np.asarray(scores, dtype=np.float64)
    if relevance.ndim != 1 or scores.shape != relevance.shape or not relevance.size:
        raise ValueError("relevance and scores must be matching nonempty 1D arrays")
    if not np.isfinite(scores).all() or not np.isin(relevance, [0, 1]).all():
        raise ValueError("scores must be finite and relevance must be binary")
    if isinstance(k, (bool, np.bool_)) or not isinstance(k, (int, np.integer)) or k < 1:
        raise ValueError("k must be a positive integer")
    limit = min(k, relevance.size)
    discount = 1 / np.log2(np.arange(2, relevance.size + 2))
    ideal = discount[:min(limit, int(relevance.sum()))].sum()
    if ideal == 0:
        return 0.0

    order = np.argsort(-scores, kind="stable")
    sorted_scores, gains = scores[order], relevance[order]
    starts = np.r_[0, np.flatnonzero(sorted_scores[1:] != sorted_scores[:-1]) + 1]
    counts = np.diff(np.r_[starts, relevance.size])
    mean_gains = np.add.reduceat(gains, starts) / counts
    expected_gains = np.repeat(mean_gains, counts)
    return float(expected_gains[:limit] @ discount[:limit] / ideal)


def evaluate_retrieval(
    rows: pd.DataFrame,
    ids: np.ndarray,
    representations: dict[str, np.ndarray],
    cutoffs: tuple[int, ...] = (5, 10),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rank all other corpus texts for each A using authored conflict labels.

    rows and vector IDs must agree in triplet/A/B/C order. C carries the
    negative_conflict label; it can be relevant to queries from other triplets.
    Topics do not filter candidates. Each query receives equal summary weight.
    """
    required = ["id", "conflict", "negative_conflict", "anchor_topic"]
    if rows.empty or rows[required].isna().any().any() or not rows.id.is_unique:
        raise ValueError("retrieval requires nonempty, uniquely identified, labeled triplets")
    if not cutoffs or len(set(cutoffs)) != len(cutoffs):
        raise ValueError("cutoffs must be nonempty and unique")
    if not representations:
        raise ValueError("at least one representation is required")
    records = rows.to_dict("records")
    expected_ids = np.array([row["id"] + "_" + role for row in records for role in ("A", "B", "C")])
    if not np.array_equal(ids, expected_ids):
        raise ValueError("retrieval vector identifiers do not match triplet/A/B/C order")
    conflicts = np.array([
        label for row in records
        for label in (row["conflict"], row["conflict"], row["negative_conflict"])
    ])
    indices = np.arange(len(ids))
    results = []
    for method, vectors in representations.items():
        vectors = np.asarray(vectors, dtype=np.float64)
        if vectors.ndim != 2 or vectors.shape[0] != len(ids) or not np.isfinite(vectors).all():
            raise ValueError(f"invalid retrieval vectors for {method}")
        lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
        if np.any(lengths <= 1e-12) or not np.isfinite(lengths).all():
            raise ValueError(f"invalid retrieval vector norms for {method}")
        unit = vectors / lengths
        similarities = unit[::3] @ unit.T
        for query, row in enumerate(records):
            candidates = indices != 3 * query
            relevance = conflicts[candidates] == row["conflict"]
            result = {
                "id": row["id"], "method": method,
                "conflict": row["conflict"], "anchor_topic": row["anchor_topic"],
                "n_candidates": int(candidates.sum()), "n_relevant": int(relevance.sum()),
            }
            for k in cutoffs:
                result[f"ndcg_at_{k}"] = binary_ndcg(relevance, similarities[query, candidates], k)
            results.append(result)
    per_query = pd.DataFrame(results)
    summary = per_query.groupby("method", as_index=False).agg(
        n_queries=("id", "size"),
        **{f"ndcg_at_{k}": (f"ndcg_at_{k}", "mean") for k in cutoffs},
    )
    return per_query, summary
