import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARTICLE_MD = ROOT / "blog/article.md"
ARTICLE_HTML = ROOT / "blog/how-text-watermarks-hide-in-plain-sight.html"
ARTIFACTS = {
    name: ROOT / f"artifacts/{path}"
    for name, path in {
        "lab01": "lab-01/summary.json",
        "lab02": "lab-02/trace.json",
        "lab03": "lab-03/trace.json",
        "lab04": "lab-04/trace.json",
        "lab05": "lab-05/trace.json",
        "lab06": "lab-06/calibration.json",
        "lab07": "lab-07/results.json",
        "lab08": "lab-08/results.json",
    }.items()
}


class ArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts = 0
        self.external_scripts = 0
        self.figures = 0
        self.buttons = 0
        self.tables = 0
        self.table_wraps = 0
        self.evidence = ""
        self._inside_evidence = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script":
            self.scripts += 1
            self.external_scripts += int("src" in attributes)
            self._inside_evidence = attributes.get("id") == "evidence"
        elif tag == "figure":
            self.figures += 1
        elif tag == "button":
            self.buttons += 1
        elif tag == "table":
            self.tables += 1
        elif tag == "div" and "table-wrap" in (attributes.get("class") or "").split():
            self.table_wraps += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._inside_evidence = False

    def handle_data(self, data: str) -> None:
        if self._inside_evidence:
            self.evidence += data


def load(name: str) -> dict[str, Any]:
    return json.loads(ARTIFACTS[name].read_text())


def embedded() -> dict[str, Any]:
    parser = ArticleParser()
    parser.feed(ARTICLE_HTML.read_text())
    return json.loads(parser.evidence)


def test_article_is_one_continuous_story_not_a_stage_report() -> None:
    source = ARTICLE_MD.read_text()
    assert source.startswith("# How does a text watermark work?")
    assert len(re.findall(r"^## ", source, re.MULTILINE)) == 19
    for forbidden in ("## Stage 1", "## Part 1", "Continue from Stage", "final lesson"):
        assert forbidden not in source
    positions = [
        source.index("## Start with two weighted coins"),
        source.index("## Follow one batch all the way through"),
        source.index("## The first experiment, in code"),
        source.index("## Give the coin a key"),
        source.index("## Replace the hand-written scores"),
        source.index("## Score outside text before trusting the cutoff"),
        source.index("## One high score needs three controls"),
        source.index("## Edits rebuild the checker history"),
        source.index("## Claude uses a SynthID-Text variant"),
    ]
    assert positions == sorted(positions)


def test_article_embeds_all_interactive_visuals_and_has_no_external_runtime() -> None:
    parser = ArticleParser()
    parser.feed(ARTICLE_HTML.read_text())
    assert parser.figures == 17
    # Thirty-four controls are present in static HTML; the evidence-backed selectors
    # for lengths, cutoffs, families, contrasts, attacks, deltas, and methods are added by JS.
    assert parser.buttons == 34
    assert parser.scripts == 2
    assert parser.external_scripts == 0
    assert parser.tables == parser.table_wraps == 7
    article = ARTICLE_HTML.read_text()
    for required in (
        "prefers-reduced-motion",
        "Scripts are off",
        "@media print",
        'role="img"',
        "Use light page",
        "Every frozen row appears on its own line",
    ):
        assert required in article
    for forbidden in ("fetch(", "localStorage", 'type="module"', "<iframe"):
        assert forbidden not in article


def test_every_stage_source_commit_is_embedded_exactly() -> None:
    evidence = embedded()
    for name in ARTIFACTS:
        assert evidence["sourceCommits"][name] == load(name)["source_commit"]


def test_stage1_and_stage2_payload_matches_artifacts() -> None:
    evidence = embedded()
    lab01 = load("lab01")
    expected = [
        {
            "length": row["length"],
            "condition": row["condition"],
            "rate": row["detection_rate"],
            "detections": row["detections"],
            "mean_hits": row["mean_hits"],
            "median_z": row["median_z"],
            "q05_z": row["q05_z"],
            "q95_z": row["q95_z"],
        }
        for row in lab01["rows"]
    ]
    assert evidence["stage1"] == expected
    lab02 = load("lab02")
    assert evidence["toy"]["vocabulary"] == lab02["config"]["vocabulary"]
    assert evidence["toy"]["steps"] == lab02["steps"]
    sentence = evidence["toySentence"]
    assert sentence["lesson_key"] == "stage-02-public-demo-key-v1"
    assert sentence["comparison_key"] == "wrong-public-key"
    assert sentence["steps"][0]["ranked"][4]["hash"].startswith("01d63f53")
    assert [step["target_word"] for step in sentence["steps"]] == ["went", "up", "the", "hill"]
    assert [step["hit"] for step in sentence["steps"]] == [True, True, False, False]
    assert sentence["comparison_hits"] == [False, False, False, False]


def test_stage3_stage4_and_stage5_payload_matches_artifacts() -> None:
    evidence = embedded()
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
    assert evidence["candidateControl"] == control["steps"][0]["candidates"]
    assert evidence["candidateMarked"] == marked["steps"][0]["candidates"]
    assert evidence["realStep"]["control_text"] == control["decoded_text"]
    assert evidence["realStep"]["marked_text"] == marked["decoded_text"]
    assert evidence["realStep"]["control_score"] == control["generation_key_score"]
    assert evidence["realStep"]["marked_score"] == marked["generation_key_score"]
    assert evidence["realStep"]["comparison_score"] == marked["comparison_key_score"]
    lab04 = load("lab04")
    assert evidence["order"] == lab04["order_probe"]
    fixture = lab04["repetition_fixture"]
    assert evidence["repetition"]["library_false"] == fixture["detector_results"][0]
    assert evidence["repetition"]["library_true"] == fixture["detector_results"][1]
    assert evidence["repetition"]["explicit_distinct"] == fixture["explicit_distinct_result"]
    assert len(evidence["smoke"]) == len(load("lab05")["records"])


def test_stage6_stage7_and_stage8_payload_matches_every_row() -> None:
    evidence = embedded()
    lab06 = load("lab06")
    assert evidence["naturalScores"] == [row["all_pairs"]["z_score"] for row in lab06["scores"]]
    assert evidence["naturalSummary"] == lab06["summary"]
    lab07 = load("lab07")
    assert evidence["prefixSummary"] == lab07["prefix_summary"]
    assert evidence["selectionRanks"] == [row["selection_rank"] for row in lab07["selected_rows"]]
    lab08 = load("lab08")
    assert evidence["attackSummary"] == lab08["attack_summary"]
    assert evidence["biasSummary"] == lab08["bias_summary"]
    assert [row["rank"] for row in evidence["attacks"]] == [
        row["selection_rank"] for row in lab08["selected_rows"]
    ]
    assert [row["rank"] for row in evidence["bias"]] == list(range(1000, 1008))


def test_new_source_timeline_and_claim_boundaries_are_present() -> None:
    source = ARTICLE_MD.read_text()
    for required in (
        "On August 14",
        'called Claude\'s watermark "a version of the SynthID-Text approach."',
        "KGW-style green-list analogue",
        "Consistent with this configured watermark and key",
        "C4 is natural-web text. It is not verified human writing",
        "NLL and repetition are model-based proxies",
        "It says nothing about intent or misconduct",
        "Page not found",
    ):
        if required == "Page not found":
            assert required in (ROOT / "docs/article-source-update-2026-08.md").read_text()
        else:
            assert required in source


def test_article_contains_no_placeholders_or_forbidden_prose_marks() -> None:
    for path in (ARTICLE_MD, ARTICLE_HTML, ROOT / "docs/article-source-update-2026-08.md"):
        text = path.read_text()
        for forbidden in (
            "\u2014",
            "\u2013",
            "\u2192",
            "\u201c",
            "\u201d",
            "[TODO]",
            "<!-- VERIFY",
            "In conclusion",
            "In summary",
            "Let's break this down",
            "Think of it as",
            "move the knobs",
        ):
            assert forbidden not in text
