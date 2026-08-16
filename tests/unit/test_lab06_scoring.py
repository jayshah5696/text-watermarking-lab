from collections import Counter
from itertools import pairwise

import pytest

from watermark_lab.lab06_scoring import (
    group_pair_queries,
    resolve_pair_memberships,
    score_sequence,
)


def membership(previous: int, target: int) -> bool:
    return (previous * 7 + target * 11) % 5 < 2


def test_grouped_selector_matches_direct_pair_scoring() -> None:
    sequences = ((1, 2, 1, 2, 3), (1, 4, 1, 2, 4))
    calls: Counter[int] = Counter()

    def selector(previous: int, targets: tuple[int, ...]) -> dict[int, bool]:
        calls[previous] += 1
        return {target: membership(previous, target) for target in targets}

    grouped = group_pair_queries(sequences)
    assert grouped == {1: (2, 4), 2: (1, 3, 4), 4: (1,)}
    resolved = resolve_pair_memberships(sequences, selector)
    assert calls == Counter({1: 1, 2: 1, 4: 1})
    for sequence in sequences:
        pairs = list(pairwise(sequence))
        expected_all = sum(membership(*pair) for pair in pairs)
        distinct = tuple(dict.fromkeys(pairs))
        counts = score_sequence(sequence, resolved)
        assert counts.all_hits == expected_all
        assert counts.all_trials == len(pairs)
        assert counts.distinct_hits == sum(membership(*pair) for pair in distinct)
        assert counts.distinct_trials == len(distinct)


def test_scoring_rejects_incomplete_membership_map_and_short_sequence() -> None:
    with pytest.raises(ValueError, match="at least two"):
        score_sequence((1,), {})
    with pytest.raises(ValueError, match="missing keyed"):
        score_sequence((1, 2), {})
    with pytest.raises(ValueError, match="one Boolean"):
        resolve_pair_memberships(((1, 2),), lambda _previous, _targets: {})
