from __future__ import annotations

from typing import Any

import pytest
import torch
from transformers import GPT2Config, WatermarkingConfig

from watermark_lab.transformers_runtime import (
    EncodedPrompt,
    SamplingProfile,
    WatermarkProfile,
    build_detector,
    detect_copied_text,
    generate_continuation,
)


class FakeModel:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate(self, **kwargs: Any) -> torch.Tensor:
        self.calls.append(kwargs)
        return torch.tensor([[10, 11, 12, 20, 21, 22]])


class FakeAdapter:
    def __init__(self) -> None:
        self._model = FakeModel()
        self._model_config = GPT2Config(vocab_size=128)
        self.last_detector_ids: tuple[int, ...] | None = None

    @property
    def model(self) -> FakeModel:
        return self._model

    @property
    def model_config(self) -> GPT2Config:
        return self._model_config

    @property
    def device(self) -> str:
        return "cpu"

    @property
    def pad_token_id(self) -> int:
        return 0

    def encode_prompt(self, prompt: str) -> EncodedPrompt:
        return EncodedPrompt(
            input_ids=torch.tensor([[10, 11, 12]]),
            attention_mask=torch.ones((1, 3), dtype=torch.long),
            prompt_length=3,
            rendered_text=prompt,
        )

    def generated_ids(self, output: torch.Tensor, *, prompt_length: int) -> tuple[int, ...]:
        return tuple(int(value) for value in output[0, prompt_length:].tolist())

    def raw_generated_text(self, generated_ids: tuple[int, ...]) -> str:
        return "<assistant>hello world</assistant>"

    def copied_text(
        self,
        raw_generated_text: str,
        generated_ids: tuple[int, ...],
        encoded: EncodedPrompt,
    ) -> str:
        return "hello world"

    def copied_token_ids(self, copied_text: str) -> tuple[int, ...]:
        return (20, 21, 22)

    def token_tensor(self, token_ids: tuple[int, ...]) -> torch.Tensor:
        self.last_detector_ids = token_ids
        return torch.tensor([token_ids])


def profiles() -> tuple[SamplingProfile, WatermarkProfile]:
    return (
        SamplingProfile(max_new_tokens=20, temperature=0.8, top_k=40, top_p=0.95),
        WatermarkProfile(green_fraction=0.25, bias=2.0, hashing_key=15485863),
    )


def test_control_and_watermarked_calls_differ_only_by_library_argument() -> None:
    adapter = FakeAdapter()
    sampling, watermark = profiles()
    encoded = adapter.encode_prompt("continue")

    control = generate_continuation(
        adapter=adapter,
        encoded=encoded,
        sampling=sampling,
        condition="control",
        watermark=None,
    )
    marked = generate_continuation(
        adapter=adapter,
        encoded=encoded,
        sampling=sampling,
        condition="watermarked",
        watermark=watermark,
    )

    control_kwargs, marked_kwargs = adapter.model.calls
    assert "watermarking_config" not in control_kwargs
    config = marked_kwargs.pop("watermarking_config")
    assert isinstance(config, WatermarkingConfig)
    assert config.hashing_key == 15485863
    assert control_kwargs == marked_kwargs
    assert control.generated_token_ids == marked.generated_token_ids == (20, 21, 22)
    assert marked.copied_text == "hello world"


@pytest.mark.parametrize(
    ("condition", "watermark"),
    [("control", WatermarkProfile(0.25, 2.0, 1)), ("watermarked", None)],
)
def test_generation_rejects_mismatched_condition_and_profile(
    condition: Any, watermark: WatermarkProfile | None
) -> None:
    adapter = FakeAdapter()
    sampling, _ = profiles()
    with pytest.raises(ValueError):
        generate_continuation(
            adapter=adapter,
            encoded=adapter.encode_prompt("continue"),
            sampling=sampling,
            condition=condition,
            watermark=watermark,
        )


def test_detector_uses_matching_adapter_profile_and_only_copied_ids() -> None:
    adapter = FakeAdapter()
    _, watermark = profiles()
    detector = build_detector(adapter=adapter, watermark=watermark)
    result = detect_copied_text(
        adapter=adapter,
        detector=detector,
        copied_text="hello world",
        z_threshold=3.0,
    )
    assert adapter.last_detector_ids == (20, 21, 22)
    assert int(result.num_tokens_scored[0]) == 2


def test_profiles_reject_invalid_settings() -> None:
    with pytest.raises(ValueError, match="green_fraction"):
        WatermarkProfile(0.0, 2.0, 1)
    with pytest.raises(ValueError, match="bias"):
        WatermarkProfile(0.25, 0.0, 1)
    with pytest.raises(TypeError, match="hashing_key"):
        WatermarkProfile(0.25, 2.0, True)
    with pytest.raises(ValueError, match="top_p"):
        SamplingProfile(max_new_tokens=20, temperature=0.8, top_k=40, top_p=0.0)
