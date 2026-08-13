# pyright: reportUnnecessaryIsInstance=false
"""Validated selected records for the Stage 3 manual model loop."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

from watermark_lab.lab03_config import Lab03Config, PromptFixture
from watermark_lab.manual_generation import GreenScore

Condition = Literal["control", "score_increase"]
StopReason = Literal["end_token", "token_limit"]


def _int(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _text(name: str, value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    if not allow_empty and not value:
        raise ValueError(f"{name} must not be empty")
    return value


def _sha(name: str, value: object, *, lengths: tuple[int, ...]) -> str:
    text = _text(name, value)
    if len(text) not in lengths or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be lowercase hexadecimal")
    return text


def _token_ids(name: str, values: object, *, allow_empty: bool = False) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of token IDs")
    checked = tuple(_int("token ID", item, minimum=0) for item in cast(Sequence[object], values))
    if not allow_empty and not checked:
        raise ValueError(f"{name} must not be empty")
    return checked


@dataclass(frozen=True, slots=True)
class CandidateTrace:
    """One leading candidate at one recorded generation position."""

    token_id: int
    token_text: str
    raw_score: float
    in_green_group: bool
    score_increase: float
    score_after_increase: float
    temperature_score: float
    final_probability: float
    selected: bool

    def __post_init__(self) -> None:
        _int("candidate token_id", self.token_id, minimum=0)
        _text("candidate token_text", self.token_text, allow_empty=True)
        _finite("candidate raw_score", self.raw_score)
        _finite("candidate score_increase", self.score_increase)
        _finite("candidate score_after_increase", self.score_after_increase)
        _finite("candidate temperature_score", self.temperature_score)
        probability = _finite("candidate final_probability", self.final_probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("candidate final_probability must be between zero and one")
        if not isinstance(self.in_green_group, bool) or not isinstance(self.selected, bool):
            raise TypeError("candidate flags must be Boolean")


@dataclass(frozen=True, slots=True)
class GenerationStep:
    """One complete model-score-to-token operation."""

    position: int
    input_length: int
    previous_token_id: int
    available_after_top_p: int
    available_after_top_k: int
    candidates: tuple[CandidateTrace, ...]
    selected_token_id: int
    selected_token_text: str
    selected_token_in_green_group: bool
    selected_raw_score: float
    selected_score_increase: float
    selected_score_after_increase: float
    selected_temperature_score: float
    selected_probability: float

    def __post_init__(self) -> None:
        _int("position", self.position, minimum=1)
        _int("input_length", self.input_length, minimum=1)
        _int("previous_token_id", self.previous_token_id, minimum=0)
        top_p = _int("available_after_top_p", self.available_after_top_p, minimum=1)
        top_k = _int("available_after_top_k", self.available_after_top_k, minimum=1)
        if top_k > top_p:
            raise ValueError("top-k cannot restore a candidate removed by top-p")
        if not isinstance(self.candidates, tuple) or not self.candidates:
            raise ValueError("candidates must be a non-empty tuple")
        if any(not isinstance(candidate, CandidateTrace) for candidate in self.candidates):
            raise TypeError("every candidate must be a CandidateTrace")
        _int("selected_token_id", self.selected_token_id, minimum=0)
        _text("selected_token_text", self.selected_token_text, allow_empty=True)
        if not isinstance(self.selected_token_in_green_group, bool):
            raise TypeError("selected_token_in_green_group must be Boolean")
        _finite("selected_raw_score", self.selected_raw_score)
        _finite("selected_score_increase", self.selected_score_increase)
        _finite("selected_score_after_increase", self.selected_score_after_increase)
        _finite("selected_temperature_score", self.selected_temperature_score)
        probability = _finite("selected_probability", self.selected_probability)
        if not 0.0 <= probability <= 1.0:
            raise ValueError("selected_probability must be between zero and one")
        selected_candidates = [candidate for candidate in self.candidates if candidate.selected]
        if len(selected_candidates) > 1:
            raise ValueError("at most one displayed candidate may be selected")


@dataclass(frozen=True, slots=True)
class ContinuationRecord:
    """One control or score-increase continuation and copied-text replay."""

    prompt_id: str
    prompt_text: str
    condition: Condition
    seed: int
    stop_reason: StopReason
    prompt_token_ids: tuple[int, ...]
    generated_token_ids: tuple[int, ...]
    decoded_text: str
    copied_token_ids: tuple[int, ...]
    copied_ids_match: bool
    generation_key_score: GreenScore
    comparison_key_score: GreenScore
    steps: tuple[GenerationStep, ...]

    def __post_init__(self) -> None:
        _text("prompt_id", self.prompt_id)
        _text("prompt_text", self.prompt_text)
        if self.condition not in ("control", "score_increase"):
            raise ValueError("condition must be control or score_increase")
        _int("seed", self.seed, minimum=0)
        if self.stop_reason not in ("end_token", "token_limit"):
            raise ValueError("stop_reason must be end_token or token_limit")
        _token_ids("prompt_token_ids", self.prompt_token_ids)
        generated = _token_ids("generated_token_ids", self.generated_token_ids)
        _text("decoded_text", self.decoded_text, allow_empty=True)
        copied = _token_ids("copied_token_ids", self.copied_token_ids)
        if not isinstance(self.copied_ids_match, bool):
            raise TypeError("copied_ids_match must be Boolean")
        if self.copied_ids_match != (generated == copied):
            raise ValueError("copied_ids_match does not match the recorded token IDs")
        if not isinstance(self.generation_key_score, GreenScore):
            raise TypeError("generation_key_score must be a GreenScore")
        if not isinstance(self.comparison_key_score, GreenScore):
            raise TypeError("comparison_key_score must be a GreenScore")
        if self.generation_key_score.key_role != "generation":
            raise ValueError("generation_key_score has the wrong role")
        if self.comparison_key_score.key_role != "comparison":
            raise ValueError("comparison_key_score has the wrong role")
        if not isinstance(self.steps, tuple) or len(self.steps) != len(generated):
            raise ValueError("steps must match generated_token_ids")
        for position, (step, token_id) in enumerate(
            zip(self.steps, generated, strict=True), start=1
        ):
            if not isinstance(step, GenerationStep):
                raise TypeError("every step must be a GenerationStep")
            if step.position != position or step.selected_token_id != token_id:
                raise ValueError("step order or selected token does not match generated IDs")


@dataclass(frozen=True, slots=True)
class Lab03Trace:
    """Complete deterministic selected evidence for the pinned local fixture."""

    schema_version: Literal[1]
    source_commit: str
    config_sha256: str
    python_version: str
    platform: str
    mlx_version: str
    mlx_lm_version: str
    config: Lab03Config
    records: tuple[ContinuationRecord, ...]

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        _sha("source_commit", self.source_commit, lengths=(40, 64))
        _sha("config_sha256", self.config_sha256, lengths=(64,))
        for name, value in (
            ("python_version", self.python_version),
            ("platform", self.platform),
            ("mlx_version", self.mlx_version),
            ("mlx_lm_version", self.mlx_lm_version),
        ):
            _text(name, value)
        if not isinstance(self.config, Lab03Config):
            raise TypeError("config must be a Lab03Config")
        expected_pairs = [
            (prompt.id, condition)
            for prompt in self.config.prompts
            for condition in ("control", "score_increase")
        ]
        actual_pairs = [(record.prompt_id, record.condition) for record in self.records]
        if actual_pairs != expected_pairs:
            raise ValueError("records must follow prompt order and control-before-increase order")


def trace_to_json_bytes(trace: Lab03Trace) -> bytes:
    """Serialize the trace as stable finite JSON."""

    text = json.dumps(asdict(trace), allow_nan=False, indent=2, sort_keys=True)
    return f"{text}\n".encode()


def trace_to_markdown_bytes(trace: Lab03Trace) -> bytes:
    """Render one complete token step and the six paired results."""

    config = trace.config
    spine = next(
        record
        for record in trace.records
        if record.prompt_id == "stage-02-continuity" and record.condition == "score_increase"
    )
    first = spine.steps[0]
    lines = [
        "# Stage 3 annotated manual-generation trace",
        "",
        "This measured local fixture used the pinned LFM2 model and tokenizer through MLX. It",
        "records where the configured score increase occurs in one explicit loop.",
        "",
        f"- Source commit: `{trace.source_commit}`",
        f"- Config SHA-256: `{trace.config_sha256}`",
        f"- Model revision: `{config.model_id}@{config.model_revision}`",
        f"- Runtime: Python `{trace.python_version}`, MLX `{trace.mlx_version}`, "
        f"MLX-LM `{trace.mlx_lm_version}` on `{trace.platform}`",
        "",
        "## First recorded token from the continuity prompt",
        "",
        f"Prompt: `{spine.prompt_text}`",
        "",
        f"The model received {first.input_length} token IDs. The previous token ID used by the",
        f"green-group calculation was `{first.previous_token_id}`. Top-p kept",
        f"{first.available_after_top_p} candidates, and top-k then kept",
        f"{first.available_after_top_k} candidates.",
        "",
        "| Token piece | ID | Model score | Green | Increase | After increase | "
        "After temperature | Final chance | Chosen |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for candidate in first.candidates:
        lines.append(
            f"| `{candidate.token_text}` | {candidate.token_id} | {candidate.raw_score:.6f} | "
            f"{'yes' if candidate.in_green_group else 'no'} | {candidate.score_increase:.1f} | "
            f"{candidate.score_after_increase:.6f} | {candidate.temperature_score:.6f} | "
            f"{candidate.final_probability:.6%} | "
            f"{'yes' if candidate.selected else 'no'} |"
        )
    lines.extend(
        [
            "",
            f"The seeded sampler chose `{first.selected_token_text}` (ID "
            f"`{first.selected_token_id}`) with final chance "
            f"`{first.selected_probability:.6%}`. The loop appended that ID before asking the "
            "model "
            "for the next score list.",
            "",
            "## Paired local results",
            "",
            "| Prompt | Score increase | Tokens | Copied IDs match | Same-key G/T | Same-key z | "
            "Comparison-key G/T | Comparison-key z |",
            "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for record in trace.records:
        generation = record.generation_key_score
        comparison = record.comparison_key_score
        lines.append(
            f"| `{record.prompt_id}` | {'off' if record.condition == 'control' else 'on'} | "
            f"{len(record.generated_token_ids)} | {'yes' if record.copied_ids_match else 'no'} | "
            f"{generation.green_hits}/{generation.eligible_tokens} | {generation.z_score:.6f} | "
            f"{comparison.green_hits}/{comparison.eligible_tokens} | {comparison.z_score:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "These six continuations show deterministic replay for this pinned local fixture. "
            "Three",
            "prompts do not measure detection accuracy or language quality. Stage 3 has no tested",
            "cutoff, and no score proves AI origin, authorship, or use of a private vendor system.",
            "",
        ]
    )
    return "\n".join(lines).encode()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be an object")
    return cast(Mapping[str, object], value)


def _keys(mapping: Mapping[str, object], expected: set[str], name: str) -> None:
    if set(mapping) != expected:
        raise ValueError(f"{name} keys differ: expected {sorted(expected)}, got {sorted(mapping)}")


def _array(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be an array")
    return cast(list[object], value)


def _score_from_mapping(value: object) -> GreenScore:
    mapping = _mapping(value, "score")
    _keys(
        mapping,
        {"key_role", "green_hits", "eligible_tokens", "expected_green_hits", "z_score"},
        "score",
    )
    role = _text("key_role", mapping["key_role"])
    if role not in ("generation", "comparison"):
        raise ValueError("key_role must be generation or comparison")
    return GreenScore(
        key_role=role,
        green_hits=_int("green_hits", mapping["green_hits"], minimum=0),
        eligible_tokens=_int("eligible_tokens", mapping["eligible_tokens"], minimum=1),
        expected_green_hits=_finite("expected_green_hits", mapping["expected_green_hits"]),
        z_score=_finite("z_score", mapping["z_score"]),
    )


def _candidate_from_mapping(value: object) -> CandidateTrace:
    mapping = _mapping(value, "candidate")
    expected = set(CandidateTrace.__dataclass_fields__)
    _keys(mapping, expected, "candidate")
    return CandidateTrace(
        token_id=_int("token_id", mapping["token_id"], minimum=0),
        token_text=_text("token_text", mapping["token_text"], allow_empty=True),
        raw_score=_finite("raw_score", mapping["raw_score"]),
        in_green_group=cast(bool, mapping["in_green_group"]),
        score_increase=_finite("score_increase", mapping["score_increase"]),
        score_after_increase=_finite("score_after_increase", mapping["score_after_increase"]),
        temperature_score=_finite("temperature_score", mapping["temperature_score"]),
        final_probability=_finite("final_probability", mapping["final_probability"]),
        selected=cast(bool, mapping["selected"]),
    )


def _step_from_mapping(value: object) -> GenerationStep:
    mapping = _mapping(value, "step")
    _keys(mapping, set(GenerationStep.__dataclass_fields__), "step")
    return GenerationStep(
        position=_int("position", mapping["position"], minimum=1),
        input_length=_int("input_length", mapping["input_length"], minimum=1),
        previous_token_id=_int("previous_token_id", mapping["previous_token_id"], minimum=0),
        available_after_top_p=_int(
            "available_after_top_p", mapping["available_after_top_p"], minimum=1
        ),
        available_after_top_k=_int(
            "available_after_top_k", mapping["available_after_top_k"], minimum=1
        ),
        candidates=tuple(
            _candidate_from_mapping(item) for item in _array(mapping["candidates"], "candidates")
        ),
        selected_token_id=_int("selected_token_id", mapping["selected_token_id"], minimum=0),
        selected_token_text=_text(
            "selected_token_text", mapping["selected_token_text"], allow_empty=True
        ),
        selected_token_in_green_group=cast(bool, mapping["selected_token_in_green_group"]),
        selected_raw_score=_finite("selected_raw_score", mapping["selected_raw_score"]),
        selected_score_increase=_finite(
            "selected_score_increase", mapping["selected_score_increase"]
        ),
        selected_score_after_increase=_finite(
            "selected_score_after_increase", mapping["selected_score_after_increase"]
        ),
        selected_temperature_score=_finite(
            "selected_temperature_score", mapping["selected_temperature_score"]
        ),
        selected_probability=_finite("selected_probability", mapping["selected_probability"]),
    )


def _config_from_mapping(value: object) -> Lab03Config:
    mapping = _mapping(value, "config")
    _keys(mapping, set(Lab03Config.__dataclass_fields__), "config")
    prompts: list[PromptFixture] = []
    for item in _array(mapping["prompts"], "prompts"):
        prompt = _mapping(item, "prompt")
        _keys(prompt, {"id", "text"}, "prompt")
        prompts.append(
            PromptFixture(
                id=_text("prompt id", prompt["id"]), text=_text("prompt text", prompt["text"])
            )
        )
    return Lab03Config(
        model_id=_text("model_id", mapping["model_id"]),
        model_revision=_text("model_revision", mapping["model_revision"]),
        base_seed=_int("base_seed", mapping["base_seed"], minimum=0),
        max_new_tokens=_int("max_new_tokens", mapping["max_new_tokens"], minimum=2),
        temperature=_finite("temperature", mapping["temperature"]),
        top_k=_int("top_k", mapping["top_k"], minimum=1),
        top_p=_finite("top_p", mapping["top_p"]),
        green_fraction=_finite("green_fraction", mapping["green_fraction"]),
        watermark_bias=_finite("watermark_bias", mapping["watermark_bias"]),
        generation_key=_int("generation_key", mapping["generation_key"], minimum=1),
        comparison_key=_int("comparison_key", mapping["comparison_key"], minimum=1),
        selector_profile=_text("selector_profile", mapping["selector_profile"]),
        context_width=_int("context_width", mapping["context_width"], minimum=1),
        trace_candidates=_int("trace_candidates", mapping["trace_candidates"], minimum=1),
        prompts=tuple(prompts),
    )


def _record_from_mapping(value: object) -> ContinuationRecord:
    mapping = _mapping(value, "record")
    _keys(mapping, set(ContinuationRecord.__dataclass_fields__), "record")
    condition = _text("condition", mapping["condition"])
    stop_reason = _text("stop_reason", mapping["stop_reason"])
    return ContinuationRecord(
        prompt_id=_text("prompt_id", mapping["prompt_id"]),
        prompt_text=_text("prompt_text", mapping["prompt_text"]),
        condition=cast(Condition, condition),
        seed=_int("seed", mapping["seed"], minimum=0),
        stop_reason=cast(StopReason, stop_reason),
        prompt_token_ids=_token_ids("prompt_token_ids", mapping["prompt_token_ids"]),
        generated_token_ids=_token_ids("generated_token_ids", mapping["generated_token_ids"]),
        decoded_text=_text("decoded_text", mapping["decoded_text"], allow_empty=True),
        copied_token_ids=_token_ids("copied_token_ids", mapping["copied_token_ids"]),
        copied_ids_match=cast(bool, mapping["copied_ids_match"]),
        generation_key_score=_score_from_mapping(mapping["generation_key_score"]),
        comparison_key_score=_score_from_mapping(mapping["comparison_key_score"]),
        steps=tuple(_step_from_mapping(item) for item in _array(mapping["steps"], "steps")),
    )


def trace_from_json_bytes(payload: bytes) -> Lab03Trace:
    """Parse selected JSON and reject non-finite or unknown values."""

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON value {value!r} is forbidden")

    parsed: Any = json.loads(payload, parse_constant=reject_constant)
    mapping = _mapping(parsed, "trace")
    _keys(mapping, set(Lab03Trace.__dataclass_fields__), "trace")
    return Lab03Trace(
        schema_version=cast(Literal[1], _int("schema_version", mapping["schema_version"])),
        source_commit=_text("source_commit", mapping["source_commit"]),
        config_sha256=_text("config_sha256", mapping["config_sha256"]),
        python_version=_text("python_version", mapping["python_version"]),
        platform=_text("platform", mapping["platform"]),
        mlx_version=_text("mlx_version", mapping["mlx_version"]),
        mlx_lm_version=_text("mlx_lm_version", mapping["mlx_lm_version"]),
        config=_config_from_mapping(mapping["config"]),
        records=tuple(_record_from_mapping(item) for item in _array(mapping["records"], "records")),
    )
