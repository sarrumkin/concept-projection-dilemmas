"""Mathematical and corpus-label checks for exploratory retrieval nDCG."""

import itertools

import numpy as np
import pandas as pd
import pytest

import ndcg


@pytest.mark.parametrize(
    "relevance,scores,k,expected",
    [
        ([1, 0], [0.9, 0.2], 2, 1.0),
        ([1, 0], [0.2, 0.9], 2, 1 / np.log2(3)),
        ([1, 0], [0.4, 0.4], 2, (1 + 1 / np.log2(3)) / 2),
        ([1, 0], [0.4, 0.4], 1, 0.5),
        ([0, 0], [0.9, 0.2], 2, 0.0),
        ([1, 1], [-0.9, -0.2], 2, 1.0),
        ([1, 0], [0.2, 0.9], 20, 1 / np.log2(3)),
    ],
)
def test_binary_ndcg_known_rankings(relevance, scores, k, expected):
    assert ndcg.binary_ndcg(np.asarray(relevance), np.asarray(scores), k) == pytest.approx(expected)


def test_tie_crossing_cutoff_equals_mean_over_every_tie_permutation():
    relevance = np.array([1, 0, 1, 0, 1])
    scores = np.array([0.9, 0.7, 0.7, 0.7, 0.1])
    discounts = 1 / np.log2(np.arange(2, 5))
    ideal = discounts.sum()
    expected = np.mean([
        relevance[[0, *permutation, 4]][:3] @ discounts / ideal
        for permutation in itertools.permutations([1, 2, 3])
    ])
    assert ndcg.binary_ndcg(relevance, scores, 3) == pytest.approx(expected)
    permutation = np.array([3, 0, 4, 2, 1])
    assert ndcg.binary_ndcg(relevance[permutation], scores[permutation], 3) == pytest.approx(expected)


def test_all_tied_scores_use_relevance_from_entire_tie_group():
    relevance = np.array([1, 0, 0, 1, 0])
    # At k=2 the ideal is two relevant items; random tie order has mean gain 2/5.
    assert ndcg.binary_ndcg(relevance, np.ones(5), 2) == pytest.approx(2 / 5)


@pytest.mark.parametrize(
    "relevance,scores,k",
    [
        ([], [], 1),
        ([1, 0], [1], 1),
        ([[1, 0]], [[0.9, 0.1]], 1),
        ([1, 0], [[0.9, 0.1]], 1),
        ([1, 0.5], [0.9, 0.1], 1),
        ([-1, 0], [0.9, 0.1], 1),
        ([2, 0], [0.9, 0.1], 1),
        ([np.nan, 0], [0.9, 0.1], 1),
        ([1, 0], [np.inf, 0.1], 1),
        ([1, 0], [np.nan, 0.1], 1),
        ([1, 0], [0.9, 0.1], 0),
        ([1, 0], [0.9, 0.1], -1),
        ([1, 0], [0.9, 0.1], 1.5),
        ([1, 0], [0.9, 0.1], True),
    ],
)
def test_binary_ndcg_rejects_invalid_inputs(relevance, scores, k):
    with pytest.raises(ValueError):
        ndcg.binary_ndcg(np.asarray(relevance), np.asarray(scores), k)


@pytest.fixture
def tiny_corpus():
    rows = pd.DataFrame([
        dict(id="q1", conflict="alpha", negative_conflict="beta",
             anchor_topic="one", positive_topic="two", variant=0, author=0),
        dict(id="q2", conflict="beta", negative_conflict="alpha",
             anchor_topic="two", positive_topic="one", variant=0, author=1),
    ])
    ids = np.array([f"{identifier}_{role}" for identifier in rows.id for role in "ABC"])
    # q1: C is the strongest distractor; q2_C is relevant through negative_conflict.
    vectors = np.array([[1., 0.], [-1., 0.], [1., 0.],
                        [0., 1.], [0.8, 0.6], [0.9, 0.1]])
    return rows, ids, vectors


def test_retrieval_uses_a_queries_excludes_self_and_maps_candidate_labels(tiny_corpus):
    rows, ids, vectors = tiny_corpus
    per_query, summary = ndcg.evaluate_retrieval(rows, ids, {"example": vectors}, cutoffs=(1, 2))
    per_query = per_query.set_index("id")
    assert set(per_query.index) == {"q1", "q2"}
    assert per_query["method"].eq("example").all()
    assert per_query["n_candidates"].eq(5).all()
    assert per_query["n_relevant"].eq(2).all()
    assert per_query.loc["q1", "conflict"] == "alpha"
    assert per_query.loc["q1", "anchor_topic"] == "one"
    assert per_query.loc["q1", "ndcg_at_1"] == 0
    assert per_query.loc["q2", "ndcg_at_1"] == 1
    discount = 1 / np.log2(3)
    assert per_query.loc["q1", "ndcg_at_2"] == pytest.approx(discount / (1 + discount))
    assert per_query.loc["q2", "ndcg_at_2"] == pytest.approx(1 / (1 + discount))
    assert summary.set_index("method").loc["example", "n_queries"] == 2
    assert summary.set_index("method").loc["example", "ndcg_at_1"] == pytest.approx(0.5)
    assert summary.set_index("method").loc["example", "ndcg_at_2"] == pytest.approx(0.5)


def test_retrieval_ranks_cosine_not_unnormalized_dot_products(tiny_corpus):
    rows, ids, vectors = tiny_corpus
    scaled = vectors * np.array([2, 11, 0.2, 7, 0.01, 50])[:, None]
    per_query, summary = ndcg.evaluate_retrieval(
        rows, ids, {"original": vectors, "scaled": scaled}, cutoffs=(1, 2, 20),
    )
    metrics = ["ndcg_at_1", "ndcg_at_2", "ndcg_at_20"]
    indexed = per_query.set_index(["method", "id"])
    np.testing.assert_allclose(indexed.loc["original", metrics], indexed.loc["scaled", metrics])
    indexed_summary = summary.set_index("method")
    np.testing.assert_allclose(indexed_summary.loc["original", metrics], indexed_summary.loc["scaled", metrics])


def test_retrieval_rejects_vector_ids_in_wrong_order(tiny_corpus):
    rows, ids, vectors = tiny_corpus
    swapped = ids.copy()
    swapped[[0, 1]] = swapped[[1, 0]]
    with pytest.raises(ValueError):
        ndcg.evaluate_retrieval(rows, swapped, {"example": vectors})


@pytest.mark.parametrize("invalid", ["missing_row", "zero_vector", "nan", "infinity", "one_dimension"])
def test_retrieval_rejects_invalid_representations(tiny_corpus, invalid):
    rows, ids, vectors = tiny_corpus
    vectors = vectors.copy()
    if invalid == "missing_row":
        vectors = vectors[:-1]
    elif invalid == "zero_vector":
        vectors[0] = 0
    elif invalid == "nan":
        vectors[0, 0] = np.nan
    elif invalid == "infinity":
        vectors[0, 0] = np.inf
    else:
        vectors = vectors[:, 0]
    with pytest.raises(ValueError):
        ndcg.evaluate_retrieval(rows, ids, {"example": vectors})
