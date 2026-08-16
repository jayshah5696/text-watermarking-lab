"""Strict configuration for Stage 6 natural-web calibration."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class Lab06Config:
    schema_version: int
    dataset_id: str
    dataset_revision: str
    dataset_config: str
    dataset_split: str
    dataset_file: str
    dataset_file_sha256: str
    dataset_file_bytes: int
    dataset_declared_rows: int
    tokenizer_id: str
    tokenizer_revision: str
    transformers_version: str
    torch_version: str
    huggingface_hub_version: str
    modal_sdk_version: str
    modal_app_name: str
    modal_gpu: str
    green_fraction: float
    watermark_bias: float
    generation_key: int
    seeding_scheme: str
    context_width: int
    z_threshold: float
    minimum_document_tokens: int
    prompt_tokens: int
    continuation_tokens: int
    calibration_rows: int
    paired_test_rows: int
    minimum_letter_fraction: float
    minimum_list_lines: int
    minimum_list_fraction: float
    minimum_code_lines: int
    minimum_code_fraction: float
    max_remote_invocations: int
    max_cost_usd: float
    use_huggingface_secret: bool
    use_volume: bool

    def __post_init__(self) -> None:
        locked: Mapping[str, object] = {
            "schema_version": 1,
            "dataset_id": "allenai/c4",
            "dataset_revision": "1588ec454efa1a09f29cd18ddd04fe05fc8653a2",
            "dataset_config": "realnewslike",
            "dataset_split": "validation",
            "dataset_file": "realnewslike/c4-validation.00000-of-00001.json.gz",
            "dataset_file_sha256": (
                "42ac859dc1c4d48d165ec602909403e2066ce1d4854149ed70b9ec9cc96dc65f"
            ),
            "dataset_file_bytes": 15_284_943,
            "dataset_declared_rows": 13_863,
            "tokenizer_id": "google/gemma-4-E2B-it",
            "tokenizer_revision": "3e22461f65e89153144f8adb70e3b8c2cc9845a7",
            "transformers_version": "5.14.1",
            "torch_version": "2.13.0",
            "huggingface_hub_version": "1.26.0",
            "modal_sdk_version": "1.5.3",
            "modal_app_name": "text-watermarking-lab-06",
            "modal_gpu": "L4",
            "green_fraction": 0.25,
            "watermark_bias": 2.0,
            "generation_key": 15_485_863,
            "seeding_scheme": "lefthash",
            "context_width": 1,
            "z_threshold": 3.0,
            "minimum_document_tokens": 500,
            "prompt_tokens": 50,
            "continuation_tokens": 400,
            "calibration_rows": 1_000,
            "paired_test_rows": 24,
            "minimum_letter_fraction": 0.65,
            "minimum_list_lines": 8,
            "minimum_list_fraction": 0.5,
            "minimum_code_lines": 5,
            "minimum_code_fraction": 0.2,
            "max_remote_invocations": 1,
            "max_cost_usd": 5.0,
            "use_huggingface_secret": False,
            "use_volume": False,
        }
        for name, expected in locked.items():
            if getattr(self, name) != expected:
                raise ValueError(f"Stage 6 locks {name} to {expected!r}")
        if self.prompt_tokens + self.continuation_tokens > self.minimum_document_tokens:
            raise ValueError("selected token ranges exceed the minimum document length")

    @property
    def selected_rows(self) -> int:
        return self.calibration_rows + self.paired_test_rows


def _integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _number(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{name} must be non-empty text")
    return value


def lab06_config_from_toml_bytes(payload: bytes) -> Lab06Config:
    raw: Any = tomllib.loads(payload.decode())
    if not isinstance(raw, dict):
        raise TypeError("Stage 6 config must be a TOML table")
    values = cast(Mapping[str, object], raw)
    expected = set(Lab06Config.__dataclass_fields__)
    if set(values) != expected:
        raise ValueError("Stage 6 config keys differ from the exact contract")
    kwargs: dict[str, object] = {}
    for name, field in Lab06Config.__dataclass_fields__.items():
        value = values[name]
        if field.type in ("int", int):
            kwargs[name] = _integer(name, value)
        elif field.type in ("float", float):
            kwargs[name] = _number(name, value)
        elif field.type in ("bool", bool):
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be Boolean")
            kwargs[name] = value
        else:
            kwargs[name] = _text(name, value)
    return Lab06Config(**cast(Any, kwargs))
