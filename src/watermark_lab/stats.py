# pyright: reportUnnecessaryIsInstance=false
"""Small, explicit statistical primitives for the biased-coin teaching lab."""

from __future__ import annotations

import hashlib
import math
import random


def _require_int(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _require_probability(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    probability = float(value)
    if not math.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1")
    return probability


def expected_hits(*, trials: int, null_probability: float) -> float:
    """Return the expected green-hit count under the configured null."""

    checked_trials = _require_int("trials", trials, minimum=1)
    probability = _require_probability("null_probability", null_probability)
    return checked_trials * probability


def green_hit_z_score(*, hits: int, trials: int, null_probability: float) -> float:
    """Standardize observed green hits against the independent binomial null."""

    checked_trials = _require_int("trials", trials, minimum=1)
    checked_hits = _require_int("hits", hits, minimum=0)
    if checked_hits > checked_trials:
        raise ValueError("hits must not exceed trials")
    probability = _require_probability("null_probability", null_probability)
    expected = checked_trials * probability
    variance = checked_trials * probability * (1.0 - probability)
    return (checked_hits - expected) / math.sqrt(variance)


def exact_binomial_upper_tail(*, hits: int, trials: int, null_probability: float) -> float:
    """Return P(X >= hits) for the Stage 1 binomial range through 400 trials."""

    checked_trials = _require_int("trials", trials, minimum=1)
    checked_hits = _require_int("hits", hits, minimum=0)
    if checked_hits > checked_trials:
        raise ValueError("hits must not exceed trials")
    probability = _require_probability("null_probability", null_probability)
    if checked_hits == 0:
        return 1.0
    complement = 1.0 - probability
    terms = (
        math.comb(checked_trials, k) * probability**k * complement ** (checked_trials - k)
        for k in range(checked_hits, checked_trials + 1)
    )
    return math.fsum(terms)


def derive_group_seed(*, base_seed: int, condition: str, trials: int) -> int:
    """Derive an independent deterministic seed for a condition/length group."""

    checked_seed = _require_int("base_seed", base_seed)
    checked_trials = _require_int("trials", trials, minimum=1)
    if not isinstance(condition, str):
        raise TypeError("condition must be text")
    if not condition or not condition.isascii():
        raise ValueError("condition must be non-empty ASCII text")
    material = f"lab-01|{checked_seed}|{condition}|{checked_trials}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=False)


def simulate_hit_counts(
    *, trials: int, hit_probability: float, replicates: int, seed: int
) -> tuple[int, ...]:
    """Simulate independent hit counts without touching module-global random state."""

    checked_trials = _require_int("trials", trials, minimum=1)
    probability = _require_probability("hit_probability", hit_probability)
    checked_replicates = _require_int("replicates", replicates, minimum=1)
    checked_seed = _require_int("seed", seed)
    generator = random.Random(checked_seed)
    return tuple(
        sum(generator.random() < probability for _ in range(checked_trials))
        for _ in range(checked_replicates)
    )
