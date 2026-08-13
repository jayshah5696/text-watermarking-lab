# pyright: reportArgumentType=false
from __future__ import annotations

import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import torch
from transformers import WatermarkingConfig

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


def _lesson_data() -> dict[str, Any]:
    lesson = LESSON.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="lessonData" type="application/json">(.*?)</script>',
        lesson,
        flags=re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_lesson_builds_a_stage_03_to_stage_04_bridge() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    for required in (
        "Measure the signal",
        "Define a green hit",
        "Generate by hand",
        "Check the implementation",
        "LFM2 through MLX",
        "Local Apple GPU",
        "GPT-2 through Transformers 5.14.1",
        "Local CPU",
        "The model, tokenizer, prompt formatting, green-set rule, device, "
        "and operation order all change",
    ):
        assert required in lesson
    for filename in (
        "text-watermarking-stage-1-walkthrough.html",
        "text-watermarking-stage-2-lesson.html",
        "text-watermarking-stage-3-lesson.html",
    ):
        assert f'href="{filename}"' in lesson


def test_lesson_carries_the_first_two_reference_tokens_into_checking() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    record = next(
        item
        for item in trace["records"]
        if item["prompt_id"] == "stage-02-continuity" and item["condition"] == "reference_watermark"
    )
    assert record["generated_token_ids"][:2] == [373, 21272]
    assert "token 1 / context only" in lesson
    assert "token 2 / first checked" in lesson
    assert "was</span><br>ID 373" in lesson
    assert "greeted</span><br>ID 21272 / green" in lesson
    assert "40 - 1 = 39" in lesson


def test_lesson_formula_and_order_values_match_selected_trace() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    probe = _trace()["order_probe"]
    assert probe["reference_counts"] == [50257, 40, 19, 19]
    assert probe["stage_03_counts"] == [50257, 50257, 11, 11]
    for formula in (
        "s_i^(temp) = s_i / 0.8",
        "rank(s) &lt;= 40",
        "cumulative P &gt;= .95",
        "s_i^(wm) = s_i + 2 x I[i is green]",
        "P(i) = exp(s_i) / sum_j exp(s_j)",
        "z = (17 - 9.75) / 2.7042 = 2.6811",
    ):
        assert formula in lesson
    assert f"{100 * probe['reference_selected_probability']:.6f}%" in lesson
    assert f"{100 * probe['stage_03_selected_probability']:.6f}%" in lesson
    for candidate in probe["candidates"]:
        assert str(candidate["token_id"]) in lesson
        assert candidate["token_text"].strip() in lesson
    assert "exp(2) = 7.3891" in lesson
    assert "exp(2.5) = 12.1825" in lesson


def test_sampling_claim_uses_the_recorded_seed_without_inventing_a_draw() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    trace = _trace()
    record = next(
        item
        for item in trace["records"]
        if item["prompt_id"] == "stage-02-continuity" and item["condition"] == "reference_watermark"
    )
    assert record["seed"] == 568285428
    assert "seed 568285428" in lesson
    assert "does not record one separate random-number draw" in lesson
    assert "78.591889%" in lesson
    assert "8.642730%" in lesson


def test_embedded_records_match_all_six_saved_continuations() -> None:
    trace = _trace()
    data = _lesson_data()
    records = {record["id"]: record for record in data["records"]}
    assert len(records) == 6
    for saved in trace["records"]:
        identity = f"{saved['prompt_id']}:{saved['condition']}"
        embedded = records[identity]
        assert embedded["prompt_text"] == saved["prompt_text"]
        assert embedded["text"] == saved["decoded_text"]
        assert embedded["ids"] == saved["generated_token_ids"]
        assert len(embedded["ids"]) == len(embedded["pieces"]) == 40
        generation = saved["detector_results"][0]
        comparison = saved["detector_results"][2]
        for key, result in (("15485863", generation), ("15485867", comparison)):
            replay = data["keys"][key][identity]
            assert replay["g"] == result["num_green_tokens"]
            assert replay["t"] == result["num_tokens_scored"]
            assert math.isclose(replay["z"], result["z_score"], abs_tol=1e-11)


def test_all_bundled_keys_replay_the_exact_transformers_memberships() -> None:
    data = _lesson_data()
    assert data["key_min"] == 15485856
    assert data["key_max"] == 15485872
    assert set(map(int, data["keys"])) == set(range(15485856, 15485873))
    for key_text, by_record in data["keys"].items():
        processor = WatermarkingConfig(
            greenlist_ratio=0.25,
            bias=2.0,
            hashing_key=int(key_text),
            seeding_scheme="lefthash",
            context_width=1,
        ).construct_processor(50257, "cpu")
        for record in data["records"]:
            expected = by_record[record["id"]]
            observed = "".join(
                "1"
                if bool(
                    torch.isin(
                        torch.tensor(current),
                        processor._get_greenlist_ids(torch.tensor([previous])),
                    )
                )
                else "0"
                for previous, current in zip(record["ids"][:-1], record["ids"][1:], strict=True)
            )
            assert observed == expected["marks"]
            assert observed.count("1") == expected["g"]
            assert len(observed) == expected["t"] == 39


def test_repetition_lesson_starts_with_occurrences_then_groups_pair_values() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    repetition = _trace()["repetition_fixture"]
    assert repetition["token_ids"] == [373, 21272, 373, 21272, 373, 21272]
    assert repetition["detector_results"][0]["num_tokens_scored"] == 5
    assert repetition["detector_results"][1]["num_tokens_scored"] == 5
    assert repetition["explicit_distinct_result"]["num_distinct_pairs"] == 2
    for required in (
        "Six tokens create five adjacent check occurrences",
        "green again",
        "red again",
        "Two different ordered pairs",
        "3/5, z 1.8074",
        "1/2, z 0.8165",
        "GPT-2 did not generate the constructed six-token sequence",
    ):
        assert required in lesson


def test_lesson_has_guided_controls_static_fallbacks_and_no_remote_runtime() -> None:
    lesson = LESSON.read_text(encoding="utf-8")
    parser = _Structure()
    parser.feed(lesson)
    assert parser.details == parser.summaries == 2
    assert parser.scripts == 3
    assert parser.external_scripts == 0
    assert parser.disabled_controls == 2
    for expected in (
        'id="nextFormula"',
        'id="previousFormula"',
        'id="replayFormula"',
        'id="predictSame"',
        'id="predictDifferent"',
        'id="replayOrders"',
        'id="animateSample"',
        'id="controlCondition"',
        'id="watermarkCondition"',
        'id="keyInput"',
        'id="generationKeyPreset"',
        'id="comparisonKeyPreset"',
        'id="nextTeachingKey"',
        'id="predictTwoPatterns"',
        'id="collapsePairs"',
        'class="static-fallback"',
        "All five operations without animation",
        "Three saved passage pairs",
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
    ):
        assert forbidden not in lesson
    for required in (
        "model preference numbers",
        "evidence score z",
        "Green is only a temporary key-selected label",
        "does not establish AI origin or authorship",
        "insufficient evidence for this exact saved text and key",
        "does not prove human origin or absence of a watermark",
        "do not measure detection accuracy, writing quality, or a false-alarm rate",
        "does not reproduce Anthropic's private Claude implementation",
    ):
        assert required.lower() in lesson.lower()
