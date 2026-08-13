from __future__ import annotations

import math

import mlx.core as mx
import pytest
from mlx_lm.sample_utils import apply_top_p

from watermark_lab.manual_generation import (
    derive_prompt_seed,
    finite_or_none,
    green_token_mask,
    process_scores,
    sample_token,
    score_copied_token_ids,
)


def _process(
    raw: mx.array,
    *,
    bias: float = 2.0,
    enabled: bool = True,
    top_p: float = 0.95,
    top_k: int = 4,
):
    return process_scores(
        raw_scores=raw,
        previous_token_id=3,
        temperature=0.8,
        top_p=top_p,
        top_k=top_k,
        green_fraction=0.25,
        bias=bias,
        hashing_key=15485863,
        enable_score_increase=enabled,
    )


def test_prompt_seed_is_stable_prompt_specific_and_pinned() -> None:
    first = derive_prompt_seed(base_seed=20260812, prompt_id="notebook")
    assert first == 640916431
    assert first == derive_prompt_seed(base_seed=20260812, prompt_id="notebook")
    assert first != derive_prompt_seed(base_seed=20260812, prompt_id="library")


@pytest.mark.parametrize(
    ("base_seed", "prompt_id", "error"),
    [
        (True, "prompt", TypeError),
        (-1, "prompt", ValueError),
        (1, 7, TypeError),
        (1, "", ValueError),
        (1, "bad|id", ValueError),
        (1, "café", ValueError),
    ],
)
def test_prompt_seed_rejects_invalid_inputs(
    base_seed: object, prompt_id: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        derive_prompt_seed(base_seed=base_seed, prompt_id=prompt_id)  # type: ignore[arg-type]


def test_portable_selector_has_exact_pinned_membership() -> None:
    mask = green_token_mask(
        previous_token_id=3,
        vocabulary_size=20,
        green_fraction=0.25,
        hashing_key=15485863,
    )
    assert [index for index, green in enumerate(mask.tolist()) if green] == [2, 8, 9, 16, 18]


def test_top_p_keeps_the_first_token_that_crosses_the_cutoff() -> None:
    probabilities = mx.array([0.40, 0.30, 0.20, 0.10], dtype=mx.float32)
    filtered = apply_top_p(mx.log(probabilities), 0.65)
    assert mx.isfinite(filtered).tolist() == [True, True, False, False]


def test_green_token_can_receive_increase_then_be_filtered() -> None:
    green = green_token_mask(
        previous_token_id=3,
        vocabulary_size=20,
        green_fraction=0.25,
        hashing_key=15485863,
    )
    removed_green = 18
    raw_values = [-10.0] * 20
    non_green = [token_id for token_id in range(20) if not bool(green[token_id].item())]
    for token_id, value in zip(non_green[:4], [4.0, 3.0, 2.0, 1.0], strict=True):
        raw_values[token_id] = value
    raw_values[removed_green] = -5.0
    processed = _process(mx.array(raw_values), top_p=1.0)
    assert bool(processed.green_mask[removed_green].item())
    assert processed.scores_after_increase[removed_green].item() == -3.0
    assert math.isinf(processed.top_k_scores[removed_green].item())
    assert processed.probabilities[removed_green].item() == 0.0


def test_bias_zero_matches_control_distribution_and_sample() -> None:
    raw = mx.array([3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -3.0, -4.0])
    off = _process(raw, bias=0.0, enabled=False, top_k=5)
    on = _process(raw, bias=0.0, enabled=True, top_k=5)
    assert bool(mx.array_equal(off.final_log_probabilities, on.final_log_probabilities).item())
    assert bool(mx.array_equal(off.probabilities, on.probabilities).item())
    mx.random.seed(99)
    first = sample_token(off)
    mx.random.seed(99)
    assert sample_token(on) == first


def test_processing_boundaries_are_separate_and_normalized() -> None:
    raw = mx.arange(8, dtype=mx.float32)
    processed = _process(raw, top_p=1.0)
    expected_increase = mx.where(processed.green_mask, 2.0, 0.0)
    assert bool(mx.allclose(processed.scores_after_increase - raw, expected_increase).item())
    assert bool(
        mx.allclose(
            processed.temperature_scores,
            processed.scores_after_increase / 0.8,
        ).item()
    )
    assert int(mx.sum(mx.isfinite(processed.top_p_scores)).item()) == 8
    assert int(mx.sum(mx.isfinite(processed.top_k_scores)).item()) == 4
    assert math.isclose(float(mx.sum(processed.probabilities).item()), 1.0, abs_tol=1e-6)


def test_copied_text_score_excludes_first_context_token_and_key_matters() -> None:
    token_ids = (1, 2, 3, 4, 5, 6, 7, 8)
    generation = score_copied_token_ids(
        token_ids=token_ids,
        vocabulary_size=20,
        green_fraction=0.25,
        hashing_key=15485863,
        key_role="generation",
        context_width=1,
    )
    comparison = score_copied_token_ids(
        token_ids=token_ids,
        vocabulary_size=20,
        green_fraction=0.25,
        hashing_key=15485867,
        key_role="comparison",
        context_width=1,
    )
    assert generation.eligible_tokens == comparison.eligible_tokens == len(token_ids) - 1
    assert generation.expected_green_hits == 1.75
    assert generation.key_role == "generation"
    assert comparison.key_role == "comparison"
    assert (generation.green_hits, generation.z_score) != (
        comparison.green_hits,
        comparison.z_score,
    )


@pytest.mark.parametrize(
    "arguments",
    [
        {"previous_token_id": -1, "vocabulary_size": 20, "green_fraction": 0.25, "hashing_key": 1},
        {"previous_token_id": 1, "vocabulary_size": 1, "green_fraction": 0.25, "hashing_key": 1},
        {"previous_token_id": 1, "vocabulary_size": 20, "green_fraction": 1.0, "hashing_key": 1},
        {"previous_token_id": 1, "vocabulary_size": 20, "green_fraction": 0.01, "hashing_key": 1},
        {"previous_token_id": 1, "vocabulary_size": 20, "green_fraction": 0.25, "hashing_key": 0},
    ],
)
def test_selector_rejects_invalid_inputs(arguments: dict[str, int | float]) -> None:
    with pytest.raises(ValueError):
        green_token_mask(**arguments)  # type: ignore[arg-type]


def test_score_processing_and_scalar_helpers_reject_bad_inputs() -> None:
    raw = mx.arange(8, dtype=mx.float32)
    with pytest.raises(ValueError, match="shape"):
        _process(raw[None])
    with pytest.raises(ValueError, match="temperature"):
        process_scores(
            raw_scores=raw,
            previous_token_id=1,
            temperature=0.0,
            top_p=0.95,
            top_k=4,
            green_fraction=0.25,
            bias=2.0,
            hashing_key=1,
            enable_score_increase=True,
        )
    with pytest.raises(ValueError, match="context"):
        score_copied_token_ids(
            token_ids=(1,),
            vocabulary_size=20,
            green_fraction=0.25,
            hashing_key=1,
            key_role="generation",
            context_width=1,
        )
    assert finite_or_none(mx.array(1.5)) == 1.5
    assert finite_or_none(mx.array(float("-inf"))) is None


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"top_p": 0.0}, "top_p"),
        ({"top_k": 8}, "top_k"),
        ({"bias": -1.0}, "bias"),
        ({"bias": float("nan")}, "bias"),
    ],
)
def test_score_processing_rejects_invalid_sampling_settings(
    changes: dict[str, int | float], message: str
) -> None:
    arguments: dict[str, object] = {
        "raw_scores": mx.arange(8, dtype=mx.float32),
        "previous_token_id": 1,
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 4,
        "green_fraction": 0.25,
        "bias": 2.0,
        "hashing_key": 1,
        "enable_score_increase": True,
    }
    arguments.update(changes)
    with pytest.raises(ValueError, match=message):
        process_scores(**arguments)  # type: ignore[arg-type]


def test_copied_text_scorer_rejects_other_context_width() -> None:
    with pytest.raises(ValueError, match="context_width"):
        score_copied_token_ids(
            token_ids=(1, 2, 3),
            vocabulary_size=20,
            green_fraction=0.25,
            hashing_key=1,
            key_role="generation",
            context_width=2,
        )
