from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-4-lesson.html"
TRACE = ROOT / "artifacts/lab-04/trace.json"


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


def _trace() -> dict[str, Any]:
    return json.loads(TRACE.read_text(encoding="utf-8"))


def test_lesson_carries_the_first_two_reference_tokens_into_checking() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    record = next(
        item
        for item in trace["records"]  # type: ignore[union-attr]
        if item["prompt_id"] == "stage-02-continuity" and item["condition"] == "reference_watermark"
    )
    assert trace["config"]["prompts"][0]["text"] in lesson  # type: ignore[index]
    assert record["generated_token_ids"][:2] == [373, 21272]
    assert "ID 373 / context only" in lesson
    assert "ID 21272 / first eligible / green" in lesson
    assert "Token 1 now becomes checker context" in lesson
    assert "Token 2 is the first counted decision" in lesson


def test_lesson_order_values_match_selected_trace() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    probe = trace["order_probe"]  # type: ignore[index]
    assert probe["reference_counts"] == [50257, 40, 19, 19]
    assert probe["stage_03_counts"] == [50257, 50257, 11, 11]
    assert f"{100 * probe['reference_selected_probability']:.6f}%" in lesson
    assert f"{100 * probe['stage_03_selected_probability']:.6f}%" in lesson
    visible_roles = {
        "selected": "recorded choice",
        "green_survivor": "highest other green survivor",
        "red_survivor": "highest red survivor",
        "green_filtered": "highest raw green removed",
        "red_filtered": "highest raw red removed",
    }
    for candidate in probe["candidates"]:
        assert str(candidate["token_id"]) in lesson
        assert str(candidate["token_text"]).strip() in lesson
        assert visible_roles[candidate["witness_role"]] in lesson
    assert "5 displayed of 50,257" in lesson
    assert "Only the Transformers order generated the saved continuation" in lesson


def test_lesson_measured_counts_hashes_and_runtime_match_trace() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    for record in trace["records"]:  # type: ignore[union-attr]
        generation = record["detector_results"][0]
        comparison = record["detector_results"][2]
        assert f"{generation['num_green_tokens']}/{generation['num_tokens_scored']}" in lesson
        assert f"{generation['z_score']:.4f}" in lesson
        assert f"{comparison['num_green_tokens']}/{comparison['num_tokens_scored']}" in lesson
        assert f"{comparison['z_score']:.4f}" in lesson
    assert str(trace["source_commit"]) in lesson
    assert str(trace["config_sha256"]) in lesson
    assert str(trace["transformers_version"]) in lesson
    assert str(trace["torch_version"]) in lesson


def test_lesson_records_repetition_mismatch_and_prompt_exclusion() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    repetition = trace["repetition_fixture"]  # type: ignore[index]
    assert repetition["detector_results"][0]["num_tokens_scored"] == 5
    assert repetition["detector_results"][1]["num_tokens_scored"] == 5
    assert repetition["explicit_distinct_result"]["num_distinct_pairs"] == 2
    for required in (
        "3/5",
        "1/2",
        "1.8074",
        "0.8165",
        "GPT-2 did not generate it",
        "0 prompt tokens",
        "0 padding tokens",
        "The prompt stops at the boundary",
    ):
        assert required in lesson


def test_lesson_has_guided_controls_and_no_remote_runtime() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    parser = _Structure()
    parser.feed(lesson)
    assert parser.details == parser.summaries == 5
    assert parser.scripts == 2
    assert parser.external_scripts == 0
    assert parser.disabled_controls == 2
    for expected in (
        'id="nextOrder"',
        'id="backOrder"',
        'id="replayOrder"',
        'id="earlierOrder"',
        'id="sameChance"',
        'id="differentChance"',
        'id="restoreOrder"',
        'id="revealChoice"',
        'id="runCheck"',
        'id="comparisonKey"',
        'id="generationKey"',
        'id="testRepeats"',
        'class="static-fallback"',
        "The complete story without animation",
        "[hidden] { display: none!important; }",
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
        "AI detection",
        "membership oracle",
        "intervention",
        "design space",
        "First define the watermark",
        "Try this",
        "scientifically useful",
        "meaning-blind",
    ):
        assert forbidden not in lesson
    for required in (
        "model preference numbers",
        "watermark evidence score",
        "Green is only a temporary label",
        "It does not mean safe, correct, or better writing",
        "No row proves AI origin or authorship",
        "insufficient evidence for this exact lab watermark and key",
        "does not prove human origin or absence of a watermark",
        "three passages cannot measure accuracy or a false-alarm rate",
        "does not reproduce Anthropic's private Claude implementation",
    ):
        assert required.lower() in lesson.lower()
