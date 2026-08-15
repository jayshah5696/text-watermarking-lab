# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOptionalSubscript=false, reportUnnecessaryCast=false, reportUnnecessaryIsInstance=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Thin, inspectable helpers around the pinned Transformers watermark API."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable
from dataclasses import dataclass
from itertools import pairwise
from typing import Any, Literal, cast

import torch
from transformers import PreTrainedConfig, WatermarkDetector, WatermarkingConfig
from transformers.generation.logits_process import (
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
)

from watermark_lab.lab04_config import Lab04Config
from watermark_lab.stats import green_hit_z_score

KeyRole = Literal["generation", "comparison"]
RepetitionPolicy = Literal["all", "unique"]
WitnessRole = Literal[
    "selected",
    "green_survivor",
    "red_survivor",
    "green_filtered",
    "red_filtered",
]


def _checked_int(name: str, value: object, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _checked_finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class DetectorEvidence:
    """Counts and scores returned for one exact detector profile."""

    key_role: KeyRole
    repetition_policy: RepetitionPolicy
    num_tokens_scored: int
    num_green_tokens: int
    green_fraction: float
    z_score: float
    independent_z_score: float
    p_value: float
    z_threshold: float
    prediction: bool

    def __post_init__(self) -> None:
        if self.key_role not in ("generation", "comparison"):
            raise ValueError("key_role must be generation or comparison")
        if self.repetition_policy not in ("all", "unique"):
            raise ValueError("repetition_policy must be all or unique")
        tokens = _checked_int("num_tokens_scored", self.num_tokens_scored, minimum=1)
        green = _checked_int("num_green_tokens", self.num_green_tokens)
        if green > tokens:
            raise ValueError("num_green_tokens must not exceed num_tokens_scored")
        fraction = _checked_finite("green_fraction", self.green_fraction)
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("green_fraction must be between zero and one")
        z_score = _checked_finite("z_score", self.z_score)
        independent = _checked_finite("independent_z_score", self.independent_z_score)
        if not math.isclose(z_score, independent, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("z_score and independent_z_score must match")
        p_value = _checked_finite("p_value", self.p_value)
        if not 0.0 <= p_value <= 1.0:
            raise ValueError("p_value must be between zero and one")
        threshold = _checked_finite("z_threshold", self.z_threshold)
        if not isinstance(self.prediction, bool):
            raise TypeError("prediction must be Boolean")
        if self.prediction != (z_score > threshold):
            raise ValueError("prediction must use the Transformers strict threshold rule")


@dataclass(frozen=True, slots=True)
class DistinctPairEvidence:
    """Value-based cross-check for the library's repeated-pair option."""

    num_distinct_pairs: int
    num_green_pairs: int
    green_fraction: float
    z_score: float

    def __post_init__(self) -> None:
        pairs = _checked_int("num_distinct_pairs", self.num_distinct_pairs, minimum=1)
        green = _checked_int("num_green_pairs", self.num_green_pairs)
        if green > pairs:
            raise ValueError("num_green_pairs must not exceed num_distinct_pairs")
        fraction = _checked_finite("green_fraction", self.green_fraction)
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("green_fraction must be between zero and one")
        _checked_finite("z_score", self.z_score)


@dataclass(frozen=True, slots=True)
class OrderCandidate:
    """One visible candidate processed through both fixed operation orders."""

    token_id: int
    token_text: str
    witness_role: WitnessRole
    raw_score: float
    in_green_group: bool
    reference_temperature_score: float
    reference_after_top_k: bool
    reference_after_top_p: bool
    reference_final_score: float | None
    reference_probability: float
    stage_03_watermark_score: float
    stage_03_temperature_score: float
    stage_03_after_top_p: bool
    stage_03_after_top_k: bool
    stage_03_final_score: float | None
    stage_03_probability: float
    selected_by_reference: bool

    def __post_init__(self) -> None:
        _checked_int("candidate token_id", self.token_id)
        if not isinstance(self.token_text, str):
            raise TypeError("candidate token_text must be text")
        if self.witness_role not in (
            "selected",
            "green_survivor",
            "red_survivor",
            "green_filtered",
            "red_filtered",
        ):
            raise ValueError("unexpected candidate witness_role")
        for name in (
            "raw_score",
            "reference_temperature_score",
            "reference_probability",
            "stage_03_watermark_score",
            "stage_03_temperature_score",
            "stage_03_probability",
        ):
            value = _checked_finite(name, getattr(self, name))
            if name.endswith("probability") and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between zero and one")
        for name in ("reference_final_score", "stage_03_final_score"):
            value = getattr(self, name)
            if value is not None:
                _checked_finite(name, value)
        for name in (
            "in_green_group",
            "reference_after_top_k",
            "reference_after_top_p",
            "stage_03_after_top_p",
            "stage_03_after_top_k",
            "selected_by_reference",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be Boolean")


@dataclass(frozen=True, slots=True)
class ProcessorOrderProbe:
    """The first saved GPT-2 score list under two declared processor orders."""

    previous_token_id: int
    previous_token_text: str
    vocabulary_size: int
    green_token_count: int
    reference_order: tuple[str, ...]
    stage_03_order: tuple[str, ...]
    reference_counts: tuple[int, ...]
    stage_03_counts: tuple[int, ...]
    selected_token_id: int
    selected_token_text: str
    reference_selected_probability: float
    stage_03_selected_probability: float
    generate_scores_match_probe: bool
    candidates: tuple[OrderCandidate, ...]

    def __post_init__(self) -> None:
        _checked_int("previous_token_id", self.previous_token_id)
        if not isinstance(self.previous_token_text, str):
            raise TypeError("previous_token_text must be text")
        vocabulary_size = _checked_int("vocabulary_size", self.vocabulary_size, minimum=2)
        green_count = _checked_int("green_token_count", self.green_token_count, minimum=1)
        if green_count >= vocabulary_size:
            raise ValueError("green_token_count must be smaller than vocabulary_size")
        if self.reference_order != ("temperature", "top_k", "top_p", "watermark"):
            raise ValueError("unexpected reference order")
        if self.stage_03_order != ("watermark", "temperature", "top_p", "top_k"):
            raise ValueError("unexpected Stage 3 order")
        if len(self.reference_counts) != 4 or len(self.stage_03_counts) != 4:
            raise ValueError("each operation order needs four candidate counts")
        for count in (*self.reference_counts, *self.stage_03_counts):
            _checked_int("candidate count", count, minimum=1)
        _checked_int("selected_token_id", self.selected_token_id)
        if not isinstance(self.selected_token_text, str):
            raise TypeError("selected_token_text must be text")
        for name in ("reference_selected_probability", "stage_03_selected_probability"):
            value = _checked_finite(name, getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between zero and one")
        if self.generate_scores_match_probe is not True:
            raise ValueError("generate scores must match the reference order probe")
        if not isinstance(self.candidates, tuple) or not self.candidates:
            raise ValueError("candidates must be a non-empty tuple")
        if any(not isinstance(candidate, OrderCandidate) for candidate in self.candidates):
            raise TypeError("every candidate must be an OrderCandidate")
        if sum(candidate.selected_by_reference for candidate in self.candidates) != 1:
            raise ValueError("exactly one displayed candidate must be the reference selection")


def derive_reference_seed(*, base_seed: int, prompt_id: str) -> int:
    """Reuse the exact Stage 3 prompt seed material without importing MLX."""

    if isinstance(base_seed, bool) or not isinstance(base_seed, int):
        raise TypeError("base_seed must be an integer")
    if base_seed < 0:
        raise ValueError("base_seed must be non-negative")
    if not isinstance(prompt_id, str):
        raise TypeError("prompt_id must be text")
    if not prompt_id or not prompt_id.isascii() or "|" in prompt_id:
        raise ValueError("prompt_id must be non-empty ASCII text without '|'")
    material = f"lab-03|{base_seed}|{prompt_id}".encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % (1 << 32)


def build_watermark_config(config: Lab04Config, *, key: int) -> WatermarkingConfig:
    """Build the exact generation or comparison-key reference configuration."""

    if key not in (config.generation_key, config.comparison_key):
        raise ValueError("key must be the configured generation or comparison key")
    return WatermarkingConfig(
        greenlist_ratio=config.green_fraction,
        bias=config.watermark_bias,
        hashing_key=key,
        seeding_scheme=config.seeding_scheme,
        context_width=config.context_width,
    )


def detector_evidence(
    *,
    detector: WatermarkDetector,
    token_ids: torch.Tensor,
    key_role: KeyRole,
    repetition_policy: RepetitionPolicy,
    green_fraction: float,
    z_threshold: float,
) -> DetectorEvidence:
    """Return counts and scores, not only the detector Boolean."""

    if token_ids.ndim != 2 or token_ids.shape[0] != 1:
        raise ValueError("token_ids must have shape (1, sequence_length)")
    result = cast(Any, detector(token_ids, z_threshold=z_threshold, return_dict=True))
    tokens = int(result.num_tokens_scored[0])
    green = int(result.num_green_tokens[0])
    z_score = float(result.z_score[0])
    independent = green_hit_z_score(
        hits=green,
        trials=tokens,
        null_probability=green_fraction,
    )
    if not math.isclose(z_score, independent, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Transformers and Stage 1 z-scores differ")
    return DetectorEvidence(
        key_role=key_role,
        repetition_policy=repetition_policy,
        num_tokens_scored=tokens,
        num_green_tokens=green,
        green_fraction=float(result.green_fraction[0]),
        z_score=z_score,
        independent_z_score=independent,
        p_value=float(result.p_value[0]),
        z_threshold=z_threshold,
        prediction=bool(result.prediction[0]),
    )


def distinct_pair_evidence(
    *, detector: WatermarkDetector, token_ids: torch.Tensor, green_fraction: float
) -> DistinctPairEvidence:
    """Score each distinct adjacent value pair once with the same library detector."""

    if token_ids.ndim != 2 or token_ids.shape[0] != 1 or token_ids.shape[1] < 2:
        raise ValueError("token_ids must contain one sequence with at least two tokens")
    values = [int(token_id) for token_id in token_ids[0].tolist()]
    distinct_pairs = tuple(dict.fromkeys(pairwise(values)))
    pair_tensor = torch.tensor(distinct_pairs, dtype=torch.long, device=token_ids.device)
    result = cast(Any, detector(pair_tensor, return_dict=True))
    scored = int(result.num_tokens_scored.sum())
    green = int(result.num_green_tokens.sum())
    if scored != len(distinct_pairs):
        raise ValueError("each explicit distinct pair must contribute exactly one score")
    return DistinctPairEvidence(
        num_distinct_pairs=scored,
        num_green_pairs=green,
        green_fraction=green / scored,
        z_score=green_hit_z_score(
            hits=green,
            trials=scored,
            null_probability=green_fraction,
        ),
    )


def _finite_count(values: torch.Tensor) -> int:
    return int(torch.isfinite(values).sum().item())


def _optional_value(values: torch.Tensor, token_id: int) -> float | None:
    value = float(values[0, token_id].item())
    return value if math.isfinite(value) else None


def _probabilities(values: torch.Tensor) -> torch.Tensor:
    return torch.softmax(values, dim=-1)


def build_order_probe(
    *,
    raw_scores: torch.Tensor,
    generated_scores: torch.Tensor,
    input_ids: torch.Tensor,
    selected_token_id: int,
    token_text: Callable[[int], str],
    config: Lab04Config,
) -> ProcessorOrderProbe:
    """Apply both public processor orders to one saved raw score list."""

    if raw_scores.ndim != 2 or raw_scores.shape[0] != 1:
        raise ValueError("raw_scores must have shape (1, vocabulary_size)")
    if generated_scores.shape != raw_scores.shape:
        raise ValueError("generated_scores must match raw_scores")
    if input_ids.ndim != 2 or input_ids.shape[0] != 1 or input_ids.shape[1] < 1:
        raise ValueError("input_ids must contain one non-empty sequence")
    vocabulary_size = raw_scores.shape[-1]
    if not 0 <= selected_token_id < vocabulary_size:
        raise ValueError("selected_token_id is outside the vocabulary")

    temperature = TemperatureLogitsWarper(config.temperature)
    top_k = TopKLogitsWarper(config.top_k)
    top_p = TopPLogitsWarper(config.top_p)
    reference_watermark = build_watermark_config(
        config, key=config.generation_key
    ).construct_processor(vocabulary_size, config.device)
    alternate_watermark = build_watermark_config(
        config, key=config.generation_key
    ).construct_processor(vocabulary_size, config.device)

    reference_temperature = temperature(input_ids, raw_scores.clone())
    reference_top_k = top_k(input_ids, reference_temperature.clone())
    reference_top_p = top_p(input_ids, reference_top_k.clone())
    reference_final = reference_watermark(input_ids, reference_top_p.clone())

    stage_03_watermark = alternate_watermark(input_ids, raw_scores.clone())
    stage_03_temperature = temperature(input_ids, stage_03_watermark.clone())
    stage_03_top_p = top_p(input_ids, stage_03_temperature.clone())
    stage_03_final = top_k(input_ids, stage_03_top_p.clone())

    zeros = torch.zeros_like(raw_scores)
    green_scores = build_watermark_config(config, key=config.generation_key).construct_processor(
        vocabulary_size, config.device
    )(input_ids, zeros)
    green_mask = green_scores[0] > 0
    reference_probabilities = _probabilities(reference_final)
    stage_03_probabilities = _probabilities(stage_03_final)
    score_match = bool(torch.equal(reference_final, generated_scores))
    if not score_match:
        raise ValueError("recorded generate scores do not match the reference order probe")

    available = torch.isfinite(reference_final[0])
    roles_and_masks: tuple[tuple[WitnessRole, torch.Tensor, torch.Tensor], ...] = (
        (
            "green_survivor",
            available & green_mask,
            reference_probabilities[0],
        ),
        (
            "red_survivor",
            available & ~green_mask,
            reference_probabilities[0],
        ),
        ("green_filtered", ~available & green_mask, raw_scores[0]),
        ("red_filtered", ~available & ~green_mask, raw_scores[0]),
    )
    selected_ids = {selected_token_id}
    witness_ids: list[tuple[WitnessRole, int]] = [("selected", selected_token_id)]
    for role, mask, ranking in roles_and_masks:
        eligible = mask.clone()
        for token_id in selected_ids:
            eligible[token_id] = False
        if not bool(eligible.any().item()):
            raise ValueError(f"no candidate is available for witness role {role}")
        ranked = torch.where(eligible, ranking, torch.tensor(-torch.inf, device=ranking.device))
        token_id = int(torch.argmax(ranked).item())
        selected_ids.add(token_id)
        witness_ids.append((role, token_id))
    if len(witness_ids) != config.trace_candidates:
        raise ValueError("trace_candidates must match the five locked witness roles")

    candidates = tuple(
        OrderCandidate(
            token_id=token_id,
            token_text=token_text(token_id),
            witness_role=role,
            raw_score=float(raw_scores[0, token_id].item()),
            in_green_group=bool(green_mask[token_id].item()),
            reference_temperature_score=float(reference_temperature[0, token_id].item()),
            reference_after_top_k=bool(torch.isfinite(reference_top_k[0, token_id]).item()),
            reference_after_top_p=bool(torch.isfinite(reference_top_p[0, token_id]).item()),
            reference_final_score=_optional_value(reference_final, token_id),
            reference_probability=float(reference_probabilities[0, token_id].item()),
            stage_03_watermark_score=float(stage_03_watermark[0, token_id].item()),
            stage_03_temperature_score=float(stage_03_temperature[0, token_id].item()),
            stage_03_after_top_p=bool(torch.isfinite(stage_03_top_p[0, token_id]).item()),
            stage_03_after_top_k=bool(torch.isfinite(stage_03_final[0, token_id]).item()),
            stage_03_final_score=_optional_value(stage_03_final, token_id),
            stage_03_probability=float(stage_03_probabilities[0, token_id].item()),
            selected_by_reference=token_id == selected_token_id,
        )
        for role, token_id in witness_ids
    )
    return ProcessorOrderProbe(
        previous_token_id=int(input_ids[0, -1].item()),
        previous_token_text=token_text(int(input_ids[0, -1].item())),
        vocabulary_size=vocabulary_size,
        green_token_count=int(green_mask.sum().item()),
        reference_order=config.reference_processor_order,
        stage_03_order=config.stage_03_processor_order,
        reference_counts=(
            _finite_count(reference_temperature),
            _finite_count(reference_top_k),
            _finite_count(reference_top_p),
            _finite_count(reference_final),
        ),
        stage_03_counts=(
            _finite_count(stage_03_watermark),
            _finite_count(stage_03_temperature),
            _finite_count(stage_03_top_p),
            _finite_count(stage_03_final),
        ),
        selected_token_id=selected_token_id,
        selected_token_text=token_text(selected_token_id),
        reference_selected_probability=float(reference_probabilities[0, selected_token_id].item()),
        stage_03_selected_probability=float(stage_03_probabilities[0, selected_token_id].item()),
        generate_scores_match_probe=score_match,
        candidates=candidates,
    )


def make_detector(
    *,
    config: Lab04Config,
    model_config: PreTrainedConfig,
    key: int,
    ignore_repeated_ngrams: bool,
) -> WatermarkDetector:
    """Construct one detector from the exact matching reference configuration."""

    return WatermarkDetector(
        model_config=model_config,
        device=config.device,
        watermarking_config=build_watermark_config(config, key=key),
        ignore_repeated_ngrams=ignore_repeated_ngrams,
    )
