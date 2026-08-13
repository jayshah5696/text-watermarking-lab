# pyright: reportArgumentType=false
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import torch
from transformers import GPT2Config
from transformers.generation.logits_process import (
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
)

from watermark_lab.hf_adapter import (
    DetectorEvidence,
    OrderCandidate,
    ProcessorOrderProbe,
    build_order_probe,
    build_watermark_config,
    derive_reference_seed,
    detector_evidence,
    make_detector,
)
from watermark_lab.lab04_config import config_from_toml_bytes
from watermark_lab.manual_generation import derive_prompt_seed

ROOT = Path(__file__).resolve().parents[2]


def _config():  # type: ignore[no-untyped-def]
    return config_from_toml_bytes((ROOT / "configs/lab_04.toml").read_bytes())


def _reference_scores(raw: torch.Tensor, input_ids: torch.Tensor) -> torch.Tensor:
    config = _config()
    values = TemperatureLogitsWarper(config.temperature)(input_ids, raw.clone())
    values = TopKLogitsWarper(config.top_k)(input_ids, values)
    values = TopPLogitsWarper(config.top_p)(input_ids, values)
    processor = build_watermark_config(config, key=config.generation_key).construct_processor(
        raw.shape[-1], config.device
    )
    return processor(input_ids, values)


def test_seed_continues_stage_03_exactly() -> None:
    config = _config()
    for prompt in config.prompts:
        assert derive_reference_seed(
            base_seed=config.base_seed, prompt_id=prompt.id
        ) == derive_prompt_seed(base_seed=config.base_seed, prompt_id=prompt.id)


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"base_seed": True, "prompt_id": "x"}, TypeError),
        ({"base_seed": -1, "prompt_id": "x"}, ValueError),
        ({"base_seed": 1, "prompt_id": 7}, TypeError),
        ({"base_seed": 1, "prompt_id": "bad|id"}, ValueError),
    ],
)
def test_seed_rejects_invalid_inputs(kwargs: dict[str, object], error: type[Exception]) -> None:
    with pytest.raises(error):
        derive_reference_seed(**kwargs)  # type: ignore[arg-type]


def test_watermark_config_is_exact_and_rejects_unknown_key() -> None:
    config = _config()
    watermark = build_watermark_config(config, key=config.generation_key)
    assert watermark.to_dict() == {
        "bias": 2.0,
        "context_width": 1,
        "greenlist_ratio": 0.25,
        "hashing_key": 15485863,
        "seeding_scheme": "lefthash",
    }
    with pytest.raises(ValueError, match="configured"):
        build_watermark_config(config, key=1)


def test_order_probe_matches_reference_processors_and_keeps_selected_candidate() -> None:
    config = _config()
    raw = torch.linspace(-3.0, 3.0, 50, dtype=torch.float32)[None]
    input_ids = torch.tensor([[4, 9]], dtype=torch.long)
    generated = _reference_scores(raw, input_ids)
    selected = 0
    probe = build_order_probe(
        raw_scores=raw,
        generated_scores=generated,
        input_ids=input_ids,
        selected_token_id=selected,
        token_text=lambda token_id: f"token-{token_id}",
        config=config,
    )
    assert probe.generate_scores_match_probe
    assert probe.reference_counts[1] == 40
    assert probe.reference_counts[-1] <= 40
    assert probe.stage_03_counts[-1] <= 40
    assert probe.green_token_count == 12
    assert any(candidate.token_id == selected for candidate in probe.candidates)
    assert sum(candidate.selected_by_reference for candidate in probe.candidates) == 1


@pytest.mark.parametrize(
    ("raw", "generated", "input_ids", "selected", "message"),
    [
        (torch.zeros(50), torch.zeros((1, 50)), torch.tensor([[1]]), 1, "raw_scores"),
        (torch.zeros((1, 50)), torch.zeros((1, 49)), torch.tensor([[1]]), 1, "match"),
        (torch.zeros((1, 50)), torch.zeros((1, 50)), torch.tensor([]), 1, "input_ids"),
        (torch.zeros((1, 50)), torch.zeros((1, 50)), torch.tensor([[1]]), 50, "vocabulary"),
    ],
)
def test_order_probe_rejects_bad_shapes(
    raw: torch.Tensor,
    generated: torch.Tensor,
    input_ids: torch.Tensor,
    selected: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        build_order_probe(
            raw_scores=raw,
            generated_scores=generated,
            input_ids=input_ids,
            selected_token_id=selected,
            token_text=str,
            config=_config(),
        )


def test_order_probe_rejects_scores_that_do_not_match_generate() -> None:
    raw = torch.linspace(-3.0, 3.0, 50)[None]
    with pytest.raises(ValueError, match="do not match"):
        build_order_probe(
            raw_scores=raw,
            generated_scores=torch.zeros_like(raw),
            input_ids=torch.tensor([[2, 3]]),
            selected_token_id=49,
            token_text=str,
            config=_config(),
        )


def test_detector_records_counts_scores_and_stage_01_recomputation() -> None:
    config = _config()
    model_config = GPT2Config(vocab_size=50, bos_token_id=49, eos_token_id=49)
    detector = make_detector(
        config=config,
        model_config=model_config,
        key=config.generation_key,
        ignore_repeated_ngrams=False,
    )
    token_ids = torch.tensor([[1, 2, 3, 4, 5, 6]], dtype=torch.long)
    result = detector_evidence(
        detector=detector,
        token_ids=token_ids,
        key_role="generation",
        repetition_policy="all",
        green_fraction=config.green_fraction,
        z_threshold=config.z_threshold,
    )
    assert result.num_tokens_scored == 5
    assert result.num_green_tokens == 2
    assert result.z_score == result.independent_z_score
    assert not result.prediction
    with pytest.raises(ValueError, match="shape"):
        detector_evidence(
            detector=detector,
            token_ids=token_ids[0],
            key_role="generation",
            repetition_policy="all",
            green_fraction=config.green_fraction,
            z_threshold=config.z_threshold,
        )


def test_detector_evidence_validates_strict_threshold_and_finite_fields() -> None:
    valid = dict(
        key_role="generation",
        repetition_policy="all",
        num_tokens_scored=4,
        num_green_tokens=1,
        green_fraction=0.25,
        z_score=0.0,
        independent_z_score=0.0,
        p_value=0.5,
        z_threshold=3.0,
        prediction=False,
    )
    assert DetectorEvidence(**valid).prediction is False  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="strict threshold"):
        DetectorEvidence(**(valid | {"prediction": True}))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="must match"):
        DetectorEvidence(**(valid | {"independent_z_score": 1.0}))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="p_value"):
        DetectorEvidence(**(valid | {"p_value": float("nan")}))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"key_role": "other"}, ValueError),
        ({"repetition_policy": "other"}, ValueError),
        ({"num_tokens_scored": True}, TypeError),
        ({"num_tokens_scored": 0}, ValueError),
        ({"num_green_tokens": 5}, ValueError),
        ({"green_fraction": -0.1}, ValueError),
        ({"p_value": 1.1}, ValueError),
        ({"prediction": 1}, TypeError),
    ],
)
def test_detector_evidence_rejects_invalid_contract_fields(
    changes: dict[str, object], error: type[Exception]
) -> None:
    values = dict(
        key_role="generation",
        repetition_policy="all",
        num_tokens_scored=4,
        num_green_tokens=1,
        green_fraction=0.25,
        z_score=0.0,
        independent_z_score=0.0,
        p_value=0.5,
        z_threshold=3.0,
        prediction=False,
    )
    with pytest.raises(error):
        DetectorEvidence(**(values | changes))  # type: ignore[arg-type]


def _candidate() -> OrderCandidate:
    return OrderCandidate(
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


def _probe() -> ProcessorOrderProbe:
    return ProcessorOrderProbe(
        previous_token_id=1,
        previous_token_text=" a",
        vocabulary_size=50,
        green_token_count=12,
        reference_order=("temperature", "top_k", "top_p", "watermark"),
        stage_03_order=("watermark", "temperature", "top_p", "top_k"),
        reference_counts=(50, 40, 20, 20),
        stage_03_counts=(50, 50, 18, 18),
        selected_token_id=2,
        selected_token_text=" b",
        reference_selected_probability=0.4,
        stage_03_selected_probability=0.5,
        generate_scores_match_probe=True,
        candidates=(_candidate(),),
    )


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("token_id", True, TypeError),
        ("token_text", 7, TypeError),
        ("raw_score", "bad", TypeError),
        ("reference_probability", 1.1, ValueError),
        ("reference_final_score", float("nan"), ValueError),
        ("reference_after_top_k", 1, TypeError),
    ],
)
def test_order_candidate_rejects_invalid_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_candidate(), **{field: value})


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("previous_token_text", 1, TypeError),
        ("vocabulary_size", 1, ValueError),
        ("green_token_count", 50, ValueError),
        ("stage_03_order", ("temperature",), ValueError),
        ("reference_counts", (1,), ValueError),
        ("stage_03_counts", (50, 50, 18, 0), ValueError),
        ("selected_token_text", 1, TypeError),
        ("reference_selected_probability", -1.0, ValueError),
        ("generate_scores_match_probe", False, ValueError),
        ("candidates", (), ValueError),
        ("candidates", ("bad",), TypeError),
    ],
)
def test_order_probe_rejects_invalid_contract_fields(
    field: str, value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        replace(_probe(), **{field: value})
