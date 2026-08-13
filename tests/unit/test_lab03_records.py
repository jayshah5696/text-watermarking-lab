from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.lab03_config import config_from_toml_bytes
from watermark_lab.lab03_records import (
    CandidateTrace,
    ContinuationRecord,
    GenerationStep,
    Lab03Trace,
    trace_from_json_bytes,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)
from watermark_lab.manual_generation import GreenScore

ROOT = Path(__file__).resolve().parents[2]


def _score(role: str, *, hits: int = 1) -> GreenScore:
    return GreenScore(
        key_role=role,  # type: ignore[arg-type]
        green_hits=hits,
        eligible_tokens=1,
        expected_green_hits=0.25,
        z_score=1.7320508075688774 if hits else -0.5773502691896258,
    )


def _candidate(*, selected: bool = True) -> CandidateTrace:
    return CandidateTrace(
        token_id=2,
        token_text=" token",
        raw_score=1.0,
        in_green_group=True,
        score_increase=2.0,
        score_after_increase=3.0,
        temperature_score=3.75,
        final_probability=0.5,
        selected=selected,
    )


def _step(position: int) -> GenerationStep:
    return GenerationStep(
        position=position,
        input_length=10 + position,
        previous_token_id=1,
        available_after_top_p=50,
        available_after_top_k=40,
        candidates=(_candidate(),),
        selected_token_id=2,
        selected_token_text=" token",
        selected_token_in_green_group=True,
        selected_raw_score=1.0,
        selected_score_increase=2.0,
        selected_score_after_increase=3.0,
        selected_temperature_score=3.75,
        selected_probability=0.5,
    )


def _record(prompt_id: str, prompt_text: str, condition: str) -> ContinuationRecord:
    return ContinuationRecord(
        prompt_id=prompt_id,
        prompt_text=prompt_text,
        condition=condition,  # type: ignore[arg-type]
        seed=123,
        stop_reason="token_limit",
        prompt_token_ids=(1, 2),
        prompt_token_pieces=("one", " two"),
        generated_token_ids=(2, 2),
        decoded_text=" token token",
        copied_token_ids=(2, 2),
        copied_ids_match=True,
        generation_key_score=_score("generation"),
        comparison_key_score=_score("comparison", hits=0),
        steps=(_step(1), _step(2)),
    )


def _trace() -> Lab03Trace:
    payload = (ROOT / "configs/lab_03.toml").read_bytes()
    config = config_from_toml_bytes(payload)
    return Lab03Trace(
        schema_version=1,
        source_commit="a" * 40,
        config_sha256=hashlib.sha256(payload).hexdigest(),
        python_version="3.12.7",
        platform="test-platform",
        mlx_version="0.32.0",
        mlx_lm_version="0.31.3",
        config=config,
        records=tuple(
            _record(prompt.id, prompt.text, condition)
            for prompt in config.prompts
            for condition in ("control", "score_increase")
        ),
    )


def test_trace_json_round_trip_is_byte_stable() -> None:
    payload = trace_to_json_bytes(_trace())
    assert payload.endswith(b"\n")
    assert trace_to_json_bytes(trace_from_json_bytes(payload)) == payload


def test_markdown_contains_spine_result_table_and_boundary() -> None:
    markdown = trace_to_markdown_bytes(_trace()).decode()
    assert "## First recorded token from the continuity prompt" in markdown
    assert markdown.count("| `stage-02-continuity` |") == 2
    assert "Stage 3 has no tested" in markdown
    assert "MLX-LM `0.31.3`" in markdown


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("schema_version", 2, ValueError),
        ("source_commit", "bad", ValueError),
        ("config_sha256", "a" * 63, ValueError),
        ("config", "bad", TypeError),
        ("records", (), ValueError),
    ],
)
def test_trace_rejects_invalid_root_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_trace(), **{field: value})


def test_records_reject_inconsistent_ids_steps_and_scores() -> None:
    record = _trace().records[0]
    with pytest.raises(ValueError, match="copied_ids_match"):
        replace(record, copied_ids_match=False)
    with pytest.raises(ValueError, match="step"):
        replace(record, steps=(record.steps[0],))
    with pytest.raises(ValueError, match="wrong role"):
        replace(record, generation_key_score=_score("comparison"))
    with pytest.raises(ValueError, match="condition"):
        replace(record, condition="bad")


def test_steps_and_candidates_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match="cannot restore"):
        replace(_step(1), available_after_top_k=51, available_after_top_p=50)
    with pytest.raises(ValueError, match="at most one"):
        replace(_step(1), candidates=(_candidate(), _candidate()))
    with pytest.raises(ValueError, match="between zero and one"):
        replace(_candidate(), final_probability=1.1)
    with pytest.raises(ValueError, match="step"):
        replace(
            _trace().records[0],
            generated_token_ids=(3, 2),
            copied_token_ids=(3, 2),
        )


def test_json_parser_rejects_unknown_nonfinite_and_invalid_shapes() -> None:
    data = json.loads(trace_to_json_bytes(_trace()))
    data["unknown"] = 1
    with pytest.raises(ValueError, match="keys differ"):
        trace_from_json_bytes(json.dumps(data).encode())
    data = json.loads(trace_to_json_bytes(_trace()))
    data["records"][0]["steps"][0]["candidates"][0]["raw_score"] = float("nan")
    with pytest.raises(ValueError, match="non-finite"):
        trace_from_json_bytes(json.dumps(data).encode())
    data = json.loads(trace_to_json_bytes(_trace()))
    data["records"] = "bad"
    with pytest.raises(TypeError, match="array"):
        trace_from_json_bytes(json.dumps(data).encode())


def test_parser_rejects_invalid_flags_and_score_role() -> None:
    data = json.loads(trace_to_json_bytes(_trace()))
    data["records"][0]["copied_ids_match"] = 1
    with pytest.raises(TypeError, match="Boolean"):
        trace_from_json_bytes(json.dumps(data).encode())
    data = json.loads(trace_to_json_bytes(_trace()))
    data["records"][0]["generation_key_score"]["key_role"] = "bad"
    with pytest.raises(ValueError, match="key_role"):
        trace_from_json_bytes(json.dumps(data).encode())


def test_record_value_validators_reject_bad_scalar_and_sequence_values() -> None:
    with pytest.raises(TypeError, match="integer"):
        replace(_candidate(), token_id=True)
    with pytest.raises(ValueError, match="at least"):
        replace(_candidate(), token_id=-1)
    with pytest.raises(TypeError, match="real number"):
        replace(_candidate(), raw_score="high")
    with pytest.raises(ValueError, match="finite"):
        replace(_candidate(), raw_score=float("inf"))
    with pytest.raises(TypeError, match="text"):
        replace(_candidate(), token_text=7)
    with pytest.raises(TypeError, match="flags"):
        replace(_candidate(), selected=1)
    with pytest.raises(ValueError, match="non-empty tuple"):
        replace(_step(1), candidates=())
    with pytest.raises(TypeError, match="CandidateTrace"):
        replace(_step(1), candidates=("bad",))
    with pytest.raises(TypeError, match="Boolean"):
        replace(_step(1), selected_token_in_green_group=1)
    with pytest.raises(ValueError, match="between zero and one"):
        replace(_step(1), selected_probability=-0.1)


def test_continuation_validators_reject_bad_nested_values() -> None:
    record = _trace().records[0]
    with pytest.raises(ValueError, match="stop_reason"):
        replace(record, stop_reason="bad")
    with pytest.raises(TypeError, match="sequence"):
        replace(record, prompt_token_ids="bad")
    with pytest.raises(ValueError, match="must not be empty"):
        replace(record, generated_token_ids=(), copied_token_ids=())
    with pytest.raises(TypeError, match="Boolean"):
        replace(record, copied_ids_match=1)
    with pytest.raises(TypeError, match="GreenScore"):
        replace(record, generation_key_score="bad")
    with pytest.raises(TypeError, match="GreenScore"):
        replace(record, comparison_key_score="bad")
    with pytest.raises(ValueError, match="wrong role"):
        replace(record, comparison_key_score=_score("generation"))
    with pytest.raises(ValueError, match="steps"):
        replace(record, steps=[])
    with pytest.raises(TypeError, match="every step"):
        replace(record, steps=("bad", record.steps[1]))


def test_json_parser_rejects_non_object_root() -> None:
    with pytest.raises(TypeError, match="object"):
        trace_from_json_bytes(b"[]")
