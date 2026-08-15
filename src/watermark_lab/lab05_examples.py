"""Selected ten-pair Stage 5 implementation-demonstration evidence."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any, cast

from watermark_lab.lab05_config import Lab05Config
from watermark_lab.stats import green_hit_z_score

DERIVED_KEYS = {"config", "pairs", "interpretation"}


def _primary(row: Mapping[str, Any]) -> Mapping[str, Any]:
    results = row.get("detector_results")
    if not isinstance(results, list):
        raise ValueError("each example needs four detector results")
    typed_results = cast(list[Mapping[str, Any]], results)
    if len(typed_results) != 4:
        raise ValueError("each example needs four detector results")
    result = typed_results[0]
    if (result.get("key_role"), result.get("repetition_policy")) != ("generation", "all"):
        raise ValueError("primary example result must use generation key and all occurrences")
    return result


def build_examples_trace(raw: Mapping[str, Any], config: Lab05Config) -> dict[str, Any]:
    """Validate exactly ten control/watermarked pairs and create a compact comparison."""

    if config.max_generation_calls != 20 or len(config.prompts) != 10:
        raise ValueError("examples mode requires exactly ten prompts and twenty calls")
    records_value = raw.get("records")
    if not isinstance(records_value, list):
        raise ValueError("examples mode requires exactly twenty generation records")
    records = cast(list[dict[str, Any]], records_value)
    if len(records) != 20:
        raise ValueError("examples mode requires exactly twenty generation records")
    expected = [
        (prompt.id, condition)
        for prompt in config.prompts
        for condition in ("control", "reference_watermark")
    ]
    if [(row.get("prompt_id"), row.get("condition")) for row in records] != expected:
        raise ValueError("example record order differs from the frozen paired contract")
    if raw.get("gpu_name") != "NVIDIA L4" or raw.get("dtype") != "torch.bfloat16":
        raise ValueError("example GPU or dtype differs from the contract")
    if raw.get("secret_used") is not False or raw.get("volume_used") is not False:
        raise ValueError("examples must use neither Secret nor Volume")
    if not isinstance(raw.get("source_commit"), str) or len(raw["source_commit"]) != 40:
        raise ValueError("source_commit must be a full Git SHA")
    if not isinstance(raw.get("config_sha256"), str) or len(raw["config_sha256"]) != 64:
        raise ValueError("config_sha256 must be a full SHA-256")

    pairs: list[dict[str, Any]] = []
    for index, prompt in enumerate(config.prompts):
        control, watermarked = records[index * 2 : index * 2 + 2]
        if control["seed"] != watermarked["seed"] or control["seed"] != config.prompt_seed(
            prompt.id
        ):
            raise ValueError("paired example seeds differ")
        output_pair: dict[str, Any] = {"prompt_id": prompt.id, "prompt_text": prompt.text}
        for name, row in (("control", control), ("watermarked", watermarked)):
            if row.get("prompt_text") != prompt.text or not row.get("copied_text"):
                raise ValueError("example prompt identity or copied text differs")
            primary = _primary(row)
            green = int(primary["num_green_tokens"])
            scored = int(primary["num_tokens_scored"])
            z_score = float(primary["z_score"])
            independent = green_hit_z_score(
                hits=green,
                trials=scored,
                null_probability=config.green_fraction,
            )
            if not math.isclose(z_score, independent, rel_tol=0.0, abs_tol=1e-10):
                raise ValueError("example z score differs from the Stage 1 formula")
            p_value = float(primary["p_value"])
            if not 0.0 <= p_value <= 1.0:
                raise ValueError("example p-value must be between zero and one")
            prediction = bool(primary["prediction"])
            if prediction != (z_score > config.z_threshold):
                raise ValueError("example decision must use the strict configured cutoff")
            output_pair[name] = {
                "text": row["copied_text"],
                "generated_token_count": len(row["generated_token_ids"]),
                "copied_token_count": len(row["copied_token_ids"]),
                "num_tokens_scored": scored,
                "num_green_tokens": green,
                "z_score": z_score,
                "p_value": p_value,
                "prediction": prediction,
            }
        pairs.append(output_pair)

    return {
        **dict(raw),
        "config": {
            "model_id": config.model_id,
            "model_revision": config.model_revision,
            "max_generation_calls": config.max_generation_calls,
            "temperature": config.temperature,
            "top_k": config.top_k,
            "top_p": config.top_p,
            "green_fraction": config.green_fraction,
            "watermark_bias": config.watermark_bias,
            "generation_key": config.generation_key,
            "seeding_scheme": config.seeding_scheme,
            "context_width": config.context_width,
            "z_threshold": config.z_threshold,
            "prompts": [{"id": prompt.id, "text": prompt.text} for prompt in config.prompts],
        },
        "pairs": pairs,
        "interpretation": {
            "p_value": (
                "Probability under the configured no-watermark baseline of evidence at least this "
                "extreme; not the probability that the text is watermarked."
            ),
            "positive_result": "Consistent with this configured watermark and key.",
            "scope": (
                "Ten paired prompts demonstrate the implementation and do not estimate detector "
                "accuracy, a false-alarm rate, quality preservation, or a production threshold."
            ),
        },
    }


def examples_to_json_bytes(trace: Mapping[str, Any]) -> bytes:
    return (json.dumps(trace, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def examples_to_markdown_bytes(trace: Mapping[str, Any]) -> bytes:
    pairs = cast(list[dict[str, Any]], trace["pairs"])
    lines = [
        "# Stage 5 ten-pair Gemma implementation demonstration",
        "",
        "Each prompt used the same seed for control and watermarked generation. The table uses the",
        "generation key and all eligible token occurrences.",
        "",
        "| Prompt | Condition | Copied tokens | G/T | z | p-value | z > 3 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for pair in pairs:
        for condition in ("control", "watermarked"):
            row = pair[condition]
            lines.append(
                f"| `{pair['prompt_id']}` | {condition} | {row['copied_token_count']} | "
                f"{row['num_green_tokens']}/{row['num_tokens_scored']} | "
                f"{row['z_score']:.4f} | {row['p_value']:.6f} | "
                f"{'yes' if row['prediction'] else 'no'} |"
            )
    lines += [
        "",
        "## Copied continuations",
        "",
    ]
    for pair in pairs:
        lines += [
            f"### {pair['prompt_id']}",
            "",
            f"Prompt: {pair['prompt_text']}",
            "",
            f"Control: {pair['control']['text']}",
            "",
            f"Watermarked: {pair['watermarked']['text']}",
            "",
        ]
    lines += [
        "## Interpretation",
        "",
        trace["interpretation"]["p_value"],
        "",
        trace["interpretation"]["scope"],
        "",
    ]
    return "\n".join(lines).encode()
