from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[2]
LESSON_PATH = REPOSITORY_ROOT / ".agent/diagrams/text-watermarking-stage-2-lesson.html"


def test_stage_02_lesson_separates_illustration_from_recorded_evidence() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")

    assert "Jack went up the" in lesson
    assert "Hand-authored concept illustration · not run data" in lesson
    assert "Recorded Stage 2 trace · synthetic scores" in lesson
    assert "Stage 2 does not run that model and did not generate this sentence" in lesson


def test_stage_02_main_path_uses_ids_instead_of_artifact_word_tags() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")
    visible_markup = lesson.split("<script>", maxsplit=1)[0]

    for artifact_word_tag in ("amber", "birch", "cobalt"):
        assert artifact_word_tag not in visible_markup

    assert "draw lands in <strong>ID 1</strong>" in visible_markup
    assert "same draw lands in <strong>ID 2</strong>" in visible_markup


def test_stage_02_lesson_keeps_guided_controls_addressable() -> None:
    lesson = LESSON_PATH.read_text(encoding="utf-8")

    for control_id in (
        "revealConcept",
        "runSelector",
        "biasOff",
        "biasOn",
        "revealFailure",
        "nextCheck",
    ):
        assert f'id="{control_id}"' in lesson
