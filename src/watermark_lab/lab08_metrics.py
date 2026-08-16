"""Small reproducible text metrics for the Stage 8 trade-off fixture."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from itertools import pairwise

_NUMBER = re.compile(r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?!\w)")


def repeated_adjacent_pair_fraction(token_ids: Sequence[int]) -> float:
    """Return the fraction of adjacent token pairs repeated after their first occurrence."""

    if len(token_ids) < 2:
        raise ValueError("repetition needs at least two token IDs")
    pairs = list(pairwise(token_ids))
    return (len(pairs) - len(set(pairs))) / len(pairs)


def distinct_ngram_fraction(token_ids: Sequence[int], *, width: int) -> float:
    """Return unique token n-grams divided by all token n-grams."""

    if width < 1:
        raise ValueError("n-gram width must be positive")
    if len(token_ids) < width:
        raise ValueError("text is shorter than the n-gram width")
    ngrams = [
        tuple(token_ids[index : index + width]) for index in range(len(token_ids) - width + 1)
    ]
    return len(set(ngrams)) / len(ngrams)


def decimal_numbers(value: str) -> tuple[str, ...]:
    """Extract decimal number surface forms in reading order."""

    return tuple(_NUMBER.findall(value))


def numbers_preserved(source: str, candidate: str) -> bool:
    """Require every source decimal-number occurrence in the candidate."""

    candidate_numbers = list(decimal_numbers(candidate))
    for number in decimal_numbers(source):
        try:
            candidate_numbers.remove(number)
        except ValueError:
            return False
    return True


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Calculate cosine similarity without hiding vector validation."""

    if not left or len(left) != len(right):
        raise ValueError("cosine vectors must have equal nonzero length")
    if any(not math.isfinite(value) for value in (*left, *right)):
        raise ValueError("cosine vectors must be finite")
    numerator = math.fsum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(math.fsum(value * value for value in left))
    right_norm = math.sqrt(math.fsum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("cosine vectors must have nonzero norm")
    return numerator / (left_norm * right_norm)
