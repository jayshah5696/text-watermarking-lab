#!/usr/bin/env python3
"""Build stable Stage 7 separation and prefix-effect figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/lab-07/results.json"
OUTPUT = ROOT / "artifacts/lab-07"
COLORS = {
    "versus_control": "#55d6e8",
    "versus_natural": "#a78bfa",
    "versus_comparison_key": "#facc15",
}
LABELS = {
    "versus_control": "marked minus model control",
    "versus_natural": "marked minus natural web",
    "versus_comparison_key": "marked minus comparison key",
}


def _style() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": "#000000",
            "axes.facecolor": "#111111",
            "axes.edgecolor": "#74777e",
            "axes.labelcolor": "#f5f7fa",
            "xtick.color": "#c5c8ce",
            "ytick.color": "#c5c8ce",
            "text.color": "#f5f7fa",
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "svg.hashsalt": "text-watermarking-lab-07",
        }
    )


def _save(figure: Figure, name: str, output: Path) -> None:
    metadata = {"Creator": "text-watermarking-lab", "Date": None}
    figure.savefig(output / f"{name}.png", dpi=180, metadata=metadata, bbox_inches="tight")
    figure.savefig(output / f"{name}.svg", metadata=metadata, bbox_inches="tight")
    plt.close(figure)


def build_separation(artifact: dict[str, Any], output: Path) -> None:
    prefix = "80"
    summary = cast(dict[str, Any], artifact["prefix_summary"])[prefix]
    figure, axes = plt.subplots(1, 3, figsize=(12, 4.8), sharey=True)
    for axis, comparison in zip(axes, COLORS, strict=True):
        result = summary["comparisons"][comparison]
        values = result["row_differences"]
        axis.axhline(0, color="#fb7185", linestyle="--", linewidth=1.2, label="equal z")
        axis.scatter(
            range(len(values)),
            values,
            color=COLORS[comparison],
            edgecolor="#000000",
            linewidth=0.5,
            s=34,
            zorder=3,
        )
        axis.axhline(result["mean_difference"], color="#4ade80", linewidth=2.2)
        axis.fill_between(
            [-0.6, len(values) - 0.4],
            result["interval_low"],
            result["interval_high"],
            color="#4ade80",
            alpha=0.13,
        )
        axis.set_title(LABELS[comparison], fontsize=10)
        axis.set_xlabel("frozen row order")
        axis.grid(axis="y", color="#303238", linewidth=0.7)
        axis.text(
            0.03,
            0.97,
            (
                f"mean {result['mean_difference']:.4f}\n"
                f"95% [{result['interval_low']:.4f}, {result['interval_high']:.4f}]\n"
                f"n={summary['complete_rows']}"
            ),
            transform=axis.transAxes,
            va="top",
            color="#f5f7fa",
            fontsize=8.5,
        )
    axes[0].set_ylabel("paired z difference")
    figure.suptitle("Stage 7 separation at 80 copied tokens", fontsize=16, fontweight="bold")
    figure.text(
        0.5,
        0.01,
        (
            "Each dot is one frozen document pair. Positive means correct-key marked z is higher. "
            "Intervals summarize this 24-row cohort."
        ),
        ha="center",
        color="#a9adb5",
        fontsize=8.5,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 0.92))
    _save(figure, "separation", output)


def build_prefix_effects(artifact: dict[str, Any], output: Path) -> None:
    summaries = cast(dict[str, Any], artifact["prefix_summary"])
    prefixes = [40, 80, 160, 200]
    figure, axis = plt.subplots(figsize=(9, 5.2))
    offsets = (-5, 0, 5)
    for offset, comparison in zip(offsets, COLORS, strict=True):
        xs = [prefix + offset for prefix in prefixes]
        results = [summaries[str(prefix)]["comparisons"][comparison] for prefix in prefixes]
        means = [result["mean_difference"] for result in results]
        low = [mean - result["interval_low"] for mean, result in zip(means, results, strict=True)]
        high = [result["interval_high"] - mean for mean, result in zip(means, results, strict=True)]
        axis.errorbar(
            xs,
            means,
            yerr=[low, high],
            color=COLORS[comparison],
            marker="o",
            linewidth=2,
            capsize=4,
            label=LABELS[comparison],
        )
    axis.axhline(0, color="#fb7185", linestyle="--", linewidth=1.2)
    axis.set_xticks(prefixes)
    axis.set_xlabel("copied-token prefix")
    axis.set_ylabel("mean paired z difference")
    axis.set_title("Evidence by available copied-token prefix", fontsize=16, fontweight="bold")
    axis.grid(color="#303238", linewidth=0.7)
    axis.legend(frameon=False, labelcolor="#f5f7fa")
    for prefix in prefixes:
        axis.text(
            prefix,
            -0.55,
            f"n={summaries[str(prefix)]['complete_rows']}",
            ha="center",
            color="#a9adb5",
            fontsize=8,
        )
    axis.text(
        0.01,
        0.98,
        "No complete 400-token pairs",
        transform=axis.transAxes,
        va="top",
        color="#fb7185",
        fontsize=9,
    )
    figure.text(
        0.5,
        0.01,
        (
            "Bars are deterministic 95% paired bootstrap intervals. Cohorts shrink when either "
            "generated output ends before the prefix."
        ),
        ha="center",
        color="#a9adb5",
        fontsize=8.5,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    _save(figure, "prefix_effects", output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=ARTIFACT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    _style()
    artifact: dict[str, Any] = json.loads(args.artifact.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    build_separation(artifact, args.output)
    build_prefix_effects(artifact, args.output)
    print("Wrote Stage 7 separation and prefix-effect PNG/SVG figures")


if __name__ == "__main__":
    main()
