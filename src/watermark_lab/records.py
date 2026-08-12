# pyright: reportUnnecessaryIsInstance=false
"""Validated records and stable JSON for Stage 1 selected evidence."""

from __future__ import annotations

import json
import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

from watermark_lab.stats import green_hit_z_score

Condition = Literal["null", "biased"]
_CONDITION_ORDER: dict[Condition, int] = {"null": 0, "biased": 1}
_CONDITIONS: tuple[Condition, Condition] = ("null", "biased")


def _require_int(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _require_finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _require_probability(name: str, value: object) -> float:
    number = _require_finite(name, value)
    if not 0.0 < number < 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1")
    return number


def _require_exact_keys(mapping: Mapping[str, object], expected: set[str], name: str) -> None:
    actual = set(mapping)
    if actual != expected:
        raise ValueError(f"{name} keys differ: expected {sorted(expected)}, got {sorted(actual)}")


@dataclass(frozen=True, slots=True)
class Lab01ConfigSnapshot:
    base_seed: int
    lengths: tuple[int, ...]
    replicates: int
    null_hit_probability: float
    alternative_hit_probability: float
    z_threshold: float

    def __post_init__(self) -> None:
        _require_int("base_seed", self.base_seed)
        if not isinstance(self.lengths, tuple):
            raise TypeError("lengths must be a tuple")
        checked_lengths = tuple(_require_int("length", value, minimum=1) for value in self.lengths)
        if not checked_lengths or tuple(sorted(set(checked_lengths))) != checked_lengths:
            raise ValueError("lengths must be non-empty, unique, and ascending")
        _require_int("replicates", self.replicates, minimum=1)
        _require_probability("null_hit_probability", self.null_hit_probability)
        _require_probability("alternative_hit_probability", self.alternative_hit_probability)
        _require_finite("z_threshold", self.z_threshold)


@dataclass(frozen=True, slots=True)
class ConditionSummary:
    length: int
    condition: Condition
    hit_probability: float
    replicates: int
    detections: int
    detection_rate: float
    monte_carlo_standard_error: float
    mean_hits: float
    mean_z: float
    q05_z: float
    median_z: float
    q95_z: float

    def __post_init__(self) -> None:
        length = _require_int("length", self.length, minimum=1)
        if self.condition not in _CONDITION_ORDER:
            raise ValueError("condition must be 'null' or 'biased'")
        _require_probability("hit_probability", self.hit_probability)
        replicates = _require_int("replicates", self.replicates, minimum=1)
        detections = _require_int("detections", self.detections, minimum=0)
        if detections > replicates:
            raise ValueError("detections must not exceed replicates")
        rate = _require_finite("detection_rate", self.detection_rate)
        if not 0.0 <= rate <= 1.0 or rate != detections / replicates:
            raise ValueError("detection_rate must equal detections / replicates")
        standard_error = _require_finite(
            "monte_carlo_standard_error", self.monte_carlo_standard_error
        )
        if standard_error < 0.0:
            raise ValueError("monte_carlo_standard_error must be non-negative")
        mean_hits = _require_finite("mean_hits", self.mean_hits)
        if not 0.0 <= mean_hits <= length:
            raise ValueError("mean_hits must be between zero and length")
        values = (
            _require_finite("q05_z", self.q05_z),
            _require_finite("median_z", self.median_z),
            _require_finite("q95_z", self.q95_z),
        )
        _require_finite("mean_z", self.mean_z)
        if values != tuple(sorted(values)):
            raise ValueError("z quantiles must be ascending")


@dataclass(frozen=True, slots=True)
class Lab01Summary:
    schema_version: Literal[1]
    source_commit: str
    config_sha256: str
    python_version: str
    platform: str
    config: Lab01ConfigSnapshot
    rows: tuple[ConditionSummary, ...]

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        if not isinstance(self.source_commit, str) or not (
            40 <= len(self.source_commit) <= 64
            and all(character in "0123456789abcdef" for character in self.source_commit)
        ):
            raise ValueError("source_commit must be a lowercase hexadecimal Git object ID")
        if not isinstance(self.config_sha256, str) or not (
            len(self.config_sha256) == 64
            and all(character in "0123456789abcdef" for character in self.config_sha256)
        ):
            raise ValueError("config_sha256 must be a lowercase SHA-256 digest")
        for name, value in (("python_version", self.python_version), ("platform", self.platform)):
            if not isinstance(value, str):
                raise TypeError(f"{name} must be text")
            if not value:
                raise ValueError(f"{name} must not be empty")
        if not isinstance(self.config, Lab01ConfigSnapshot):
            raise TypeError("config must be a Lab01ConfigSnapshot")
        if not isinstance(self.rows, tuple) or not all(
            isinstance(row, ConditionSummary) for row in self.rows
        ):
            raise TypeError("rows must be a tuple of ConditionSummary records")
        expected_keys = [
            (length, condition) for length in self.config.lengths for condition in _CONDITIONS
        ]
        actual_keys = [(row.length, row.condition) for row in self.rows]
        if actual_keys != expected_keys:
            raise ValueError(
                "rows must contain exactly null then biased for every configured length"
            )
        for row in self.rows:
            expected_probability = (
                self.config.null_hit_probability
                if row.condition == "null"
                else self.config.alternative_hit_probability
            )
            if (
                row.hit_probability != expected_probability
                or row.replicates != self.config.replicates
            ):
                raise ValueError("row does not match the configuration snapshot")


def build_condition_summary(
    *,
    length: int,
    condition: Condition,
    hit_probability: float,
    hit_counts: Sequence[int],
    null_probability: float,
    z_threshold: float,
) -> ConditionSummary:
    """Aggregate one condition/length group using the locked Stage 1 rules."""

    if not hit_counts:
        raise ValueError("hit_counts must not be empty")
    z_scores = tuple(
        green_hit_z_score(hits=hits, trials=length, null_probability=null_probability)
        for hits in hit_counts
    )
    sorted_z = sorted(z_scores)
    replicates = len(hit_counts)
    detections = sum(score >= z_threshold for score in z_scores)
    rate = detections / replicates

    def nearest_rank(quantile: float) -> float:
        return sorted_z[round(quantile * (replicates - 1))]

    return ConditionSummary(
        length=length,
        condition=condition,
        hit_probability=hit_probability,
        replicates=replicates,
        detections=detections,
        detection_rate=rate,
        monte_carlo_standard_error=math.sqrt(rate * (1.0 - rate) / replicates),
        mean_hits=statistics.fmean(hit_counts),
        mean_z=statistics.fmean(z_scores),
        q05_z=nearest_rank(0.05),
        median_z=nearest_rank(0.50),
        q95_z=nearest_rank(0.95),
    )


def build_lab01_summary(
    *,
    source_commit: str,
    config_sha256: str,
    python_version: str,
    platform: str,
    config: Lab01ConfigSnapshot,
    rows: Iterable[ConditionSummary],
) -> Lab01Summary:
    """Sort and validate the complete selected Stage 1 summary."""

    sorted_rows = tuple(sorted(rows, key=lambda row: (row.length, _CONDITION_ORDER[row.condition])))
    return Lab01Summary(
        schema_version=1,
        source_commit=source_commit,
        config_sha256=config_sha256,
        python_version=python_version,
        platform=platform,
        config=config,
        rows=sorted_rows,
    )


def summary_to_json_bytes(summary: Lab01Summary) -> bytes:
    """Serialize selected evidence to deterministic, finite UTF-8 JSON."""

    text = json.dumps(asdict(summary), allow_nan=False, indent=2, sort_keys=True)
    return f"{text}\n".encode()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a JSON object")
    untyped = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in untyped):
        raise TypeError(f"{name} must be a JSON object")
    return cast(Mapping[str, object], untyped)


def _condition(value: object) -> Condition:
    if value not in _CONDITION_ORDER:
        raise ValueError("condition must be 'null' or 'biased'")
    return value


def summary_from_json_bytes(payload: bytes) -> Lab01Summary:
    """Parse selected evidence while rejecting unknown fields and non-finite numbers."""

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number is not allowed: {value}")

    parsed: Any = json.loads(payload.decode("utf-8"), parse_constant=reject_constant)
    root = _mapping(parsed, "summary")
    _require_exact_keys(
        root,
        {
            "schema_version",
            "source_commit",
            "config_sha256",
            "python_version",
            "platform",
            "config",
            "rows",
        },
        "summary",
    )
    config_data = _mapping(root["config"], "config")
    _require_exact_keys(
        config_data,
        {
            "base_seed",
            "lengths",
            "replicates",
            "null_hit_probability",
            "alternative_hit_probability",
            "z_threshold",
        },
        "config",
    )
    lengths_value = config_data["lengths"]
    if not isinstance(lengths_value, list):
        raise TypeError("config.lengths must be a JSON array")
    lengths_items = cast(list[object], lengths_value)
    config = Lab01ConfigSnapshot(
        base_seed=_require_int("base_seed", config_data["base_seed"]),
        lengths=tuple(_require_int("length", item, minimum=1) for item in lengths_items),
        replicates=_require_int("replicates", config_data["replicates"], minimum=1),
        null_hit_probability=_require_probability(
            "null_hit_probability", config_data["null_hit_probability"]
        ),
        alternative_hit_probability=_require_probability(
            "alternative_hit_probability", config_data["alternative_hit_probability"]
        ),
        z_threshold=_require_finite("z_threshold", config_data["z_threshold"]),
    )
    rows_value = root["rows"]
    if not isinstance(rows_value, list):
        raise TypeError("rows must be a JSON array")
    row_items = cast(list[object], rows_value)
    rows: list[ConditionSummary] = []
    row_keys = {
        "length",
        "condition",
        "hit_probability",
        "replicates",
        "detections",
        "detection_rate",
        "monte_carlo_standard_error",
        "mean_hits",
        "mean_z",
        "q05_z",
        "median_z",
        "q95_z",
    }
    for index, raw_row in enumerate(row_items):
        row = _mapping(raw_row, f"rows[{index}]")
        _require_exact_keys(row, row_keys, f"rows[{index}]")
        rows.append(
            ConditionSummary(
                length=_require_int("length", row["length"], minimum=1),
                condition=_condition(row["condition"]),
                hit_probability=_require_probability("hit_probability", row["hit_probability"]),
                replicates=_require_int("replicates", row["replicates"], minimum=1),
                detections=_require_int("detections", row["detections"], minimum=0),
                detection_rate=_require_finite("detection_rate", row["detection_rate"]),
                monte_carlo_standard_error=_require_finite(
                    "monte_carlo_standard_error", row["monte_carlo_standard_error"]
                ),
                mean_hits=_require_finite("mean_hits", row["mean_hits"]),
                mean_z=_require_finite("mean_z", row["mean_z"]),
                q05_z=_require_finite("q05_z", row["q05_z"]),
                median_z=_require_finite("median_z", row["median_z"]),
                q95_z=_require_finite("q95_z", row["q95_z"]),
            )
        )
    schema_version = _require_int("schema_version", root["schema_version"])
    if schema_version != 1:
        raise ValueError("schema_version must be 1")
    for name in ("source_commit", "config_sha256", "python_version", "platform"):
        if not isinstance(root[name], str):
            raise TypeError(f"{name} must be text")
    return Lab01Summary(
        schema_version=1,
        source_commit=cast(str, root["source_commit"]),
        config_sha256=cast(str, root["config_sha256"]),
        python_version=cast(str, root["python_version"]),
        platform=cast(str, root["platform"]),
        config=config,
        rows=tuple(rows),
    )
