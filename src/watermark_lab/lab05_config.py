# pyright: reportUnknownArgumentType=false
"""Strict loading for the locked Stage 5 Modal/Gemma smoke fixture."""

from __future__ import annotations

import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from watermark_lab.hf_adapter import derive_reference_seed


@dataclass(frozen=True, slots=True)
class SmokePrompt:
    id: str
    text: str


@dataclass(frozen=True, slots=True)
class Lab05Config:
    model_id: str
    model_revision: str
    model_license: str
    model_safetensors_bytes: int
    model_class: str
    modal_app_name: str
    modal_gpu: str
    modal_sdk_version: str
    python_version: str
    torch_version: str
    torchvision_version: str
    transformers_version: str
    huggingface_hub_version: str
    librosa_version: str
    dtype: str
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
    instruction_prefix: str
    max_remote_invocations: int
    max_generation_calls: int
    minimum_tokens_per_second: float
    minimum_vram_headroom_fraction: float
    max_cost_usd: float
    projected_rows: int
    short_projection_tokens_per_output: int
    long_projection_tokens_per_output: int
    l4_usd_per_second: float
    cpu_usd_per_core_second: float
    memory_usd_per_gib_second: float
    volume_usd_per_gib_month: float
    price_source: str
    price_retrieved: str
    use_huggingface_secret: bool
    use_volume: bool
    prompts: tuple[SmokePrompt, ...]

    def __post_init__(self) -> None:
        locked = {
            "model_id": "google/gemma-4-E2B-it",
            "model_revision": "3e22461f65e89153144f8adb70e3b8c2cc9845a7",
            "model_license": "apache-2.0",
            "model_safetensors_bytes": 10_246_621_918,
            "model_class": "Gemma4ForConditionalGeneration",
            "modal_app_name": "text-watermarking-lab-05",
            "modal_gpu": "L4",
            "modal_sdk_version": "1.5.3",
            "python_version": "3.12",
            "torch_version": "2.13.0",
            "torchvision_version": "0.28.0",
            "transformers_version": "5.14.1",
            "huggingface_hub_version": "1.26.0",
            "librosa_version": "0.11.0",
            "dtype": "bfloat16",
            "base_seed": 20260812,
            "max_new_tokens": 200,
            "temperature": 0.8,
            "top_k": 40,
            "top_p": 0.95,
            "green_fraction": 0.25,
            "watermark_bias": 2.0,
            "generation_key": 15485863,
            "comparison_key": 15485867,
            "seeding_scheme": "lefthash",
            "context_width": 1,
            "z_threshold": 3.0,
            "max_remote_invocations": 1,
            "max_generation_calls": 6,
            "minimum_tokens_per_second": 2.0,
            "minimum_vram_headroom_fraction": 0.20,
            "max_cost_usd": 5.0,
            "projected_rows": 24,
            "short_projection_tokens_per_output": 200,
            "long_projection_tokens_per_output": 400,
            "l4_usd_per_second": 0.000222,
            "cpu_usd_per_core_second": 0.0000131,
            "memory_usd_per_gib_second": 0.00000222,
            "volume_usd_per_gib_month": 0.09,
            "price_source": "https://modal.com/pricing",
            "price_retrieved": "2026-08-15",
            "use_huggingface_secret": False,
            "use_volume": False,
        }
        for name, expected in locked.items():
            if getattr(self, name) != expected:
                raise ValueError(f"Stage 5 locks {name} to {expected!r}")
        if not self.instruction_prefix.endswith("\n\n"):
            raise ValueError("instruction_prefix must end with one blank line")
        if len(self.prompts) != 3 or len({prompt.id for prompt in self.prompts}) != 3:
            raise ValueError("Stage 5 requires exactly three unique prompts")
        if any(
            not prompt.id.isascii() or not prompt.id or not prompt.text for prompt in self.prompts
        ):
            raise ValueError("prompt IDs and text must be non-empty")

    def prompt_seed(self, prompt_id: str) -> int:
        return derive_reference_seed(base_seed=self.base_seed, prompt_id=prompt_id)


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


def config_from_toml_bytes(payload: bytes) -> Lab05Config:
    raw: Any = tomllib.loads(payload.decode("utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("config must be a TOML table")
    values = cast(Mapping[str, object], raw)
    expected = set(Lab05Config.__dataclass_fields__) | {"schema_version"}
    if set(values) != expected:
        raise ValueError("Stage 5 config keys differ from the exact contract")
    if _integer("schema_version", values["schema_version"]) != 1:
        raise ValueError("schema_version must be 1")
    raw_prompts = values["prompts"]
    if not isinstance(raw_prompts, list):
        raise TypeError("prompts must be an array of tables")
    prompts: list[SmokePrompt] = []
    for item in cast(list[object], raw_prompts):
        if not isinstance(item, dict) or set(item) != {"id", "text"}:
            raise ValueError("each prompt must contain only id and text")
        prompt = cast(Mapping[str, object], item)
        prompts.append(
            SmokePrompt(
                id=_text("prompt id", prompt["id"]), text=_text("prompt text", prompt["text"])
            )
        )
    kwargs: dict[str, object] = {}
    for name, field in Lab05Config.__dataclass_fields__.items():
        if name == "prompts":
            kwargs[name] = tuple(prompts)
        elif field.type in ("int", int):
            kwargs[name] = _integer(name, values[name])
        elif field.type in ("float", float):
            kwargs[name] = _number(name, values[name])
        elif field.type in ("bool", bool):
            value = values[name]
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be Boolean")
            kwargs[name] = value
        else:
            kwargs[name] = _text(name, values[name])
    return Lab05Config(**cast(Any, kwargs))
