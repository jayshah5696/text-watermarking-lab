import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-6-lesson.html"
ARTIFACT = ROOT / "artifacts/lab-06/calibration.json"


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


def test_lesson_continues_stage_05_story_and_defines_stage_06_question() -> None:
    lesson = LESSON.read_text()
    for required in (
        "What scores does the Stage 5 checker assign",
        "0 <small>of 12 controls</small>",
        "The objects stay. The source changes.",
        "G hits",
        "T checks",
        "z score",
        "1,000 <small>natural-web rows</small>",
        "No model runs here",
    ):
        assert required in lesson


def test_lesson_carries_one_recorded_row_through_the_full_mechanism() -> None:
    lesson = LESSON.read_text()
    for required in (
        "Follow the first accepted row",
        "dataset row</b><span>0",
        "2019-04-19T18:35:24Z",
        "13b538ab00534c60",
        "988",
        "50<br>future prompt",
        "400<br>scored now",
        "81",
        "99.75",
        "8.6494",
        "-2.1678",
        'id="tokenBox"',
        'id="tokenPlay"',
        'id="tokenPause"',
        'id="tokenPrev"',
        'id="tokenNext"',
        'id="tokenReplay"',
    ):
        assert required in lesson


def test_lesson_preserves_full_cohort_and_failure_case() -> None:
    lesson = LESSON.read_text()
    selected = json.loads(ARTIFACT.read_text())
    assert len(selected["scores"]) == 1_000
    assert selected["summary"]["positive_all_pair_rows"] == 4
    assert selected["summary"]["positive_distinct_pair_rows"] == 1
    assert selected["summary"]["maximum_all_pair_z"] == 3.7285728689537163
    for required in (
        'data-count="12"',
        'data-count="100"',
        'data-count="1000"',
        "Four crossed strict z greater than 3",
        "132 / 399",
        "3.7286",
        "114 / 358",
        "2.9904",
        "The inconvenient row stays",
        "empirical false alarm",
        "Count every pair",
        "Count distinct value-pairs",
    ):
        assert required in lesson


def test_lesson_matches_every_displayed_summary_measurement() -> None:
    lesson = LESSON.read_text()
    selected = json.loads(ARTIFACT.read_text())
    summary = selected["summary"]
    for value in (
        f"{summary['all_pair_z_quantiles']['median']:.4f}",
        f"{summary['all_pair_z_quantiles']['q95']:.4f}",
        f"{summary['all_pair_z_quantiles']['q99']:.4f}",
        f"{summary['maximum_all_pair_z']:.4f}",
        str(summary["source_rows_scanned"]),
        str(summary["rejection_counts"]["too_short"]),
        str(summary["rejection_counts"]["obvious_list"]),
    ):
        assert value in lesson
    for score in selected["scores"]:
        assert repr(score["all_pairs"]["z_score"]) in lesson
        assert repr(score["distinct_pairs"]["z_score"]) in lesson


def test_lesson_is_self_contained_accessible_and_has_static_fallback() -> None:
    lesson = LESSON.read_text()
    parser = Structure()
    parser.feed(lesson)
    assert parser.scripts == 1
    assert parser.external_scripts == 0
    assert parser.details == parser.summaries == 3
    for required in (
        'role="img"',
        'aria-labelledby="scoreTitle scoreDesc"',
        'aria-live="polite"',
        "prefers-reduced-motion",
        "@media(max-width:800px)",
        "<noscript><style>.static{display:block}</style></noscript>",
        "Scripts-off summary",
    ):
        assert required in lesson
    for forbidden in ("fetch(", "localStorage", 'type="module"', "http://"):
        assert forbidden not in lesson


def test_claims_remain_narrow_and_prose_avoids_forbidden_marks() -> None:
    lesson = LESSON.read_text().lower()
    for required in (
        "natural-web text. we do not know that every row was written only by a human",
        "does not establish verified human authorship, a production false-alarm rate",
        "consistent with this configured watermark and key",
        "does not prove ai origin, authorship, or model source",
        "stage 7 generation has not started",
        "a one-in-100,000 claim would need evidence at a much larger scale",
    ):
        assert required in lesson
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
