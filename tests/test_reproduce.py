import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import reproduce


def test_output_guard_rejects_protected_and_nonempty_paths(tmp_path):
    with pytest.raises(ValueError):
        reproduce._guard_output(reproduce.ROOT / "study" / "generated")
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep.txt").write_text("user data")
    with pytest.raises(FileExistsError):
        reproduce._guard_output(occupied)
    assert reproduce._guard_output(reproduce.ROOT / "artifacts" / "new") == (reproduce.ROOT / "artifacts" / "new").resolve()


def test_cached_reproduction_computes_expected_scientific_outputs(tmp_path):
    verification_path = reproduce.run("cached", tmp_path / "cached")
    verification = json.loads(verification_path.read_text())
    summary = pd.read_csv(verification_path.parent / "summary.csv").set_index("method")
    assert verification["main_rows"] == 720
    assert verification["random_rows"] == 28800
    assert verification["bootstrap_intervals"] == 18
    assert verification["primary_preferences_exact"] is True
    assert verification["numeric_max_abs_error"] <= 1e-9
    assert summary.loc["concept207", "correct_score"] == 145
    assert summary.loc["concept207", "n_triplets"] == 240
    assert summary.loc["hybrid50", "accuracy"] >= summary.loc["embedding", "accuracy"]
    retrieval = pd.read_csv(verification_path.parent / "retrieval_per_query.csv")
    ranking_summary = pd.read_csv(verification_path.parent / "retrieval_summary.csv").set_index("method")
    assert len(retrieval) == 720
    assert not retrieval.duplicated(["id", "method"]).any()
    assert retrieval.n_candidates.eq(719).all()
    assert retrieval.n_relevant.eq(59).all()
    assert ranking_summary.n_queries.eq(240).all()
    assert verification["exploratory_retrieval"]["frozen_reference_comparison"] is False
    # Independently computed from all-pairs cosine ranking and binary labels.
    assert ranking_summary.loc["embedding", "ndcg_at_5"] == pytest.approx(0.6167957864916223)
    assert ranking_summary.loc["concept207", "ndcg_at_10"] == pytest.approx(0.5457676170142596)
    assert ranking_summary.loc["hybrid50", "ndcg_at_10"] == pytest.approx(0.6098630930061627)
    for metric in ["ndcg_at_5", "ndcg_at_10"]:
        assert retrieval[metric].between(0, 1).all()
        pd.testing.assert_series_equal(
            ranking_summary[metric], retrieval.groupby("method")[metric].mean(),
            check_exact=False, atol=1e-11, rtol=0,
        )


def test_saved_embedding_corruption_is_detected(monkeypatch, tmp_path):
    module = reproduce._load_experiment()
    corrupt = tmp_path / "main_vectors.npz"
    corrupt.write_bytes((reproduce.SOURCE / "results" / "main_vectors.npz").read_bytes() + b"corrupt")
    original_sha = reproduce._sha256
    monkeypatch.setattr(reproduce, "_sha256", lambda path: original_sha(corrupt) if path.name == "main_vectors.npz" else original_sha(path))
    with pytest.raises(RuntimeError, match="SHA-256"):
        reproduce._verify_saved_vectors(module)


def test_full_mode_uses_fresh_encoder_for_texts_and_anchors(monkeypatch, tmp_path):
    calls = []
    rng = np.random.default_rng(4)
    def fake_encoder():
        def encode(texts):
            calls.append(len(texts))
            return reproduce._unit(rng.standard_normal((len(texts), 384))), [8] * len(texts)
        return encode
    monkeypatch.setattr(reproduce, "_fresh_encoder", fake_encoder)
    monkeypatch.setattr(reproduce, "_comparison", lambda output, mode: {"mode": mode})
    real_version = reproduce.importlib.metadata.version
    monkeypatch.setattr(reproduce.importlib.metadata, "version", lambda package: "test-double" if package in {"sentence-transformers", "torch", "transformers"} else real_version(package))
    reproduce.run("full", tmp_path / "full")
    assert calls[0] > 414
    assert 720 in calls
    provenance = json.loads((tmp_path / "full" / "verification.json").read_text())["provenance"]
    assert provenance["embedding_source"] == "fresh_model_inference"
    assert provenance["anchors_source"] == "fresh_bhatia_phrase_inference"
    with np.load(tmp_path / "full" / "anchors_multi.npz", allow_pickle=False) as anchors:
        assert anchors["anchors"].shape == (207, 384)
        assert len(anchors["names"]) == 207
    with np.load(tmp_path / "full" / "main_vectors.npz", allow_pickle=False) as vectors:
        rows, _ = reproduce._load_experiment().read_data()
        _, expected = reproduce.evaluate_retrieval(
            rows, vectors["ids"], {method: vectors[method] for method in ["embedding", "concept207", "hybrid50"]},
        )
    actual = pd.read_csv(tmp_path / "full" / "retrieval_summary.csv")
    pd.testing.assert_frame_equal(actual, expected, check_exact=False, atol=1e-11, rtol=0)
