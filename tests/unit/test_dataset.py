from collections.abc import Sequence
from pathlib import Path

import pytest

from watermark_lab.dataset import (
    Candidate,
    letter_fraction,
    rejection_reason,
    select_rows,
    selection_manifest,
    text_sha256,
)
from watermark_lab.lab06_config import lab06_config_from_toml_bytes


class WordsTokenizer:
    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]:
        assert add_special_tokens is False
        return list(range(len(text.split())))

    def decode(
        self, token_ids: Sequence[int], *, clean_up_tokenization_spaces: bool = False
    ) -> str:
        return " ".join(str(token_id) for token_id in token_ids)


@pytest.fixture
def config():
    base = lab06_config_from_toml_bytes(Path("configs/lab_06.toml").read_bytes())
    object.__setattr__(base, "minimum_document_tokens", 5)
    object.__setattr__(base, "prompt_tokens", 1)
    object.__setattr__(base, "continuation_tokens", 3)
    object.__setattr__(base, "calibration_rows", 2)
    object.__setattr__(base, "paired_test_rows", 1)
    return base


def candidate(text: str, tokens: int = 10) -> Candidate:
    return Candidate(
        0,
        "https://example.test",
        "2020-01-01T00:00:00Z",
        text,
        tuple(range(tokens)),
        text_sha256(text),
    )


def test_rejection_reason_order_and_literal_filters(config) -> None:
    assert rejection_reason(candidate("short", 4), seen_hashes=set(), config=config) == "too_short"
    duplicate = candidate("ordinary letters here")
    assert (
        rejection_reason(duplicate, seen_hashes={duplicate.text_sha256}, config=config)
        == "duplicate_text"
    )
    listed = candidate("\n".join(f"- item {index}" for index in range(8)))
    assert rejection_reason(listed, seen_hashes=set(), config=config) == "obvious_list"
    coded = candidate("\n".join(["def x():"] * 5 + ["plain sentence"] * 5))
    assert rejection_reason(coded, seen_hashes=set(), config=config) == "code_dump"
    symbols = candidate("1234 !!! ????")
    assert rejection_reason(symbols, seen_hashes=set(), config=config) == "low_letter_fraction"
    assert letter_fraction("abc 123") == pytest.approx(0.5)


def test_selection_fills_disjoint_splits_in_file_order(config) -> None:
    rows = [
        {"text": "too short", "timestamp": "t0", "url": "u0"},
        {"text": "one two three four five six", "timestamp": "t1", "url": "u1"},
        {"text": "seven eight nine ten eleven twelve", "timestamp": "t2", "url": "u2"},
        {
            "text": "thirteen fourteen fifteen sixteen seventeen eighteen",
            "timestamp": "t3",
            "url": "u3",
        },
        {"text": "unused row has enough ordinary words", "timestamp": "t4", "url": "u4"},
    ]
    selected, counts, last_index = select_rows(rows, WordsTokenizer(), config)
    assert [item.candidate.row_index for item in selected] == [1, 2, 3]
    assert [item.split for item in selected] == ["calibration", "calibration", "paired_test"]
    assert counts["too_short"] == 1
    assert last_index == 3
    manifests = [selection_manifest(item, config) for item in selected]
    assert manifests[0]["prompt_token_range"] == [0, 1]
    assert manifests[0]["continuation_token_range"] == [1, 4]
    assert "text" not in manifests[0]
    assert len({item["text_sha256"] for item in manifests}) == 3


def test_selection_rejects_schema_drift_and_short_stream(config) -> None:
    with pytest.raises(ValueError, match="fields differ"):
        select_rows(({"text": "one two three four five", "url": "u"},), WordsTokenizer(), config)
    with pytest.raises(ValueError, match="ended before"):
        select_rows((), WordsTokenizer(), config)
