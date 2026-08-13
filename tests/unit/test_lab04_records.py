from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.hf_adapter import DetectorEvidence, OrderCandidate, ProcessorOrderProbe
from watermark_lab.lab04_config import config_from_toml_bytes
from watermark_lab.lab04_records import (
    ContinuationRecord,
    Lab04Trace,
    PaddingEntry,
    PaddingValidation,
    RepetitionFixture,
    trace_from_json_bytes,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)

ROOT = Path(__file__).resolve().parents[2]


def _config():  # type: ignore[no-untyped-def]
    return config_from_toml_bytes((ROOT / "configs/lab_04.toml").read_bytes())


def _evidence(key_role: str, policy: str) -> DetectorEvidence:
    return DetectorEvidence(
        key_role=key_role,  # type: ignore[arg-type]
        repetition_policy=policy,  # type: ignore[arg-type]
        num_tokens_scored=4,
        num_green_tokens=1,
        green_fraction=0.25,
        z_score=0.0,
        independent_z_score=0.0,
        p_value=0.5,
        z_threshold=3.0,
        prediction=False,
    )


def _results() -> tuple[DetectorEvidence, ...]:
    return tuple(
        _evidence(key_role, policy)
        for key_role in ("generation", "comparison")
        for policy in ("all", "unique")
    )


def _probe() -> ProcessorOrderProbe:
    candidate = OrderCandidate(
        token_id=2,
        token_text=" b",
        raw_score=1.0,
        in_green_group=True,
        reference_temperature_score=1.25,
        reference_after_top_k=True,
        reference_after_top_p=True,
        reference_final_score=3.25,
        reference_probability=0.4,
        stage_03_watermark_score=3.0,
        stage_03_temperature_score=3.75,
        stage_03_after_top_p=True,
        stage_03_after_top_k=True,
        stage_03_final_score=3.75,
        stage_03_probability=0.5,
        selected_by_reference=True,
    )
    return ProcessorOrderProbe(
        previous_token_id=1,
        previous_token_text=" a",
        vocabulary_size=50_257,
        green_token_count=12_564,
        reference_order=("temperature", "top_k", "top_p", "watermark"),
        stage_03_order=("watermark", "temperature", "top_p", "top_k"),
        reference_counts=(50_257, 40, 20, 20),
        stage_03_counts=(50_257, 50_257, 18, 18),
        selected_token_id=2,
        selected_token_text=" b",
        reference_selected_probability=0.4,
        stage_03_selected_probability=0.5,
        generate_scores_match_probe=True,
        candidates=(candidate,),
    )


def _record(prompt_id: str, prompt_text: str, condition: str) -> ContinuationRecord:
    return ContinuationRecord(
        prompt_id=prompt_id,
        prompt_text=prompt_text,
        condition=condition,  # type: ignore[arg-type]
        seed=7,
        stop_reason="token_limit",
        prompt_token_ids=(10, 11),
        prompt_token_pieces=("prompt", " text"),
        generated_token_ids=(1, 2, 3, 4, 5),
        decoded_text="a b c d e",
        copied_token_ids=(1, 2, 3, 4, 5),
        copied_ids_match=True,
        detector_results=_results(),
    )


def _trace() -> Lab04Trace:
    config = _config()
    records = tuple(
        _record(prompt.id, prompt.text, condition)
        for prompt in config.prompts
        for condition in ("control", "reference_watermark")
    )
    repetition = RepetitionFixture(
        source_prompt_id="stage-02-continuity",
        construction="alternate-first-two-copied-ids-three-times",
        token_ids=(1, 2, 1, 2, 1, 2),
        token_pieces=("a", " b", "a", " b", "a", " b"),
        detector_results=(_evidence("generation", "all"), _evidence("generation", "unique")),
    )
    padding = PaddingValidation(
        pad_token_id=50_256,
        padding_side="left",
        padded_width=4,
        prompt_tokens_in_detector=0,
        padding_tokens_in_detector=0,
        entries=(
            PaddingEntry("stage-02-continuity", 4, 0, 4, 4),
            PaddingEntry("notebook", 3, 1, 3, 4),
            PaddingEntry("library", 2, 2, 2, 4),
        ),
    )
    return Lab04Trace(
        schema_version=1,
        source_commit="a" * 40,
        config_sha256="b" * 64,
        python_version="3.12.0",
        platform="test-platform",
        torch_version="2.13.0",
        transformers_version="5.14.1",
        config=config,
        watermark_profile={"hashing_key": config.generation_key},
        records=records,
        order_probe=_probe(),
        repetition_fixture=repetition,
        padding_validation=padding,
    )


def test_trace_round_trip_is_stable_and_markdown_contains_boundaries() -> None:
    trace = _trace()
    payload = trace_to_json_bytes(trace)
    loaded = trace_from_json_bytes(payload)
    assert loaded == trace
    assert trace_to_json_bytes(loaded) == payload
    markdown = trace_to_markdown_bytes(trace).decode()
    assert "Only the Transformers order produced the saved continuation" in markdown
    assert "first eligible decision" in markdown
    assert "no prompt or padding tokens" in markdown
    assert "consistent with this configured watermark and key" in markdown


def test_trace_json_rejects_unknown_keys_and_nonfinite_numbers() -> None:
    parsed = json.loads(trace_to_json_bytes(_trace()))
    parsed["unknown"] = 1
    with pytest.raises(ValueError, match="keys differ"):
        trace_from_json_bytes(json.dumps(parsed).encode())
    parsed.pop("unknown")
    parsed["records"][0]["detector_results"][0]["p_value"] = float("nan")
    with pytest.raises(ValueError, match="p_value"):
        trace_from_json_bytes(json.dumps(parsed).encode())


def test_continuation_record_rejects_mismatches_and_result_order() -> None:
    record = _record("one", "Prompt", "control")
    with pytest.raises(ValueError, match="copied_ids_match"):
        replace(record, copied_ids_match=False)
    with pytest.raises(ValueError, match="context plus"):
        replace(record, generated_token_ids=(1,), copied_token_ids=(1,))
    with pytest.raises(ValueError, match="policy order"):
        replace(record, detector_results=tuple(reversed(record.detector_results)))


def test_padding_and_repetition_contracts_reject_bad_shapes() -> None:
    padding = _trace().padding_validation
    with pytest.raises(ValueError, match="prompt and padding"):
        replace(padding, prompt_tokens_in_detector=1)
    with pytest.raises(ValueError, match="padded input width"):
        replace(padding.entries[0], continuation_slice_start=3)
    repetition = _trace().repetition_fixture
    with pytest.raises(ValueError, match="alternate"):
        replace(repetition, token_ids=(1, 2, 1, 3, 1, 2))
    with pytest.raises(ValueError, match="policy order"):
        replace(repetition, detector_results=tuple(reversed(repetition.detector_results)))


@pytest.mark.parametrize(
    ("target", "field", "value", "error"),
    [
        ("entry", "attention_mask_count", 3, ValueError),
        ("padding", "padding_side", "right", ValueError),
        ("padding", "entries", (), ValueError),
        ("padding", "entries", ("bad", "bad", "bad"), TypeError),
        ("padding", "padded_width", 5, ValueError),
        ("record", "condition", "bad", ValueError),
        ("record", "stop_reason", "bad", ValueError),
        ("record", "prompt_token_pieces", ("only-one",), ValueError),
        ("record", "copied_ids_match", 1, TypeError),
        ("record", "detector_results", (), ValueError),
        ("repetition", "construction", "bad", ValueError),
        ("repetition", "token_pieces", (), ValueError),
        ("repetition", "detector_results", (), ValueError),
    ],
)
def test_nested_record_contracts_reject_invalid_values(
    target: str, field: str, value: object, error: type[Exception]
) -> None:
    trace = _trace()
    item = {
        "entry": trace.padding_validation.entries[0],
        "padding": trace.padding_validation,
        "record": trace.records[0],
        "repetition": trace.repetition_fixture,
    }[target]
    with pytest.raises(error):
        replace(item, **{field: value})


def test_order_records_reject_invalid_probabilities_and_selection() -> None:
    probe = _probe()
    candidate = probe.candidates[0]
    with pytest.raises(ValueError, match="probability"):
        replace(candidate, reference_probability=2.0)
    with pytest.raises(ValueError, match="exactly one"):
        replace(probe, candidates=(replace(candidate, selected_by_reference=False),))
    with pytest.raises(ValueError, match="unexpected reference"):
        replace(probe, reference_order=("watermark",))


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("schema_version", 2, ValueError),
        ("source_commit", "bad", ValueError),
        ("config", "bad", TypeError),
        ("watermark_profile", "bad", TypeError),
        ("records", (), ValueError),
        ("order_probe", "bad", TypeError),
        ("repetition_fixture", "bad", TypeError),
        ("padding_validation", "bad", TypeError),
    ],
)
def test_trace_contract_rejects_invalid_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_trace(), **{field: value})
