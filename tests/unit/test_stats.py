from __future__ import annotations

import random

import pytest
from scipy.stats import binom

from watermark_lab.stats import (
    derive_group_seed,
    exact_binomial_upper_tail,
    expected_hits,
    green_hit_z_score,
    simulate_hit_counts,
)


def test_fixed_all_hit_vector() -> None:
    assert expected_hits(trials=4, null_probability=0.25) == 1.0
    assert green_hit_z_score(hits=4, trials=4, null_probability=0.25) == pytest.approx(
        3.464101615137755, abs=1e-15
    )
    assert exact_binomial_upper_tail(hits=4, trials=4, null_probability=0.25) == 0.00390625


def test_fixed_zero_hit_vector() -> None:
    assert green_hit_z_score(hits=0, trials=4, null_probability=0.25) == pytest.approx(
        -1.1547005383792517, abs=1e-15
    )
    assert exact_binomial_upper_tail(hits=0, trials=4, null_probability=0.25) == 1.0


@pytest.mark.parametrize("trials", [1, 4, 40, 400])
@pytest.mark.parametrize("probability", [0.1, 0.25, 0.5])
def test_exact_upper_tail_matches_scipy(trials: int, probability: float) -> None:
    for hits in sorted({0, trials // 3, trials // 2, trials}):
        actual = exact_binomial_upper_tail(hits=hits, trials=trials, null_probability=probability)
        oracle = float(binom.sf(hits - 1, trials, probability))
        assert actual == pytest.approx(oracle, abs=1e-12)


@pytest.mark.parametrize(
    ("function", "kwargs"),
    [
        (expected_hits, {"trials": 0, "null_probability": 0.25}),
        (green_hit_z_score, {"hits": -1, "trials": 4, "null_probability": 0.25}),
        (green_hit_z_score, {"hits": 5, "trials": 4, "null_probability": 0.25}),
        (exact_binomial_upper_tail, {"hits": 1, "trials": 4, "null_probability": 0.0}),
        (exact_binomial_upper_tail, {"hits": 5, "trials": 4, "null_probability": 0.25}),
        (simulate_hit_counts, {"trials": 4, "hit_probability": 1.0, "replicates": 2, "seed": 1}),
        (simulate_hit_counts, {"trials": 4, "hit_probability": 0.5, "replicates": 0, "seed": 1}),
    ],
)
def test_domain_errors_raise_value_error(function: object, kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        function(**kwargs)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("function", "kwargs"),
    [
        (expected_hits, {"trials": True, "null_probability": 0.25}),
        (green_hit_z_score, {"hits": False, "trials": 4, "null_probability": 0.25}),
        (exact_binomial_upper_tail, {"hits": 1, "trials": 4.0, "null_probability": 0.25}),
        (simulate_hit_counts, {"trials": 4, "hit_probability": True, "replicates": 2, "seed": 1}),
        (simulate_hit_counts, {"trials": 4, "hit_probability": 0.5, "replicates": True, "seed": 1}),
        (derive_group_seed, {"base_seed": 1, "condition": 3, "trials": 4}),
    ],
)
def test_type_errors_are_not_silently_coerced(function: object, kwargs: dict[str, object]) -> None:
    with pytest.raises(TypeError):
        function(**kwargs)  # type: ignore[operator]


def test_group_seed_is_stable_and_group_specific() -> None:
    first = derive_group_seed(base_seed=20260811, condition="null", trials=40)
    assert first == derive_group_seed(base_seed=20260811, condition="null", trials=40)
    assert first != derive_group_seed(base_seed=20260811, condition="biased", trials=40)
    assert first != derive_group_seed(base_seed=20260811, condition="null", trials=80)


@pytest.mark.parametrize("condition", ["", "naïve"])
def test_group_seed_rejects_invalid_condition(condition: str) -> None:
    with pytest.raises(ValueError):
        derive_group_seed(base_seed=1, condition=condition, trials=4)


def test_simulation_is_deterministic_and_preserves_global_random_state() -> None:
    random.seed(9876)
    before = random.getstate()
    first = simulate_hit_counts(trials=12, hit_probability=0.25, replicates=8, seed=42)
    after = random.getstate()
    second = simulate_hit_counts(trials=12, hit_probability=0.25, replicates=8, seed=42)
    assert before == after
    assert first == second
