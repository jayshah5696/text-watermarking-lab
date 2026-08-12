from __future__ import annotations

import hashlib
import json
import random
from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.lab02_config import config_from_toml_bytes
from watermark_lab.lab02_records import (
    Lab02ConfigSnapshot,
    Lab02Trace,
    build_lab02_trace,
    trace_from_json_bytes,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)
from watermark_lab.toy_greenlist import toy_green_token_ids

ROOT = Path(__file__).resolve().parents[2]


def _config() -> Lab02ConfigSnapshot:
    return config_from_toml_bytes((ROOT / "configs/lab_02.toml").read_bytes())


def _trace() -> Lab02Trace:
    payload = (ROOT / "configs/lab_02.toml").read_bytes()
    return build_lab02_trace(
        source_commit="a" * 40,
        config_sha256=hashlib.sha256(payload).hexdigest(),
        config=config_from_toml_bytes(payload),
    )


def test_fixed_trace_replays_generation_and_detector() -> None:
    trace = _trace()
    observed = [
        (
            step.context,
            step.green_token_ids,
            step.baseline_token_id,
            step.sampled_token_id,
            step.green_hits,
            step.z_score,
        )
        for step in trace.steps
    ]
    assert observed == [
        ((3, 7, 11, 15), (0, 10, 11, 12, 14), 0, 0, 1, 1.7320508075688774),
        ((7, 11, 15, 0), (2, 4, 9, 11, 17), 0, 1, 1, 0.8164965809277261),
        ((11, 15, 0, 1), (8, 12, 15, 16, 19), 0, 1, 1, 0.3333333333333333),
        ((15, 0, 1, 1), (2, 5, 6, 10, 11), 1, 2, 2, 1.1547005383792517),
    ]


def test_trace_does_not_change_global_random_state() -> None:
    state = random.getstate()
    _trace()
    assert random.getstate() == state


def test_wrong_key_does_not_replay_the_recorded_hits() -> None:
    trace = _trace()
    config = trace.config
    history = list(config.initial_context)
    wrong_key_hits = 0
    for step in trace.steps:
        wrong_green = toy_green_token_ids(
            vocabulary_size=len(config.vocabulary),
            context=tuple(history[-config.context_width :]),
            development_key="wrong-public-key",
            gamma=config.gamma,
        )
        wrong_key_hits += int(step.sampled_token_id in wrong_green)
        history.append(step.sampled_token_id)
    assert wrong_key_hits == 0
    assert trace.steps[-1].green_hits == 2


def test_trace_json_round_trip_is_byte_stable() -> None:
    payload = trace_to_json_bytes(_trace())
    assert trace_to_json_bytes(trace_from_json_bytes(payload)) == payload
    assert payload.endswith(b"\n")


def test_markdown_contains_every_step_and_claim_boundary() -> None:
    markdown = trace_to_markdown_bytes(_trace()).decode()
    assert markdown.count("## Position") == 4
    assert "exp(2.0) = 7.389056" in markdown
    assert "same-context no-boost comparison" in markdown
    assert "Original probability (no boost)" in markdown
    assert "not an upstream KGW" in markdown
    assert "## Claim boundary" in markdown


def test_trace_rejects_modified_step() -> None:
    trace = _trace()
    bad_step = replace(trace.steps[0], sampled_token_id=19)
    with pytest.raises(ValueError, match="deterministic replay"):
        replace(trace, steps=(bad_step, *trace.steps[1:]))


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("schema_version", 2, ValueError),
        ("source_commit", "bad", ValueError),
        ("source_commit", 7, TypeError),
        ("config_sha256", "a" * 63, ValueError),
        ("config", "bad", TypeError),
        ("steps", (), ValueError),
    ],
)
def test_trace_rejects_invalid_root_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_trace(), **{field: value})


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("base_seed", True, TypeError),
        ("development_key", 7, TypeError),
        ("development_key", "", ValueError),
        ("gamma", float("nan"), ValueError),
        ("delta", -1.0, ValueError),
        ("context_width", 0, ValueError),
        ("steps", 0, ValueError),
        ("vocabulary", ["a", "b"], TypeError),
        ("vocabulary", ("a", "a"), ValueError),
        ("vocabulary", ("a", "café"), ValueError),
        ("initial_context", [3, 7, 11, 15], TypeError),
        ("initial_context", (3,), ValueError),
        ("initial_context", (3, 7, 11, 20), ValueError),
        ("raw_logits", [0.0] * 20, TypeError),
        ("raw_logits", (0.0,), ValueError),
        ("raw_logits", (0.0,) * 19 + (float("inf"),), ValueError),
    ],
)
def test_config_record_rejects_invalid_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_config(), **{field: value})


def test_json_parser_rejects_unknown_root_field() -> None:
    data = json.loads(trace_to_json_bytes(_trace()))
    data["unknown"] = 1
    with pytest.raises(ValueError, match="keys differ"):
        trace_from_json_bytes(json.dumps(data).encode())


def test_json_parser_rejects_unknown_config_and_step_fields() -> None:
    data = json.loads(trace_to_json_bytes(_trace()))
    data["config"]["unknown"] = 1
    with pytest.raises(ValueError, match="keys differ"):
        trace_from_json_bytes(json.dumps(data).encode())
    data = json.loads(trace_to_json_bytes(_trace()))
    data["steps"][0]["unknown"] = 1
    with pytest.raises(ValueError, match="keys differ"):
        trace_from_json_bytes(json.dumps(data).encode())


@pytest.mark.parametrize(
    ("path", "value", "error"),
    [
        (("schema_version",), True, TypeError),
        (("source_commit",), 7, TypeError),
        (("config", "vocabulary"), "bad", TypeError),
        (("config", "vocabulary", 0), 7, TypeError),
        (("steps",), "bad", TypeError),
        (("steps", 0, "sampled_token_is_green"), 1, TypeError),
        (("steps", 0, "sample_draw"), float("nan"), ValueError),
    ],
)
def test_json_parser_rejects_invalid_shapes(
    path: tuple[object, ...], value: object, error: type[Exception]
) -> None:
    data = json.loads(trace_to_json_bytes(_trace()))
    target = data
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value
    payload = json.dumps(data, allow_nan=True).encode()
    with pytest.raises(error):
        trace_from_json_bytes(payload)


def test_json_parser_rejects_nonfinite_literal() -> None:
    payload = trace_to_json_bytes(_trace()).replace(
        b'"sample_draw": 0.03533183782698912', b'"sample_draw": NaN'
    )
    with pytest.raises(ValueError, match="non-finite"):
        trace_from_json_bytes(payload)
