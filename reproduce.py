"""Bounded public reproducer for the frozen concept-projection experiment."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "study" / "original"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
SEED = 20260911
NUMERIC_TOLERANCE = 1e-9


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_experiment():
    spec = importlib.util.spec_from_file_location("frozen_public_experiment", SOURCE / "experiment.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen experiment")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _guard_output(output: Path) -> Path:
    output = output.expanduser().resolve()
    protected_trees = [ROOT / "study", ROOT / "docs", ROOT / "data"]
    if output == ROOT or any(output == path.resolve() or path.resolve() in output.parents for path in protected_trees):
        raise ValueError(f"output must be outside protected source paths: {output}")
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise FileExistsError(f"output already exists and is not empty: {output}")
    return output


def _verify_public_source() -> int:
    manifest = json.loads((SOURCE / "verification.json").read_text())
    hashes = manifest.get("sha256", {})
    if len(hashes) != 194:
        raise RuntimeError(f"public verification must enumerate 194 artifacts, found {len(hashes)}")
    for relative, expected in hashes.items():
        path = SOURCE / relative
        if not path.is_file() or _sha256(path) != expected:
            raise RuntimeError(f"public source artifact failed SHA-256 verification: {relative}")
    return len(hashes)


def _verify_saved_vectors(module) -> tuple[np.ndarray, list[int]]:
    vector_path = SOURCE / "results" / "main_vectors.npz"
    verification = json.loads((SOURCE / "verification.json").read_text())
    expected_hash = verification["sha256"]["results/main_vectors.npz"]
    if _sha256(vector_path) != expected_hash:
        raise RuntimeError("saved embedding artifact failed its published SHA-256 check")
    rows, _ = module.read_data()
    expected_ids = np.array(
        [r["id"] + "_" + key for r in rows.to_dict("records") for key in ("A", "B", "C")]
    )
    with np.load(vector_path, allow_pickle=False) as saved:
        if not np.array_equal(saved["ids"], expected_ids):
            raise RuntimeError("saved embedding identifiers do not match the frozen corpus")
        vectors = np.asarray(saved["embedding"], dtype=np.float64)
    if vectors.shape != (720, 384) or not np.isfinite(vectors).all():
        raise RuntimeError("saved embeddings have invalid shape or values")
    lengths = json.loads((SOURCE / "results" / "environment.json").read_text())["token_lengths"]
    if len(lengths) != 720 or max(lengths) > 128:
        raise RuntimeError("saved token-length provenance is invalid")
    return vectors, lengths


def _fresh_encoder() -> Callable[[list[str]], tuple[np.ndarray, list[int]]]:
    import torch
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    model = SentenceTransformer(MODEL, revision=REVISION, device="cpu")
    model.max_seq_length = 128

    def encode(texts: list[str]) -> tuple[np.ndarray, list[int]]:
        lengths = [len(x) for x in model.tokenizer(texts, truncation=False)["input_ids"]]
        if max(lengths) > 128:
            raise RuntimeError(f"input would be silently truncated (maximum {max(lengths)} tokens)")
        vectors = model.encode(
            texts, batch_size=32, normalize_embeddings=False,
            show_progress_bar=False, convert_to_numpy=True,
        )
        return _unit(vectors), lengths

    return encode


def _unit(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    lengths = np.linalg.norm(values, axis=-1, keepdims=True)
    if np.any(lengths <= 1e-12):
        raise RuntimeError("cannot normalize a zero vector")
    return values / lengths


def _regenerate_anchors(encode: Callable[[list[str]], tuple[np.ndarray, list[int]]]):
    source_path = ROOT / "data" / "bhatia" / "attributes.csv"
    frame = pd.read_csv(source_path, encoding="cp1252")
    if len(frame) != 414 or frame.Name.nunique() != 207:
        raise RuntimeError("Bhatia attributes must contain 414 directional rows and 207 names")
    pro_names = frame[frame.Direction.eq("pro")].Name.tolist()
    con_names = frame[frame.Direction.eq("con")].Name.tolist()
    if pro_names != con_names:
        raise RuntimeError("pro/con attribute ordering differs")
    with np.load(SOURCE / "data" / "anchors_multi.npz", allow_pickle=False) as saved_bank:
        if pro_names != saved_bank["names"].tolist():
            raise RuntimeError("Bhatia attribute ordering differs from the frozen anchor bank")
    phrases = [
        [piece.strip().rstrip(".").strip() for piece in text.split(";") if piece.strip()]
        for text in frame.Sentences
    ]
    flat = [phrase for group in phrases for phrase in group]
    vectors, lengths = encode(flat)
    edges = np.r_[0, np.cumsum([len(group) for group in phrases])]
    directional = _unit(np.stack([vectors[edges[i]:edges[i + 1]].mean(0) for i in range(414)]))
    anchors = _unit(directional[frame.Direction.eq("pro")] + directional[frame.Direction.eq("con")])
    if anchors.shape != (207, 384):
        raise RuntimeError("fresh anchors have an invalid shape")
    return anchors, {"attribute_names": pro_names, "n_anchor_phrases": len(flat), "max_anchor_tokens": max(lengths)}


def _comparison(output: Path, mode: str) -> dict:
    source_results = SOURCE / "results"
    files = sorted(p.name for p in source_results.glob("*.csv"))
    comparisons, max_error = {}, 0.0
    primary_preferences_match = True
    for name in files:
        expected = pd.read_csv(source_results / name)
        actual = pd.read_csv(output / name)
        if list(actual.columns) != list(expected.columns) or actual.shape != expected.shape:
            raise RuntimeError(f"{name} schema or row count differs from the frozen result")
        numeric = expected.select_dtypes(include="number").columns
        error = float(np.nanmax(np.abs(actual[numeric].to_numpy() - expected[numeric].to_numpy()))) if len(numeric) else 0.0
        exact_columns = [column for column in expected.columns if column not in numeric]
        exact = all(actual[c].fillna("<NA>").equals(expected[c].fillna("<NA>")) for c in exact_columns)
        comparisons[name] = {"rows": len(actual), "numeric_max_abs_error": error, "nonnumeric_exact": exact}
        max_error = max(max_error, error)
        if name == "per_triplet.csv":
            primary_preferences_match = bool(np.array_equal(actual["score"].to_numpy(), expected["score"].to_numpy()))
        if not exact:
            raise RuntimeError(f"categorical values or identifiers differ in {name}")
        if mode == "cached" and (error > NUMERIC_TOLERANCE or not exact):
            raise RuntimeError(f"cached reproduction differs in {name}: max error {error:g}, exact={exact}")
    if not primary_preferences_match:
        raise RuntimeError("primary preference outcomes differ from the frozen experiment")
    return {
        "mode": mode,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "study/original",
        "numeric_tolerance": NUMERIC_TOLERANCE if mode == "cached" else None,
        "numeric_max_abs_error": max_error,
        "primary_preferences_exact": primary_preferences_match,
        "main_rows": comparisons["per_triplet.csv"]["rows"],
        "random_rows": comparisons["random_per_triplet.csv"]["rows"],
        "bootstrap_intervals": comparisons["intervals.csv"]["rows"],
        "files": comparisons,
    }


def run(mode: str, output: str | Path) -> Path:
    if mode not in {"cached", "full"}:
        raise ValueError("mode must be 'cached' or 'full'")
    destination = _guard_output(Path(output))
    verified_artifacts = _verify_public_source()
    module = _load_experiment()
    module.verify_freeze()
    provenance: dict = {"model": MODEL, "revision": REVISION, "device": "cpu", "seed": SEED}
    restore_version = None
    fresh_anchors = None
    with tempfile.TemporaryDirectory(prefix="dilemma-reproduce-") as temporary:
        if mode == "cached":
            vectors, lengths = _verify_saved_vectors(module)
            module.encode = lambda texts: (vectors.copy(), list(lengths))
            real_version = module.importlib.metadata.version
            restore_version = real_version
            def available_version(package):
                try:
                    return real_version(package)
                except module.importlib.metadata.PackageNotFoundError:
                    return "not-installed (not required for cached mode)"
            module.importlib.metadata.version = available_version
            provenance.update(embedding_source="study/original/results/main_vectors.npz", anchors_source="study/original/data/anchors_multi.npz")
        else:
            encode = _fresh_encoder()
            anchors, anchor_info = _regenerate_anchors(encode)
            fresh_anchors = anchors
            scratch_data = Path(temporary) / "data"
            shutil.copytree(SOURCE / "data", scratch_data)
            np.savez_compressed(scratch_data / "anchors_multi.npz", anchors=anchors)
            original_verify = module.verify_freeze
            def verified_then_switch():
                module.DATA = SOURCE / "data"
                result = original_verify()
                module.DATA = scratch_data
                return result
            module.verify_freeze = verified_then_switch
            module.encode = encode
            provenance.update(embedding_source="fresh_model_inference", anchors_source="fresh_bhatia_phrase_inference", **anchor_info)
        destination.mkdir(parents=True, exist_ok=True)
        if fresh_anchors is not None:
            np.savez_compressed(destination / "anchors_multi.npz", anchors=fresh_anchors, names=np.asarray(provenance["attribute_names"]))
        module.RESULTS = destination
        try:
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                module.run()
            action = "Recomputing from saved embeddings and fixed anchors." if mode == "cached" else "Freshly encoded 720 texts and regenerated 207 anchors."
            print(action, flush=True)
            lines = captured.getvalue().splitlines()
            if lines and lines[0].startswith("Encoding 720 English paragraphs"):
                lines = lines[1:]
            if lines:
                print("\n".join(lines), flush=True)
        finally:
            if restore_version is not None:
                module.importlib.metadata.version = restore_version
    if fresh_anchors is not None:
        with np.load(SOURCE / "data" / "anchors_multi.npz", allow_pickle=False) as reference_anchors:
            provenance["anchors_max_abs_error_vs_reference"] = float(np.max(np.abs(fresh_anchors - reference_anchors["anchors"])))
        with np.load(destination / "main_vectors.npz", allow_pickle=False) as fresh_vectors, np.load(SOURCE / "results" / "main_vectors.npz", allow_pickle=False) as reference_vectors:
            provenance["text_embeddings_max_abs_error_vs_reference"] = float(np.max(np.abs(fresh_vectors["embedding"] - reference_vectors["embedding"])))
    verification = _comparison(destination, mode)
    verification["public_source_artifacts_verified"] = verified_artifacts
    verification["provenance"] = provenance
    (destination / "verification.json").write_text(json.dumps(verification, indent=2, ensure_ascii=False) + "\n")
    return destination / "verification.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("cached", "full"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.mode, args.output)
    try:
        print(result.relative_to(ROOT))
    except ValueError:
        print(result.name)


if __name__ == "__main__":
    main()
