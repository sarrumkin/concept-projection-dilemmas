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
