#!/usr/bin/env python3
"""Render stable Stage 8 evidence figures from the selected JSON artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

mpl.rcParams["svg.hashsalt"] = "text-watermarking-lab-08"

COLORS = {
    "normalization": "#60a5fa",
    "homoglyph_1": "#facc15",
    "homoglyph_5": "#eab308",
    "deletion_10": "#fb7185",
    "deletion_30": "#e11d48",
    "mixing_25": "#55d6e8",
    "mixing_50": "#0891b2",
    "paraphrase": "#a78bfa",
}
LABELS = {
    "normalization": "Normalize",
    "homoglyph_1": "Homoglyph 1%",
    "homoglyph_5": "Homoglyph 5%",
    "deletion_10": "Delete 10%",
    "deletion_30": "Delete 30%",
    "mixing_25": "Mix 25%",
    "mixing_50": "Mix 50%",
    "paraphrase": "Paraphrase",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=Path("artifacts/lab-08/results.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/lab-08"))
    return parser.parse_args()


def save(figure: Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    metadata = {"Date": None}
    figure.savefig(output / f"{stem}.png", dpi=180, metadata=metadata, bbox_inches="tight")
    figure.savefig(output / f"{stem}.svg", metadata=metadata, bbox_inches="tight")
    plt.close(figure)


def edit_figure(artifact: dict[str, Any], output: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.8), layout="constrained")
    rows = cast(list[dict[str, Any]], artifact["selected_rows"])
    labels = list(COLORS)
    for index, label in enumerate(labels):
        records = [row["attacks"][label] for row in rows]
        changes = [record["z_change"] for record in records]
        ratios = [record["length_ratio"] for record in records]
        axes[0].scatter(
            [index] * len(changes), changes, color=COLORS[label], edgecolor="#111827", s=42
        )
        axes[1].scatter(
            [index] * len(ratios), ratios, color=COLORS[label], edgecolor="#111827", s=42
        )
    axes[0].axhline(0, color="#111827", linewidth=1)
    axes[0].set_ylabel("Edited z minus unedited z at 80 copied tokens")
    axes[0].set_title("Correct-key evidence change")
    axes[1].axhspan(0.8, 1.2, color="#4ade80", alpha=0.12)
    axes[1].axhline(1, color="#111827", linewidth=1)
    axes[1].set_ylabel("Edited copied-token length / source length")
    axes[1].set_title("Retained copied-token length")
    for axis in axes:
        axis.set_xticks(
            range(len(labels)), [LABELS[label] for label in labels], rotation=38, ha="right"
        )
        axis.grid(axis="y", alpha=0.22)
    figure.suptitle("Stage 8: every frozen row after each declared edit", fontweight="bold")
    save(figure, output, "edit_signal_loss")


def bias_figure(artifact: dict[str, Any], output: Path) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(13, 5), layout="constrained")
    rows = [row for row in artifact["selected_rows"] if row["bias_generations"] is not None]
    colors = ["#60a5fa", "#4ade80", "#fb7185"]
    for row in rows:
        records = row["bias_generations"]
        biases = [1, 2, 3]
        axes[0].plot(
            biases,
            [records[str(bias)]["score"].get("z_score") for bias in biases],
            color="#6b7280",
            alpha=0.55,
            marker="o",
        )
        axes[1].plot(
            biases,
            [records[str(bias)]["conditional_nll"] for bias in biases],
            color="#6b7280",
            alpha=0.55,
            marker="o",
        )
        axes[2].plot(
            biases,
            [records[str(bias)]["repeated_pair_fraction"] for bias in biases],
            color="#6b7280",
            alpha=0.55,
            marker="o",
        )
    summaries = artifact["bias_summary"]
    for index, bias in enumerate((1, 2, 3)):
        axes[0].scatter(bias, summaries[str(bias)]["mean_z"], color=colors[index], s=100, zorder=5)
        axes[1].scatter(
            bias, summaries[str(bias)]["mean_nll"], color=colors[index], s=100, zorder=5
        )
        axes[2].scatter(
            bias,
            summaries[str(bias)]["mean_repeated_pair_fraction"],
            color=colors[index],
            s=100,
            zorder=5,
        )
    axes[0].axhline(3, color="#facc15", linestyle="--", label="strict z > 3")
    axes[0].set_ylabel("Correct-key z at 80 copied tokens")
    axes[0].legend(frameon=False)
    axes[1].set_ylabel("Conditional NLL, lower is better under Gemma")
    axes[2].set_ylabel("Repeated adjacent-pair fraction")
    for axis in axes:
        axis.set_xlabel("Watermark bias delta")
        axis.set_xticks((1, 2, 3))
        axis.grid(axis="y", alpha=0.22)
    figure.suptitle("Stage 8: same eight prompts and seeds, delta changes alone", fontweight="bold")
    save(figure, output, "bias_tradeoff")


def main() -> int:
    args = parse_args()
    artifact: dict[str, Any] = json.loads(args.artifact.read_text())
    edit_figure(artifact, args.output)
    bias_figure(artifact, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
