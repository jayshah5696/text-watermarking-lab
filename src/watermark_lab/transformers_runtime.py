"""Reusable generation-time watermark boundaries for compatible Transformers models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol, cast

from transformers import PreTrainedConfig, WatermarkDetector, WatermarkingConfig

Condition = Literal["control", "watermarked"]


@dataclass(frozen=True, slots=True)
class WatermarkProfile:
    """The complete maintained Transformers watermark recipe and key."""

    green_fraction: float
    bias: float
    hashing_key: int
    seeding_scheme: str = "lefthash"
    context_width: int = 1

    def __post_init__(self) -> None:
        if not 0.0 < self.green_fraction < 1.0:
            raise ValueError("green_fraction must be between zero and one")
        if self.bias <= 0.0:
            raise ValueError("bias must be positive")
        if isinstance(self.hashing_key, bool):
            raise TypeError("hashing_key must be an integer")
        if self.hashing_key < 0:
            raise ValueError("hashing_key must be non-negative")
        if not self.seeding_scheme:
            raise ValueError("seeding_scheme must not be empty")
        if self.context_width < 1:
            raise ValueError("context_width must be positive")

    def to_transformers(self) -> WatermarkingConfig:
        """Construct the library object passed to generation and detection."""

        return WatermarkingConfig(
            greenlist_ratio=self.green_fraction,
            bias=self.bias,
            hashing_key=self.hashing_key,
            seeding_scheme=self.seeding_scheme,
            context_width=self.context_width,
        )


@dataclass(frozen=True, slots=True)
class SamplingProfile:
    """Safe generation fields shared by control and watermarked calls."""

    max_new_tokens: int
    temperature: float
    top_k: int
    top_p: float

    def __post_init__(self) -> None:
        if self.max_new_tokens < 1:
            raise ValueError("max_new_tokens must be positive")
        if self.temperature <= 0.0:
            raise ValueError("temperature must be positive")
        if self.top_k < 1:
            raise ValueError("top_k must be positive")
        if not 0.0 < self.top_p <= 1.0:
            raise ValueError("top_p must be in (0, 1]")


@dataclass(frozen=True, slots=True)
class EncodedPrompt:
    """Model inputs and the exact text-token boundary before generation."""

    input_ids: Any
    attention_mask: Any
    prompt_length: int
    rendered_text: str

    def __post_init__(self) -> None:
        if self.prompt_length < 1:
            raise ValueError("prompt_length must be positive")
        if not self.rendered_text:
            raise ValueError("rendered_text must not be empty")


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Generated IDs and only the copied assistant continuation."""

    condition: Condition
    generated_token_ids: tuple[int, ...]
    raw_generated_text: str
    copied_text: str
    copied_token_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.condition not in ("control", "watermarked"):
            raise ValueError("condition must be control or watermarked")
        if not self.generated_token_ids:
            raise ValueError("generated_token_ids must not be empty")
        if not self.copied_text:
            raise ValueError("copied_text must not be empty")
        if len(self.copied_token_ids) < 2:
            raise ValueError("copied_text must contain at least two token IDs")


class GenerationModel(Protocol):
    """The part of a compatible Transformers generation model used by the core."""

    def generate(self, **kwargs: Any) -> Any: ...


class TextGenerationAdapter(Protocol):
    """Model-specific text, config, and continuation operations."""

    @property
    def model(self) -> GenerationModel: ...

    @property
    def model_config(self) -> PreTrainedConfig: ...

    @property
    def device(self) -> str: ...

    @property
    def pad_token_id(self) -> int: ...

    def encode_prompt(self, prompt: str) -> EncodedPrompt: ...

    def generated_ids(self, output: Any, *, prompt_length: int) -> tuple[int, ...]: ...

    def raw_generated_text(self, generated_ids: tuple[int, ...]) -> str: ...

    def copied_text(
        self,
        raw_generated_text: str,
        generated_ids: tuple[int, ...],
        encoded: EncodedPrompt,
    ) -> str: ...

    def copied_token_ids(self, copied_text: str) -> tuple[int, ...]: ...

    def token_tensor(self, token_ids: tuple[int, ...]) -> Any: ...


def generation_kwargs(
    *,
    adapter: TextGenerationAdapter,
    encoded: EncodedPrompt,
    sampling: SamplingProfile,
    condition: Condition,
    watermark: WatermarkProfile | None,
) -> dict[str, Any]:
    """Build the exact library call; the key enters only in `watermarking_config`."""

    if condition == "watermarked" and watermark is None:
        raise ValueError("watermarked generation requires a watermark profile")
    if condition == "control" and watermark is not None:
        raise ValueError("control generation must not receive a watermark profile")

    kwargs: dict[str, Any] = {
        "input_ids": encoded.input_ids,
        "attention_mask": encoded.attention_mask,
        "do_sample": True,
        "max_new_tokens": sampling.max_new_tokens,
        "temperature": sampling.temperature,
        "top_k": sampling.top_k,
        "top_p": sampling.top_p,
        "pad_token_id": adapter.pad_token_id,
    }
    if watermark is not None:
        kwargs["watermarking_config"] = watermark.to_transformers()
    return kwargs


def finalize_generation(
    *,
    adapter: TextGenerationAdapter,
    encoded: EncodedPrompt,
    output: Any,
    condition: Condition,
) -> GenerationResult:
    """Slice the prompt, isolate assistant content, and re-tokenize copied text."""

    generated = adapter.generated_ids(output, prompt_length=encoded.prompt_length)
    raw_text = adapter.raw_generated_text(generated)
    copied_text = adapter.copied_text(raw_text, generated, encoded)
    copied_ids = adapter.copied_token_ids(copied_text)
    return GenerationResult(
        condition=condition,
        generated_token_ids=generated,
        raw_generated_text=raw_text,
        copied_text=copied_text,
        copied_token_ids=copied_ids,
    )


def generate_continuation(
    *,
    adapter: TextGenerationAdapter,
    encoded: EncodedPrompt,
    sampling: SamplingProfile,
    condition: Condition,
    watermark: WatermarkProfile | None,
) -> GenerationResult:
    """Generate one continuation through the reusable model adapter."""

    kwargs = generation_kwargs(
        adapter=adapter,
        encoded=encoded,
        sampling=sampling,
        condition=condition,
        watermark=watermark,
    )
    output = adapter.model.generate(**kwargs)
    return finalize_generation(
        adapter=adapter,
        encoded=encoded,
        output=output,
        condition=condition,
    )


def build_detector(
    *,
    adapter: TextGenerationAdapter,
    watermark: WatermarkProfile,
    ignore_repeated_ngrams: bool = False,
) -> WatermarkDetector:
    """Build the matching detector from the same model text config, device, profile, and key."""

    return WatermarkDetector(
        model_config=adapter.model_config,
        device=adapter.device,
        watermarking_config=watermark.to_transformers(),
        ignore_repeated_ngrams=ignore_repeated_ngrams,
    )


def detect_copied_text(
    *,
    adapter: TextGenerationAdapter,
    detector: WatermarkDetector,
    copied_text: str,
    z_threshold: float,
) -> Any:
    """Tokenize only copied text and return the maintained detector record."""

    token_ids = adapter.copied_token_ids(copied_text)
    if len(token_ids) < 2:
        raise ValueError("copied_text must contain at least two token IDs")
    return cast(
        Any,
        detector(
            adapter.token_tensor(token_ids),
            z_threshold=z_threshold,
            return_dict=True,
        ),
    )
