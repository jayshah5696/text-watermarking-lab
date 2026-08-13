# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false
"""Pinned MLX runtime for the explicit Stage 3 LFM2 loop."""

from __future__ import annotations

import platform
from importlib.metadata import version
from typing import Any, Literal, cast

import mlx.core as mx
from huggingface_hub import snapshot_download
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache

from watermark_lab.lab03_config import Lab03Config, PromptFixture
from watermark_lab.lab03_records import (
    CandidateTrace,
    Condition,
    ContinuationRecord,
    GenerationStep,
    Lab03Trace,
)
from watermark_lab.manual_generation import (
    ProcessedScores,
    derive_prompt_seed,
    process_scores,
    sample_token,
    score_copied_token_ids,
)


def _token_piece(tokenizer: Any, token_id: int) -> str:
    return cast(
        str,
        tokenizer.decode(
            [token_id],
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
    )


def _encode(tokenizer: Any, text: str) -> tuple[int, ...]:
    encoded = tokenizer.encode(text, add_special_tokens=False)
    return tuple(int(token_id) for token_id in encoded)


def _encode_model_input(
    tokenizer: Any, *, passage: str, instruction_prefix: str
) -> tuple[int, ...]:
    encoded = tokenizer.apply_chat_template(
        [{"role": "user", "content": f"{instruction_prefix}{passage}"}],
        tokenize=True,
        add_generation_prompt=True,
    )
    return tuple(int(token_id) for token_id in encoded)


def _value(values: mx.array, token_id: int) -> float:
    return float(values[token_id].item())


def _record_candidates(
    *,
    tokenizer: Any,
    raw_scores: mx.array,
    processed: ProcessedScores,
    selected_token_id: int,
    count: int,
    enable_score_increase: bool,
    bias: float,
) -> tuple[CandidateTrace, ...]:
    leading = mx.argpartition(-processed.final_log_probabilities, kth=count - 1)[:count]
    selected_ids = [int(token_id) for token_id in leading.tolist()]
    if selected_token_id not in selected_ids:
        selected_ids[-1] = selected_token_id
    selected_ids.sort(key=lambda token_id: _value(processed.probabilities, token_id), reverse=True)
    candidates = []
    for token_id in selected_ids:
        in_green_group = bool(processed.green_mask[token_id].item())
        score_increase = bias if enable_score_increase and in_green_group else 0.0
        candidates.append(
            CandidateTrace(
                token_id=token_id,
                token_text=_token_piece(tokenizer, token_id),
                raw_score=_value(raw_scores, token_id),
                in_green_group=in_green_group,
                score_increase=score_increase,
                score_after_increase=_value(processed.scores_after_increase, token_id),
                temperature_score=_value(processed.temperature_scores, token_id),
                final_probability=_value(processed.probabilities, token_id),
                selected=token_id == selected_token_id,
            )
        )
    return tuple(candidates)


def _generate_record(
    *,
    model: Any,
    tokenizer: Any,
    vocabulary_size: int,
    config: Lab03Config,
    prompt: PromptFixture,
    condition: Condition,
) -> ContinuationRecord:
    prompt_ids = _encode_model_input(
        tokenizer,
        passage=prompt.text,
        instruction_prefix=config.instruction_prefix,
    )
    if not prompt_ids:
        raise ValueError(f"prompt {prompt.id!r} produced no token IDs")
    seed = derive_prompt_seed(base_seed=config.base_seed, prompt_id=prompt.id)
    mx.random.seed(seed)
    prompt_cache = make_prompt_cache(model)
    model_input = mx.array(prompt_ids, dtype=mx.int32)[None]
    generated: list[int] = []
    steps: list[GenerationStep] = []
    stop_reason: Literal["end_token", "token_limit"] = "token_limit"
    enable_score_increase = condition == "score_increase"

    for position in range(1, config.max_new_tokens + 1):
        logits = model(model_input, cache=prompt_cache)
        raw_scores = logits[0, -1, :].astype(mx.float32)
        previous_token_id = prompt_ids[-1] if not generated else generated[-1]
        processed = process_scores(
            raw_scores=raw_scores,
            previous_token_id=previous_token_id,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            green_fraction=config.green_fraction,
            bias=config.watermark_bias,
            hashing_key=config.generation_key,
            enable_score_increase=enable_score_increase,
        )
        selected_token_id = sample_token(processed)
        mx.eval(
            raw_scores,
            processed.green_mask,
            processed.scores_after_increase,
            processed.temperature_scores,
            processed.top_p_scores,
            processed.top_k_scores,
            processed.probabilities,
        )
        in_green_group = bool(processed.green_mask[selected_token_id].item())
        score_increase = config.watermark_bias if enable_score_increase and in_green_group else 0.0
        candidates = _record_candidates(
            tokenizer=tokenizer,
            raw_scores=raw_scores,
            processed=processed,
            selected_token_id=selected_token_id,
            count=config.trace_candidates,
            enable_score_increase=enable_score_increase,
            bias=config.watermark_bias,
        )
        steps.append(
            GenerationStep(
                position=position,
                input_length=len(prompt_ids) + len(generated),
                previous_token_id=previous_token_id,
                available_after_top_p=int(mx.sum(mx.isfinite(processed.top_p_scores)).item()),
                available_after_top_k=int(mx.sum(mx.isfinite(processed.top_k_scores)).item()),
                candidates=candidates,
                selected_token_id=selected_token_id,
                selected_token_text=_token_piece(tokenizer, selected_token_id),
                selected_token_in_green_group=in_green_group,
                selected_raw_score=_value(raw_scores, selected_token_id),
                selected_score_increase=score_increase,
                selected_score_after_increase=_value(
                    processed.scores_after_increase, selected_token_id
                ),
                selected_temperature_score=_value(processed.temperature_scores, selected_token_id),
                selected_probability=_value(processed.probabilities, selected_token_id),
            )
        )
        generated.append(selected_token_id)
        if selected_token_id == int(tokenizer.eos_token_id):
            stop_reason = "end_token"
            break
        model_input = mx.array([[selected_token_id]], dtype=mx.int32)

    decoded_text = cast(
        str,
        tokenizer.decode(
            generated,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
    )
    copied_ids = _encode(tokenizer, decoded_text)
    if len(copied_ids) <= config.context_width:
        raise ValueError("copied continuation is too short for the Stage 3 checker")
    mx.clear_cache()
    return ContinuationRecord(
        prompt_id=prompt.id,
        prompt_text=prompt.text,
        condition=condition,
        seed=seed,
        stop_reason=stop_reason,
        prompt_token_ids=prompt_ids,
        prompt_token_pieces=tuple(_token_piece(tokenizer, token_id) for token_id in prompt_ids),
        generated_token_ids=tuple(generated),
        decoded_text=decoded_text,
        copied_token_ids=copied_ids,
        copied_ids_match=tuple(generated) == copied_ids,
        generation_key_score=score_copied_token_ids(
            token_ids=copied_ids,
            vocabulary_size=vocabulary_size,
            green_fraction=config.green_fraction,
            hashing_key=config.generation_key,
            key_role="generation",
            context_width=config.context_width,
        ),
        comparison_key_score=score_copied_token_ids(
            token_ids=copied_ids,
            vocabulary_size=vocabulary_size,
            green_fraction=config.green_fraction,
            hashing_key=config.comparison_key,
            key_role="comparison",
            context_width=config.context_width,
        ),
        steps=tuple(steps),
    )


def build_lab03_trace(
    *,
    source_commit: str,
    config_sha256: str,
    config: Lab03Config,
    local_files_only: bool,
) -> Lab03Trace:
    """Load the pinned fixture and generate all six deterministic records."""

    model_path = snapshot_download(
        repo_id=config.model_id,
        revision=config.model_revision,
        local_files_only=local_files_only,
    )
    model, tokenizer = cast(tuple[Any, Any], load(model_path, lazy=False))
    vocabulary_size = int(model.args.vocab_size)
    records = tuple(
        _generate_record(
            model=model,
            tokenizer=tokenizer,
            vocabulary_size=vocabulary_size,
            config=config,
            prompt=prompt,
            condition=condition,
        )
        for prompt in config.prompts
        for condition in ("control", "score_increase")
    )
    return Lab03Trace(
        schema_version=1,
        source_commit=source_commit,
        config_sha256=config_sha256,
        python_version=platform.python_version(),
        platform=platform.platform(),
        mlx_version=version("mlx"),
        mlx_lm_version=version("mlx-lm"),
        config=config,
        records=records,
    )
