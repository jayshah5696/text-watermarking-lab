#!/usr/bin/env python3
"""Stage 1: expose green-hit detection with an independent biased coin."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform as platform_module
import subprocess
import sys
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from watermark_lab.records import (
    Condition,
    ConditionSummary,
    Lab01ConfigSnapshot,
    build_condition_summary,
    build_lab01_summary,
    summary_to_json_bytes,
)
from watermark_lab.stats import (
    derive_group_seed,
    green_hit_z_score,
    simulate_hit_counts,
)

CAVEAT = (
    "This is a biased-coin demonstration under independent trials, not a measured "
    "false-positive or true-positive rate for an LLM watermark."
)
CONDITIONS: tuple[Condition, Condition] = ("null", "biased")


class LabError(RuntimeError):
    """An actionable problem with an evidence-generation precondition."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_01.toml"))
    parser.add_argument("--runs-dir", type=Path, default=Path("runs/lab-01"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-01"))
    return parser.parse_args()


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=repo, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise LabError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout.strip()


def _clean_source_commit(repo: Path) -> str:
    dirty = _git(repo, "status", "--porcelain", "--untracked-files=normal")
    if dirty:
        raise LabError(
            "refusing to generate evidence from a dirty Git worktree; commit, ignore, or remove "
            "the listed changes first:\n" + dirty
        )
    return _git(repo, "rev-parse", "HEAD")


def _require_int(mapping: Mapping[str, object], name: str, *, minimum: int | None = None) -> int:
    value = mapping[name]
    if isinstance(value, bool) or not isinstance(value, int):
        raise LabError(f"config field {name!r} must be an integer")
    if minimum is not None and value < minimum:
        raise LabError(f"config field {name!r} must be at least {minimum}")
    return value


def _require_float(mapping: Mapping[str, object], name: str) -> float:
    value = mapping[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LabError(f"config field {name!r} must be a real number")
    return float(value)


def _load_config(path: Path) -> tuple[Lab01ConfigSnapshot, bytes]:
    try:
        payload = path.read_bytes()
        parsed: Any = tomllib.loads(payload.decode("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise LabError(f"could not read config {path}: {error}") from error
    if not isinstance(parsed, dict) or not all(isinstance(key, str) for key in parsed):
        raise LabError("config must be a TOML table")
    mapping = cast(Mapping[str, object], parsed)
    expected_keys = {
        "schema_version",
        "base_seed",
        "lengths",
        "replicates",
        "null_hit_probability",
        "alternative_hit_probability",
        "z_threshold",
    }
    if set(mapping) != expected_keys:
        raise LabError(
            f"config keys differ: expected {sorted(expected_keys)}, got {sorted(mapping)}"
        )
    if _require_int(mapping, "schema_version") != 1:
        raise LabError("config schema_version must be 1")
    raw_lengths = mapping["lengths"]
    if not isinstance(raw_lengths, list):
        raise LabError("config field 'lengths' must be an array")
    lengths: list[int] = []
    for value in raw_lengths:
        if isinstance(value, bool) or not isinstance(value, int):
            raise LabError("every configured length must be an integer")
        lengths.append(value)
    try:
        snapshot = Lab01ConfigSnapshot(
            base_seed=_require_int(mapping, "base_seed"),
            lengths=tuple(lengths),
            replicates=_require_int(mapping, "replicates", minimum=1),
            null_hit_probability=_require_float(mapping, "null_hit_probability"),
            alternative_hit_probability=_require_float(mapping, "alternative_hit_probability"),
            z_threshold=_require_float(mapping, "z_threshold"),
        )
    except (TypeError, ValueError) as error:
        raise LabError(f"invalid config: {error}") from error
    return snapshot, payload


def _probability(config: Lab01ConfigSnapshot, condition: Condition) -> float:
    return (
        config.null_hit_probability if condition == "null" else config.alternative_hit_probability
    )


def _write_raw_and_summarize(
    *,
    raw_directory: Path,
    config: Lab01ConfigSnapshot,
    source_commit: str,
    config_sha256: str,
) -> tuple[ConditionSummary, ...]:
    raw_directory.mkdir(parents=True, exist_ok=True)
    metadata = {
        "config": asdict(config),
        "config_sha256": config_sha256,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform_module.platform(),
        "python_version": platform_module.python_version(),
        "source_commit": source_commit,
    }
    (raw_directory / "metadata.json").write_text(
        json.dumps(metadata, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summaries: list[ConditionSummary] = []
    with (raw_directory / "simulations.jsonl").open("w", encoding="utf-8", newline="\n") as raw:
        for length in config.lengths:
            for condition in CONDITIONS:
                probability = _probability(config, condition)
                seed = derive_group_seed(
                    base_seed=config.base_seed, condition=condition, trials=length
                )
                hit_counts = simulate_hit_counts(
                    trials=length,
                    hit_probability=probability,
                    replicates=config.replicates,
                    seed=seed,
                )
                for replicate, hits in enumerate(hit_counts):
                    z_score = green_hit_z_score(
                        hits=hits,
                        trials=length,
                        null_probability=config.null_hit_probability,
                    )
                    row = {
                        "condition": condition,
                        "hits": hits,
                        "is_detected": z_score >= config.z_threshold,
                        "length": length,
                        "replicate": replicate,
                        "z_score": z_score,
                    }
                    raw.write(json.dumps(row, allow_nan=False, sort_keys=True) + "\n")
                summaries.append(
                    build_condition_summary(
                        length=length,
                        condition=condition,
                        hit_probability=probability,
                        hit_counts=hit_counts,
                        null_probability=config.null_hit_probability,
                        z_threshold=config.z_threshold,
                    )
                )
    return tuple(summaries)


def _condition_rows(
    rows: Sequence[ConditionSummary], condition: Condition
) -> list[ConditionSummary]:
    return [row for row in rows if row.condition == condition]


def _render_figure(
    *, rows: Sequence[ConditionSummary], config: Lab01ConfigSnapshot, artifacts: Path
) -> None:
    matplotlib.rcParams["svg.hashsalt"] = "text-watermarking-lab-01"
    colors: dict[Condition, str] = {"null": "#0072B2", "biased": "#D55E00"}
    labels: dict[Condition, str] = {"null": "Null p=0.25", "biased": "Biased p=0.40"}
    markers: dict[Condition, str] = {"null": "o", "biased": "s"}
    styles: dict[Condition, str] = {"null": "--", "biased": "-"}

    figure, (rate_axis, evidence_axis) = plt.subplots(1, 2, figsize=(12, 5.8))
    for condition in CONDITIONS:
        selected = _condition_rows(rows, condition)
        lengths = [row.length for row in selected]
        rates = [row.detection_rate for row in selected]
        errors = [1.96 * row.monte_carlo_standard_error for row in selected]
        lower = [max(0.0, rate - error) for rate, error in zip(rates, errors, strict=True)]
        upper = [min(1.0, rate + error) for rate, error in zip(rates, errors, strict=True)]
        rate_axis.plot(
            lengths,
            rates,
            color=colors[condition],
            label=labels[condition],
            marker=markers[condition],
            linestyle=styles[condition],
        )
        rate_axis.fill_between(lengths, lower, upper, color=colors[condition], alpha=0.16)

        medians = [row.median_z for row in selected]
        evidence_axis.plot(
            lengths,
            medians,
            color=colors[condition],
            label=labels[condition],
            marker=markers[condition],
            linestyle=styles[condition],
        )
        evidence_axis.fill_between(
            lengths,
            [row.q05_z for row in selected],
            [row.q95_z for row in selected],
            color=colors[condition],
            alpha=0.16,
        )

    rate_axis.set_title("Detection rate by sequence length")
    rate_axis.set_xlabel("Eligible trials T")
    rate_axis.set_ylabel("Simulated detection rate")
    rate_axis.set_ylim(0.0, 1.0)
    rate_axis.legend()
    rate_axis.grid(alpha=0.25)

    evidence_axis.axhline(config.z_threshold, color="#333333", linestyle=":", label="z=3")
    evidence_axis.set_title("Detector evidence by sequence length")
    evidence_axis.set_xlabel("Eligible trials T")
    evidence_axis.set_ylabel("z-score (median and 5th-95th percentile)")
    evidence_axis.legend()
    evidence_axis.grid(alpha=0.25)

    figure.suptitle("Biased-coin detector: evidence grows with eligible length", fontsize=15)
    figure.text(
        0.5,
        0.915,
        f"gamma={config.null_hit_probability:.2f} | pedagogical alternative "
        f"p={config.alternative_hit_probability:.2f} | threshold z>={config.z_threshold:g} | "
        f"{config.replicates:,} replicates",
        ha="center",
        fontsize=10,
    )
    figure.text(0.5, 0.018, CAVEAT, ha="center", fontsize=8.5)
    figure.tight_layout(rect=(0.02, 0.07, 0.98, 0.89))
    artifacts.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        artifacts / "detection_by_length.svg",
        format="svg",
        metadata={"Date": None, "Creator": "text-watermarking-lab"},
    )
    figure.savefig(
        artifacts / "detection_by_length.png",
        format="png",
        dpi=160,
        metadata={"Software": "text-watermarking-lab"},
    )
    plt.close(figure)


def _print_summary(rows: Sequence[ConditionSummary]) -> None:
    print("length  condition  detections  rate     mean_z")
    for row in rows:
        print(
            f"{row.length:>6}  {row.condition:<9}  {row.detections:>10}  "
            f"{row.detection_rate:>7.4f}  {row.mean_z:>7.3f}"
        )
    print(CAVEAT)


def main() -> int:
    arguments = _parse_args()
    try:
        config, config_bytes = _load_config(arguments.config)
        repository = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
        source_commit = _clean_source_commit(repository)
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        raw_directory = arguments.runs_dir / source_commit / config_sha256
        rows = _write_raw_and_summarize(
            raw_directory=raw_directory,
            config=config,
            source_commit=source_commit,
            config_sha256=config_sha256,
        )
        summary = build_lab01_summary(
            source_commit=source_commit,
            config_sha256=config_sha256,
            python_version=platform_module.python_version(),
            platform=platform_module.platform(),
            config=config,
            rows=rows,
        )
        arguments.artifacts.mkdir(parents=True, exist_ok=True)
        (arguments.artifacts / "summary.json").write_bytes(summary_to_json_bytes(summary))
        _render_figure(rows=summary.rows, config=config, artifacts=arguments.artifacts)
        _print_summary(summary.rows)
    except (LabError, OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
