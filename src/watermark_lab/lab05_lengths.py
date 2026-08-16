"""Validation and rendering for Stage 5 natural-length evidence."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any, cast

from watermark_lab.lab05_lengths_config import Lab05LengthsConfig
from watermark_lab.stats import green_hit_z_score

DERIVED_KEYS = {"config", "pairs", "summary", "interpretation"}


def build_lengths_trace(raw: Mapping[str, Any], config: Lab05LengthsConfig) -> dict[str, Any]:
    records_value = raw.get("records")
    if not isinstance(records_value, list):
        raise ValueError("length ladder records must be a list")
    records = cast(list[dict[str, Any]], records_value)
    if len(records) != 24:
        raise ValueError("length ladder requires exactly twenty-four records")
    expected = [
        (prompt.id, prompt.max_new_tokens, condition)
        for prompt in config.prompts
        for condition in ("control", "reference_watermark")
    ]
    if [
        (row.get("prompt_id"), row.get("max_new_tokens"), row.get("condition")) for row in records
    ] != expected:
        raise ValueError("length record prompt, cap, or condition order differs")
    if raw.get("gpu_name") != "NVIDIA L4" or raw.get("dtype") != "torch.bfloat16":
        raise ValueError("length ladder GPU or dtype differs")
    if raw.get("secret_used") is not False or raw.get("volume_used") is not False:
        raise ValueError("length ladder must use neither Secret nor Volume")
    if not isinstance(raw.get("source_commit"), str) or len(raw["source_commit"]) != 40:
        raise ValueError("source_commit must be a full Git SHA")
    if not isinstance(raw.get("config_sha256"), str) or len(raw["config_sha256"]) != 64:
        raise ValueError("config_sha256 must be full SHA-256")

    pairs: list[dict[str, Any]] = []
    for index, prompt in enumerate(config.prompts):
        pair: dict[str, Any] = {
            "prompt_id": prompt.id,
            "prompt_text": prompt.text,
            "max_new_tokens": prompt.max_new_tokens,
        }
        control, watermarked = records[index * 2 : index * 2 + 2]
        if control["seed"] != watermarked["seed"] or control["seed"] != config.prompt_seed(
            prompt.id
        ):
            raise ValueError("length paired seeds differ")
        for label, row in (("control", control), ("watermarked", watermarked)):
            copied_ids = cast(list[int], row["copied_token_ids"])
            tokens = cast(list[dict[str, Any]], row["token_evidence"])
            if len(tokens) != len(copied_ids):
                raise ValueError("token evidence length differs from copied IDs")
            for position, (token_id, token) in enumerate(zip(copied_ids, tokens, strict=True)):
                expected_eligible = position >= config.context_width
                if (
                    token.get("position") != position
                    or token.get("token_id") != token_id
                    or token.get("eligible") is not expected_eligible
                    or (not expected_eligible and token.get("is_green") is not None)
                    or (expected_eligible and not isinstance(token.get("is_green"), bool))
                ):
                    raise ValueError("token evidence identity or eligibility differs")
            evidence = cast(dict[str, Any], row["evidence"])
            scored = sum(token["eligible"] for token in tokens)
            green = sum(token["is_green"] is True for token in tokens)
            if (scored, green) != (
                evidence["num_tokens_scored"],
                evidence["num_green_tokens"],
            ):
                raise ValueError("token colors differ from detector totals")
            independent = green_hit_z_score(
                hits=green, trials=scored, null_probability=config.green_fraction
            )
            if not math.isclose(evidence["z_score"], independent, abs_tol=1e-10):
                raise ValueError("length z score differs from Stage 1")
            if not 0 <= evidence["p_value"] <= 1:
                raise ValueError("length p-value is outside zero and one")
            if evidence["prediction"] != (evidence["z_score"] > config.z_threshold):
                raise ValueError("length decision differs from strict cutoff")
            pair[label] = {
                "copied_text": row["copied_text"],
                "copied_token_ids": copied_ids,
                "achieved_copied_tokens": len(copied_ids),
                "generated_token_count": len(row["generated_token_ids"]),
                "stop_reason": row["stop_reason"],
                "evidence": evidence,
                "token_evidence": tokens,
            }
        pairs.append(pair)

    watermarked = [cast(dict[str, Any], pair["watermarked"]) for pair in pairs]
    summary = {
        "positive_control_rows": sum(pair["control"]["evidence"]["prediction"] for pair in pairs),
        "positive_watermarked_rows": sum(row["evidence"]["prediction"] for row in watermarked),
        "max_control_z": max(pair["control"]["evidence"]["z_score"] for pair in pairs),
        "max_watermarked_z": max(row["evidence"]["z_score"] for row in watermarked),
        "minimum_achieved_copied_tokens": min(
            min(
                pair["control"]["achieved_copied_tokens"],
                pair["watermarked"]["achieved_copied_tokens"],
            )
            for pair in pairs
        ),
        "maximum_achieved_copied_tokens": max(
            max(
                pair["control"]["achieved_copied_tokens"],
                pair["watermarked"]["achieved_copied_tokens"],
            )
            for pair in pairs
        ),
    }
    return {
        **dict(raw),
        "config": {
            "model_id": config.model_id,
            "model_revision": config.model_revision,
            "green_fraction": config.green_fraction,
            "watermark_bias": config.watermark_bias,
            "generation_key": config.generation_key,
            "temperature": config.temperature,
            "top_k": config.top_k,
            "top_p": config.top_p,
            "context_width": config.context_width,
            "z_threshold": config.z_threshold,
            "prompts": [
                {"id": prompt.id, "text": prompt.text, "max_new_tokens": prompt.max_new_tokens}
                for prompt in config.prompts
            ],
        },
        "pairs": pairs,
        "summary": summary,
        "interpretation": {
            "green": (
                "Eligible copied token is green for the public generation key and prior token."
            ),
            "red": "Eligible copied token is outside that keyed green set.",
            "unscored": "First copied token supplies context and is not scored.",
            "p_value": (
                "Probability under the configured no-watermark baseline of evidence at least this "
                "extreme; not the probability that the text is watermarked."
            ),
            "scope": (
                "Twelve varied prompts show natural achieved lengths. They do not isolate a causal "
                "length effect or estimate detector accuracy."
            ),
        },
    }


def lengths_to_json_bytes(trace: Mapping[str, Any]) -> bytes:
    return (json.dumps(trace, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def lengths_to_markdown_bytes(trace: Mapping[str, Any]) -> bytes:
    pairs = cast(list[dict[str, Any]], trace["pairs"])
    lines = [
        "# Stage 5 natural-length evidence ladder",
        "",
        "Normal end-token behavior remained active. Caps are safety limits, not achieved lengths.",
        "",
        "| Prompt | Cap | Condition | Achieved copied tokens | Stop | G/T | z | p-value | z > 3 |",
        "| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for pair in pairs:
        for condition in ("control", "watermarked"):
            row = pair[condition]
            evidence = row["evidence"]
            lines.append(
                f"| `{pair['prompt_id']}` | {pair['max_new_tokens']} | {condition} | "
                f"{row['achieved_copied_tokens']} | {row['stop_reason']} | "
                f"{evidence['num_green_tokens']}/{evidence['num_tokens_scored']} | "
                f"{evidence['z_score']:.4f} | {evidence['p_value']:.6f} | "
                f"{'yes' if evidence['prediction'] else 'no'} |"
            )
    lines += [
        "",
        "Green and red token pieces are stored in `lengths.json`. Green means keyed membership,",
        "not semantic quality. The first copied token is unscored context.",
        "",
        trace["interpretation"]["p_value"],
        "",
        trace["interpretation"]["scope"],
        "",
    ]
    return "\n".join(lines).encode()
