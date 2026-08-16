"""Grouped exact-pair scoring helpers for Stage 6."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise

Pair = tuple[int, int]
PairSelector = Callable[[int, tuple[int, ...]], Mapping[int, bool]]


@dataclass(frozen=True, slots=True)
class PairCounts:
    all_hits: int
    all_trials: int
    distinct_hits: int
    distinct_trials: int


def group_pair_queries(sequences: Sequence[Sequence[int]]) -> dict[int, tuple[int, ...]]:
    grouped: defaultdict[int, set[int]] = defaultdict(set)
    for sequence in sequences:
        for previous, target in pairwise(sequence):
            grouped[previous].add(target)
    return {previous: tuple(sorted(targets)) for previous, targets in sorted(grouped.items())}


def resolve_pair_memberships(
    sequences: Sequence[Sequence[int]], selector: PairSelector
) -> dict[Pair, bool]:
    memberships: dict[Pair, bool] = {}
    for previous, targets in group_pair_queries(sequences).items():
        selected = selector(previous, targets)
        if set(selected) != set(targets):
            raise ValueError("pair selector must return one Boolean for every requested target")
        memberships.update({(previous, target): selected[target] for target in targets})
    return memberships


def score_sequence(sequence: Sequence[int], memberships: Mapping[Pair, bool]) -> PairCounts:
    pairs = list(pairwise(sequence))
    if not pairs:
        raise ValueError("a scored sequence needs at least two tokens")
    try:
        outcomes = [memberships[pair] for pair in pairs]
    except KeyError as error:
        raise ValueError("missing keyed membership for a sequence pair") from error
    distinct_pairs = tuple(dict.fromkeys(pairs))
    return PairCounts(
        all_hits=sum(outcomes),
        all_trials=len(outcomes),
        distinct_hits=sum(memberships[pair] for pair in distinct_pairs),
        distinct_trials=len(distinct_pairs),
    )
