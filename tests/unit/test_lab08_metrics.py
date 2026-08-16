import math

import pytest

from watermark_lab.lab08_metrics import (
    cosine_similarity,
    decimal_numbers,
    distinct_ngram_fraction,
    numbers_preserved,
    repeated_adjacent_pair_fraction,
)


def test_repetition_and_distinct_ngram_metrics_use_token_sequences() -> None:
    ids = (1, 2, 1, 2, 3)
    assert repeated_adjacent_pair_fraction(ids) == 1 / 4
    assert distinct_ngram_fraction(ids, width=2) == 3 / 4
    assert distinct_ngram_fraction(ids, width=3) == 1.0


def test_number_preservation_keeps_surface_forms_and_duplicate_counts() -> None:
    source = "Revenue was 12.5 in 2024, then 12.5 again."
    assert decimal_numbers(source) == ("12.5", "2024", "12.5")
    assert numbers_preserved(source, "In 2024 it stayed at 12.5 and later 12.5.")
    assert not numbers_preserved(source, "In 2024 it stayed at 12.5.")


def test_cosine_similarity_handles_known_vectors() -> None:
    assert cosine_similarity((1.0, 0.0), (1.0, 0.0)) == 1.0
    assert cosine_similarity((1.0, 0.0), (0.0, 1.0)) == 0.0
    assert math.isclose(cosine_similarity((1.0, 1.0), (1.0, 0.0)), 2**-0.5)


def test_metric_validation_rejects_undefined_inputs() -> None:
    for call in (
        lambda: repeated_adjacent_pair_fraction((1,)),
        lambda: distinct_ngram_fraction((1,), width=2),
        lambda: distinct_ngram_fraction((1,), width=0),
        lambda: cosine_similarity((), ()),
        lambda: cosine_similarity((0.0,), (0.0,)),
        lambda: cosine_similarity((math.nan,), (1.0,)),
    ):
        with pytest.raises(ValueError):
            call()
