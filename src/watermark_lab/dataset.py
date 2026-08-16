"""Deterministic Stage 6 C4 selection and compact record helpers."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol, cast

from watermark_lab.lab06_config import Lab06Config

RejectionReason = Literal[
    "too_short", "duplicate_text", "obvious_list", "code_dump", "low_letter_fraction"
]
SplitName = Literal["calibration", "paired_test"]

_LIST_PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
_CODE_PREFIX = re.compile(
    r"^\s*(?:```|~~~|(?:def|class|function|import|from|const|let|var)\s+|"
    r"(?:if|for|while)\s*\(|</?[A-Za-z][^>]*>|[{}][;,]?\s*$)"
)


class Tokenizer(Protocol):
    def encode(self, text: str, *, add_special_tokens: bool) -> list[int]: ...

    def decode(
        self, token_ids: Sequence[int], *, clean_up_tokenization_spaces: bool = False
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class Candidate:
    row_index: int
    url: str
    timestamp: str
    text: str
    token_ids: tuple[int, ...]
    text_sha256: str


@dataclass(frozen=True, slots=True)
class Selection:
    split: SplitName
    selection_rank: int
    candidate: Candidate


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def letter_fraction(text: str) -> float:
    visible = [character for character in text if not character.isspace()]
    if not visible:
        return 0.0
    letters = sum(unicodedata.category(character).startswith("L") for character in visible)
    return letters / len(visible)


def _nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def rejection_reason(
    candidate: Candidate, *, seen_hashes: set[str], config: Lab06Config
) -> RejectionReason | None:
    if len(candidate.token_ids) < config.minimum_document_tokens:
        return "too_short"
    if candidate.text_sha256 in seen_hashes:
        return "duplicate_text"
    lines = _nonempty_lines(candidate.text)
    list_lines = sum(bool(_LIST_PREFIX.match(line)) for line in lines)
    if (
        len(lines) >= config.minimum_list_lines
        and list_lines / len(lines) >= config.minimum_list_fraction
    ):
        return "obvious_list"
    code_lines = sum(bool(_CODE_PREFIX.match(line)) for line in lines)
    if (
        code_lines >= config.minimum_code_lines
        and code_lines / len(lines) >= config.minimum_code_fraction
    ):
        return "code_dump"
    if letter_fraction(candidate.text) < config.minimum_letter_fraction:
        return "low_letter_fraction"
    return None


def select_rows(
    rows: Iterable[Mapping[str, Any]], tokenizer: Tokenizer, config: Lab06Config
) -> tuple[tuple[Selection, ...], dict[str, int], int]:
    selected: list[Selection] = []
    seen_hashes: set[str] = set()
    counts = {
        "too_short": 0,
        "duplicate_text": 0,
        "obvious_list": 0,
        "code_dump": 0,
        "low_letter_fraction": 0,
    }
    last_index = -1
    for row_index, row in enumerate(rows):
        last_index = row_index
        if set(row) != {"text", "timestamp", "url"}:
            raise ValueError("C4 row fields differ from text, timestamp, and url")
        text = row["text"]
        url = row["url"]
        timestamp = row["timestamp"]
        if not all(isinstance(value, str) for value in (text, url, timestamp)):
            raise TypeError("C4 text, URL, and timestamp must be strings")
        digest = text_sha256(cast(str, text))
        token_ids = tuple(tokenizer.encode(cast(str, text), add_special_tokens=False))
        candidate = Candidate(
            row_index=row_index,
            url=cast(str, url),
            timestamp=cast(str, timestamp),
            text=cast(str, text),
            token_ids=token_ids,
            text_sha256=digest,
        )
        reason = rejection_reason(candidate, seen_hashes=seen_hashes, config=config)
        seen_hashes.add(digest)
        if reason is not None:
            counts[reason] += 1
            continue
        rank = len(selected)
        split: SplitName = "calibration" if rank < config.calibration_rows else "paired_test"
        selected.append(Selection(split=split, selection_rank=rank, candidate=candidate))
        if len(selected) == config.selected_rows:
            break
    if len(selected) != config.selected_rows:
        raise ValueError("C4 stream ended before both Stage 6 splits were filled")
    return tuple(selected), counts, last_index


def selection_manifest(selection: Selection, config: Lab06Config) -> dict[str, Any]:
    candidate = selection.candidate
    return {
        "dataset_row_index": candidate.row_index,
        "url": candidate.url,
        "timestamp": candidate.timestamp,
        "text_sha256": candidate.text_sha256,
        "full_token_count": len(candidate.token_ids),
        "split": selection.split,
        "selection_rank": selection.selection_rank,
        "prompt_token_range": [0, config.prompt_tokens],
        "continuation_token_range": [
            config.prompt_tokens,
            config.prompt_tokens + config.continuation_tokens,
        ],
    }


def continuation_ids(selection: Selection, config: Lab06Config) -> tuple[int, ...]:
    start = config.prompt_tokens
    return selection.candidate.token_ids[start : start + config.continuation_tokens]


def short_excerpt(token_ids: Sequence[int], tokenizer: Tokenizer, *, limit: int = 180) -> str:
    text = tokenizer.decode(token_ids, clean_up_tokenization_spaces=False).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
