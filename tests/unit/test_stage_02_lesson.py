import hashlib
from html.parser import HTMLParser
from pathlib import Path

import pytest

from watermark_lab.toy_greenlist import (
    apply_green_logit_bias,
    sample_from_probabilities,
    softmax,
    toy_green_token_ids,
)

REPOSITORY_ROOT = Path(__file__).parents[2]
LESSON_PATH = REPOSITORY_ROOT / ".agent/diagrams/text-watermarking-stage-2-lesson.html"

VOCABULARY = (
    "Early",
    "one",
    "morning",
    "Jack",
    "went",
    "up",
    "the",
    "hill",
    "walked",
    "ran",
    "road",
    "path",
    "stairs",
    "and",
    "saw",
    "snow",
    "down",
    "home",
    ".",
    "trail",
)
KEY = "stage-02-public-demo-key-v1"
CONTEXTS = ((0, 1, 2, 3), (1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 6))
GREEN_SETS = (
    (0, 4, 8, 15, 19),
    (3, 5, 7, 12, 14),
    (1, 4, 12, 15, 19),
    (4, 10, 12, 14, 19),
)
TARGETS = (4, 5, 6, 7)
DRAWS = (0.30, 0.35, 0.13, 0.06)
HIGH_SCORES = (
    {4: 1.7, 8: 1.4, 9: 1.9, 14: 1.2, 13: 0.5, 17: 0.2},
    {5: 1.7, 16: 1.9, 17: 1.5, 13: 0.8, 10: 0.4, 18: 0.1},
    {6: 2.2, 7: 1.3, 10: 1.1, 11: 0.9, 12: 0.7, 19: 0.5, 18: 0.2},
    {7: 2.5, 10: 1.8, 11: 1.6, 12: 1.4, 19: 1.2, 16: 0.4, 18: 0.2},
)


class _LessonStructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.details_count = 0
        self.summary_count = 0
        self.script_count = 0
        self.external_script_count = 0
        self.disabled_controls = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "details":
            self.details_count += 1
        elif tag == "summary":
            self.summary_count += 1
        elif tag == "script":
            self.script_count += 1
            if "src" in attributes:
                self.external_script_count += 1
        if tag in {"button", "input", "select"} and "disabled" in attributes:
            self.disabled_controls += 1


def _logits(position: int) -> tuple[float, ...]:
    return tuple(HIGH_SCORES[position].get(token_id, -2.2) for token_id in range(20))


def test_stage_02_lesson_uses_one_sentence_as_the_main_spine() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")

    assert "Early one morning Jack went up the hill" in lesson
    assert "We wrote the sentence, scores, and random numbers for this lesson" in lesson
    assert "No language model produced them" in lesson
    assert "Repository tests use a separate trace with four positions" in lesson


def test_stage_02_lesson_defines_key_ownership_and_limits_before_use() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")
    key_section = lesson.index('id="key"')
    choice_section = lesson.index('id="moving-window"')

    assert key_section < choice_section
    for required_copy in (
        "The repository author chose this value",
        "The operator stores the key outside the model",
        "The checker uses the key after generation",
        "We show this key so anyone can repeat the lesson",
        "What people normally use",
        "protected key storage",
    ):
        assert required_copy in lesson


def test_sentence_fixture_replays_selector_sampling_and_membership() -> None:
    choices: list[int] = []
    hits: list[bool] = []

    for position, context in enumerate(CONTEXTS):
        green = toy_green_token_ids(
            vocabulary_size=len(VOCABULARY),
            context=context,
            development_key=KEY,
            gamma=0.25,
        )
        assert green == GREEN_SETS[position]
        adjusted = apply_green_logit_bias(
            logits=_logits(position), green_token_ids=green, delta=2.0
        )
        choice = sample_from_probabilities(
            probabilities=softmax(logits=adjusted), draw=DRAWS[position]
        )
        choices.append(choice)
        hits.append(choice in green)

    assert tuple(choices) == TARGETS
    assert tuple(VOCABULARY[token_id] for token_id in choices) == ("went", "up", "the", "hill")
    assert hits == [True, True, False, False]
    next_contexts = tuple(
        (*context[1:], target) for context, target in zip(CONTEXTS, TARGETS, strict=True)
    )
    assert next_contexts == (
        (1, 2, 3, 4),
        (2, 3, 4, 5),
        (3, 4, 5, 6),
        (4, 5, 6, 7),
    )


def test_alternate_demo_key_changes_only_the_selected_set() -> None:
    first_set = toy_green_token_ids(
        vocabulary_size=len(VOCABULARY),
        context=CONTEXTS[0],
        development_key="wrong-public-key",
        gamma=0.25,
    )
    assert first_set == (6, 7, 11, 15, 17)
    wrong_key_hits = sum(
        target
        in toy_green_token_ids(
            vocabulary_size=len(VOCABULARY),
            context=context,
            development_key="wrong-public-key",
            gamma=0.25,
        )
        for context, target in zip(CONTEXTS, TARGETS, strict=True)
    )
    assert wrong_key_hits == 0


def test_key_change_reorders_hashes_without_changing_green_count() -> None:
    def ranked(key: str) -> list[tuple[str, int]]:
        context = "0,1,2,3"
        return sorted(
            (
                hashlib.sha256(f"lab-02|v1|{key}|{context}|{token_id}".encode("ascii")).hexdigest(),
                token_id,
            )
            for token_id in range(20)
        )

    lesson_ranking = ranked(KEY)
    comparison_ranking = ranked("wrong-public-key")
    assert lesson_ranking[0] == (
        "01d63f5375ca94a19b30e3b6f3dc123a5f5f4d0771916c9df608fe9e3aee3817",
        4,
    )
    assert [token_id for _, token_id in lesson_ranking[:5]] == [4, 19, 15, 0, 8]
    assert [token_id for _, token_id in comparison_ranking[:5]] == [17, 11, 15, 6, 7]
    assert len(lesson_ranking[:5]) == len(comparison_ranking[:5]) == 5


def test_first_choice_shows_shared_normalization_and_fixed_draw() -> None:
    raw = _logits(0)
    before = softmax(logits=raw)
    adjusted = apply_green_logit_bias(logits=raw, green_token_ids=GREEN_SETS[0], delta=2.0)
    after = softmax(logits=adjusted)

    assert sample_from_probabilities(probabilities=before, draw=0.30) == 8
    assert sample_from_probabilities(probabilities=after, draw=0.30) == 4
    assert before[4] == pytest.approx(0.228495, abs=1e-6)
    assert after[4] == pytest.approx(0.465112, abs=1e-6)
    assert raw[9] == adjusted[9] == 1.9
    assert before[9] == pytest.approx(0.279084, abs=1e-6)
    assert after[9] == pytest.approx(0.076882, abs=1e-6)


def test_stage_02_lesson_has_one_repeatable_runner_and_static_fallback() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")
    parser = _LessonStructureParser()
    parser.feed(lesson)

    assert parser.details_count == parser.summary_count == 3
    assert parser.script_count == 1
    assert parser.external_script_count == 0
    assert parser.disabled_controls == 0
    for required_markup in (
        'id="nextToken"',
        'id="restartRun"',
        'id="contextTrack"',
        'id="sentenceLive"',
        'class="static-fallback"',
        "Choose next token",
        "Replay from start",
        "Start over",
        "The same four transitions without animation",
        'id="lessonKeyPreset"',
        'id="comparisonKeyPreset"',
        'id="keyUniverse"',
        'id="generationUniverse"',
        'id="checkerKey"',
        'id="checkerText"',
        'id="startChecker"',
        'id="nextCheck"',
        'id="checkerUniverse"',
        "Stage 2 defines a hit for text",
        "The key does not appear in the z score formula",
        "crypto.subtle.digest",
        "lab-02|v1|",
    ):
        assert required_markup in lesson
    for forbidden_runtime in ("fetch(", "import(", "localStorage", 'type="module"'):
        assert forbidden_runtime not in lesson


def test_stage_02_lesson_visible_copy_passes_plain_language_punctuation_gate() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")

    for forbidden in (
        "\u2014",
        "\u2013",
        "\u2192",
        "\u2194",
        "\u201c",
        "\u201d",
        "\u2018",
        "\u2019",
        "quietly",
        "A random number still decides",
        "A separate trace checks",
        "after the page converts",
        "The key selected",
        "The key adds",
        "chance expects",
        "The repository keeps a separate four position trace",
        "Previous words:",
        "Selected words:",
        "Count:",
        "the key chooses the next word",
        "the key changes the probability",
    ):
        assert forbidden not in lesson
