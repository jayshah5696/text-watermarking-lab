"""Deterministic text edits for the Stage 8 teaching experiment."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass

HOMOGLYPHS = {
    "a": "\u0430",
    "c": "\u0441",
    "e": "\u0435",
    "i": "\u0456",
    "o": "\u043e",
    "p": "\u0440",
    "x": "\u0445",
    "y": "\u0443",
    "A": "\u0410",
    "B": "\u0412",
    "C": "\u0421",
    "E": "\u0415",
    "H": "\u041d",
    "K": "\u041a",
    "M": "\u041c",
    "O": "\u041e",
    "P": "\u0420",
    "T": "\u0422",
    "X": "\u0425",
}
_WORD = re.compile(r"\S+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class EditOperation:
    """One auditable change to a character or word position."""

    index: int
    source: str
    replacement: str

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("edit index must be non-negative")
        if not self.source:
            raise ValueError("edit source must not be empty")


@dataclass(frozen=True, slots=True)
class EditedText:
    """A deterministic edited string and its exact operations."""

    text: str
    operations: tuple[EditOperation, ...]

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("edited text must not be empty")


def _chosen_indices(count: int, changed: int, seed: int) -> tuple[int, ...]:
    if count < 0 or changed < 0 or changed > count:
        raise ValueError("invalid deterministic edit count")
    seed_bytes = seed.to_bytes(8, "big")
    ranked = sorted(
        range(count),
        key=lambda index: hashlib.sha256(seed_bytes + index.to_bytes(8, "big")).digest(),
    )
    return tuple(sorted(ranked[:changed]))


def normalize_text(value: str) -> EditedText:
    """Apply the complete frozen Stage 8 normalization recipe."""

    if not value:
        raise ValueError("text must not be empty")
    normalized = unicodedata.normalize("NFKC", value)
    table = str.maketrans(
        {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u00a0": " ",
        }
    )
    normalized = " ".join(normalized.translate(table).split())
    operation = EditOperation(index=0, source=value, replacement=normalized)
    return EditedText(text=normalized, operations=(operation,))


def substitute_homoglyphs(value: str, *, rate: float, seed: int) -> EditedText:
    """Replace a fixed fraction of eligible ASCII letters with declared Cyrillic lookalikes."""

    if not value:
        raise ValueError("text must not be empty")
    if not 0.0 < rate < 1.0:
        raise ValueError("homoglyph rate must be between zero and one")
    eligible = [index for index, character in enumerate(value) if character in HOMOGLYPHS]
    changed = min(len(eligible), max(1, round(rate * len(eligible)))) if eligible else 0
    selected = _chosen_indices(len(eligible), changed, seed)
    characters = list(value)
    operations: list[EditOperation] = []
    for selected_index in selected:
        index = eligible[selected_index]
        source = characters[index]
        replacement = HOMOGLYPHS[source]
        characters[index] = replacement
        operations.append(EditOperation(index=index, source=source, replacement=replacement))
    return EditedText(text="".join(characters), operations=tuple(operations))


def delete_words(value: str, *, rate: float, seed: int) -> EditedText:
    """Delete a fixed fraction of Unicode non-whitespace runs."""

    if not value:
        raise ValueError("text must not be empty")
    if not 0.0 < rate < 1.0:
        raise ValueError("deletion rate must be between zero and one")
    words = _WORD.findall(value)
    changed = min(len(words) - 1, max(1, round(rate * len(words))))
    selected = set(_chosen_indices(len(words), changed, seed))
    operations = tuple(
        EditOperation(index=index, source=word, replacement="")
        for index, word in enumerate(words)
        if index in selected
    )
    retained = [word for index, word in enumerate(words) if index not in selected]
    return EditedText(text=" ".join(retained), operations=operations)


def mix_with_control(marked: str, control: str, *, rate: float, seed: int) -> EditedText:
    """Replace aligned marked words with paired-control words at fixed positions."""

    if not marked or not control:
        raise ValueError("marked and control text must not be empty")
    if not 0.0 < rate < 1.0:
        raise ValueError("mixing rate must be between zero and one")
    marked_words = _WORD.findall(marked)
    control_words = _WORD.findall(control)
    aligned = min(len(marked_words), len(control_words))
    changed = min(aligned, max(1, round(rate * aligned))) if aligned else 0
    selected = _chosen_indices(aligned, changed, seed)
    output = list(marked_words)
    operations: list[EditOperation] = []
    for index in selected:
        source = output[index]
        replacement = control_words[index]
        output[index] = replacement
        operations.append(EditOperation(index=index, source=source, replacement=replacement))
    return EditedText(text=" ".join(output), operations=tuple(operations))
