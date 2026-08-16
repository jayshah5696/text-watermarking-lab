"""Strict configuration for Stage 8 editing and bias trade-offs."""

from __future__ import annotations

import hashlib
import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class Lab08Config:
    schema_version: int
    base_seed: int
    stage7_source_commit: str
    stage7_config_sha256: str
    stage7_selected_sha256: str
    model_id: str
    model_revision: str
    model_safetensors_bytes: int
    model_class: str
    tokenizer_id: str
    tokenizer_revision: str
    transformers_version: str
    torch_version: str
    huggingface_hub_version: str
    modal_sdk_version: str
    modal_app_name: str
    modal_gpu: str
    dtype: str
    attack_selection_ranks: tuple[int, ...]
    bias_selection_ranks: tuple[int, ...]
    attack_prefix: int
    homoglyph_rates: tuple[float, ...]
    deletion_rates: tuple[float, ...]
    mixing_rates: tuple[float, ...]
    bias_values: tuple[float, ...]
    temperature: float
    top_k: int
    top_p: float
    green_fraction: float
    generation_key: int
    seeding_scheme: str
    context_width: int
    z_threshold: float
    max_new_tokens: int
    similarity_threshold: float
    min_length_ratio: float
    max_length_ratio: float
    paraphrase_template: str
    max_remote_invocations: int
    max_generation_calls: int
    max_generated_token_ids: int
    max_cost_usd: float
    l4_usd_per_second: float
    use_huggingface_secret: bool
    use_volume: bool

    def __post_init__(self) -> None:
        locked: Mapping[str, object] = {
            "schema_version": 1,
            "base_seed": 20_260_814,
            "stage7_source_commit": "6b911ce4052794bfb6762859847e5cdcc197c165",
            "stage7_config_sha256": (
                "61c66a02966bed4565d1693e2603bc8218b849a40109e8589bf8a9e97ba7c0ab"
            ),
            "stage7_selected_sha256": (
                "34ea4a807fb20273dc035fcbf3131f512e506fa576889a391fcdf31a8351a57f"
            ),
            "model_id": "google/gemma-4-E2B-it",
            "model_revision": "3e22461f65e89153144f8adb70e3b8c2cc9845a7",
            "model_safetensors_bytes": 10_246_621_918,
            "model_class": "Gemma4ForConditionalGeneration",
            "tokenizer_id": "google/gemma-4-E2B-it",
            "tokenizer_revision": "3e22461f65e89153144f8adb70e3b8c2cc9845a7",
            "transformers_version": "5.14.1",
            "torch_version": "2.13.0",
            "huggingface_hub_version": "1.26.0",
            "modal_sdk_version": "1.5.3",
            "modal_app_name": "text-watermarking-lab-08",
            "modal_gpu": "L4",
            "dtype": "bfloat16",
            "attack_selection_ranks": tuple(range(1000, 1012)),
            "bias_selection_ranks": tuple(range(1000, 1008)),
            "attack_prefix": 80,
            "homoglyph_rates": (0.01, 0.05),
            "deletion_rates": (0.10, 0.30),
            "mixing_rates": (0.25, 0.50),
            "bias_values": (1.0, 2.0, 3.0),
            "temperature": 0.8,
            "top_k": 40,
            "top_p": 0.95,
            "green_fraction": 0.25,
            "generation_key": 15_485_863,
            "seeding_scheme": "lefthash",
            "context_width": 1,
            "z_threshold": 3.0,
            "max_new_tokens": 400,
            "similarity_threshold": 0.8,
            "min_length_ratio": 0.8,
            "max_length_ratio": 1.2,
            "paraphrase_template": (
                "Rewrite the passage below in fresh wording. Preserve every factual claim, named "
                "entity, number, and qualification. Keep roughly the same length. Return only the "
                "rewritten passage.\n\n<passage>\n{passage}\n</passage>"
            ),
            "max_remote_invocations": 1,
            "max_generation_calls": 28,
            "max_generated_token_ids": 11_200,
            "max_cost_usd": 5.0,
            "l4_usd_per_second": 0.000222,
            "use_huggingface_secret": False,
            "use_volume": False,
        }
        for name, expected in locked.items():
            if getattr(self, name) != expected:
                raise ValueError(f"Stage 8 locks {name} to {expected!r}")
        expected_calls = len(self.attack_selection_ranks) + len(self.bias_selection_ranks) * 2
        if self.max_generation_calls != expected_calls:
            raise ValueError("Stage 8 call ceiling differs from the frozen fixture")
        if self.max_generated_token_ids != self.max_generation_calls * self.max_new_tokens:
            raise ValueError("Stage 8 token ceiling differs from calls times cap")

    def derive_seed(self, operation: str, rank: int, text_sha256: str, rate: str = "") -> int:
        message = f"lab-08|{self.base_seed}|{operation}|{rank}|{rate}|{text_sha256}"
        return int.from_bytes(hashlib.sha256(message.encode()).digest()[:8], "big")

    def paraphrase_seed(self, rank: int, text_sha256: str) -> int:
        return self.derive_seed("paraphrase", rank, text_sha256)


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


def lab08_config_from_toml_bytes(payload: bytes) -> Lab08Config:
    raw: Any = tomllib.loads(payload.decode())
    if not isinstance(raw, dict):
        raise TypeError("Stage 8 config must be a TOML table")
    values = cast(Mapping[str, object], raw)
    expected = set(Lab08Config.__dataclass_fields__)
    if set(values) != expected:
        raise ValueError("Stage 8 config keys differ from the exact contract")
    integer_lists = {"attack_selection_ranks", "bias_selection_ranks"}
    float_lists = {"homoglyph_rates", "deletion_rates", "mixing_rates", "bias_values"}
    kwargs: dict[str, object] = {}
    for name, field in Lab08Config.__dataclass_fields__.items():
        value = values[name]
        if name in integer_lists:
            if not isinstance(value, list):
                raise TypeError(f"{name} must be an integer list")
            integer_items = cast(list[object], value)
            if any(isinstance(item, bool) or not isinstance(item, int) for item in integer_items):
                raise TypeError(f"{name} must be an integer list")
            kwargs[name] = tuple(cast(list[int], integer_items))
        elif name in float_lists:
            if not isinstance(value, list):
                raise TypeError(f"{name} must be a number list")
            number_items = cast(list[object], value)
            kwargs[name] = tuple(_number(name, item) for item in number_items)
        elif field.type in ("int", int):
            kwargs[name] = _integer(name, value)
        elif field.type in ("float", float):
            kwargs[name] = _number(name, value)
        elif field.type in ("bool", bool):
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be Boolean")
            kwargs[name] = value
        else:
            kwargs[name] = _text(name, value)
    return Lab08Config(**cast(Any, kwargs))
