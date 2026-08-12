# pyright: reportUnnecessaryIsInstance=false
"""Strict TOML loading for the locked Stage 2 teaching configuration."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping
from typing import Any, cast

from watermark_lab.lab02_records import Lab02ConfigSnapshot

CONFIG_KEYS = {
    "schema_version",
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


def _int(mapping: Mapping[str, object], name: str, *, minimum: int | None = None) -> int:
    value = mapping[name]
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"config field {name!r} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"config field {name!r} must be at least {minimum}")
    return value


def _float(mapping: Mapping[str, object], name: str) -> float:
    value = mapping[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"config field {name!r} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"config field {name!r} must be finite")
    return number


def _array(mapping: Mapping[str, object], name: str) -> list[object]:
    value = mapping[name]
    if not isinstance(value, list):
        raise TypeError(f"config field {name!r} must be an array")
    return cast(list[object], value)


def config_from_toml_bytes(payload: bytes) -> Lab02ConfigSnapshot:
    """Parse exact Stage 2 TOML bytes into a validated snapshot."""

    parsed: Any = tomllib.loads(payload.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise TypeError("config must be a TOML table")
    untyped = cast(dict[object, object], parsed)
    if not all(isinstance(key, str) for key in untyped):
        raise TypeError("config must be a TOML table")
    mapping = cast(Mapping[str, object], untyped)
    if set(mapping) != CONFIG_KEYS:
        raise ValueError(
            f"config keys differ: expected {sorted(CONFIG_KEYS)}, got {sorted(mapping)}"
        )
    if _int(mapping, "schema_version") != 1:
        raise ValueError("config schema_version must be 1")
    development_key = mapping["development_key"]
    if not isinstance(development_key, str):
        raise TypeError("config field 'development_key' must be text")
    vocabulary_values = _array(mapping, "vocabulary")
    if not all(isinstance(value, str) for value in vocabulary_values):
        raise TypeError("every vocabulary label must be text")
    initial_context_values = _array(mapping, "initial_context")
    raw_logit_values = _array(mapping, "raw_logits")
    initial_context: list[int] = []
    for value in initial_context_values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("every initial context token ID must be an integer")
        initial_context.append(value)
    raw_logits: list[float] = []
    for value in raw_logit_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("every raw logit must be a real number")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("every raw logit must be finite")
        raw_logits.append(number)
    return Lab02ConfigSnapshot(
        base_seed=_int(mapping, "base_seed"),
        development_key=development_key,
        gamma=_float(mapping, "gamma"),
        delta=_float(mapping, "delta"),
        context_width=_int(mapping, "context_width", minimum=1),
        steps=_int(mapping, "steps", minimum=1),
        vocabulary=tuple(cast(list[str], vocabulary_values)),
        initial_context=tuple(initial_context),
        raw_logits=tuple(raw_logits),
    )
