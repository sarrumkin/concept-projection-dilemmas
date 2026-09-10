"""Generate the paper-style figures from recomputed experiment tables."""
from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ORDER = ["embedding", "concept207", "hybrid50"]
NAMES = {"embedding": "Embedding", "concept207": "Concept207", "hybrid50": "Hybrid50"}
COLORS = {"embedding": "#78818b", "concept207": "#13786f", "hybrid50": "#5279ac"}


def make_figures(results, output):
    results, output = Path(results), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(results / "summary.csv").set_index("method").loc[ORDER]
    intervals = pd.read_csv(results / "intervals.csv")
    controls = pd.read_csv(results / "random_summary.csv")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "svg.fonttype": "none",
                         "figure.facecolor": "white", "savefig.facecolor": "white"})

    def save(fig, name):
        for extension in ("png", "svg"):
            fig.savefig(output / f"{name}.{extension}", dpi=180, bbox_inches="tight",
                        metadata={"Creator": "concept-projection-dilemmas"} if extension == "svg" else {})
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 3.5), layout="constrained")
    positions = np.arange(3)
    accuracy = summary.accuracy.to_numpy() * 100
    ax.barh(positions, accuracy, color=[COLORS[m] for m in ORDER], height=0.58)
    ax.set_yticks(positions, [NAMES[m] for m in ORDER])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Conflict preference accuracy (%)")
    concept = summary.loc["concept207"]
    ax.set_title(f"Concept207: {int(concept.correct_score)} of {int(concept.n_triplets)} authored conflict matches")
    for i, method in enumerate(ORDER):
        row = summary.loc[method]
        ax.text(accuracy[i] + 1.5, i, f"{accuracy[i]:.2f}%  ({int(row.correct_score)}/240)", va="center")
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.16)
    save(fig, "accuracy")

    fig, ax = plt.subplots(figsize=(8.5, 3.3), layout="constrained")
    for i, method in enumerate(ORDER[1:]):
        row = intervals[(intervals.method == method) & (intervals.baseline == "embedding") &
                        (intervals.grouping == "conflict_and_topic") & (intervals.metric == "accuracy")].iloc[0]
        value, low, high = 100 * np.array([row.difference, row.low, row.high])
        ax.errorbar(value, i, xerr=[[value - low], [high - value]], fmt="o", markersize=8,
                    capsize=5, color=COLORS[method], linewidth=2)
        ax.text(high + 0.9, i, f"+{value:.2f} pp\n[{low:.2f}, {high:.2f}]", va="center", fontsize=10)
    ax.axvline(0, color="#999999", linewidth=1)
    ax.set_yticks([0, 1], ["Concept207 − Embedding", "Hybrid50 − Embedding"])
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(-2, 37)
    ax.set_xlabel("Accuracy difference (percentage points)")
    ax.set_title("Paired differences on the fixed synthetic corpus")
    ax.text(0, -0.36, "95% descriptive intervals · 10,000 conflict-and-topic bootstrap draws",
            transform=ax.transAxes, fontsize=9, color="#555555")
    ax.grid(axis="x", alpha=0.16)
    save(fig, "effects")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), layout="constrained", sharex=True, sharey=True)
    families = ["gaussian", "spectrum_matched"]
    jitter = np.random.default_rng(431).uniform(-0.12, 0.12, 30)
    for ax, blend, method in zip(axes, ["projection", "hybrid50"], ORDER[1:]):
        for j, family in enumerate(families):
            values = controls[(controls.blend == blend) & (controls.family == family)].sort_values("replicate").accuracy.to_numpy() * 100
            assert len(values) == 30
            ax.scatter(values, j + jitter, s=25, alpha=0.65, color="#929ba5", edgecolors="none")
        value = float(summary.loc[method, "accuracy"]) * 100
        ax.axvline(value, color=COLORS[method], linewidth=2, label=f"{NAMES[method]}: {value:.2f}%")
        ax.set_title("Attribute projection" if blend == "projection" else "Secondary: 50/50 mixture")
        ax.set_xlabel("Conflict preference accuracy (%)")
        ax.set_yticks([0, 1], ["Gaussian\n30 maps", "Spectrum matched\n30 maps"])
        ax.set_ylim(1.55, -0.55)
        ax.set_xlim(32, 64)
        ax.legend(loc="lower left", frameon=False, fontsize=9)
        ax.grid(axis="x", alpha=0.16)
    fig.suptitle("Same texts and labels; 60 fixed random maps per comparison", fontsize=12)
    save(fig, "random_controls")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    make_figures(args.results, args.output)
    print("Generated accuracy, effects and random-control figures (PNG and SVG).")
