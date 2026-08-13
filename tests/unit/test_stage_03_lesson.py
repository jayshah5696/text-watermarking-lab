from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-3-lesson.html"
TRACE = ROOT / "artifacts/lab-03/trace.json"


class _Structure(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.details = 0
        self.summaries = 0
        self.scripts = 0
        self.external_scripts = 0
        self.disabled_controls = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "details":
            self.details += 1
        elif tag == "summary":
            self.summaries += 1
        elif tag == "script":
            self.scripts += 1
            self.external_scripts += int("src" in attributes)
        if tag in {"button", "input", "select"}:
            self.disabled_controls += int("disabled" in attributes)


def _trace() -> dict[str, object]:
    return json.loads(TRACE.read_text(encoding="utf-8"))


def test_lesson_uses_stage_2_continuity_and_complete_model_input() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    record = next(
        item
        for item in trace["records"]  # type: ignore[union-attr]
        if item["prompt_id"] == "stage-02-continuity" and item["condition"] == "score_increase"
    )
    assert record["prompt_text"] in lesson
    assert trace["config"]["instruction_prefix"].strip() in lesson  # type: ignore[index]
    assert "36 model-input tokens" in lesson
    assert "chat control tokens" in lesson
    assert "An earlier diagnostic omitted this documented chat framing" in lesson


def test_lesson_measured_values_match_selected_trace() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    for record in trace["records"]:  # type: ignore[union-attr]
        generation = record["generation_key_score"]
        comparison = record["comparison_key_score"]
        assert f"{generation['green_hits']}/{generation['eligible_tokens']}" in lesson
        assert f"{generation['z_score']:.4f}" in lesson
        assert f"{comparison['green_hits']}/{comparison['eligible_tokens']}" in lesson
        assert f"{comparison['z_score']:.4f}" in lesson
    assert str(trace["source_commit"]) in lesson
    assert str(trace["config_sha256"]) in lesson


def test_lesson_first_token_values_match_trace() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    spine = next(
        item
        for item in trace["records"]  # type: ignore[union-attr]
        if item["prompt_id"] == "stage-02-continuity" and item["condition"] == "score_increase"
    )
    step = spine["steps"][0]
    assert step["selected_token_text"] == "Jack"
    assert str(step["selected_token_id"]) in lesson
    assert f"{step['selected_raw_score']:.4f}" in lesson
    assert f"{step['selected_score_after_increase']:.4f}" in lesson
    assert f"{100 * step['selected_probability']:.4f}%" in lesson


def test_lesson_has_guided_controls_static_fallback_and_no_remote_runtime() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    parser = _Structure()
    parser.feed(lesson)
    assert parser.details == parser.summaries == 2
    assert parser.scripts == 2
    assert parser.external_scripts == 0
    assert parser.disabled_controls == 0
    for expected in (
        'id="revealTokens"',
        'id="nextLoop"',
        'id="restartLoop"',
        'id="nextCheck"',
        'id="comparisonKey"',
        'id="restartCheck"',
        'class="static-fallback"',
        "The complete lesson without animation",
        "Green tokens counted (G)",
        "Stage 3 has no tested cutoff",
    ):
        assert expected in lesson
    for forbidden in ("fetch(", "import(", "localStorage", 'type="module"'):
        assert forbidden not in lesson


def test_visible_copy_passes_plain_language_and_claim_boundary_gate() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    for forbidden in (
        "\u2014",
        "\u2013",
        "\u2192",
        "\u2194",
        "\u201c",
        "\u201d",
        "wrong key",
        "correct key",
        "positive result",
        "AI detection",
        "membership oracle",
        "intervention",
    ):
        assert forbidden not in lesson
    for required in (
        "same key used during generation",
        "comparison key",
        "No row proves AI origin or authorship",
        "Being green does not force a token",
        "A token can receive the score increase and still be removed",
    ):
        assert required in lesson
