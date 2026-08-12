# pyright: reportUnnecessaryIsInstance=false
"""Validated configuration and deterministic trace records for Stage 2."""

from __future__ import annotations

import json
import math
import random
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

from watermark_lab.stats import green_hit_z_score
from watermark_lab.toy_greenlist import (
    apply_green_logit_bias,
    green_token_count,
    sample_from_probabilities,
    softmax,
    toy_green_token_ids,
)


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


def _require_sha(name: str, value: object, *, lengths: tuple[int, ...]) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    if len(value) not in lengths or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{name} must be lowercase hexadecimal")
    return value


@dataclass(frozen=True, slots=True)
class Lab02ConfigSnapshot:
    base_seed: int
    development_key: str
    gamma: float
    delta: float
    context_width: int
    steps: int
    vocabulary: tuple[str, ...]
    initial_context: tuple[int, ...]
    raw_logits: tuple[float, ...]

    def __post_init__(self) -> None:
        _require_int("base_seed", self.base_seed)
        if not isinstance(self.development_key, str):
            raise TypeError("development_key must be text")
        if not self.development_key or not self.development_key.isascii():
            raise ValueError("development_key must be non-empty ASCII text")
        gamma = _require_finite("gamma", self.gamma)
        delta = _require_finite("delta", self.delta)
        if delta < 0.0:
            raise ValueError("delta must be non-negative")
        width = _require_int("context_width", self.context_width, minimum=1)
        _require_int("steps", self.steps, minimum=1)
        if not isinstance(self.vocabulary, tuple) or len(self.vocabulary) < 2:
            raise TypeError("vocabulary must be a tuple with at least two labels")
        if any(
            not isinstance(label, str) or not label or not label.isascii()
            for label in self.vocabulary
        ):
            raise ValueError("vocabulary labels must be non-empty ASCII text")
        if len(set(self.vocabulary)) != len(self.vocabulary):
            raise ValueError("vocabulary labels must be unique")
        green_token_count(vocabulary_size=len(self.vocabulary), gamma=gamma)
        if not isinstance(self.initial_context, tuple):
            raise TypeError("initial_context must be a tuple")
        if len(self.initial_context) != width:
            raise ValueError("initial_context length must equal context_width")
        for token_id in self.initial_context:
            checked_id = _require_int("initial context token ID", token_id, minimum=0)
            if checked_id >= len(self.vocabulary):
                raise ValueError("initial_context contains an ID outside the vocabulary")
        if not isinstance(self.raw_logits, tuple):
            raise TypeError("raw_logits must be a tuple")
        if len(self.raw_logits) != len(self.vocabulary):
            raise ValueError("raw_logits length must equal vocabulary length")
        for logit in self.raw_logits:
            _require_finite("raw logit", logit)


@dataclass(frozen=True, slots=True)
class Lab02TraceStep:
    position: int
    context: tuple[int, ...]
    green_token_ids: tuple[int, ...]
    raw_logits: tuple[float, ...]
    adjusted_logits: tuple[float, ...]
    baseline_probabilities: tuple[float, ...]
    watermarked_probabilities: tuple[float, ...]
    sample_draw: float
    baseline_token_id: int
    sampled_token_id: int
    sampled_token_is_green: bool
    green_hits: int
    eligible_tokens: int
    z_score: float


@dataclass(frozen=True, slots=True)
class Lab02Trace:
    schema_version: Literal[1]
    source_commit: str
    config_sha256: str
    config: Lab02ConfigSnapshot
    steps: tuple[Lab02TraceStep, ...]

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        _require_sha("source_commit", self.source_commit, lengths=(40, 64))
        _require_sha("config_sha256", self.config_sha256, lengths=(64,))
        if not isinstance(self.config, Lab02ConfigSnapshot):
            raise TypeError("config must be a Lab02ConfigSnapshot")
        if not isinstance(self.steps, tuple) or len(self.steps) != self.config.steps:
            raise ValueError("steps must match the configured step count")
        generated: list[int] = []
        hits = 0
        for position, step in enumerate(self.steps, start=1):
            if not isinstance(step, Lab02TraceStep):
                raise TypeError("every step must be a Lab02TraceStep")
            expected_context = tuple(
                ([*self.config.initial_context, *generated])[-self.config.context_width :]
            )
            expected_green = toy_green_token_ids(
                vocabulary_size=len(self.config.vocabulary),
                context=expected_context,
                development_key=self.config.development_key,
                gamma=self.config.gamma,
            )
            expected_adjusted = apply_green_logit_bias(
                logits=self.config.raw_logits,
                green_token_ids=expected_green,
                delta=self.config.delta,
            )
            expected_baseline = softmax(logits=self.config.raw_logits)
            expected_watermarked = softmax(logits=expected_adjusted)
            baseline_token = sample_from_probabilities(
                probabilities=expected_baseline, draw=step.sample_draw
            )
            sampled_token = sample_from_probabilities(
                probabilities=expected_watermarked, draw=step.sample_draw
            )
            hit = sampled_token in expected_green
            hits += int(hit)
            expected_z = green_hit_z_score(
                hits=hits, trials=position, null_probability=self.config.gamma
            )
            expected = (
                position,
                expected_context,
                expected_green,
                self.config.raw_logits,
                expected_adjusted,
                expected_baseline,
                expected_watermarked,
                baseline_token,
                sampled_token,
                hit,
                hits,
                position,
                expected_z,
            )
            actual = (
                step.position,
                step.context,
                step.green_token_ids,
                step.raw_logits,
                step.adjusted_logits,
                step.baseline_probabilities,
                step.watermarked_probabilities,
                step.baseline_token_id,
                step.sampled_token_id,
                step.sampled_token_is_green,
                step.green_hits,
                step.eligible_tokens,
                step.z_score,
            )
            if actual != expected:
                raise ValueError(f"trace step {position} does not match deterministic replay")
            generated.append(sampled_token)


def build_lab02_trace(
    *, source_commit: str, config_sha256: str, config: Lab02ConfigSnapshot
) -> Lab02Trace:
    """Build the fixed generation trace and replay its detector state."""

    generator = random.Random(config.base_seed)
    baseline_probabilities = softmax(logits=config.raw_logits)
    generated: list[int] = []
    hits = 0
    rows: list[Lab02TraceStep] = []
    for position in range(1, config.steps + 1):
        context = tuple(([*config.initial_context, *generated])[-config.context_width :])
        green_ids = toy_green_token_ids(
            vocabulary_size=len(config.vocabulary),
            context=context,
            development_key=config.development_key,
            gamma=config.gamma,
        )
        adjusted = apply_green_logit_bias(
            logits=config.raw_logits, green_token_ids=green_ids, delta=config.delta
        )
        watermarked_probabilities = softmax(logits=adjusted)
        draw = generator.random()
        baseline_token = sample_from_probabilities(probabilities=baseline_probabilities, draw=draw)
        sampled_token = sample_from_probabilities(
            probabilities=watermarked_probabilities, draw=draw
        )
        is_green = sampled_token in green_ids
        hits += int(is_green)
        rows.append(
            Lab02TraceStep(
                position=position,
                context=context,
                green_token_ids=green_ids,
                raw_logits=config.raw_logits,
                adjusted_logits=adjusted,
                baseline_probabilities=baseline_probabilities,
                watermarked_probabilities=watermarked_probabilities,
                sample_draw=draw,
                baseline_token_id=baseline_token,
                sampled_token_id=sampled_token,
                sampled_token_is_green=is_green,
                green_hits=hits,
                eligible_tokens=position,
                z_score=green_hit_z_score(
                    hits=hits, trials=position, null_probability=config.gamma
                ),
            )
        )
        generated.append(sampled_token)
    return Lab02Trace(
        schema_version=1,
        source_commit=source_commit,
        config_sha256=config_sha256,
        config=config,
        steps=tuple(rows),
    )


def trace_to_json_bytes(trace: Lab02Trace) -> bytes:
    """Serialize the selected trace as stable, finite UTF-8 JSON."""

    text = json.dumps(asdict(trace), allow_nan=False, indent=2, sort_keys=True)
    return f"{text}\n".encode()


def trace_to_markdown_bytes(trace: Lab02Trace) -> bytes:
    """Render every Stage 2 number in a compact hand-checkable trace."""

    config = trace.config
    green_count = green_token_count(vocabulary_size=len(config.vocabulary), gamma=config.gamma)
    lines = [
        "# Stage 2 annotated toy-vocabulary trace",
        "",
        "This deterministic trace uses a 20-item teaching vocabulary. The SHA-256 selector is",
        "a toy rule, not an upstream KGW pseudorandom function or a deployment key system.",
        "",
        f"- Source commit: `{trace.source_commit}`",
        f"- Config SHA-256: `{trace.config_sha256}`",
        f"- Public development key: `{config.development_key}`",
        f"- Green fraction: `{config.gamma}` ({green_count} of {len(config.vocabulary)} IDs)",
        f"- Logit bias: `{config.delta}` "
        f"(`exp(delta) = {math.exp(config.delta):.6f}` before normalization)",
        f"- Initial context IDs: `{list(config.initial_context)}`",
        "",
    ]
    for step in trace.steps:
        baseline_label = config.vocabulary[step.baseline_token_id]
        sampled_label = config.vocabulary[step.sampled_token_id]
        lines.extend(
            [
                f"## Position {step.position}",
                "",
                f"Context: `{list(step.context)}`. Green IDs: `{list(step.green_token_ids)}`.",
                f"The visible draw is `{step.sample_draw:.12f}`. Without bias it selects "
                f"`{step.baseline_token_id}:{baseline_label}`. With bias it selects "
                f"`{step.sampled_token_id}:{sampled_label}`.",
                f"Detector replay: `G={step.green_hits}`, `T={step.eligible_tokens}`, "
                f"`z={step.z_score:.12f}`.",
                "",
                "| ID | Label | Green | Raw logit | Adjusted logit | "
                "Baseline probability | Watermarked probability |",
                "|---:|---|:---:|---:|---:|---:|---:|",
            ]
        )
        for token_id, label in enumerate(config.vocabulary):
            lines.append(
                f"| {token_id} | {label} | {'yes' if token_id in step.green_token_ids else 'no'} | "
                f"{step.raw_logits[token_id]:.6f} | {step.adjusted_logits[token_id]:.6f} | "
                f"{step.baseline_probabilities[token_id]:.12f} | "
                f"{step.watermarked_probabilities[token_id]:.12f} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Claim boundary",
            "",
            "This trace shows how this configured toy selector and public key change token odds",
            "and how the detector replays the same choices. It does not measure language quality,",
            "an LLM watermark, a false-positive rate, or Anthropic's private implementation.",
            "",
        ]
    )
    return "\n".join(lines).encode()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a JSON object")
    untyped = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in untyped):
        raise TypeError(f"{name} must be a JSON object")
    return cast(Mapping[str, object], untyped)


def _exact_keys(mapping: Mapping[str, object], expected: set[str], name: str) -> None:
    if set(mapping) != expected:
        raise ValueError(f"{name} keys differ: expected {sorted(expected)}, got {sorted(mapping)}")


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be a JSON array")
    return cast(list[object], value)


def _int_tuple(value: object, name: str) -> tuple[int, ...]:
    return tuple(_require_int(f"{name} item", item) for item in _list(value, name))


def _float_tuple(value: object, name: str) -> tuple[float, ...]:
    return tuple(_require_finite(f"{name} item", item) for item in _list(value, name))


def trace_from_json_bytes(payload: bytes) -> Lab02Trace:
    """Parse a trace while rejecting unknown fields and non-finite numbers."""

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number is not allowed: {value}")

    parsed: Any = json.loads(payload.decode("utf-8"), parse_constant=reject_constant)
    root = _mapping(parsed, "trace")
    _exact_keys(
        root, {"schema_version", "source_commit", "config_sha256", "config", "steps"}, "trace"
    )
    config_data = _mapping(root["config"], "config")
    config_keys = {
        "base_seed",
        "development_key",
        "gamma",
        "delta",
        "context_width",
        "steps",
        "vocabulary",
        "initial_context",
        "raw_logits",
    }
    _exact_keys(config_data, config_keys, "config")
    vocabulary_items = _list(config_data["vocabulary"], "vocabulary")
    if not all(isinstance(item, str) for item in vocabulary_items):
        raise TypeError("every vocabulary label must be text")
    key = config_data["development_key"]
    if not isinstance(key, str):
        raise TypeError("development_key must be text")
    config = Lab02ConfigSnapshot(
        base_seed=_require_int("base_seed", config_data["base_seed"]),
        development_key=key,
        gamma=_require_finite("gamma", config_data["gamma"]),
        delta=_require_finite("delta", config_data["delta"]),
        context_width=_require_int("context_width", config_data["context_width"], minimum=1),
        steps=_require_int("steps", config_data["steps"], minimum=1),
        vocabulary=tuple(cast(list[str], vocabulary_items)),
        initial_context=_int_tuple(config_data["initial_context"], "initial_context"),
        raw_logits=_float_tuple(config_data["raw_logits"], "raw_logits"),
    )
    step_keys = {
        "position",
        "context",
        "green_token_ids",
        "raw_logits",
        "adjusted_logits",
        "baseline_probabilities",
        "watermarked_probabilities",
        "sample_draw",
        "baseline_token_id",
        "sampled_token_id",
        "sampled_token_is_green",
        "green_hits",
        "eligible_tokens",
        "z_score",
    }
    rows: list[Lab02TraceStep] = []
    for index, value in enumerate(_list(root["steps"], "steps")):
        row = _mapping(value, f"steps[{index}]")
        _exact_keys(row, step_keys, f"steps[{index}]")
        is_green = row["sampled_token_is_green"]
        if not isinstance(is_green, bool):
            raise TypeError("sampled_token_is_green must be a boolean")
        rows.append(
            Lab02TraceStep(
                position=_require_int("position", row["position"], minimum=1),
                context=_int_tuple(row["context"], "context"),
                green_token_ids=_int_tuple(row["green_token_ids"], "green_token_ids"),
                raw_logits=_float_tuple(row["raw_logits"], "raw_logits"),
                adjusted_logits=_float_tuple(row["adjusted_logits"], "adjusted_logits"),
                baseline_probabilities=_float_tuple(
                    row["baseline_probabilities"], "baseline_probabilities"
                ),
                watermarked_probabilities=_float_tuple(
                    row["watermarked_probabilities"], "watermarked_probabilities"
                ),
                sample_draw=_require_finite("sample_draw", row["sample_draw"]),
                baseline_token_id=_require_int(
                    "baseline_token_id", row["baseline_token_id"], minimum=0
                ),
                sampled_token_id=_require_int(
                    "sampled_token_id", row["sampled_token_id"], minimum=0
                ),
                sampled_token_is_green=is_green,
                green_hits=_require_int("green_hits", row["green_hits"], minimum=0),
                eligible_tokens=_require_int("eligible_tokens", row["eligible_tokens"], minimum=1),
                z_score=_require_finite("z_score", row["z_score"]),
            )
        )
    schema_version = _require_int("schema_version", root["schema_version"])
    if schema_version != 1:
        raise ValueError("schema_version must be 1")
    return Lab02Trace(
        schema_version=1,
        source_commit=_require_sha("source_commit", root["source_commit"], lengths=(40, 64)),
        config_sha256=_require_sha("config_sha256", root["config_sha256"], lengths=(64,)),
        config=config,
        steps=tuple(rows),
    )
