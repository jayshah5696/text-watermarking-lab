from __future__ import annotations

import math
from typing import Any, cast

import pytest

from watermark_lab.toy_greenlist import (
    apply_green_logit_bias,
    green_token_count,
    odds_multiplier,
    sample_from_probabilities,
    softmax,
    toy_green_token_ids,
)


def test_frozen_green_list_vector() -> None:
    assert toy_green_token_ids(
        vocabulary_size=20,
        context=(3, 7, 11, 15),
        development_key="stage-02-public-demo-key-v1",
        gamma=0.25,
    ) == (0, 10, 11, 12, 14)


def test_same_inputs_reproduce_membership() -> None:
    arguments = {
        "vocabulary_size": 20,
        "context": (3, 7, 11, 15),
        "development_key": "stage-02-public-demo-key-v1",
        "gamma": 0.25,
    }
    assert toy_green_token_ids(**arguments) == toy_green_token_ids(**arguments)


def test_wrong_key_and_changed_context_change_membership() -> None:
    expected = toy_green_token_ids(
        vocabulary_size=20,
        context=(3, 7, 11, 15),
        development_key="stage-02-public-demo-key-v1",
        gamma=0.25,
    )
    assert (
        toy_green_token_ids(
            vocabulary_size=20,
            context=(3, 7, 11, 15),
            development_key="wrong-public-key",
            gamma=0.25,
        )
        != expected
    )
    assert (
        toy_green_token_ids(
            vocabulary_size=20,
            context=(3, 7, 11, 16),
            development_key="stage-02-public-demo-key-v1",
            gamma=0.25,
        )
        != expected
    )


def test_green_token_count_is_exact() -> None:
    assert green_token_count(vocabulary_size=20, gamma=0.25) == 5
    assert green_token_count(vocabulary_size=20, gamma=0.5) == 10


@pytest.mark.parametrize(
    ("vocabulary_size", "gamma", "error"),
    [
        (True, 0.25, TypeError),
        (1, 0.25, ValueError),
        (20, True, TypeError),
        (20, float("nan"), ValueError),
        (20, 0.0, ValueError),
        (20, 1.0, ValueError),
        (20, 0.26, ValueError),
    ],
)
def test_green_token_count_rejects_invalid_inputs(
    vocabulary_size: object, gamma: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        green_token_count(vocabulary_size=vocabulary_size, gamma=gamma)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"context": "3,7"}, TypeError),
        ({"context": ()}, ValueError),
        ({"context": (3, True)}, TypeError),
        ({"context": (3, 20)}, ValueError),
        ({"development_key": 7}, TypeError),
        ({"development_key": ""}, ValueError),
        ({"development_key": "bad|key"}, ValueError),
        ({"development_key": "café"}, ValueError),
    ],
)
def test_toy_selector_rejects_invalid_inputs(
    overrides: dict[str, object], error: type[Exception]
) -> None:
    arguments: dict[str, object] = {
        "vocabulary_size": 20,
        "context": (3, 7, 11, 15),
        "development_key": "stage-02-public-demo-key-v1",
        "gamma": 0.25,
    }
    arguments.update(overrides)
    with pytest.raises(error):
        toy_green_token_ids(**arguments)  # type: ignore[arg-type]


def test_bias_changes_only_green_logits_and_multiplies_relative_odds() -> None:
    raw = (1.0, 0.0, -1.0)
    adjusted = apply_green_logit_bias(logits=raw, green_token_ids={1}, delta=2.0)
    assert adjusted == (1.0, 2.0, -1.0)
    before = softmax(logits=raw)
    after = softmax(logits=adjusted)
    before_odds = before[1] / before[0]
    after_odds = after[1] / after[0]
    assert after_odds / before_odds == pytest.approx(math.exp(2.0))
    assert odds_multiplier(delta=2.0) == pytest.approx(math.exp(2.0))


@pytest.mark.parametrize(
    ("logits", "green", "delta", "error"),
    [
        ("bad", {0}, 2.0, TypeError),
        ((0.0,), {0}, 2.0, ValueError),
        ((0.0, float("inf")), {0}, 2.0, ValueError),
        ((0.0, 1.0), "bad", 2.0, TypeError),
        ((0.0, 1.0), set(), 2.0, ValueError),
        ((0.0, 1.0), {True}, 2.0, TypeError),
        ((0.0, 1.0), {2}, 2.0, ValueError),
        ((0.0, 1.0), {0}, -1.0, ValueError),
        ((0.0, 1.0), {0}, True, TypeError),
    ],
)
def test_bias_rejects_invalid_inputs(
    logits: object, green: object, delta: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        apply_green_logit_bias(
            logits=cast(Any, logits),
            green_token_ids=cast(Any, green),
            delta=cast(Any, delta),
        )


def test_softmax_is_stable_and_normalized() -> None:
    probabilities = softmax(logits=(1000.0, 999.0, 998.0))
    assert math.fsum(probabilities) == pytest.approx(1.0)
    assert probabilities[0] > probabilities[1] > probabilities[2]


@pytest.mark.parametrize(
    ("logits", "error"),
    [
        ("bad", TypeError),
        ((0.0,), ValueError),
        ((0.0, True), TypeError),
        ((0.0, float("nan")), ValueError),
    ],
)
def test_softmax_rejects_invalid_inputs(logits: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        softmax(logits=logits)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("draw", "expected"),
    [(0.0, 0), (0.199999, 0), (0.2, 1), (0.699999, 1), (0.7, 2), (0.999999, 2)],
)
def test_sampling_uses_visible_cumulative_intervals(draw: float, expected: int) -> None:
    assert sample_from_probabilities(probabilities=(0.2, 0.5, 0.3), draw=draw) == expected


@pytest.mark.parametrize(
    ("probabilities", "draw", "error"),
    [
        ("bad", 0.1, TypeError),
        ((1.0,), 0.1, ValueError),
        ((0.5, True), 0.1, TypeError),
        ((0.5, -0.5), 0.1, ValueError),
        ((0.4, 0.4), 0.1, ValueError),
        ((0.5, 0.5), True, TypeError),
        ((0.5, 0.5), -0.1, ValueError),
        ((0.5, 0.5), 1.0, ValueError),
    ],
)
def test_sampling_rejects_invalid_inputs(
    probabilities: object, draw: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        sample_from_probabilities(probabilities=cast(Any, probabilities), draw=cast(Any, draw))


@pytest.mark.parametrize("delta", [True, float("inf")])
def test_odds_multiplier_rejects_invalid_delta(delta: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        odds_multiplier(delta=delta)  # type: ignore[arg-type]
