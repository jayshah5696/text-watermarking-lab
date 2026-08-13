# pyright: reportUnnecessaryIsInstance=false
"""Strict loading for the locked Stage 4 Transformers fixture."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

ROOT_KEYS = {
    "schema_version",
    "model_id",
    "model_revision",
    "model_license",
    "model_safetensors_bytes",
    "device",
    "base_seed",
    "max_new_tokens",
    "temperature",
    "top_k",
    "top_p",
    "green_fraction",
    "watermark_bias",
    "generation_key",
    "comparison_key",
    "seeding_scheme",
    "context_width",
    "z_threshold",
    "trace_candidates",
    "reference_processor_order",
    "stage_03_processor_order",
    "prompts",
}
PROMPT_KEYS = {"id", "text"}
REFERENCE_ORDER = ("temperature", "top_k", "top_p", "watermark")
STAGE_03_ORDER = ("watermark", "temperature", "top_p", "top_k")


def _integer(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"config field {name!r} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"config field {name!r} must be at least {minimum}")
    return value


def _number(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"config field {name!r} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"config field {name!r} must be finite")
    return result


def _text(name: str, value: object, *, ascii_only: bool = True) -> str:
    if not isinstance(value, str):
        raise TypeError(f"config field {name!r} must be text")
    if not value or (ascii_only and not value.isascii()):
        detail = "non-empty ASCII text" if ascii_only else "non-empty text"
        raise ValueError(f"config field {name!r} must be {detail}")
    return value


def _order(name: str, value: object, expected: tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"config field {name!r} must be an array")
    result = tuple(_text(name, item) for item in cast(Sequence[object], value))
    if result != expected:
        raise ValueError(f"config field {name!r} must be {list(expected)!r}")
    return result


@dataclass(frozen=True, slots=True)
class ReferencePrompt:
    """One fixed passage shared with Stage 3."""

    id: str
    text: str

    def __post_init__(self) -> None:
        _text("prompt id", self.id)
        _text("prompt text", self.text, ascii_only=False)


@dataclass(frozen=True, slots=True)
class Lab04Config:
    """Validated Stage 4 settings parsed from exact TOML bytes."""

    model_id: str
    model_revision: str
    model_license: str
    model_safetensors_bytes: int
    device: str
    base_seed: int
    max_new_tokens: int
    temperature: float
    top_k: int
    top_p: float
    green_fraction: float
    watermark_bias: float
    generation_key: int
    comparison_key: int
    seeding_scheme: str
    context_width: int
    z_threshold: float
    trace_candidates: int
    reference_processor_order: tuple[str, ...]
    stage_03_processor_order: tuple[str, ...]
    prompts: tuple[ReferencePrompt, ...]

    def __post_init__(self) -> None:
        if self.model_id != "openai-community/gpt2":
            raise ValueError("Stage 4 locks model_id to openai-community/gpt2")
        revision = _text("model_revision", self.model_revision)
        if len(revision) != 40 or any(
            character not in "0123456789abcdef" for character in revision
        ):
            raise ValueError("model_revision must be a 40-character lowercase Git SHA")
        if self.model_license != "mit":
            raise ValueError("Stage 4 locks the recorded model license to mit")
        _integer("model_safetensors_bytes", self.model_safetensors_bytes, minimum=1)
        if self.device != "cpu":
            raise ValueError("Stage 4 locks device to cpu")
        _integer("base_seed", self.base_seed, minimum=0)
        _integer("max_new_tokens", self.max_new_tokens, minimum=2)
        if _number("temperature", self.temperature) <= 0.0:
            raise ValueError("temperature must be greater than zero")
        _integer("top_k", self.top_k, minimum=1)
        top_p = _number("top_p", self.top_p)
        if not 0.0 < top_p <= 1.0:
            raise ValueError("top_p must be greater than zero and at most one")
        green_fraction = _number("green_fraction", self.green_fraction)
        if not 0.0 < green_fraction < 1.0:
            raise ValueError("green_fraction must be strictly between zero and one")
        if _number("watermark_bias", self.watermark_bias) < 0.0:
            raise ValueError("watermark_bias must be non-negative")
        _integer("generation_key", self.generation_key, minimum=1)
        _integer("comparison_key", self.comparison_key, minimum=1)
        if self.generation_key == self.comparison_key:
            raise ValueError("generation_key and comparison_key must differ")
        if self.seeding_scheme != "lefthash":
            raise ValueError("Stage 4 locks seeding_scheme to lefthash")
        if self.context_width != 1:
            raise ValueError("Stage 4 locks context_width to 1")
        _number("z_threshold", self.z_threshold)
        trace_candidates = _integer("trace_candidates", self.trace_candidates, minimum=1)
        if trace_candidates > self.top_k:
            raise ValueError("trace_candidates must not exceed top_k")
        if self.reference_processor_order != REFERENCE_ORDER:
            raise ValueError("Stage 4 locks the Transformers processor order")
        if self.stage_03_processor_order != STAGE_03_ORDER:
            raise ValueError("Stage 4 locks the Stage 3 comparison order")
        if not isinstance(self.prompts, tuple) or len(self.prompts) != 3:
            raise ValueError("Stage 4 requires exactly three prompts")
        if any(not isinstance(prompt, ReferencePrompt) for prompt in self.prompts):
            raise TypeError("every prompt must be a ReferencePrompt")
        if len({prompt.id for prompt in self.prompts}) != 3:
            raise ValueError("prompt IDs must be unique")


def config_from_toml_bytes(payload: bytes) -> Lab04Config:
    """Parse exact Stage 4 TOML bytes and reject implicit settings."""

    parsed: Any = tomllib.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise TypeError("config must be a TOML table")
    mapping = cast(Mapping[str, object], parsed)
    if set(mapping) != ROOT_KEYS:
        raise ValueError(f"config keys differ: expected {sorted(ROOT_KEYS)}, got {sorted(mapping)}")
    if _integer("schema_version", mapping["schema_version"]) != 1:
        raise ValueError("config schema_version must be 1")
    raw_prompts = mapping["prompts"]
    if not isinstance(raw_prompts, list):
        raise TypeError("config field 'prompts' must be an array of tables")
    prompts: list[ReferencePrompt] = []
    for index, raw_prompt in enumerate(cast(list[object], raw_prompts)):
        if not isinstance(raw_prompt, dict):
            raise TypeError(f"prompt {index} must be a table")
        prompt = cast(Mapping[str, object], raw_prompt)
        if set(prompt) != PROMPT_KEYS:
            raise ValueError(f"prompt {index} keys differ from {sorted(PROMPT_KEYS)}")
        prompts.append(
            ReferencePrompt(
                id=_text(f"prompts[{index}].id", prompt["id"]),
                text=_text(f"prompts[{index}].text", prompt["text"], ascii_only=False),
            )
        )
    return Lab04Config(
        model_id=_text("model_id", mapping["model_id"]),
        model_revision=_text("model_revision", mapping["model_revision"]),
        model_license=_text("model_license", mapping["model_license"]),
        model_safetensors_bytes=_integer(
            "model_safetensors_bytes", mapping["model_safetensors_bytes"], minimum=1
        ),
        device=_text("device", mapping["device"]),
        base_seed=_integer("base_seed", mapping["base_seed"], minimum=0),
        max_new_tokens=_integer("max_new_tokens", mapping["max_new_tokens"], minimum=2),
        temperature=_number("temperature", mapping["temperature"]),
        top_k=_integer("top_k", mapping["top_k"], minimum=1),
        top_p=_number("top_p", mapping["top_p"]),
        green_fraction=_number("green_fraction", mapping["green_fraction"]),
        watermark_bias=_number("watermark_bias", mapping["watermark_bias"]),
        generation_key=_integer("generation_key", mapping["generation_key"], minimum=1),
        comparison_key=_integer("comparison_key", mapping["comparison_key"], minimum=1),
        seeding_scheme=_text("seeding_scheme", mapping["seeding_scheme"]),
        context_width=_integer("context_width", mapping["context_width"], minimum=1),
        z_threshold=_number("z_threshold", mapping["z_threshold"]),
        trace_candidates=_integer("trace_candidates", mapping["trace_candidates"], minimum=1),
        reference_processor_order=_order(
            "reference_processor_order", mapping["reference_processor_order"], REFERENCE_ORDER
        ),
        stage_03_processor_order=_order(
            "stage_03_processor_order", mapping["stage_03_processor_order"], STAGE_03_ORDER
        ),
        prompts=tuple(prompts),
    )
