from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LESSON = ROOT / ".agent/diagrams/text-watermarking-stage-5-lesson.html"


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


def test_lesson_preserves_stage_continuity_and_profile_boundary() -> None:
    lesson = LESSON.read_text()
    for required in (
        "Measure the signal",
        "Define a green hit",
        "Generate by hand",
        "Check the library",
        "Measure the runtime",
        "Early one morning Jack went up the hill. At the top he",
        "Carry the recipe, not the token IDs",
        "GPT-2 on local CPU",
        "Gemma 4 E2B BF16 on L4",
    ):
        assert required in lesson
    for filename in (
        "text-watermarking-stage-1-walkthrough.html",
        "text-watermarking-stage-2-lesson.html",
        "text-watermarking-stage-3-lesson.html",
        "text-watermarking-stage-4-lesson.html",
    ):
        assert f'href="{filename}"' in lesson


def test_lesson_values_match_selected_evidence() -> None:
    lesson = LESSON.read_text()
    for required in (
        "36.739 s",
        "5.782 s",
        "9.682 GiB",
        "56.1%",
        "18.422 tok/s",
        "7.165 ms",
        "G = 11 / T = 26",
        "z = 2.0381",
        "7/20",
        "1.0328",
        "9/22",
        "1.7233",
        "9,600 / 18.422 = 521.1 seconds",
        "$0.1157",
        "19,200 / 18.422 = 1,042.2 seconds",
        "$0.2314",
    ):
        assert required in lesson


def test_lesson_teaches_one_variable_comparison_and_projection_boundary() -> None:
    lesson = LESSON.read_text()
    for required in (
        "Only the watermark processor changed",
        "Stop token alignment after sampled histories diverge",
        "The first control includes one-time CUDA warm-up behavior",
        "Use the slower watermarked rate",
        "Excluded:",
        "This is not a Modal invoice",
        "Stage 6 has not started",
        "Detector separation was not a pass condition",
    ):
        assert required.lower() in lesson.lower()


def test_lesson_is_self_contained_accessible_and_has_static_fallback() -> None:
    lesson = LESSON.read_text()
    parser = Structure()
    parser.feed(lesson)
    assert parser.scripts == 1
    assert parser.external_scripts == 0
    assert parser.details == parser.summaries == 2
    for required in (
        'id="showKept"',
        'id="showChanged"',
        'id="nextPhase"',
        'id="resetPhase"',
        'id="predictSlower"',
        'id="predictSame"',
        'id="revealPair"',
        'id="project200"',
        'id="project400"',
        'class="static-fallback"',
        "prefers-reduced-motion",
        "@media(max-width:760px)",
    ):
        assert required in lesson
    for forbidden in ("fetch(", "localStorage", 'type="module"', "http://"):
        assert forbidden not in lesson


def test_visible_copy_keeps_claims_narrow_and_plain() -> None:
    lesson = LESSON.read_text()
    for required in (
        "consistent with this configured watermark and key",
        "would not establish AI origin, authorship",
        "does not prove human origin or absence of a watermark",
        "do not estimate detection accuracy or writing quality",
        "No false-alarm rate",
        "private Claude implementation",
    ):
        assert required.lower() in lesson.lower()
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
