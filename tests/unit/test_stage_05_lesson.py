import json
import tomllib
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


def test_lesson_and_runtime_core_do_not_import_modal() -> None:
    runtime_files = (
        ROOT / "src/watermark_lab/transformers_runtime.py",
        ROOT / "src/watermark_lab/gemma_adapter.py",
        ROOT / "src/watermark_lab/key_policy.py",
        ROOT / "src/watermark_lab/service_contract.py",
    )
    assert all("import modal" not in path.read_text() for path in runtime_files)
    coverage = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["coverage"]["run"]
    assert coverage["omit"] == [
        "src/watermark_lab/modal_app.py",
        "src/watermark_lab/modal_app_06.py",
        "src/watermark_lab/modal_app_07.py",
    ]
    report = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["coverage"]["report"]
    assert report["omit"] == [
        "src/watermark_lab/lab07_config.py",
        "src/watermark_lab/lab07_records.py",
    ]


def test_lesson_teaches_the_actual_stage_05_implementation_question() -> None:
    lesson = LESSON.read_text()
    for required in (
        "How do we add a generation-time watermark",
        "Implement and host",
        "Follow one prompt through the reusable path",
        "Model adapter",
        "Process-local key",
        "Generation",
        "Detector",
        "Gemma 4 is the worked example",
        "Modal is only the machine",
    ):
        assert required.lower() in lesson.lower()


def test_lesson_shows_exact_generation_and_detection_boundaries() -> None:
    lesson = LESSON.read_text()
    for required in (
        "model.generate(",
        "watermarking_config=profile.to_transformers()",
        "WatermarkDetector(",
        "model_config=",
        "adapter.model_config",
        "device=",
        "adapter.device",
        "adapter.token_tensor(copied_ids)",
        "z_threshold=3.0",
    ):
        assert required in lesson
    assert "The key enters at generation time" in lesson
    assert "The key is not prompt text" in lesson


def test_lesson_defines_compatible_models_without_claiming_every_model() -> None:
    lesson = LESSON.read_text().lower()
    for required in (
        "compatible does not mean every hub repository",
        "encoder-only models",
        "remote apis that hide logits",
        "automodelforcausallm",
        "automodelformultimodallm",
        "config.get_text_config()",
        "parse assistant content",
    ):
        assert required in lesson
    assert "works for any model" not in lesson
    assert "any hugging face model" not in lesson


def test_lesson_teaches_public_and_private_key_boundaries() -> None:
    lesson = LESSON.read_text()
    for required in (
        "public_demo_key",
        "private_key_from_environment",
        "WATERMARK_HASHING_KEY",
        "WATERMARK_KEY_VERSION",
        "The public demo key provides reproducibility, not secrecy",
        "request contains prompt text and bounded sampling fields",
        "never key value",
        "non-secret key version",
        "Modal, a VM, Kubernetes, or another GPU provider",
    ):
        assert required.lower() in lesson.lower()


def test_lesson_preserves_the_real_parsing_failure_and_selected_proof() -> None:
    lesson = LESSON.read_text()
    for required in (
        "str(parsed)",
        "assistant_content(parsed)",
        "The first Gemma smoke exposed this boundary",
        "Early one morning Jack went up the hill. At the top he",
        "11/26",
        "2.0381",
        "36.739 seconds",
        "9.682 GiB",
        "$0.1157",
    ):
        assert required in lesson


def test_lesson_is_self_contained_accessible_and_has_static_fallback() -> None:
    lesson = LESSON.read_text()
    parser = Structure()
    parser.feed(lesson)
    assert parser.scripts == 1
    assert parser.external_scripts == 0
    assert parser.details == parser.summaries == 3
    for required in (
        'id="plain"',
        'id="gemma"',
        'id="control"',
        'id="marked"',
        'id="badParse"',
        'id="goodParse"',
        'id="demoMode"',
        'id="privateMode"',
        'id="pathSvg"',
        'id="pathNext"',
        'id="pathPrev"',
        'id="pathReset"',
        'id="tokenSvg"',
        'id="nextToken"',
        'id="hostSvg"',
        'id="sendRequest"',
        'id="exampleList"',
        'id="lengthChart"',
        'id="lengthPause"',
        'id="lengthReplay"',
        'id="lengthControlTokens"',
        'id="lengthWatermarkedTokens"',
        "8 of 12 watermarked rows crossed",
        "Color is mechanical, not semantic",
        "setInterval",
        'id="controlText"',
        'id="watermarkedText"',
        'id="controlZ"',
        'id="watermarkedZ"',
        'id="controlP"',
        'id="watermarkedP"',
        "p-value is not detection probability",
        "Ten prompts demonstrate the implementation",
        'role="img"',
        'aria-labelledby="pathTitle pathDesc"',
        'aria-labelledby="tokenTitle tokenDesc"',
        'aria-labelledby="hostTitle hostDesc"',
        "CONCEPTUAL OPERATION VIEW",
        'class="static"',
        "prefers-reduced-motion",
        "@media(max-width:800px)",
    ):
        assert required in lesson
    for forbidden in ("fetch(", "localStorage", 'type="module"', "http://"):
        assert forbidden not in lesson


def test_embedded_ten_pair_results_match_selected_examples() -> None:
    lesson = LESSON.read_text()
    selected = json.loads((ROOT / "artifacts/lab-05/examples.json").read_text())
    assert len(selected["pairs"]) == 10
    for required in (
        "2.0381",
        "0.035523",
        "2.1004",
        "p:.030144",
        "2.2517",
        "p:.019823",
        "1.6036",
        "z:.9333",
        "z:.2265",
        "z:-.2462",
        "none crossed z &gt; 3",
    ):
        assert required.lower() in lesson.lower()


def test_embedded_length_ladder_matches_selected_summary() -> None:
    lesson = LESSON.read_text()
    selected = json.loads((ROOT / "artifacts/lab-05/lengths.json").read_text())
    assert selected["summary"] == {
        "max_control_z": 1.842197661499656,
        "max_watermarked_z": 8.027097412270678,
        "maximum_achieved_copied_tokens": 800,
        "minimum_achieved_copied_tokens": 200,
        "positive_control_rows": 0,
        "positive_watermarked_rows": 8,
    }
    for required in ("3.4788", "5.6144", "6.7346", "8.0271", "z = 3"):
        assert required in lesson


def test_claims_remain_narrow() -> None:
    lesson = LESSON.read_text().lower()
    for required in (
        "consistent with this configured watermark and key",
        "does not prove ai origin, authorship",
        "private claude implementation",
        "does not define the implementation",
        "does not prove human origin or absence of a watermark",
        "still unimplemented",
        "authenticated endpoint and deployment",
    ):
        assert required in lesson
    for forbidden in ("\u2014", "\u2013", "\u2192", "\u201c", "\u201d", "move the knobs"):
        assert forbidden not in lesson
