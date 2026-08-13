from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import mlx.core as mx
import pytest

import watermark_lab.lab03_runtime as runtime
from watermark_lab.lab03_config import config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]


class FakeTokenizer:
    eos_token_id = 99

    def apply_chat_template(
        self,
        messages: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
    ) -> list[int]:
        assert messages[0]["role"] == "user"
        assert tokenize is True
        assert add_generation_prompt is True
        return [1, 2]

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert add_special_tokens is False
        if text.startswith("ids:"):
            return [int(value) for value in text.removeprefix("ids:").split(",")]
        return [1, 2]

    def decode(
        self,
        token_ids: list[int],
        *,
        skip_special_tokens: bool,
        clean_up_tokenization_spaces: bool,
    ) -> str:
        assert skip_special_tokens is False
        assert clean_up_tokenization_spaces is False
        return "ids:" + ",".join(str(token_id) for token_id in token_ids)


class FakeModel:
    args = SimpleNamespace(vocab_size=8)

    def __call__(self, token_ids: mx.array, *, cache: list[Any]) -> mx.array:
        del cache
        scores = mx.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
        return mx.broadcast_to(scores, (1, token_ids.shape[1], scores.shape[0]))


class EmptyPromptTokenizer(FakeTokenizer):
    def apply_chat_template(
        self,
        messages: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
    ) -> list[int]:
        return []


class ShortCopyTokenizer(FakeTokenizer):
    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        return [1]


class EndTokenTokenizer(FakeTokenizer):
    eos_token_id = 6

    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        if text.startswith("ids:"):
            return [0, 6]
        return [1, 2]


def _small_config():
    config = config_from_toml_bytes((ROOT / "configs/lab_03.toml").read_bytes())
    return replace(config, max_new_tokens=2, top_k=4, trace_candidates=3)


def test_generate_record_uses_cache_and_copied_text_replay(monkeypatch) -> None:
    monkeypatch.setattr(runtime, "make_prompt_cache", lambda model: [])
    monkeypatch.setattr(
        runtime,
        "sample_token",
        lambda processed: int(mx.argmax(processed.final_log_probabilities).item()),
    )
    config = _small_config()
    record = runtime._generate_record(
        model=FakeModel(),
        tokenizer=FakeTokenizer(),
        vocabulary_size=8,
        config=config,
        prompt=config.prompts[0],
        condition="score_increase",
    )
    assert len(record.steps) == 2
    assert record.copied_ids_match
    assert record.generation_key_score.eligible_tokens == 1
    assert record.steps[0].available_after_top_k <= record.steps[0].available_after_top_p
    assert record.steps[0].candidates[0].final_probability > 0.0


def test_build_trace_loads_pinned_snapshot_and_six_pairs(monkeypatch) -> None:
    calls: list[tuple[str, str, bool]] = []

    def fake_snapshot_download(*, repo_id: str, revision: str, local_files_only: bool) -> str:
        calls.append((repo_id, revision, local_files_only))
        return "/tmp/fake-lfm2"

    monkeypatch.setattr(runtime, "snapshot_download", fake_snapshot_download)
    monkeypatch.setattr(runtime, "load", lambda path, lazy: (FakeModel(), FakeTokenizer()))
    monkeypatch.setattr(runtime, "make_prompt_cache", lambda model: [])
    monkeypatch.setattr(runtime, "version", lambda package: f"test-{package}")
    monkeypatch.setattr(
        runtime,
        "sample_token",
        lambda processed: int(mx.argmax(processed.final_log_probabilities).item()),
    )
    config = _small_config()
    trace = runtime.build_lab03_trace(
        source_commit="a" * 40,
        config_sha256="b" * 64,
        config=config,
        local_files_only=True,
    )
    assert calls == [(config.model_id, config.model_revision, True)]
    assert trace.mlx_version == "test-mlx"
    assert trace.mlx_lm_version == "test-mlx-lm"
    assert [(record.prompt_id, record.condition) for record in trace.records] == [
        (prompt.id, condition)
        for prompt in config.prompts
        for condition in ("control", "score_increase")
    ]


def test_candidate_record_keeps_selected_survivor_outside_display_cutoff() -> None:
    raw = mx.arange(8, dtype=mx.float32)
    processed = runtime.process_scores(
        raw_scores=raw,
        previous_token_id=3,
        temperature=0.8,
        top_p=1.0,
        top_k=4,
        green_fraction=0.25,
        bias=2.0,
        hashing_key=15485863,
        enable_score_increase=True,
    )
    survivors = [
        token_id
        for token_id, probability in enumerate(processed.probabilities.tolist())
        if probability > 0.0
    ]
    selected = min(survivors, key=lambda token_id: processed.probabilities[token_id].item())
    candidates = runtime._record_candidates(
        tokenizer=FakeTokenizer(),
        raw_scores=raw,
        processed=processed,
        selected_token_id=selected,
        count=1,
        enable_score_increase=True,
        bias=2.0,
    )
    assert candidates[0].selected


def test_generate_record_rejects_empty_prompt_and_short_copy(monkeypatch) -> None:
    monkeypatch.setattr(runtime, "make_prompt_cache", lambda model: [])
    monkeypatch.setattr(
        runtime,
        "sample_token",
        lambda processed: int(mx.argmax(processed.final_log_probabilities).item()),
    )
    config = _small_config()
    with pytest.raises(ValueError, match="no token IDs"):
        runtime._generate_record(
            model=FakeModel(),
            tokenizer=EmptyPromptTokenizer(),
            vocabulary_size=8,
            config=config,
            prompt=config.prompts[0],
            condition="control",
        )
    with pytest.raises(ValueError, match="too short"):
        runtime._generate_record(
            model=FakeModel(),
            tokenizer=ShortCopyTokenizer(),
            vocabulary_size=8,
            config=config,
            prompt=config.prompts[0],
            condition="control",
        )


def test_generate_record_stops_on_end_token(monkeypatch) -> None:
    monkeypatch.setattr(runtime, "make_prompt_cache", lambda model: [])
    monkeypatch.setattr(runtime, "sample_token", lambda processed: 6)
    config = _small_config()
    record = runtime._generate_record(
        model=FakeModel(),
        tokenizer=EndTokenTokenizer(),
        vocabulary_size=8,
        config=config,
        prompt=config.prompts[0],
        condition="control",
    )
    assert record.stop_reason == "end_token"
    assert len(record.steps) == 1
