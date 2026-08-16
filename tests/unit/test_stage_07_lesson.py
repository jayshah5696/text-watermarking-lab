import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-7-lesson.html"
ARTIFACT = ROOT / "artifacts/lab-07/results.json"


class Structure(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts = 0
        self.external_scripts = 0
        self.details = 0
        self.summaries = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script":
            self.scripts += 1
            self.external_scripts += int("src" in attributes)
        elif tag == "details":
            self.details += 1
        elif tag == "summary":
            self.summaries += 1


def test_lesson_continues_stage_06_with_fixed_row_and_one_causal_change() -> None:
    lesson = LESSON.read_text()
    for required in (
        "The 24 prompts were already in the drawer",
        "1000 <small>manifest rank</small>",
        "Exact source token IDs 0 through 49",
        "Fork one prompt into two generation calls",
        "watermarking_config",
        "The paths share an input, then keep their own history",
        "Control, achieved 198 copied tokens",
        "Marked, achieved 392 copied tokens",
    ):
        assert required in lesson


def test_lesson_teaches_one_score_before_four_controls() -> None:
    lesson = LESSON.read_text()
    for required in (
        "Concrete numbers before notation",
        "39.75",
        "58",
        "159",
        "5.4601",
        "3.3424",
        "No single control can do all three jobs",
        "Marked / right key",
        "Model control / right key",
        "Natural web / right key",
        "Marked / another key",
        "-1.9688",
    ):
        assert required in lesson


def test_lesson_keeps_every_prefix_denominator_and_inconvenient_row() -> None:
    lesson = LESSON.read_text()
    selected = json.loads(ARTIFACT.read_text())
    assert selected["teaching_selection"] == {
        "spine_selection_rank": 1000,
        "inconvenient_selection_rank": 1001,
        "inconvenient_reason": "watermarked_not_above_control",
        "inconvenient_prefix": 80,
    }
    for prefix, expected in ((40, 24), (80, 24), (160, 21), (200, 17), (400, 0)):
        assert selected["prefix_summary"][str(prefix)]["complete_rows"] == expected
        assert f"<td>{prefix}</td><td>{expected}</td>" in lesson
    for required in (
        "26/79, z 1.6239",
        "The missing 400 row is a result",
        "No pair reached 400 copied tokens",
        "Every dot remains visible",
    ):
        assert required in lesson


def test_every_displayed_summary_measurement_matches_selected_artifact() -> None:
    lesson = LESSON.read_text()
    selected = json.loads(ARTIFACT.read_text())
    for prefix in (40, 80, 160, 200):
        summary = selected["prefix_summary"][str(prefix)]
        for comparison in summary["comparisons"].values():
            for value in (
                comparison["mean_difference"],
                comparison["interval_low"],
                comparison["interval_high"],
            ):
                assert repr(value) in lesson
    assert f"{selected['runtime_ns'] / 1e9:.1f}" in lesson
    assert f"{selected['runtime_ns'] / 1e9 * 0.000222:.4f}" in lesson
    assert f"{selected['generated_token_id_count']:,}" in lesson


def test_lesson_is_self_contained_accessible_and_has_static_fallback() -> None:
    lesson = LESSON.read_text()
    parser = Structure()
    parser.feed(lesson)
    assert parser.scripts == 1
    assert parser.external_scripts == 0
    assert parser.details == parser.summaries == 2
    for required in (
        'aria-live="polite"',
        'role="img"',
        "prefers-reduced-motion",
        "@media(max-width:800px)",
        "Scripts-off fallback",
        "Previous token",
        "Replay",
    ):
        assert required in lesson
    for forbidden in ("fetch(", "localStorage", 'type="module"', "http://"):
        assert forbidden not in lesson


def test_claims_remain_narrow_and_prose_avoids_forbidden_marks() -> None:
    lesson = LESSON.read_text().lower()
    for required in (
        "consistent with this configured watermark and key",
        "does not establish generic ai detection, human authorship, production error rates",
        "stage 8 has not started",
        "it is not the provider's total bill",
    ):
        assert required in lesson
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
