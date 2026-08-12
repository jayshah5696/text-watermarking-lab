# pyright: reportUnnecessaryIsInstance=false
"""Pure teaching primitives for the Stage 2 toy vocabulary.

This module deliberately defines a toy SHA-256 selector. It is not the PRF used by
an upstream KGW implementation and must not be reused as a reference adapter.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Collection, Sequence


def _require_int(name: str, value: object, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _require_finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _require_token_ids(
    name: str, values: Sequence[int], *, vocabulary_size: int, allow_empty: bool
) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of token IDs")
    checked = tuple(_require_int("token ID", value, minimum=0) for value in values)
    if not allow_empty and not checked:
        raise ValueError(f"{name} must not be empty")
    if any(value >= vocabulary_size for value in checked):
        raise ValueError(f"{name} contains a token ID outside the vocabulary")
    return checked


def green_token_count(*, vocabulary_size: int, gamma: float) -> int:
    """Return the exact toy green-set size, rejecting ambiguous fractions."""

    size = _require_int("vocabulary_size", vocabulary_size, minimum=2)
    fraction = _require_finite("gamma", gamma)
    if not 0.0 < fraction < 1.0:
        raise ValueError("gamma must be strictly between zero and one")
    unrounded = size * fraction
    count = int(unrounded)
    if not math.isclose(unrounded, count, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("gamma times vocabulary_size must be a whole number in the toy lab")
    if not 1 <= count < size:
        raise ValueError("the toy green set must contain between one and vocabulary_size - 1 IDs")
    return count


def toy_green_token_ids(
    *, vocabulary_size: int, context: Sequence[int], development_key: str, gamma: float
) -> tuple[int, ...]:
    """Select the lowest SHA-256 scores under the documented toy rule.

    Each candidate score hashes the ASCII text
    ``lab-02|v1|<key>|<comma-separated-context>|<token-id>``.
    """

    size = _require_int("vocabulary_size", vocabulary_size, minimum=2)
    checked_context = _require_token_ids(
        "context", context, vocabulary_size=size, allow_empty=False
    )
    if not isinstance(development_key, str):
        raise TypeError("development_key must be text")
    if not development_key or not development_key.isascii() or "|" in development_key:
        raise ValueError("development_key must be non-empty ASCII text without '|'")
    count = green_token_count(vocabulary_size=size, gamma=gamma)
    context_text = ",".join(str(token_id) for token_id in checked_context)

    def score(token_id: int) -> bytes:
        material = f"lab-02|v1|{development_key}|{context_text}|{token_id}".encode("ascii")
        return hashlib.sha256(material).digest()

    selected = sorted(range(size), key=lambda token_id: (score(token_id), token_id))[:count]
    return tuple(sorted(selected))


def apply_green_logit_bias(
    *, logits: Sequence[float], green_token_ids: Collection[int], delta: float
) -> tuple[float, ...]:
    """Add ``delta`` to green logits and leave every red logit unchanged."""

    if isinstance(logits, (str, bytes)) or not isinstance(logits, Sequence):
        raise TypeError("logits must be a sequence of real numbers")
    checked_logits = tuple(_require_finite("logit", value) for value in logits)
    if len(checked_logits) < 2:
        raise ValueError("logits must contain at least two values")
    if isinstance(green_token_ids, (str, bytes)) or not isinstance(green_token_ids, Collection):
        raise TypeError("green_token_ids must be a collection of token IDs")
    checked_green = {_require_int("green token ID", value, minimum=0) for value in green_token_ids}
    if not checked_green:
        raise ValueError("green_token_ids must not be empty")
    if any(token_id >= len(checked_logits) for token_id in checked_green):
        raise ValueError("green_token_ids contains an ID outside logits")
    checked_delta = _require_finite("delta", delta)
    if checked_delta < 0.0:
        raise ValueError("delta must be non-negative")
    return tuple(
        logit + checked_delta if token_id in checked_green else logit
        for token_id, logit in enumerate(checked_logits)
    )


def softmax(*, logits: Sequence[float]) -> tuple[float, ...]:
    """Convert finite logits into normalized probabilities."""

    if isinstance(logits, (str, bytes)) or not isinstance(logits, Sequence):
        raise TypeError("logits must be a sequence of real numbers")
    checked = tuple(_require_finite("logit", value) for value in logits)
    if len(checked) < 2:
        raise ValueError("logits must contain at least two values")
    maximum = max(checked)
    weights = tuple(math.exp(value - maximum) for value in checked)
    total = math.fsum(weights)
    return tuple(weight / total for weight in weights)


def sample_from_probabilities(*, probabilities: Sequence[float], draw: float) -> int:
    """Map one visible draw in ``[0, 1)`` to a categorical token ID."""

    if isinstance(probabilities, (str, bytes)) or not isinstance(probabilities, Sequence):
        raise TypeError("probabilities must be a sequence of real numbers")
    checked = tuple(_require_finite("probability", value) for value in probabilities)
    if len(checked) < 2:
        raise ValueError("probabilities must contain at least two values")
    if any(value < 0.0 for value in checked):
        raise ValueError("probabilities must be non-negative")
    if not math.isclose(math.fsum(checked), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("probabilities must sum to one")
    checked_draw = _require_finite("draw", draw)
    if not 0.0 <= checked_draw < 1.0:
        raise ValueError("draw must be at least zero and less than one")
    cumulative = 0.0
    for token_id, probability in enumerate(checked):
        cumulative += probability
        if checked_draw < cumulative:
            return token_id
    return len(checked) - 1


def odds_multiplier(*, delta: float) -> float:
    """Return the green-versus-red relative odds multiplier before normalization."""

    checked_delta = _require_finite("delta", delta)
    return math.exp(checked_delta)
