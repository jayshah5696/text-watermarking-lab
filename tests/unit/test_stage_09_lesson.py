import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-9-final-lesson.html"
ARTIFACTS = {
    "lab01": ROOT / "artifacts/lab-01/summary.json",
    "lab03": ROOT / "artifacts/lab-03/trace.json",
    "lab06": ROOT / "artifacts/lab-06/calibration.json",
    "lab07": ROOT / "artifacts/lab-07/results.json",
    "lab08": ROOT / "artifacts/lab-08/results.json",
}


class Structure(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts = 0
        self.external_scripts = 0
        self.details = 0
        self.summaries = 0
        self.evidence_text = ""
        self._inside_evidence = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script":
            self.scripts += 1
            self.external_scripts += int("src" in attributes)
            self._inside_evidence = attributes.get("id") == "evidence"
        elif tag == "details":
            self.details += 1
        elif tag == "summary":
            self.summaries += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._inside_evidence = False

    def handle_data(self, data: str) -> None:
        if self._inside_evidence:
            self.evidence_text += data


def load(name: str) -> dict[str, Any]:
    return json.loads(ARTIFACTS[name].read_text())


def evidence() -> dict[str, Any]:
    parser = Structure()
    parser.feed(LESSON.read_text())
    return json.loads(parser.evidence_text)


def test_lesson_continues_exact_stage08_spine_before_rewinding() -> None:
    lesson = LESSON.read_text()
    for required in (
        "Continue from Stage 8",
        "The same rank 1000 string is still the object",
        "28/79",
        "z 2.1436",
        "25/79",
        "z 1.3641",
        "26/79",
        "z 1.6239",
        "Stage 9 selects no replacement row and runs no model",
    ):
        assert required in lesson
    assert lesson.index("Continue from Stage 8") < lesson.index("Rewind to Stage 3")


def test_lesson_teaches_candidate_change_before_generation_loop() -> None:
    lesson = LESSON.read_text()
    lab03 = load("lab03")
    control = next(
        row
        for row in lab03["records"]
        if row["prompt_id"] == "stage-02-continuity" and row["condition"] == "control"
    )
    marked = next(
        row
        for row in lab03["records"]
        if row["prompt_id"] == "stage-02-continuity" and row["condition"] == "score_increase"
    )
    for step in (control["steps"][0], marked["steps"][0]):
        assert step["selected_token_text"] == "Jack"
        assert f"{step['selected_probability'] * 100:.4f}" in lesson
    assert "The saved draw selects Jack in both paths" in lesson
    assert lesson.index("Change the chances before one token is drawn") < lesson.index(
        "Replay the generation key"
    )


def test_embedded_stage07_evidence_matches_every_prefix_summary() -> None:
    lab07 = load("lab07")
    embedded = evidence()
    assert embedded["lab07_source_commit"] == lab07["source_commit"]
    assert embedded["spine_rank"] == 1000
    assert (
        embedded["spine_80"]
        == lab07["selected_rows"][0]["prefix_scores"]["80"]["watermarked_correct"]
    )
    assert embedded["spine_160"] == lab07["selected_rows"][0]["prefix_scores"]["160"]
    assert embedded["prefix_summary"] == lab07["prefix_summary"]


def test_embedded_stage08_evidence_matches_all_summaries() -> None:
    lab08 = load("lab08")
    embedded = evidence()
    assert embedded["lab08_source_commit"] == lab08["source_commit"]
    assert embedded["attack_summary"] == lab08["attack_summary"]
    assert embedded["bias_summary"] == lab08["bias_summary"]


def test_all_stage1_rows_and_external_claim_boundaries_are_present() -> None:
    lesson = LESSON.read_text()
    lab01 = load("lab01")
    for row in lab01["rows"]:
        assert f'"length":{row["length"]}' in lesson
        assert f'"condition":"{row["condition"]}"' in lesson
        assert f'"rate":{row["detection_rate"]}' in lesson
    for required in (
        "It does not classify arbitrary prose as AI or human",
        "consistent with this configured watermark and key",
        "This repository did not implement it",
        "The page does not disclose an algorithm that this project could reproduce",
        "C4 is natural web, not verified human writing",
        "model-based proxies, not human quality judgments",
    ):
        assert required in lesson


def test_natural_web_summary_matches_artifact() -> None:
    lesson = LESSON.read_text()
    summary = load("lab06")["summary"]
    assert f"{summary['positive_all_pair_rows']}/1000" in lesson
    assert f"{summary['all_pair_z_quantiles']['median']:.4f}" in lesson
    assert f"{summary['all_pair_z_quantiles']['q99']:.4f}" in lesson
    assert f"{summary['maximum_all_pair_z']:.4f}" in lesson


def test_lesson_is_standalone_accessible_and_has_static_fallback() -> None:
    lesson = LESSON.read_text()
    parser = Structure()
    parser.feed(lesson)
    assert parser.scripts == 2
    assert parser.external_scripts == 0
    assert parser.details == parser.summaries == 3
    assert LESSON.stat().st_size < 512 * 1024
    for required in (
        'aria-live="polite"',
        'role="img"',
        "prefers-reduced-motion",
        "Scripts-off fallback",
        "Previous token",
        "Replay",
        "@media(max-width:820px)",
    ):
        assert required in lesson
    for forbidden in ("fetch(", "localStorage", 'type="module"', "http://"):
        assert forbidden not in lesson


def test_visible_prose_avoids_forbidden_marks_and_dashboard_copy() -> None:
    lesson = LESSON.read_text()
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
