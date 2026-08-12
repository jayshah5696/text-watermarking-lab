from __future__ import annotations

import json
from dataclasses import replace
from typing import Literal, cast

import pytest

from watermark_lab.records import (
    Condition,
    ConditionSummary,
    Lab01ConfigSnapshot,
    build_condition_summary,
    build_lab01_summary,
    summary_from_json_bytes,
    summary_to_json_bytes,
)


def _config() -> Lab01ConfigSnapshot:
    return Lab01ConfigSnapshot(
        base_seed=20260811,
        lengths=(4,),
        replicates=4,
        null_hit_probability=0.25,
        alternative_hit_probability=0.40,
        z_threshold=3.0,
    )


def _row(condition: Condition) -> ConditionSummary:
    return build_condition_summary(
        length=4,
        condition=condition,
        hit_probability=0.25 if condition == "null" else 0.40,
        hit_counts=(0, 1, 2, 4),
        null_probability=0.25,
        z_threshold=3.0,
    )


def _summary():
    return build_lab01_summary(
        source_commit="a" * 40,
        config_sha256="b" * 64,
        python_version="3.12.7",
        platform="test-platform",
        config=_config(),
        rows=(_row("biased"), _row("null")),
    )


def test_valid_round_trip_produces_stable_bytes_and_sorts_rows() -> None:
    summary = _summary()
    assert [row.condition for row in summary.rows] == ["null", "biased"]
    payload = summary_to_json_bytes(summary)
    assert payload.endswith(b"\n")
    assert summary_to_json_bytes(summary_from_json_bytes(payload)) == payload


def test_condition_summary_rejects_unknown_condition() -> None:
    with pytest.raises(ValueError, match="condition"):
        replace(_row("null"), condition=cast(Condition, "unknown"))


@pytest.mark.parametrize(
    "changes",
    [
        {"base_seed": True},
        {"lengths": cast(tuple[int, ...], [4])},
        {"lengths": ()},
        {"lengths": (4, 4)},
        {"replicates": 0},
        {"null_hit_probability": 0.0},
        {"alternative_hit_probability": float("nan")},
        {"z_threshold": "three"},
    ],
)
def test_config_rejects_invalid_domains_and_types(changes: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        replace(_config(), **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"detections": 5},
        {"detection_rate": 0.5},
        {"hit_probability": 1.0},
        {"replicates": True},
        {"monte_carlo_standard_error": -0.1},
        {"mean_hits": 5.0},
        {"mean_z": float("nan")},
        {"q05_z": 10.0},
    ],
)
def test_condition_summary_rejects_invalid_counts_rates_and_order(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        replace(_row("null"), **changes)


def test_condition_builder_rejects_empty_counts() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        build_condition_summary(
            length=4,
            condition="null",
            hit_probability=0.25,
            hit_counts=(),
            null_probability=0.25,
            z_threshold=3.0,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": cast(Literal[1], 2)},
        {"source_commit": "not-a-commit"},
        {"config_sha256": "bad"},
        {"python_version": ""},
        {"platform": cast(str, 3)},
        {"config": cast(Lab01ConfigSnapshot, object())},
        {"rows": cast(tuple[ConditionSummary, ...], [])},
        {"rows": (_row("null"),)},
        {"rows": (_row("null"), replace(_row("biased"), hit_probability=0.41))},
        {
            "rows": (
                _row("null"),
                replace(
                    _row("biased"),
                    replicates=5,
                    detections=0,
                    detection_rate=0.0,
                    monte_carlo_standard_error=0.0,
                ),
            )
        },
    ],
)
def test_summary_rejects_invalid_provenance_shape_and_row_contract(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        replace(_summary(), **changes)


def test_json_rejects_unknown_fields() -> None:
    payload = summary_to_json_bytes(_summary()).replace(b'"schema_version": 1', b'"extra": 1')
    with pytest.raises(ValueError, match="keys differ"):
        summary_from_json_bytes(payload)


@pytest.mark.parametrize(
    ("path", "value", "error"),
    [
        (("config", "lengths"), "not-an-array", TypeError),
        (("rows",), "not-an-array", TypeError),
        (("schema_version",), 2, ValueError),
        (("source_commit",), 3, TypeError),
        (("rows", 0, "condition"), "unknown", ValueError),
        (("rows", 0, "length"), True, TypeError),
    ],
)
def test_json_rejects_invalid_nested_shapes(
    path: tuple[object, ...], value: object, error: type[Exception]
) -> None:
    data = json.loads(summary_to_json_bytes(_summary()))
    target = data
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = value
    with pytest.raises(error):
        summary_from_json_bytes(json.dumps(data).encode())


def test_json_rejects_non_object_root() -> None:
    with pytest.raises(TypeError, match="JSON object"):
        summary_from_json_bytes(b"[]")


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_json_rejects_non_finite_numbers(constant: bytes) -> None:
    data = json.loads(summary_to_json_bytes(_summary()))
    data["rows"][0]["mean_z"] = float(constant.decode())
    payload = json.dumps(data).encode()
    with pytest.raises(ValueError, match="non-finite"):
        summary_from_json_bytes(payload)
