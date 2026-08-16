"""Strict configuration for the Stage 7 paired core experiment."""

from __future__ import annotations

import hashlib
import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class Lab07Config:
    schema_version: int
    base_seed: int
    dataset_id: str
    dataset_revision: str
    dataset_config: str
    dataset_split: str
    dataset_file: str
    dataset_file_sha256: str
    dataset_file_bytes: int
    manifest_sha256: str
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
    paired_rows: int
    prompt_tokens: int
    natural_continuation_tokens: int
    max_new_tokens: int
    prefixes: tuple[int, ...]
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
    bootstrap_replicates: int
    instruction_prefix: str
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
            "base_seed": 20_260_813,
            "dataset_id": "allenai/c4",
            "dataset_revision": "1588ec454efa1a09f29cd18ddd04fe05fc8653a2",
            "dataset_config": "realnewslike",
            "dataset_split": "validation",
            "dataset_file": "realnewslike/c4-validation.00000-of-00001.json.gz",
            "dataset_file_sha256": (
                "42ac859dc1c4d48d165ec602909403e2066ce1d4854149ed70b9ec9cc96dc65f"
            ),
            "dataset_file_bytes": 15_284_943,
            "manifest_sha256": ("44a6c1a2b18009b78c65562e00054cb4d3817c9ca34dde1da97961407add5ea8"),
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
            "modal_app_name": "text-watermarking-lab-07",
            "modal_gpu": "L4",
            "dtype": "bfloat16",
            "paired_rows": 24,
            "prompt_tokens": 50,
            "natural_continuation_tokens": 400,
            "max_new_tokens": 400,
            "prefixes": (40, 80, 160, 200, 400),
            "temperature": 0.8,
            "top_k": 40,
            "top_p": 0.95,
            "green_fraction": 0.25,
            "watermark_bias": 2.0,
            "generation_key": 15_485_863,
            "comparison_key": 15_485_867,
            "seeding_scheme": "lefthash",
            "context_width": 1,
            "z_threshold": 3.0,
            "bootstrap_replicates": 10_000,
            "instruction_prefix": (
                "Continue the passage naturally with a detailed, coherent response. "
                "Do not summarize early. Return only the continuation.\n\n"
            ),
            "max_remote_invocations": 1,
            "max_generation_calls": 48,
            "max_generated_token_ids": 19_200,
            "max_cost_usd": 5.0,
            "l4_usd_per_second": 0.000222,
            "use_huggingface_secret": False,
            "use_volume": False,
        }
        for name, expected in locked.items():
            if getattr(self, name) != expected:
                raise ValueError(f"Stage 7 locks {name} to {expected!r}")
        if self.max_generation_calls != self.paired_rows * 2:
            raise ValueError("Stage 7 call ceiling must equal two calls per paired row")
        if self.max_generated_token_ids != self.max_generation_calls * self.max_new_tokens:
            raise ValueError("Stage 7 generated-token ceiling differs from calls times cap")

    def prompt_seed(self, selection_rank: int, text_sha256: str) -> int:
        message = f"lab-07|{self.base_seed}|{selection_rank}|{text_sha256}"
        return int.from_bytes(hashlib.sha256(message.encode()).digest()[:8], "big")

    def bootstrap_seed(self, prefix: int, comparison: str) -> int:
        message = f"lab-07-bootstrap|{self.base_seed}|{prefix}|{comparison}"
        return int.from_bytes(hashlib.sha256(message.encode()).digest()[:8], "big")


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


def lab07_config_from_toml_bytes(payload: bytes) -> Lab07Config:
    raw: Any = tomllib.loads(payload.decode())
    if not isinstance(raw, dict):
        raise TypeError("Stage 7 config must be a TOML table")
    values = cast(Mapping[str, object], raw)
    expected = set(Lab07Config.__dataclass_fields__)
    if set(values) != expected:
        raise ValueError("Stage 7 config keys differ from the exact contract")
    kwargs: dict[str, object] = {}
    for name, field in Lab07Config.__dataclass_fields__.items():
        value = values[name]
        if name == "prefixes":
            if not isinstance(value, list):
                raise TypeError("prefixes must be an integer list")
            items = cast(list[object], value)
            if any(isinstance(item, bool) or not isinstance(item, int) for item in items):
                raise TypeError("prefixes must be an integer list")
            kwargs[name] = tuple(cast(list[int], items))
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
    return Lab07Config(**cast(Any, kwargs))
