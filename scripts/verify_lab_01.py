#!/usr/bin/env python3
"""Recompute the selected Stage 1 summary from ignored raw simulation rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from watermark_lab.records import (
    Condition,
    ConditionSummary,
    Lab01ConfigSnapshot,
    Lab01Summary,
    build_condition_summary,
    build_lab01_summary,
    summary_from_json_bytes,
    summary_to_json_bytes,
)
from watermark_lab.stats import green_hit_z_score

CONDITIONS: tuple[Condition, Condition] = ("null", "biased")
RAW_KEYS = {"condition", "hits", "is_detected", "length", "replicate", "z_score"}


class VerificationError(RuntimeError):
    """A mismatch between raw data, provenance, and selected evidence."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_01.toml"))
    parser.add_argument("--runs-dir", type=Path, default=Path("runs/lab-01"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-01"))
    return parser.parse_args()


def _load_json(path: Path) -> object:
    def reject_constant(value: str) -> None:
        raise VerificationError(f"non-finite JSON number in {path}: {value}")

    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"could not read {path}: {error}") from error
    return cast(object, payload)


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise VerificationError(f"{name} must be a JSON object")
    untyped = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in untyped):
        raise VerificationError(f"{name} must be a JSON object")
    return cast(Mapping[str, object], untyped)


def _int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VerificationError(f"{name} must be an integer")
    return value


def _float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise VerificationError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise VerificationError(f"{name} must be finite")
    return number


def _verify_metadata(
    path: Path, summary_config: Lab01ConfigSnapshot, source: str, config_hash: str
) -> Mapping[str, object]:
    metadata = _mapping(_load_json(path), "metadata")
    expected_keys = {
        "config",
        "config_sha256",
        "created_at_utc",
        "platform",
        "python_version",
        "source_commit",
    }
    if set(metadata) != expected_keys:
        raise VerificationError("metadata keys do not match the Stage 1 contract")
    expected_config = json.loads(json.dumps(asdict(summary_config), allow_nan=False))
    if metadata["config"] != expected_config:
        raise VerificationError("raw metadata config does not match selected summary")
    if metadata["source_commit"] != source or metadata["config_sha256"] != config_hash:
        raise VerificationError("raw metadata provenance does not match selected summary")
    for name in ("created_at_utc", "platform", "python_version"):
        if not isinstance(metadata[name], str) or not metadata[name]:
            raise VerificationError(f"metadata {name} must be non-empty text")
    return metadata


def _read_raw_rows(path: Path, summary: Lab01Summary) -> dict[tuple[int, Condition], list[int]]:
    config = summary.config
    expected_rows = len(config.lengths) * len(CONDITIONS) * config.replicates
    grouped: dict[tuple[int, Condition], list[int]] = {
        (length, condition): [] for length in config.lengths for condition in CONDITIONS
    }
    try:
        raw_file = path.open(encoding="utf-8")
    except OSError as error:
        raise VerificationError(f"could not open {path}: {error}") from error
    actual_rows = 0
    with raw_file:
        for index, line in enumerate(raw_file):
            if index >= expected_rows:
                raise VerificationError("raw simulations contain more rows than configured")
            try:
                parsed: Any = json.loads(line)
            except json.JSONDecodeError as error:
                raise VerificationError(f"invalid raw JSON on line {index + 1}: {error}") from error
            row = _mapping(parsed, f"raw row {index + 1}")
            if set(row) != RAW_KEYS:
                raise VerificationError(f"raw row {index + 1} keys do not match the contract")

            group_index, expected_replicate = divmod(index, config.replicates)
            expected_length = config.lengths[group_index // len(CONDITIONS)]
            expected_condition = CONDITIONS[group_index % len(CONDITIONS)]
            length = _int(row["length"], "length")
            replicate = _int(row["replicate"], "replicate")
            hits = _int(row["hits"], "hits")
            condition = row["condition"]
            if (
                length != expected_length
                or condition != expected_condition
                or replicate != expected_replicate
            ):
                raise VerificationError(f"raw row {index + 1} is out of canonical order")
            expected_z = green_hit_z_score(
                hits=hits,
                trials=length,
                null_probability=config.null_hit_probability,
            )
            if _float(row["z_score"], "z_score") != expected_z:
                raise VerificationError(f"raw row {index + 1} has an incorrect z-score")
            if not isinstance(row["is_detected"], bool):
                raise VerificationError(f"raw row {index + 1} is_detected must be Boolean")
            if row["is_detected"] != (expected_z >= config.z_threshold):
                raise VerificationError(f"raw row {index + 1} has an incorrect detection flag")
            grouped[(length, expected_condition)].append(hits)
            actual_rows = index + 1
    if actual_rows != expected_rows:
        raise VerificationError(f"expected {expected_rows} raw rows, found {actual_rows}")
    return grouped


def verify(config_path: Path, runs_dir: Path, artifacts: Path) -> None:
    summary_path = artifacts / "summary.json"
    try:
        selected_bytes = summary_path.read_bytes()
        summary = summary_from_json_bytes(selected_bytes)
    except (OSError, UnicodeError, TypeError, ValueError) as error:
        raise VerificationError(f"invalid selected summary: {error}") from error
    if summary_to_json_bytes(summary) != selected_bytes:
        raise VerificationError("selected summary is not in canonical stable JSON form")
    try:
        config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
    except OSError as error:
        raise VerificationError(f"could not read config {config_path}: {error}") from error
    if config_hash != summary.config_sha256:
        raise VerificationError("config file hash does not match selected summary")

    raw_directory = runs_dir / summary.source_commit / summary.config_sha256
    metadata = _verify_metadata(
        raw_directory / "metadata.json",
        summary.config,
        summary.source_commit,
        summary.config_sha256,
    )
    grouped = _read_raw_rows(raw_directory / "simulations.jsonl", summary)
    rows: list[ConditionSummary] = []
    for length in summary.config.lengths:
        for condition in CONDITIONS:
            probability = (
                summary.config.null_hit_probability
                if condition == "null"
                else summary.config.alternative_hit_probability
            )
            rows.append(
                build_condition_summary(
                    length=length,
                    condition=condition,
                    hit_probability=probability,
                    hit_counts=grouped[(length, condition)],
                    null_probability=summary.config.null_hit_probability,
                    z_threshold=summary.config.z_threshold,
                )
            )
    recomputed = build_lab01_summary(
        source_commit=summary.source_commit,
        config_sha256=summary.config_sha256,
        python_version=cast(str, metadata["python_version"]),
        platform=cast(str, metadata["platform"]),
        config=summary.config,
        rows=rows,
    )
    if summary_to_json_bytes(recomputed) != selected_bytes:
        raise VerificationError("selected summary does not match recomputed raw evidence")


def main() -> int:
    arguments = _parse_args()
    try:
        verify(arguments.config, arguments.runs_dir, arguments.artifacts)
    except (VerificationError, TypeError, ValueError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 1 summary verified against raw rows, config hash, and source commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
