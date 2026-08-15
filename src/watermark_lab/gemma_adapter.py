"""Gemma 4 text-generation adapter for the reusable Transformers watermark core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import torch
from transformers import PreTrainedConfig

from watermark_lab.transformers_runtime import EncodedPrompt, GenerationModel


def assistant_content(parsed: object, *, decoded_fallback: str) -> str:
    """Extract only assistant content from a processor response or decoded fallback."""

    if parsed is None:
        content = decoded_fallback
    elif isinstance(parsed, str):
        content = parsed
    elif isinstance(parsed, dict):
        content = cast(dict[object, object], parsed).get("content")
        if not isinstance(content, str):
            raise TypeError("parsed response content is not text")
    else:
        raise TypeError("parsed response has an unsupported shape")
    content = content.strip()
    if content:
        return content
    fallback = decoded_fallback.strip()
    if fallback:
        return fallback
    raise ValueError("parsed and decoded continuation text are empty")


@dataclass(slots=True)
class Gemma4Adapter:
    """Supply Gemma-specific loading-independent text operations to the shared core."""

    _model: GenerationModel
    processor: Any
    _device: str = "cuda"

    @property
    def model(self) -> GenerationModel:
        return self._model

    @property
    def model_config(self) -> PreTrainedConfig:
        config = cast(Any, self._model).config
        return cast(PreTrainedConfig, config.get_text_config())

    @property
    def device(self) -> str:
        return self._device

    @property
    def pad_token_id(self) -> int:
        tokenizer = self.processor.tokenizer
        token_id = tokenizer.pad_token_id
        if token_id is None:
            token_id = tokenizer.eos_token_id
        if token_id is None:
            raise ValueError("Gemma tokenizer must define a pad or end token")
        return int(token_id)

    def encode_prompt(self, prompt: str) -> EncodedPrompt:
        if not prompt:
            raise ValueError("prompt must not be empty")
        messages = [{"role": "user", "content": prompt}]
        rendered = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        encoded = self.processor(text=rendered, return_tensors="pt")
        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)
        return EncodedPrompt(
            input_ids=input_ids,
            attention_mask=attention_mask,
            prompt_length=int(input_ids.shape[1]),
            rendered_text=str(rendered),
        )

    def generated_ids(self, output: Any, *, prompt_length: int) -> tuple[int, ...]:
        values = output[0, prompt_length:].tolist()
        return tuple(int(value) for value in values)

    def raw_generated_text(self, generated_ids: tuple[int, ...]) -> str:
        return str(self.processor.decode(generated_ids, skip_special_tokens=False))

    def copied_text(
        self,
        raw_generated_text: str,
        generated_ids: tuple[int, ...],
        encoded: EncodedPrompt,
    ) -> str:
        decoded_fallback = str(self.processor.decode(generated_ids, skip_special_tokens=True))
        try:
            parsed = self.processor.parse_response(
                raw_generated_text,
                prefix=encoded.input_ids[0],
            )
        except (KeyError, TypeError, ValueError):
            parsed = None
        try:
            return assistant_content(parsed, decoded_fallback=decoded_fallback)
        except (KeyError, TypeError, ValueError):
            return assistant_content(None, decoded_fallback=decoded_fallback)

    def copied_token_ids(self, copied_text: str) -> tuple[int, ...]:
        values = self.processor.tokenizer.encode(copied_text, add_special_tokens=False)
        return tuple(int(value) for value in values)

    def token_tensor(self, token_ids: tuple[int, ...]) -> torch.Tensor:
        return torch.tensor([token_ids], device=self.device, dtype=torch.long)
