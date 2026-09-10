#!/usr/bin/env python3
"""Independent numeric audit for the concept_layers_large_en study.

This module intentionally does not import the study's experiment module.  It
only consumes a saved study package (data/ and results/) and needs numpy,
pandas, and scipy.  It writes numeric_audit.json and numeric_audit.md beside
itself, unless --output-dir is supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine

SEED = 20260911
LABELS = [
    "ambition_vs_belonging", "security_vs_care", "health_vs_duty",
    "freedom_vs_safety", "truth_vs_loyalty", "discipline_vs_comfort",
    "autonomy_vs_approval", "change_vs_tradition", "fairness_vs_mercy",
    "privacy_vs_openness", "quality_vs_speed", "personal_gain_vs_collective_impact",
]
METHODS = ["embedding", "concept207", "hybrid50"]
CONTRASTS = [("hybrid50", "embedding"), ("concept207", "embedding"),
             ("hybrid50", "concept207")]
TOL = 1e-10
NUMERIC_ERRORS = {}


def fail(msg: str):
    raise AssertionError(msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b, msg, tol=TOL):
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    err = float(np.nanmax(np.abs(aa - bb))) if aa.size else 0.0
    NUMERIC_ERRORS[msg] = max(NUMERIC_ERRORS.get(msg, 0.0), err)
    check(np.allclose(aa, bb, atol=tol, rtol=0), f"{msg}: max abs error {err:.3g}")
    return err


def load_json(path):
    return json.loads(Path(path).read_text())


def normalized(x):
    x = np.asarray(x, dtype=float)
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    check(np.all(n > 1e-12), "zero vector")
    return x / n


def score_rows(vectors, ids):
    """Reference implementation: scipy cosine for every AB and AC pair."""
    v = normalized(vectors).reshape(-1, 3, vectors.shape[-1])
    rows = []
    for i, (a, b, c) in enumerate(v):
        dab = cosine(a, b)
        dac = cosine(a, c)
        margin = dac - dab
        rows.append({"id": ids[i], "d_same_conflict": dab,
                     "d_same_topic": dac, "margin": margin,
                     "score": float(margin > 0) + .5 * float(margin == 0)})
    return pd.DataFrame(rows)


def read_main_data(base: Path):
    data = base / "data"
    trips = pd.DataFrame(load_json(data / "triplets.json")).sort_values("id").reset_index(drop=True)
    check(len(trips) == 240 and trips.id.is_unique, "triplet count/id uniqueness")
    check(set(trips.conflict) == set(LABELS), "conflict labels")
    topics = load_json(data / "domains.json")
    check(len(topics) == 10 and len(set(topics)) == 10, "topic list")
    check(trips.groupby(["conflict", "anchor_topic"]).size().eq(2).all(), "12x10x2 balance")
    check(trips.groupby(["author", "conflict"]).size().eq(5).all(), "author/conflict balance")
    check(trips.groupby(["author", "anchor_topic"]).size().eq(6).all(), "author/topic balance")
    texts = [r[k] for r in trips.to_dict("records") for k in ("A", "B", "C")]
    check(len(texts) == len(set(texts)) == 720, "unique texts")
    for i in (1, 2):
        audit = pd.DataFrame(load_json(data / f"audit_labels_{i}.json")).set_index("id")
        key = load_json(data / f"audit_key_{i}.json")
        check(len(audit) == 240 and set(audit.index) == set(trips.id), f"audit {i} ids")
        check(set(audit.choice).issubset({"X", "Y", "both", "neither"}), f"audit {i} choices")
        normalized_choice = {rid: ("B" if ch == key[rid] else "C") if ch in ("X", "Y") else ch
                             for rid, ch in audit.choice.items()}
        trips[f"audit_{i}"] = trips.id.map(normalized_choice)
        trips[f"audit_{i}_agrees"] = trips[f"audit_{i}"].eq("B")
    trips["both_audits_agree"] = trips.audit_1_agrees & trips.audit_2_agrees
    return trips, topics


def verify_manifests(base: Path):
    data = base / "data"
    checks = {"design_manifest": "ok", "frozen_manifest": "ok"}
    for name in ("design_manifest.json", "frozen_manifest.json"):
        p = data / name
        if not p.exists():
            fail(f"missing required {name}")
        manifest = load_json(p)
        errors = []
        for rel, expected in manifest.get("sha256", {}).items():
            target = base / rel
            if not target.exists():
                errors.append(f"missing:{rel}")
            elif sha(target) != expected:
                errors.append(f"hash:{rel}")
        check(not errors, f"{name}: {errors}")
    nb_manifest = data / "notebook_code_manifest.json"
    check(nb_manifest.exists(), "missing required notebook_code_manifest.json")
    nb_spec = load_json(nb_manifest)
    notebook = base / "notebooks" / nb_spec["notebook"]
    if not notebook.exists():
        notebook = base / nb_spec["notebook"]
    check(notebook.exists(), f"missing notebook {nb_spec['notebook']}")
    notebook_json = load_json(notebook)
    # nbformat commonly serializes source as a list of lines; hashing str(list)
    # would validate the JSON representation rather than the cell source.
    def source_text(cell):
        source = cell.get("source", "")
        return "".join(source) if isinstance(source, list) else source
    actual_cells = [hashlib.sha256(source_text(cell).encode()).hexdigest()
                    for cell in notebook_json.get("cells", []) if cell.get("cell_type") == "code"]
    check(actual_cells == nb_spec["code_cell_sha256"], "notebook code-cell SHA256")
    return checks


def expected_main(base: Path, trips: pd.DataFrame):
    r = base / "results"
    vec = np.load(r / "main_vectors.npz", allow_pickle=False)
    required = {"ids", "embedding", "concept207", "hybrid50"}
    check(required.issubset(vec.files), "main_vectors keys")
    ids = [str(x) for x in vec["ids"]]
    expected_ids = [rid + "_" + role for rid in trips.id for role in ("A", "B", "C")]
    check(ids == expected_ids, "main_vectors ordered ids")
    z, c, h = vec["embedding"], vec["concept207"], vec["hybrid50"]
    check(z.shape == (720, 384) and c.shape == (720, 207) and h.shape == (720, 591), "vector shapes")
    close(np.linalg.norm(z, axis=1), 1, "embedding norms")
    close(np.linalg.norm(c, axis=1), 1, "concept norms")
    close(np.linalg.norm(h, axis=1), 1, "hybrid norms")
    anchors = np.load(base / "data" / "anchors_multi.npz", allow_pickle=False)["anchors"]
    check(anchors.shape == (207, 384), "anchor shape")
    close(np.linalg.norm(anchors, axis=1), 1, "anchor norms")
    centered = anchors - anchors.mean(axis=0)
    c_expected = normalized(z @ centered.T)
    h_expected = np.concatenate((np.sqrt(.5) * z, np.sqrt(.5) * c_expected), axis=1)
    close(c, c_expected, "concept reconstruction")
    close(h, h_expected, "hybrid reconstruction")
    per = pd.read_csv(r / "per_triplet.csv")
    check(len(per) == 720 and set(per.method) == set(METHODS), "per_triplet rows/methods")
    records = []
    for method, vectors in (("embedding", z), ("concept207", c), ("hybrid50", h)):
        s = score_rows(vectors, trips.id.tolist()).assign(method=method)
        records.append(s.merge(trips.drop(columns=["A", "B", "C"]), on="id", validate="one_to_one"))
    expected = pd.concat(records, ignore_index=True)
    actual = per.sort_values(["method", "id"]).reset_index(drop=True)
    exp = expected.sort_values(["method", "id"]).reset_index(drop=True)
    for col in ("d_same_conflict", "d_same_topic", "margin", "score"):
        close(actual[col], exp[col], f"per_triplet {col}")
    for col in ("id", "method"):
        check(actual[col].tolist() == exp[col].tolist(), f"per_triplet {col}")
    metadata = ["conflict", "anchor_topic", "positive_topic", "negative_conflict",
                "variant", "author", "audit_1", "audit_2", "audit_1_agrees",
                "audit_2_agrees", "both_audits_agree"]
    for col in metadata:
        check(col in actual and col in exp, f"per_triplet missing metadata {col}")
        check(actual[col].tolist() == exp[col].tolist(), f"per_triplet {col}")
    return vec, expected, centered


def summary_tables(base, trips, expected):
    r = base / "results"
    summary = expected.groupby("method", as_index=False).agg(n_triplets=("score", "size"),
        correct_score=("score", "sum"), accuracy=("score", "mean"), mean_margin=("margin", "mean"))
    actual = pd.read_csv(r / "summary.csv").sort_values("method").reset_index(drop=True)
    close(actual[["n_triplets", "correct_score", "accuracy", "mean_margin"]],
          summary.sort_values("method").reset_index(drop=True)[["n_triplets", "correct_score", "accuracy", "mean_margin"]], "summary")
    check(actual.method.tolist() == summary.sort_values("method").method.tolist(), "summary methods")
    wide = expected.pivot(index="id", columns="method", values="margin")
    close(wide.hybrid50, .5 * (wide.embedding + wide.concept207), "hybrid margin identity")
    scores = expected.pivot(index="id", columns="method", values="score")
    transitions = []
    for method, baseline in CONTRASTS:
        transitions.append({"method": method, "baseline": baseline,
            "improved_triplets": int(scores[method].gt(scores[baseline]).sum()),
            "worsened_triplets": int(scores[method].lt(scores[baseline]).sum()),
            "unchanged_triplets": int(scores[method].eq(scores[baseline]).sum())})
    check(pd.read_csv(r / "transitions.csv").to_dict("records") == transitions, "transitions")
    return summary


def bootstrap_intervals(base, expected):
    r = base / "results"
    out, loo = [], []
    for method, baseline in CONTRASTS:
        a = expected[expected.method.eq(method)].set_index("id")
        b = expected[expected.method.eq(baseline)].set_index("id").loc[a.index]
        d = a[["score", "margin"]] - b[["score", "margin"]]
        d["conflict"], d["anchor_topic"], d["variant"] = a.conflict, a.anchor_topic, a.variant
        grid = d.set_index(["conflict", "anchor_topic", "variant"])[["score", "margin"]].reindex(
            pd.MultiIndex.from_product([LABELS, load_json(base / "data" / "domains.json"), [0, 1]]))
        check(not grid.isna().any().any(), f"bootstrap grid {method}/{baseline}")
        grid = grid.to_numpy().reshape(12, 10, 2, 2).mean(axis=2)
        for grouping in ("conflict_and_topic", "conflict", "anchor_topic"):
            rng = np.random.default_rng(SEED)
            if grouping == "conflict_and_topic":
                ki = rng.integers(0, 12, size=(10000, 12)); ti = rng.integers(0, 10, size=(10000, 10))
                # Weighted counts make the two-factor resampling explicit and
                # independent of the study implementation's fancy indexing.
                kc = np.stack([np.bincount(row, minlength=12) for row in ki])
                tc = np.stack([np.bincount(row, minlength=10) for row in ti])
                samples = np.column_stack([
                    np.einsum("bi,ij,bj->b", kc, grid[:, :, j], tc) / 120.0
                    for j in range(2)])
            else:
                blocks = grid.mean(axis=1 if grouping == "conflict" else 0)
                draws = rng.integers(0, len(blocks), size=(10000, len(blocks)))
                counts = np.stack([np.bincount(row, minlength=len(blocks)) for row in draws])
                samples = counts @ blocks / float(len(blocks))
            for j, metric in enumerate(("accuracy", "mean_margin")):
                low, high = np.quantile(samples[:, j], [.025, .975])
                out.append(dict(method=method, baseline=baseline, grouping=grouping, metric=metric,
                                difference=float(grid[:, :, j].mean()), low=float(low), high=float(high)))
        for author in range(4):
            keep = a.author.ne(author)
            loo.append(dict(method=method, baseline=baseline, excluded_author=author,
                            n_triplets=int(keep.sum()), accuracy_difference=float(d.loc[keep, "score"].mean()),
                            margin_difference=float(d.loc[keep, "margin"].mean())))
    actual = pd.read_csv(r / "intervals.csv")
    actual = actual.sort_values(list(actual.columns)).reset_index(drop=True)
    exp = pd.DataFrame(out).sort_values(list(actual.columns)).reset_index(drop=True)
    for col in ("difference", "low", "high"):
        close(actual[col], exp[col], f"intervals {col}")
    check(actual[["method", "baseline", "grouping", "metric"]].to_dict("records") == exp[["method", "baseline", "grouping", "metric"]].to_dict("records"), "interval labels")
    actual_loo = pd.read_csv(r / "leave_one_author_out.csv").sort_values(list(pd.DataFrame(loo).columns)).reset_index(drop=True)
    exp_loo = pd.DataFrame(loo).sort_values(list(actual_loo.columns)).reset_index(drop=True)
    for col in ("n_triplets", "accuracy_difference", "margin_difference"):
        close(actual_loo[col], exp_loo[col], f"leave-one-author {col}")
    return out, loo


def random_controls(base, trips, z, centered, expected, summary):
    r = base / "results"
    specs = load_json(r / "random_map_specs.json")
    check(len(specs) == 60, "random map spec count")
    sv = np.linalg.svd(centered, compute_uv=False)
    records = []
    seen = set()
    for spec in specs:
        family, rep, seed = spec["family"], int(spec["replicate"]), int(spec["map_seed"])
        check(0 <= rep < 30, "map replicate range")
        check((family, rep) not in seen, "duplicate random map family/replicate")
        seen.add((family, rep))
        check(spec["input_dimension"] == 384 and spec["output_dimension"] == 207, "map dimensions")
        expected_seed = SEED + rep + (1000 if family == "spectrum_matched" else 0)
        check(seed == expected_seed, "map seed")
        g = np.random.default_rng(seed).standard_normal((384, 207))
        if family == "gaussian": matrix = g / np.sqrt(207)
        elif family == "spectrum_matched":
            q, rr = np.linalg.qr(g, mode="reduced"); q = q * np.where(np.diag(rr) < 0, -1., 1.)
            matrix = q * sv
            close(matrix.T @ matrix, np.diag(sv ** 2), "spectrum Gram")
        else: fail(f"unknown map family {family}")
        rc = normalized(z @ matrix)
        for blend, v in (("projection", rc), ("hybrid50", np.concatenate((np.sqrt(.5)*z, np.sqrt(.5)*rc), axis=1))):
            s = score_rows(v, trips.id.tolist()).assign(family=family, replicate=rep, map_seed=seed, blend=blend)
            records.append(s)
    check(sum(f == "gaussian" for f, _ in seen) == 30, "30 Gaussian maps")
    check(sum(f == "spectrum_matched" for f, _ in seen) == 30, "30 spectrum-matched maps")
    check({r for f, r in seen if f == "gaussian"} == set(range(30)), "Gaussian replicas 0..29")
    check({r for f, r in seen if f == "spectrum_matched"} == set(range(30)), "spectrum replicas 0..29")
    controls = pd.concat(records, ignore_index=True)
    actual = pd.read_csv(r / "random_per_triplet.csv")
    check(len(actual) == 28800, "random per-triplet row count")
    key = ["family", "replicate", "map_seed", "blend", "id"]
    aa, ee = actual.sort_values(key).reset_index(drop=True), controls.sort_values(key).reset_index(drop=True)
    for col in ("d_same_conflict", "d_same_topic", "margin", "score"):
        close(aa[col], ee[col], f"random per-triplet {col}")
    check(aa[key].to_dict("records") == ee[key].to_dict("records"), "random per-triplet keys")
    # Recompute map summaries from the independent rows, then compare all fields.
    rs = controls.groupby(["family", "replicate", "map_seed", "blend"], as_index=False).agg(
        correct_score=("score", "sum"), accuracy=("score", "mean"), mean_margin=("margin", "mean"))
    ar = pd.read_csv(r / "random_summary.csv").sort_values(list(rs.columns)).reset_index(drop=True)
    er = rs.sort_values(list(rs.columns)).reset_index(drop=True)
    for col in ("correct_score", "accuracy", "mean_margin"): close(ar[col], er[col], f"random summary {col}")
    check(ar[["family", "replicate", "map_seed", "blend"]].to_dict("records") == er[["family", "replicate", "map_seed", "blend"]].to_dict("records"), "random summary keys")
    dist = []
    for (family, blend), group in rs.groupby(["family", "blend"]):
        ref = summary.set_index("method").loc["concept207" if blend == "projection" else "hybrid50"]
        dist.append({"family": family, "blend": blend, "n_maps": len(group),
            "accuracy_min": group.accuracy.min(), "accuracy_median": group.accuracy.median(),
            "accuracy_p95": group.accuracy.quantile(.95), "accuracy_max": group.accuracy.max(),
            "n_accuracy_strictly_above_concept": int(group.accuracy.gt(ref.accuracy).sum()),
            "n_accuracy_equal_concept": int(group.accuracy.eq(ref.accuracy).sum()),
            "margin_min": group.mean_margin.min(), "margin_median": group.mean_margin.median(),
            "margin_max": group.mean_margin.max()})
    ad = pd.read_csv(r / "random_distributions.csv").sort_values(["family", "blend"]).reset_index(drop=True)
    ed = pd.DataFrame(dist).sort_values(["family", "blend"]).reset_index(drop=True)
    for col in ad.columns:
        if col not in ("family", "blend"): close(ad[col], ed[col], f"random distributions {col}")
    check(ad[["family", "blend"]].to_dict("records") == ed[["family", "blend"]].to_dict("records"), "random distribution keys")


def metadata_tables(base, trips, expected):
    r = base / "results"
    sensitivity = expected[expected.both_audits_agree].groupby("method", as_index=False).agg(
        n_triplets=("score", "size"), correct_score=("score", "sum"), accuracy=("score", "mean"), mean_margin=("margin", "mean"))
    accepted = trips[trips.both_audits_agree]
    sensitivity["n_conflicts"] = accepted.conflict.nunique(); sensitivity["n_topics"] = accepted.anchor_topic.nunique()
    sensitivity["interpretable"] = len(accepted) >= 120 and accepted.conflict.nunique() >= 8 and accepted.anchor_topic.nunique() >= 6
    actual = pd.read_csv(r / "agreed_audit_sensitivity.csv").sort_values("method").reset_index(drop=True)
    exp = sensitivity.sort_values("method").reset_index(drop=True)
    for col in ("n_triplets", "correct_score", "accuracy", "mean_margin", "n_conflicts", "n_topics"):
        close(actual[col], exp[col], f"sensitivity {col}")
    check(actual[["method", "interpretable"]].to_dict("records") == exp[["method", "interpretable"]].to_dict("records"), "sensitivity labels")
    agreements = pd.read_csv(r / "audit_agreements.csv")
    expected_agreements = trips[["id", "audit_1", "audit_2", "audit_1_agrees", "audit_2_agrees", "both_audits_agree"]].copy()
    aa = agreements.sort_values("id").reset_index(drop=True)
    ea = expected_agreements.sort_values("id").reset_index(drop=True)
    check(aa.columns.tolist() == ea.columns.tolist(), "audit agreements fields")
    check(aa.to_dict("records") == ea.to_dict("records"), "audit agreements rows")
    expected_by_conflict = trips.groupby("conflict", as_index=False).agg(
        n=("id", "size"), auditor_1_agrees=("audit_1_agrees", "sum"),
        auditor_2_agrees=("audit_2_agrees", "sum"), both_agree=("both_audits_agree", "sum"))
    actual_by_conflict = pd.read_csv(r / "audit_by_conflict.csv").sort_values("conflict").reset_index(drop=True)
    expected_by_conflict = expected_by_conflict.sort_values("conflict").reset_index(drop=True)
    check(actual_by_conflict.to_dict("records") == expected_by_conflict.to_dict("records"), "audit_by_conflict rows")
    # Preserve the pre-repair AI audit subset as a disclosed sensitivity check.
    initial = trips[["id", "conflict", "anchor_topic", "author"]].copy()
    for i in (1, 2):
        labels = pd.DataFrame(load_json(base / "data" / "audit_initial" / f"audit_labels_{i}.json")).set_index("id")
        key = load_json(base / "data" / f"audit_key_{i}.json")
        normalized_choice = {rid: ("B" if ch == key[rid] else "C") if ch in ("X", "Y") else ch
                             for rid, ch in labels.choice.items()}
        initial[f"audit_{i}"] = initial.id.map(normalized_choice)
        initial[f"audit_{i}_agrees"] = initial[f"audit_{i}"].eq("B")
    initial["both_audits_agree"] = initial.audit_1_agrees & initial.audit_2_agrees
    initial_expected = expected.merge(initial[["id", "both_audits_agree"]].rename(columns={"both_audits_agree": "initial_both_audits_agree"}), on="id")
    initial_summary = initial_expected[initial_expected.initial_both_audits_agree].groupby("method", as_index=False).agg(
        n_triplets=("score", "size"), correct_score=("score", "sum"), accuracy=("score", "mean"), mean_margin=("margin", "mean"))
    initial_accepted = initial[initial.both_audits_agree]
    initial_summary["n_conflicts"] = initial_accepted.conflict.nunique()
    initial_summary["n_topics"] = initial_accepted.anchor_topic.nunique()
    initial_summary["interpretable"] = (len(initial_accepted) >= 120 and initial_accepted.conflict.nunique() >= 8
                                         and initial_accepted.anchor_topic.nunique() >= 6)
    actual_initial = pd.read_csv(r / "initial_audit_sensitivity.csv").sort_values("method").reset_index(drop=True)
    expected_initial = initial_summary.sort_values("method").reset_index(drop=True)
    for col in ("n_triplets", "correct_score", "accuracy", "mean_margin", "n_conflicts", "n_topics"):
        close(actual_initial[col], expected_initial[col], f"initial sensitivity {col}")
    check(actual_initial[["method", "interpretable"]].to_dict("records") ==
          expected_initial[["method", "interpretable"]].to_dict("records"), "initial sensitivity labels")
    for factor in ("conflict", "anchor_topic", "author"):
        actual = pd.read_csv(r / f"by_{factor}.csv")
        exp = expected.groupby([factor, "method"], as_index=False).agg(n_triplets=("score", "size"), correct_score=("score", "sum"), accuracy=("score", "mean"), mean_margin=("margin", "mean"))
        actual, exp = actual.sort_values([factor, "method"]).reset_index(drop=True), exp.sort_values([factor, "method"]).reset_index(drop=True)
        check(actual[[factor, "method"]].to_dict("records") == exp[[factor, "method"]].to_dict("records"), f"by_{factor} keys")
        for col in ("n_triplets", "correct_score", "accuracy", "mean_margin"): close(actual[col], exp[col], f"by_{factor} {col}")


def run(base: Path, output: Path):
    NUMERIC_ERRORS.clear()
    base = base.resolve(); output.mkdir(parents=True, exist_ok=True)
    trips, _ = read_main_data(base)
    manifest = verify_manifests(base)
    vec, expected, centered = expected_main(base, trips)
    summary = summary_tables(base, trips, expected)
    bootstrap_intervals(base, expected)
    random_controls(base, trips, vec["embedding"], centered, expected, summary)
    metadata_tables(base, trips, expected)
    result = {"status": "ok", "study": str(base), "checks": {
        "manifests": manifest, "main_rows": 720, "triplets": 240,
        "methods": METHODS, "bootstrap_seed": SEED, "random_maps": 60,
        "max_abs_tolerance": TOL, "max_abs_errors": NUMERIC_ERRORS}}
    (output / "numeric_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "numeric_audit.md").write_text(
        "# Independent numeric audit\n\n"
        f"Status: **OK**. Read the saved 720 encoder vectors, reconstructed the concept207 "
        "and hybrid50 representations, and independently recomputed all 720 main per-triplet rows, "
        "28,800 random-control rows, summaries, transitions, audit sensitivity, "
        "leave-one-author-out tables, and the 18 bootstrap intervals from saved artifacts.\n\n"
        f"Study package: `{base}`\n\n"
        "The reference uses `scipy.spatial.distance.cosine` pair by pair. "
        "All comparisons tolerate at most 1e-10 absolute error (CSV values are written to 12 significant digits). "
        "No encoder, prior study, or experiment module was imported. This is an AI numeric check of saved "
        "artifacts, not human semantic validation.\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("study", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[2] / "notebooks" / "concept_layers_large_en",
                        help="standalone study package containing data/ and results/")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(run(args.study, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
