# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUnnecessaryIsInstance=false
"""MLX-native primitives for the explicit Stage 3 sampling loop."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Literal

import mlx.core as mx
from mlx_lm.sample_utils import apply_top_k, apply_top_p

from watermark_lab.stats import expected_hits, green_hit_z_score

UINT32_MODULUS = 1 << 32


def derive_prompt_seed(*, base_seed: int, prompt_id: str) -> int:
    """Derive a stable per-prompt seed in MLX's unsigned 32-bit range."""

    if isinstance(base_seed, bool) or not isinstance(base_seed, int):
        raise TypeError("base_seed must be an integer")
    if base_seed < 0:
        raise ValueError("base_seed must be non-negative")
    if not isinstance(prompt_id, str):
        raise TypeError("prompt_id must be text")
    if not prompt_id or not prompt_id.isascii() or "|" in prompt_id:
        raise ValueError("prompt_id must be non-empty ASCII text without '|'")
    material = f"lab-03|{base_seed}|{prompt_id}".encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % UINT32_MODULUS


def green_token_mask(
    *, previous_token_id: int, vocabulary_size: int, green_fraction: float, hashing_key: int
) -> mx.array:
    """Return the exact Stage 3 green group with a vectorized 32-bit mixer.

    The mixer is deterministic and portable within this lab profile. It is not a
    cryptographic pseudo-random function.
    """

    if previous_token_id < 0:
        raise ValueError("previous_token_id must be non-negative")
    if vocabulary_size < 2:
        raise ValueError("vocabulary_size must be at least two")
    if not 0.0 < green_fraction < 1.0:
        raise ValueError("green_fraction must be strictly between zero and one")
    if hashing_key < 1:
        raise ValueError("hashing_key must be positive")
    green_count = math.floor(green_fraction * vocabulary_size)
    if not 0 < green_count < vocabulary_size:
        raise ValueError("green_fraction must select at least one but not every token")

    candidate_ids = mx.arange(vocabulary_size, dtype=mx.uint32)
    context = mx.array(previous_token_id % UINT32_MODULUS, dtype=mx.uint32)
    key = mx.array(hashing_key % UINT32_MODULUS, dtype=mx.uint32)
    mixed = candidate_ids ^ key ^ (context * mx.array(0x9E3779B1, dtype=mx.uint32))
    mixed = mixed ^ (mixed >> 16)
    mixed = mixed * mx.array(0x7FEB352D, dtype=mx.uint32)
    mixed = mixed ^ (mixed >> 15)
    mixed = mixed * mx.array(0x846CA68B, dtype=mx.uint32)
    mixed = mixed ^ (mixed >> 16)
    green_ids = mx.argpartition(mixed, kth=green_count - 1)[:green_count]
    return mx.put_along_axis(
        mx.zeros((vocabulary_size,), dtype=mx.bool_), green_ids, mx.array(True), axis=-1
    )


@dataclass(frozen=True, slots=True)
class ProcessedScores:
    """Scores at each locked Stage 3 processing boundary."""

    green_mask: mx.array
    scores_after_increase: mx.array
    temperature_scores: mx.array
    top_p_scores: mx.array
    top_k_scores: mx.array
    final_log_probabilities: mx.array
    probabilities: mx.array


def process_scores(
    *,
    raw_scores: mx.array,
    previous_token_id: int,
    temperature: float,
    top_p: float,
    top_k: int,
    green_fraction: float,
    bias: float,
    hashing_key: int,
    enable_score_increase: bool,
) -> ProcessedScores:
    """Apply score increase, temperature, top-p, top-k, and normalization."""

    if raw_scores.ndim != 1:
        raise ValueError("raw_scores must have shape (vocabulary_size,)")
    vocabulary_size = raw_scores.shape[0]
    if not temperature > 0.0:
        raise ValueError("temperature must be greater than zero")
    if not 0.0 < top_p <= 1.0:
        raise ValueError("top_p must be greater than zero and at most one")
    if not 0 < top_k < vocabulary_size:
        raise ValueError("top_k must be positive and smaller than the vocabulary")
    if bias < 0.0 or not math.isfinite(bias):
        raise ValueError("bias must be finite and non-negative")

    green_mask = green_token_mask(
        previous_token_id=previous_token_id,
        vocabulary_size=vocabulary_size,
        green_fraction=green_fraction,
        hashing_key=hashing_key,
    )
    increase = mx.where(green_mask, mx.array(bias, raw_scores.dtype), 0.0)
    if not enable_score_increase:
        increase = mx.zeros_like(raw_scores)
    scores_after_increase = raw_scores + increase
    temperature_scores = scores_after_increase / temperature
    log_probabilities = temperature_scores - mx.logsumexp(temperature_scores)
    top_p_scores = apply_top_p(log_probabilities, top_p)
    top_k_scores = apply_top_k(top_p_scores, top_k)
    final_log_probabilities = top_k_scores - mx.logsumexp(top_k_scores)
    probabilities = mx.exp(final_log_probabilities)
    return ProcessedScores(
        green_mask=green_mask,
        scores_after_increase=scores_after_increase,
        temperature_scores=temperature_scores,
        top_p_scores=top_p_scores,
        top_k_scores=top_k_scores,
        final_log_probabilities=final_log_probabilities,
        probabilities=probabilities,
    )


def sample_token(processed: ProcessedScores) -> int:
    """Sample one token from a processed score vector using MLX random state."""

    return int(mx.random.categorical(processed.final_log_probabilities).item())


@dataclass(frozen=True, slots=True)
class GreenScore:
    """Stage 1 count reconstructed from copied Stage 3 token IDs."""

    key_role: Literal["generation", "comparison"]
    green_hits: int
    eligible_tokens: int
    expected_green_hits: float
    z_score: float


def score_copied_token_ids(
    *,
    token_ids: tuple[int, ...],
    vocabulary_size: int,
    green_fraction: float,
    hashing_key: int,
    key_role: Literal["generation", "comparison"],
    context_width: int,
) -> GreenScore:
    """Rebuild green membership from copied IDs and return the Stage 1 count."""

    if context_width != 1:
        raise ValueError("Stage 3 locks context_width to one")
    if len(token_ids) <= context_width:
        raise ValueError("copied token IDs must contain context and at least one eligible token")
    hits = 0
    for position in range(context_width, len(token_ids)):
        mask = green_token_mask(
            previous_token_id=token_ids[position - 1],
            vocabulary_size=vocabulary_size,
            green_fraction=green_fraction,
            hashing_key=hashing_key,
        )
        hits += int(mask[token_ids[position]].item())
    trials = len(token_ids) - context_width
    return GreenScore(
        key_role=key_role,
        green_hits=hits,
        eligible_tokens=trials,
        expected_green_hits=expected_hits(trials=trials, null_probability=green_fraction),
        z_score=green_hit_z_score(hits=hits, trials=trials, null_probability=green_fraction),
    )


def finite_or_none(value: mx.array) -> float | None:
    """Convert a scalar MLX array to a finite JSON value or ``None``."""

    number = float(value.item())
    return number if math.isfinite(number) else None
