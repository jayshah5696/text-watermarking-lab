# pyright: reportUnnecessaryIsInstance=false
"""Strict loading for the locked Stage 3 model fixture."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

ROOT_KEYS = {
    "schema_version",
    "model_id",
    "model_revision",
    "base_seed",
    "max_new_tokens",
    "temperature",
    "top_k",
    "top_p",
    "green_fraction",
    "watermark_bias",
    "generation_key",
    "comparison_key",
    "selector_profile",
    "context_width",
    "trace_candidates",
    "prompts",
}
PROMPT_KEYS = {"id", "text"}


def _require_int(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"config field {name!r} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"config field {name!r} must be at least {minimum}")
    return value


def _require_float(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"config field {name!r} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"config field {name!r} must be finite")
    return number


def _require_text(name: str, value: object, *, ascii_only: bool) -> str:
    if not isinstance(value, str):
        raise TypeError(f"config field {name!r} must be text")
    if not value or (ascii_only and not value.isascii()):
        suffix = " non-empty ASCII text" if ascii_only else " non-empty text"
        raise ValueError(f"config field {name!r} must be{suffix}")
    return value


@dataclass(frozen=True, slots=True)
class PromptFixture:
    """One predeclared prompt used by the paired Stage 3 trace."""

    id: str
    text: str

    def __post_init__(self) -> None:
        _require_text("prompt id", self.id, ascii_only=True)
        _require_text("prompt text", self.text, ascii_only=False)


@dataclass(frozen=True, slots=True)
class Lab03Config:
    """Validated Stage 3 settings parsed from exact TOML bytes."""

    model_id: str
    model_revision: str
    base_seed: int
    max_new_tokens: int
    temperature: float
    top_k: int
    top_p: float
    green_fraction: float
    watermark_bias: float
    generation_key: int
    comparison_key: int
    selector_profile: str
    context_width: int
    trace_candidates: int
    prompts: tuple[PromptFixture, ...]

    def __post_init__(self) -> None:
        _require_text("model_id", self.model_id, ascii_only=True)
        revision = _require_text("model_revision", self.model_revision, ascii_only=True)
        if len(revision) != 40 or any(
            character not in "0123456789abcdef" for character in revision
        ):
            raise ValueError("model_revision must be a 40-character lowercase Git SHA")
        _require_int("base_seed", self.base_seed, minimum=0)
        _require_int("max_new_tokens", self.max_new_tokens, minimum=2)
        temperature = _require_float("temperature", self.temperature)
        if temperature <= 0.0:
            raise ValueError("temperature must be greater than zero")
        _require_int("top_k", self.top_k, minimum=1)
        top_p = _require_float("top_p", self.top_p)
        if not 0.0 < top_p <= 1.0:
            raise ValueError("top_p must be greater than zero and at most one")
        green_fraction = _require_float("green_fraction", self.green_fraction)
        if not 0.0 < green_fraction < 1.0:
            raise ValueError("green_fraction must be strictly between zero and one")
        bias = _require_float("watermark_bias", self.watermark_bias)
        if bias < 0.0:
            raise ValueError("watermark_bias must be non-negative")
        _require_int("generation_key", self.generation_key, minimum=1)
        _require_int("comparison_key", self.comparison_key, minimum=1)
        if self.generation_key == self.comparison_key:
            raise ValueError("generation_key and comparison_key must differ")
        if self.selector_profile != "mlx-mix-v1":
            raise ValueError("Stage 3 locks selector_profile to 'mlx-mix-v1'")
        if self.context_width != 1:
            raise ValueError("Stage 3 locks context_width to 1")
        trace_candidates = _require_int("trace_candidates", self.trace_candidates, minimum=1)
        if trace_candidates > self.top_k:
            raise ValueError("trace_candidates must not exceed top_k")
        if not isinstance(self.prompts, tuple) or len(self.prompts) != 3:
            raise ValueError("Stage 3 requires exactly three prompts")
        if any(not isinstance(prompt, PromptFixture) for prompt in self.prompts):
            raise TypeError("every prompt must be a PromptFixture")
        if len({prompt.id for prompt in self.prompts}) != len(self.prompts):
            raise ValueError("prompt IDs must be unique")


def config_from_toml_bytes(payload: bytes) -> Lab03Config:
    """Parse exact Stage 3 TOML bytes and reject implicit settings."""

    parsed: Any = tomllib.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise TypeError("config must be a TOML table")
    mapping = cast(Mapping[str, object], parsed)
    if set(mapping) != ROOT_KEYS:
        raise ValueError(f"config keys differ: expected {sorted(ROOT_KEYS)}, got {sorted(mapping)}")
    if _require_int("schema_version", mapping["schema_version"]) != 1:
        raise ValueError("config schema_version must be 1")
    prompt_values = mapping["prompts"]
    if not isinstance(prompt_values, list):
        raise TypeError("config field 'prompts' must be an array of tables")
    prompts: list[PromptFixture] = []
    for index, value in enumerate(cast(list[object], prompt_values)):
        if not isinstance(value, dict):
            raise TypeError(f"prompt {index} must be a table")
        prompt = cast(Mapping[str, object], value)
        if set(prompt) != PROMPT_KEYS:
            raise ValueError(f"prompt {index} keys differ from {sorted(PROMPT_KEYS)}")
        prompts.append(
            PromptFixture(
                id=_require_text(f"prompts[{index}].id", prompt["id"], ascii_only=True),
                text=_require_text(f"prompts[{index}].text", prompt["text"], ascii_only=False),
            )
        )
    return Lab03Config(
        model_id=_require_text("model_id", mapping["model_id"], ascii_only=True),
        model_revision=_require_text("model_revision", mapping["model_revision"], ascii_only=True),
        base_seed=_require_int("base_seed", mapping["base_seed"], minimum=0),
        max_new_tokens=_require_int("max_new_tokens", mapping["max_new_tokens"], minimum=2),
        temperature=_require_float("temperature", mapping["temperature"]),
        top_k=_require_int("top_k", mapping["top_k"], minimum=1),
        top_p=_require_float("top_p", mapping["top_p"]),
        green_fraction=_require_float("green_fraction", mapping["green_fraction"]),
        watermark_bias=_require_float("watermark_bias", mapping["watermark_bias"]),
        generation_key=_require_int("generation_key", mapping["generation_key"], minimum=1),
        comparison_key=_require_int("comparison_key", mapping["comparison_key"], minimum=1),
        selector_profile=_require_text(
            "selector_profile", mapping["selector_profile"], ascii_only=True
        ),
        context_width=_require_int("context_width", mapping["context_width"], minimum=1),
        trace_candidates=_require_int("trace_candidates", mapping["trace_candidates"], minimum=1),
        prompts=tuple(prompts),
    )
