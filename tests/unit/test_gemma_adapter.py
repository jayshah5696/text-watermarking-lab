from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
import torch

from watermark_lab.gemma_adapter import Gemma4Adapter, assistant_content
from watermark_lab.transformers_runtime import EncodedPrompt


def test_assistant_content_extracts_only_structured_content() -> None:
    parsed = {"role": "assistant", "content": "  copied continuation  "}
    assert assistant_content(parsed, decoded_fallback="fallback") == "copied continuation"
    assert "role" not in assistant_content(parsed, decoded_fallback="fallback")


def test_assistant_content_supports_text_and_rejects_bad_shapes() -> None:
    assert assistant_content(" answer ", decoded_fallback="fallback") == "answer"
    with pytest.raises(TypeError, match="content is not text"):
        assistant_content({"role": "assistant"}, decoded_fallback="fallback")
    with pytest.raises(TypeError, match="unsupported shape"):
        assistant_content(["answer"], decoded_fallback="fallback")
    assert assistant_content(" ", decoded_fallback="fallback") == "fallback"
    assert assistant_content(None, decoded_fallback="fallback") == "fallback"


class FakeTokenizer:
    pad_token_id = None
    eos_token_id = 2

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert add_special_tokens is False
        return [ord(character) % 31 for character in text]


class FakeProcessor:
    def __init__(self, parsed: object) -> None:
        self.tokenizer = FakeTokenizer()
        self.parsed = parsed

    def apply_chat_template(self, messages: Any, **kwargs: Any) -> str:
        assert messages == [{"role": "user", "content": "continue"}]
        assert kwargs == {
            "tokenize": False,
            "add_generation_prompt": True,
            "enable_thinking": False,
        }
        return "<user>continue</user><assistant>"

    def __call__(self, *, text: str, return_tensors: str) -> dict[str, torch.Tensor]:
        assert return_tensors == "pt"
        return {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]]),
        }

    def decode(self, values: Any, *, skip_special_tokens: bool) -> str:
        if skip_special_tokens:
            return "decoded fallback"
        return "<assistant>generated</assistant>"

    def parse_response(self, raw: str, *, prefix: Any) -> object:
        return self.parsed


class FakeConfig:
    def get_text_config(self) -> object:
        return SimpleNamespace(vocab_size=262_144)


class FakeModel:
    config = FakeConfig()

    def generate(self, **kwargs: Any) -> Any:
        raise AssertionError("not used")


def test_gemma_adapter_encodes_chat_and_extracts_content() -> None:
    adapter = Gemma4Adapter(FakeModel(), FakeProcessor({"content": "generated"}), "cpu")
    encoded = adapter.encode_prompt("continue")
    assert encoded.rendered_text == "<user>continue</user><assistant>"
    assert encoded.prompt_length == 3
    assert adapter.pad_token_id == 2
    assert adapter.model_config.vocab_size == 262_144
    assert adapter.copied_text("raw", (4, 5), encoded) == "generated"


def test_gemma_adapter_falls_back_after_parser_error() -> None:
    processor = FakeProcessor({"role": "assistant"})

    def fail(raw: str, *, prefix: Any) -> object:
        raise ValueError("bad parser")

    processor.parse_response = fail  # type: ignore[method-assign]
    adapter = Gemma4Adapter(FakeModel(), processor, "cpu")
    encoded = EncodedPrompt(torch.tensor([[1]]), torch.tensor([[1]]), 1, "rendered")
    assert adapter.copied_text("raw", (4, 5), encoded) == "decoded fallback"


def test_gemma_adapter_falls_back_after_malformed_parser_record() -> None:
    adapter = Gemma4Adapter(FakeModel(), FakeProcessor({"role": "assistant"}), "cpu")
    encoded = EncodedPrompt(torch.tensor([[1]]), torch.tensor([[1]]), 1, "rendered")
    assert adapter.copied_text("raw", (4, 5), encoded) == "decoded fallback"
