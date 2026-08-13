# pyright: reportArgumentType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnnecessaryIsInstance=false
"""Validated selected records for the Stage 4 Transformers adapter."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

from watermark_lab.hf_adapter import (
    DetectorEvidence,
    DistinctPairEvidence,
    OrderCandidate,
    ProcessorOrderProbe,
)
from watermark_lab.lab04_config import Lab04Config, ReferencePrompt

Condition = Literal["control", "reference_watermark"]
StopReason = Literal["end_token", "token_limit"]


def _integer(name: str, value: object, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _text(name: str, value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be text")
    if not allow_empty and not value:
        raise ValueError(f"{name} must not be empty")
    return value


def _token_ids(name: str, value: object) -> tuple[int, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be a sequence")
    result = tuple(_integer("token ID", item) for item in cast(Sequence[object], value))
    if not result:
        raise ValueError(f"{name} must not be empty")
    return result


@dataclass(frozen=True, slots=True)
class PaddingEntry:
    """One row in the fixed left-padding boundary check."""

    prompt_id: str
    prompt_token_count: int
    left_padding_count: int
    attention_mask_count: int
    continuation_slice_start: int

    def __post_init__(self) -> None:
        _text("padding prompt_id", self.prompt_id)
        prompt_count = _integer("prompt_token_count", self.prompt_token_count, minimum=1)
        padding_count = _integer("left_padding_count", self.left_padding_count)
        if self.attention_mask_count != prompt_count:
            raise ValueError("attention_mask_count must equal prompt_token_count")
        if self.continuation_slice_start != prompt_count + padding_count:
            raise ValueError("continuation_slice_start must equal the padded input width")


@dataclass(frozen=True, slots=True)
class PaddingValidation:
    """Proof that prompt and padding tokens stay outside primary detection."""

    pad_token_id: int
    padding_side: Literal["left"]
    padded_width: int
    prompt_tokens_in_detector: Literal[0]
    padding_tokens_in_detector: Literal[0]
    entries: tuple[PaddingEntry, ...]

    def __post_init__(self) -> None:
        _integer("pad_token_id", self.pad_token_id)
        if self.padding_side != "left":
            raise ValueError("Stage 4 padding_side must be left")
        width = _integer("padded_width", self.padded_width, minimum=1)
        if self.prompt_tokens_in_detector != 0 or self.padding_tokens_in_detector != 0:
            raise ValueError("prompt and padding tokens must not enter primary detection")
        if not isinstance(self.entries, tuple) or len(self.entries) != 3:
            raise ValueError("padding validation requires three entries")
        if any(not isinstance(entry, PaddingEntry) for entry in self.entries):
            raise TypeError("every padding entry must be a PaddingEntry")
        if any(entry.continuation_slice_start != width for entry in self.entries):
            raise ValueError("all padding entries must use the padded width")


@dataclass(frozen=True, slots=True)
class ContinuationRecord:
    """One saved control or reference-watermarked continuation."""

    prompt_id: str
    prompt_text: str
    condition: Condition
    seed: int
    stop_reason: StopReason
    prompt_token_ids: tuple[int, ...]
    prompt_token_pieces: tuple[str, ...]
    generated_token_ids: tuple[int, ...]
    decoded_text: str
    copied_token_ids: tuple[int, ...]
    copied_ids_match: bool
    detector_results: tuple[DetectorEvidence, ...]

    def __post_init__(self) -> None:
        _text("prompt_id", self.prompt_id)
        _text("prompt_text", self.prompt_text)
        if self.condition not in ("control", "reference_watermark"):
            raise ValueError("condition must be control or reference_watermark")
        _integer("seed", self.seed)
        if self.stop_reason not in ("end_token", "token_limit"):
            raise ValueError("stop_reason must be end_token or token_limit")
        prompt_ids = _token_ids("prompt_token_ids", self.prompt_token_ids)
        if not isinstance(self.prompt_token_pieces, tuple) or len(self.prompt_token_pieces) != len(
            prompt_ids
        ):
            raise ValueError("prompt_token_pieces must match prompt_token_ids")
        for piece in self.prompt_token_pieces:
            _text("prompt token piece", piece, allow_empty=True)
        generated = _token_ids("generated_token_ids", self.generated_token_ids)
        _text("decoded_text", self.decoded_text, allow_empty=True)
        copied = _token_ids("copied_token_ids", self.copied_token_ids)
        if not isinstance(self.copied_ids_match, bool):
            raise TypeError("copied_ids_match must be Boolean")
        if self.copied_ids_match != (generated == copied):
            raise ValueError("copied_ids_match differs from the token IDs")
        if len(copied) < 2:
            raise ValueError("copied continuation needs context plus one eligible token")
        if not isinstance(self.detector_results, tuple) or len(self.detector_results) != 4:
            raise ValueError("each continuation needs four detector results")
        expected = [
            (key_role, policy)
            for key_role in ("generation", "comparison")
            for policy in ("all", "unique")
        ]
        actual = [(result.key_role, result.repetition_policy) for result in self.detector_results]
        if actual != expected:
            raise ValueError("detector results must follow key and repetition-policy order")


@dataclass(frozen=True, slots=True)
class RepetitionFixture:
    """A derived six-token sequence for the repeated-pair policy."""

    source_prompt_id: str
    construction: str
    token_ids: tuple[int, ...]
    token_pieces: tuple[str, ...]
    detector_results: tuple[DetectorEvidence, ...]
    explicit_distinct_result: DistinctPairEvidence

    def __post_init__(self) -> None:
        _text("source_prompt_id", self.source_prompt_id)
        if self.construction != "alternate-first-two-copied-ids-three-times":
            raise ValueError("unexpected repetition construction")
        ids = _token_ids("repetition token_ids", self.token_ids)
        if len(ids) != 6 or ids != (ids[0], ids[1], ids[0], ids[1], ids[0], ids[1]):
            raise ValueError("repetition token IDs must alternate twice across six positions")
        if not isinstance(self.token_pieces, tuple) or len(self.token_pieces) != 6:
            raise ValueError("repetition token pieces must match six IDs")
        for piece in self.token_pieces:
            _text("repetition token piece", piece, allow_empty=True)
        if not isinstance(self.detector_results, tuple) or len(self.detector_results) != 2:
            raise ValueError("repetition fixture needs all and unique results")
        actual = [result.repetition_policy for result in self.detector_results]
        if actual != ["all", "unique"] or any(
            result.key_role != "generation" for result in self.detector_results
        ):
            raise ValueError("repetition results must use the generation key in policy order")
        if not isinstance(self.explicit_distinct_result, DistinctPairEvidence):
            raise TypeError("explicit_distinct_result must be a DistinctPairEvidence")


@dataclass(frozen=True, slots=True)
class Lab04Trace:
    """Complete selected evidence for the pinned Transformers CPU fixture."""

    schema_version: Literal[1]
    source_commit: str
    config_sha256: str
    python_version: str
    platform: str
    torch_version: str
    transformers_version: str
    config: Lab04Config
    watermark_profile: Mapping[str, object]
    records: tuple[ContinuationRecord, ...]
    order_probe: ProcessorOrderProbe
    repetition_fixture: RepetitionFixture
    padding_validation: PaddingValidation

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")
        for name, value, length in (
            ("source_commit", self.source_commit, 40),
            ("config_sha256", self.config_sha256, 64),
        ):
            text = _text(name, value)
            if len(text) != length or any(
                character not in "0123456789abcdef" for character in text
            ):
                raise ValueError(f"{name} must be lowercase hexadecimal")
        for name, value in (
            ("python_version", self.python_version),
            ("platform", self.platform),
            ("torch_version", self.torch_version),
            ("transformers_version", self.transformers_version),
        ):
            _text(name, value)
        if not isinstance(self.config, Lab04Config):
            raise TypeError("config must be a Lab04Config")
        if not isinstance(self.watermark_profile, Mapping):
            raise TypeError("watermark_profile must be a mapping")
        expected_pairs = [
            (prompt.id, condition)
            for prompt in self.config.prompts
            for condition in ("control", "reference_watermark")
        ]
        actual_pairs = [(record.prompt_id, record.condition) for record in self.records]
        if actual_pairs != expected_pairs:
            raise ValueError("records must follow prompt and condition order")
        if not isinstance(self.order_probe, ProcessorOrderProbe):
            raise TypeError("order_probe must be a ProcessorOrderProbe")
        if not isinstance(self.repetition_fixture, RepetitionFixture):
            raise TypeError("repetition_fixture must be a RepetitionFixture")
        if not isinstance(self.padding_validation, PaddingValidation):
            raise TypeError("padding_validation must be a PaddingValidation")


def trace_to_json_bytes(trace: Lab04Trace) -> bytes:
    """Serialize the trace as stable finite JSON."""

    text = json.dumps(asdict(trace), allow_nan=False, indent=2, sort_keys=True)
    return f"{text}\n".encode()


def _format_evidence(result: DetectorEvidence) -> str:
    return f"{result.num_green_tokens}/{result.num_tokens_scored} | {result.z_score:.6f}"


def trace_to_markdown_bytes(trace: Lab04Trace) -> bytes:
    """Render the two-order probe, six saved rows, and boundary checks."""

    probe = trace.order_probe
    continuity = next(
        record
        for record in trace.records
        if record.prompt_id == "stage-02-continuity" and record.condition == "reference_watermark"
    )
    primary = continuity.detector_results[0]
    comparison = continuity.detector_results[2]
    repeat_all, repeat_unique = trace.repetition_fixture.detector_results
    lines = [
        "# Stage 4 annotated Transformers reference trace",
        "",
        "This measured local fixture used the pinned GPT-2 model and Transformers watermark",
        "adapter on the CPU. It compares one saved score list with the earlier Stage 3 order.",
        "",
        f"- Source commit: `{trace.source_commit}`",
        f"- Config SHA-256: `{trace.config_sha256}`",
        f"- Model revision: `{trace.config.model_id}@{trace.config.model_revision}`",
        f"- Runtime: Python `{trace.python_version}`, PyTorch `{trace.torch_version}`, ",
        f"  Transformers `{trace.transformers_version}` on `{trace.platform}`",
        "",
        "## One saved score list under two orders",
        "",
        f"The previous token was `{probe.previous_token_text}` (ID `{probe.previous_token_id}`).",
        f"Transformers kept {probe.reference_counts[-1]} choices. The earlier order kept",
        f"{probe.stage_03_counts[-1]} choices. The saved reference token",
        f"`{probe.selected_token_text}` (ID `{probe.selected_token_id}`) had chance",
        f"`{probe.reference_selected_probability:.6%}` under the Transformers order and",
        f"`{probe.stage_03_selected_probability:.6%}` under the earlier order.",
        "",
        "| Witness | Token piece | ID | Green | Raw preference | Reference chance | "
        "Earlier-order chance | Saved choice |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for candidate in probe.candidates:
        lines.append(
            f"| {candidate.witness_role.replace('_', ' ')} | `{candidate.token_text}` | "
            f"{candidate.token_id} | "
            f"{'yes' if candidate.in_green_group else 'no'} | {candidate.raw_score:.6f} | "
            f"{candidate.reference_probability:.6%} | {candidate.stage_03_probability:.6%} | "
            f"{'yes' if candidate.selected_by_reference else 'no'} |"
        )
    lines.extend(
        [
            "",
            "Only the Transformers order produced the saved continuation. The earlier-order values",
            "are calculations on the same saved GPT-2 score list.",
            "",
            "## Six copied-continuation results",
            "",
            "| Prompt | Watermark | Tokens | Copied IDs | Generation key G/T | z | "
            "Comparison key G/T | z |",
            "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for record in trace.records:
        generation = record.detector_results[0]
        other_key = record.detector_results[2]
        lines.append(
            f"| `{record.prompt_id}` | "
            f"{'off' if record.condition == 'control' else 'on'} | "
            f"{len(record.generated_token_ids)} | "
            f"{'match' if record.copied_ids_match else 'differ'} | "
            f"{generation.num_green_tokens}/{generation.num_tokens_scored} | "
            f"{generation.z_score:.6f} | "
            f"{other_key.num_green_tokens}/{other_key.num_tokens_scored} | "
            f"{other_key.z_score:.6f} |"
        )
    first_piece = trace.repetition_fixture.token_pieces[0]
    second_piece = trace.repetition_fixture.token_pieces[1]
    explicit = trace.repetition_fixture.explicit_distinct_result
    lines.extend(
        [
            "",
            "## Detector boundaries",
            "",
            f"For the continuity reference row, the first copied token `{first_piece}` supplies",
            f"context. The second token `{second_piece}` is the first eligible decision. The",
            f"generation-key result is {_format_evidence(primary)}. The comparison-key result is",
            f"{_format_evidence(comparison)}.",
            "",
            "The derived alternating sequence has six tokens and five adjacent occurrences. ",
            f"The library's all-pairs mode gives {_format_evidence(repeat_all)}. Its documented ",
            f"unique-pair option also gives {_format_evidence(repeat_unique)} in this pinned run. ",
            f"Listing the two distinct value pairs explicitly gives {explicit.num_green_pairs}/",
            f"{explicit.num_distinct_pairs} | {explicit.z_score:.6f}. GPT-2 did not generate this ",
            "constructed sequence.",
            "",
            "The primary checker received no prompt or padding tokens.",
            "",
            "## Claim boundary",
            "",
            "These records verify one pinned local Transformers profile. Three prompts do not ",
            "measure detection accuracy or language quality. A score above the configured cutoff ",
            "means only",
            "consistent with this configured watermark and key. It does not prove AI origin,",
            "authorship, or use of a private vendor system.",
            "",
        ]
    )
    return "\n".join(lines).encode()


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be an object")
    return cast(Mapping[str, object], value)


def _keys(mapping: Mapping[str, object], expected: set[str], name: str) -> None:
    if set(mapping) != expected:
        raise ValueError(f"{name} keys differ")


def _array(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{name} must be an array")
    return cast(list[object], value)


def _evidence(value: object) -> DetectorEvidence:
    mapping = _mapping(value, "detector result")
    _keys(mapping, set(DetectorEvidence.__dataclass_fields__), "detector result")
    return DetectorEvidence(**cast(dict[str, Any], dict(mapping)))


def _candidate(value: object) -> OrderCandidate:
    mapping = _mapping(value, "order candidate")
    _keys(mapping, set(OrderCandidate.__dataclass_fields__), "order candidate")
    return OrderCandidate(**cast(dict[str, Any], dict(mapping)))


def _distinct(value: object) -> DistinctPairEvidence:
    mapping = _mapping(value, "distinct pair result")
    _keys(mapping, set(DistinctPairEvidence.__dataclass_fields__), "distinct pair result")
    return DistinctPairEvidence(**cast(dict[str, Any], dict(mapping)))


def trace_from_json_bytes(payload: bytes) -> Lab04Trace:
    """Load selected JSON through the same strict dataclass contracts."""

    raw: object = json.loads(payload.decode("utf-8"))
    root = _mapping(raw, "trace")
    _keys(root, set(Lab04Trace.__dataclass_fields__), "trace")
    config_raw = _mapping(root["config"], "config")
    prompts = tuple(
        ReferencePrompt(**cast(dict[str, Any], dict(_mapping(item, "prompt"))))
        for item in _array(config_raw["prompts"], "prompts")
    )
    config_values = dict(config_raw)
    config_values["prompts"] = prompts
    config_values["reference_processor_order"] = tuple(
        _array(config_values["reference_processor_order"], "reference_processor_order")
    )
    config_values["stage_03_processor_order"] = tuple(
        _array(config_values["stage_03_processor_order"], "stage_03_processor_order")
    )
    config = Lab04Config(**cast(dict[str, Any], config_values))

    records: list[ContinuationRecord] = []
    for item in _array(root["records"], "records"):
        values = dict(_mapping(item, "record"))
        values["prompt_token_ids"] = tuple(_array(values["prompt_token_ids"], "prompt_token_ids"))
        values["prompt_token_pieces"] = tuple(
            _array(values["prompt_token_pieces"], "prompt_token_pieces")
        )
        values["generated_token_ids"] = tuple(
            _array(values["generated_token_ids"], "generated_token_ids")
        )
        values["copied_token_ids"] = tuple(_array(values["copied_token_ids"], "copied_token_ids"))
        values["detector_results"] = tuple(
            _evidence(result) for result in _array(values["detector_results"], "detector_results")
        )
        records.append(ContinuationRecord(**cast(dict[str, Any], values)))

    probe_values = dict(_mapping(root["order_probe"], "order_probe"))
    probe_values["reference_order"] = tuple(
        _array(probe_values["reference_order"], "reference_order")
    )
    probe_values["stage_03_order"] = tuple(_array(probe_values["stage_03_order"], "stage_03_order"))
    probe_values["reference_counts"] = tuple(
        _array(probe_values["reference_counts"], "reference_counts")
    )
    probe_values["stage_03_counts"] = tuple(
        _array(probe_values["stage_03_counts"], "stage_03_counts")
    )
    probe_values["candidates"] = tuple(
        _candidate(item) for item in _array(probe_values["candidates"], "candidates")
    )
    order_probe = ProcessorOrderProbe(**cast(dict[str, Any], probe_values))

    repetition_values = dict(_mapping(root["repetition_fixture"], "repetition_fixture"))
    repetition_values["token_ids"] = tuple(
        _array(repetition_values["token_ids"], "repetition token_ids")
    )
    repetition_values["token_pieces"] = tuple(
        _array(repetition_values["token_pieces"], "repetition token_pieces")
    )
    repetition_values["detector_results"] = tuple(
        _evidence(item)
        for item in _array(repetition_values["detector_results"], "detector_results")
    )
    repetition_values["explicit_distinct_result"] = _distinct(
        repetition_values["explicit_distinct_result"]
    )
    repetition = RepetitionFixture(**cast(dict[str, Any], repetition_values))

    padding_values = dict(_mapping(root["padding_validation"], "padding_validation"))
    padding_values["entries"] = tuple(
        PaddingEntry(**cast(dict[str, Any], dict(_mapping(item, "padding entry"))))
        for item in _array(padding_values["entries"], "padding entries")
    )
    padding = PaddingValidation(**cast(dict[str, Any], padding_values))

    return Lab04Trace(
        schema_version=cast(Literal[1], root["schema_version"]),
        source_commit=cast(str, root["source_commit"]),
        config_sha256=cast(str, root["config_sha256"]),
        python_version=cast(str, root["python_version"]),
        platform=cast(str, root["platform"]),
        torch_version=cast(str, root["torch_version"]),
        transformers_version=cast(str, root["transformers_version"]),
        config=config,
        watermark_profile=_mapping(root["watermark_profile"], "watermark_profile"),
        records=tuple(records),
        order_probe=order_probe,
        repetition_fixture=repetition,
        padding_validation=padding,
    )
