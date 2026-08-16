import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-8-lesson.html"
ARTIFACT = ROOT / "artifacts/lab-08/results.json"


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


def test_lesson_continues_exact_stage07_spine_before_editing() -> None:
    lesson = LESSON.read_text()
    for required in (
        "The same recorded output returns",
        "1000 <small>manifest rank</small>",
        "28/79 <small>green checks</small>",
        "z 2.1436 with the generation key",
        "Delete the fixed 10 percent of words",
        "The first token-ID mismatch is position",
    ):
        assert required in lesson


def test_lesson_traces_string_token_history_and_checker_in_order() -> None:
    lesson = LESSON.read_text()
    assert lesson.index("One visible operation") < lesson.index("Old and edited token lanes")
    assert lesson.index("Old and edited token lanes") < lesson.index("Replay the key")
    for required in (
        "Edited hits",
        "25",
        "among 79 checks",
        "1.3641",
        "Meaning not certified",
        "not called a meaning-preserving removal",
    ):
        assert required in lesson


def test_every_attack_and_bias_summary_matches_selected_artifact() -> None:
    lesson = LESSON.read_text()
    artifact = json.loads(ARTIFACT.read_text())
    for summary in artifact["attack_summary"].values():
        for key in ("mean_z_change", "mean_length_ratio"):
            assert f"{summary[key]:.4f}" in lesson
    for summary in artifact["bias_summary"].values():
        for key in ("mean_z", "mean_nll", "mean_repeated_pair_fraction"):
            assert f"{summary[key]:.4f}" in lesson
        assert f"{summary['mean_copied_tokens']:.1f}" in lesson


def test_lesson_keeps_preservation_and_proxy_boundaries_visible() -> None:
    lesson = LESSON.read_text().lower()
    for required in (
        "this is not semantic paraphrasing",
        "the review was not independent",
        "model-based proxy, not a human quality score",
        "consistent with this configured watermark and key",
        "does not establish adaptive security, universal edit robustness",
        "a first invocation failed after model load",
    ):
        assert required in lesson


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


def test_visible_prose_avoids_forbidden_marks_and_dashboard_copy() -> None:
    lesson = LESSON.read_text()
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
