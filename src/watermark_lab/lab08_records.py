"""Selected Stage 8 evidence construction and validation."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any, cast

from watermark_lab.lab08_config import Lab08Config
from watermark_lab.stats import exact_binomial_upper_tail, green_hit_z_score

ATTACK_LABELS = (
    "normalization",
    "homoglyph_1",
    "homoglyph_5",
    "deletion_10",
    "deletion_30",
    "mixing_25",
    "mixing_50",
    "paraphrase",
)
RAW_KEYS = {
    "schema_version",
    "source_commit",
    "config_sha256",
    "stage7_selected_sha256",
    "python_version",
    "torch_version",
    "transformers_version",
    "huggingface_hub_version",
    "modal_sdk_version",
    "model_revision",
    "model_class",
    "model_safetensors_bytes",
    "gpu_name",
    "cuda_runtime",
    "dtype",
    "total_vram_bytes",
    "model_download_ns",
    "model_load_ns",
    "runtime_ns",
    "secret_used",
    "volume_used",
    "generation_call_count",
    "generated_token_id_count",
    "rows",
}


def score_trace(tokens: Sequence[Mapping[str, Any]], config: Lab08Config) -> dict[str, Any]:
    """Validate one token trace and score its fixed copied prefix."""

    prefix = min(config.attack_prefix, len(tokens))
    green = 0
    eligible = 0
    for position, token in enumerate(tokens):
        if token.get("position") != position or not isinstance(token.get("token_id"), int):
            raise ValueError("Stage 8 token identity differs")
        expected_eligible = position >= config.context_width
        if token.get("eligible") is not expected_eligible:
            raise ValueError("Stage 8 token eligibility differs")
        if expected_eligible and not isinstance(token.get("is_green"), bool):
            raise ValueError("Stage 8 eligible token needs Boolean membership")
        if not expected_eligible and token.get("is_green") is not None:
            raise ValueError("Stage 8 unscored token cannot have membership")
        if position < prefix and expected_eligible:
            eligible += 1
            green += int(cast(bool, token["is_green"]))
    if prefix < config.attack_prefix:
        return {
            "status": "insufficient_copied_tokens",
            "copied_prefix": prefix,
            "num_green_tokens": green,
            "num_tokens_scored": eligible,
        }
    z = green_hit_z_score(hits=green, trials=eligible, null_probability=config.green_fraction)
    return {
        "status": "scored",
        "copied_prefix": prefix,
        "num_green_tokens": green,
        "num_tokens_scored": eligible,
        "green_fraction": green / eligible,
        "z_score": z,
        "exact_upper_tail": exact_binomial_upper_tail(
            hits=green, trials=eligible, null_probability=config.green_fraction
        ),
        "z_threshold": config.z_threshold,
        "prediction": z > config.z_threshold,
    }


def _mean(values: Sequence[float]) -> float | None:
    return math.fsum(values) / len(values) if values else None


def build_stage08_artifact(
    raw: Mapping[str, Any],
    stage7: Mapping[str, Any],
    manual_review: Mapping[str, Any],
    config: Lab08Config,
) -> dict[str, Any]:
    """Cross-check Stage 7 continuity and build compact measured summaries."""

    if set(raw) != RAW_KEYS or raw.get("schema_version") != 1:
        raise ValueError("Stage 8 raw schema differs")
    if (
        raw.get("stage7_selected_sha256") != config.stage7_selected_sha256
        or raw.get("model_revision") != config.model_revision
        or raw.get("gpu_name") != "NVIDIA L4"
        or raw.get("dtype") != "torch.bfloat16"
        or raw.get("secret_used") is not False
        or raw.get("volume_used") is not False
        or raw.get("generation_call_count") != config.max_generation_calls
    ):
        raise ValueError("Stage 8 resource or input identity differs")
    generated_count = raw.get("generated_token_id_count")
    if (
        not isinstance(generated_count, int)
        or not 0 < generated_count <= config.max_generated_token_ids
    ):
        raise ValueError("Stage 8 generated-token count differs")
    if (
        stage7.get("source_commit") != config.stage7_source_commit
        or stage7.get("config_sha256") != config.stage7_config_sha256
    ):
        raise ValueError("Stage 7 continuity identity differs")

    review_rows = cast(list[dict[str, Any]], manual_review.get("rows"))
    reviews = {row["selection_rank"]: row for row in review_rows}
    if (
        manual_review.get("status") != "complete"
        or manual_review.get("independent") is not False
        or set(reviews) != set(config.attack_selection_ranks)
        or any(row.get("decision") not in {"pass", "fail", "uncertain"} for row in review_rows)
    ):
        raise ValueError("Stage 8 manual review is incomplete or differs")

    stage7_rows = {row["selection_rank"]: row for row in stage7["selected_rows"]}
    raw_rows = cast(list[dict[str, Any]], raw["rows"])
    if [row["selection_rank"] for row in raw_rows] != list(config.attack_selection_ranks):
        raise ValueError("Stage 8 row order differs")
    selected_rows: list[dict[str, Any]] = []
    for raw_row in raw_rows:
        rank = cast(int, raw_row["selection_rank"])
        inherited = cast(dict[str, Any], stage7_rows[rank])
        inherited_marked = cast(dict[str, Any], inherited["conditions"]["watermarked"])
        inherited_text = cast(str, inherited_marked["copied_text"])
        if raw_row["stage7_text_sha256"] != hashlib.sha256(inherited_text.encode()).hexdigest():
            raise ValueError("Stage 8 inherited text differs")
        attacks = cast(dict[str, dict[str, Any]], raw_row["attacks"])
        if set(attacks) != set(ATTACK_LABELS):
            raise ValueError("Stage 8 attack labels differ")
        baseline = cast(dict[str, Any], inherited["prefix_scores"])[str(config.attack_prefix)][
            "watermarked_correct"
        ]
        attack_records: dict[str, Any] = {}
        for label in ATTACK_LABELS:
            attack = attacks[label]
            score = score_trace(cast(list[dict[str, Any]], attack["token_evidence"]), config)
            if attack["copied_token_count"] != len(attack["copied_token_ids"]):
                raise ValueError("Stage 8 attack copied length differs")
            record = {
                "label": label,
                "text": attack["text"] if label != "paraphrase" else attack["copied_text"],
                "copied_token_count": attack["copied_token_count"],
                "length_ratio": attack["length_ratio"],
                "score": score,
                "z_change": (
                    score["z_score"] - baseline["z_score"] if score["status"] == "scored" else None
                ),
            }
            if label == "paraphrase":
                record.update(
                    {
                        "embedding_cosine": attack["embedding_cosine"],
                        "numbers_preserved": attack["numbers_preserved"],
                        "automatic_preservation_pass": attack["automatic_preservation_pass"],
                        "manual_review": reviews[rank],
                        "meaning_preservation_pass": bool(
                            attack["automatic_preservation_pass"]
                            and reviews[rank]["decision"] == "pass"
                        ),
                        "stop_reason": attack["stop_reason"],
                        "generation_wall_ns": attack["generation_wall_ns"],
                        "prompt": attack["prompt"],
                    }
                )
            else:
                record["operations"] = attack["operations"]
            attack_records[label] = record

        bias_records: dict[str, Any] | None = None
        if rank in config.bias_selection_ranks:
            bias_records = {}
            raw_biases = cast(dict[str, dict[str, Any]], raw_row["bias_generations"])
            for bias in config.bias_values:
                label = str(int(bias))
                generation = raw_biases[label]
                trace = cast(list[dict[str, Any]], generation["token_evidence"])
                score = (
                    score_trace(trace, config)
                    if trace
                    else {
                        "status": "insufficient_copied_tokens",
                        "copied_prefix": generation["copied_token_count"],
                        "num_green_tokens": 0,
                        "num_tokens_scored": max(0, generation["copied_token_count"] - 1),
                    }
                )
                bias_records[label] = {
                    "bias": bias,
                    "copied_text": generation["copied_text"],
                    "copied_token_count": generation["copied_token_count"],
                    "generated_token_count": generation["generated_token_count"],
                    "stop_reason": generation["stop_reason"],
                    "generation_wall_ns": generation["generation_wall_ns"],
                    "conditional_nll": generation["conditional_nll"],
                    "repeated_pair_fraction": generation["repeated_pair_fraction"],
                    "distinct_2_fraction": generation["distinct_2_fraction"],
                    "distinct_3_fraction": generation["distinct_3_fraction"],
                    "source_embedding_cosine": generation["source_embedding_cosine"],
                    "reused_stage7": generation["reused_stage7"],
                    "score": score,
                }
        selected_rows.append(
            {
                "selection_rank": rank,
                "text_sha256": inherited["text_sha256"],
                "stage7_seed": inherited["seed"],
                "source_prompt_text": inherited["source_prompt_text"],
                "original_text": inherited_text,
                "original_copied_token_count": inherited_marked["copied_token_count"],
                "baseline_score": baseline,
                "attacks": attack_records,
                "bias_generations": bias_records,
                "spine_token_evidence": {
                    label: attacks[label]["token_evidence"]
                    for label in ("deletion_10", "paraphrase")
                }
                if rank == 1000
                else None,
            }
        )

    attack_summary: dict[str, Any] = {}
    for label in ATTACK_LABELS:
        records = [row["attacks"][label] for row in selected_rows]
        changes = [record["z_change"] for record in records if record["z_change"] is not None]
        attack_summary[label] = {
            "rows": len(records),
            "scored_rows": len(changes),
            "mean_z_change": _mean(cast(list[float], changes)),
            "cutoff_crossings": sum(record["score"].get("prediction", False) for record in records),
            "mean_length_ratio": _mean([record["length_ratio"] for record in records]),
            "automatic_preservation_passes": (
                sum(record["automatic_preservation_pass"] for record in records)
                if label == "paraphrase"
                else None
            ),
            "manual_passes": (
                sum(record["manual_review"]["decision"] == "pass" for record in records)
                if label == "paraphrase"
                else None
            ),
            "meaning_preservation_passes": (
                sum(record["meaning_preservation_pass"] for record in records)
                if label == "paraphrase"
                else None
            ),
        }

    bias_summary: dict[str, Any] = {}
    bias_rows = [row for row in selected_rows if row["bias_generations"] is not None]
    for bias in config.bias_values:
        label = str(int(bias))
        records = [row["bias_generations"][label] for row in bias_rows]
        scored = [record for record in records if record["score"]["status"] == "scored"]
        bias_summary[label] = {
            "rows": len(records),
            "scored_rows": len(scored),
            "mean_z": _mean([record["score"]["z_score"] for record in scored]),
            "cutoff_crossings": sum(record["score"].get("prediction", False) for record in records),
            "mean_nll": _mean(
                [
                    record["conditional_nll"]
                    for record in records
                    if record["conditional_nll"] is not None
                ]
            ),
            "mean_repeated_pair_fraction": _mean(
                [
                    record["repeated_pair_fraction"]
                    for record in records
                    if record["repeated_pair_fraction"] is not None
                ]
            ),
            "mean_copied_tokens": _mean([record["copied_token_count"] for record in records]),
        }

    return {
        **dict(raw),
        "config": {
            "attack_selection_ranks": list(config.attack_selection_ranks),
            "bias_selection_ranks": list(config.bias_selection_ranks),
            "attack_prefix": config.attack_prefix,
            "bias_values": list(config.bias_values),
            "green_fraction": config.green_fraction,
            "generation_key": config.generation_key,
            "z_threshold": config.z_threshold,
            "similarity_threshold": config.similarity_threshold,
            "length_ratio_bounds": [config.min_length_ratio, config.max_length_ratio],
        },
        "selected_rows": selected_rows,
        "attack_summary": attack_summary,
        "bias_summary": bias_summary,
        "teaching_selection": {
            "spine_selection_rank": 1000,
            "inconvenient_selection_rank": 1001,
            "spine_attack": "deletion_10",
        },
        "interpretation": {
            "positive": "Consistent with this configured watermark and key.",
            "scope": (
                "This is one pinned 12-row editing fixture and 8-row bias sweep. It does not "
                "establish universal robustness, human quality, authorship, or generic AI origin."
            ),
        },
    }


def stage08_json_bytes(artifact: Mapping[str, Any]) -> bytes:
    return (json.dumps(artifact, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def stage08_markdown_bytes(artifact: Mapping[str, Any]) -> bytes:
    lines = [
        "# Stage 8 editing and bias trade-offs",
        "",
        "## Editing summary",
        "",
        "| Edit | Rows | Scored | Mean z change | Cutoff crossings | Mean length ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, summary in cast(dict[str, Any], artifact["attack_summary"]).items():
        mean_change = summary["mean_z_change"]
        lines.append(
            f"| `{label}` | {summary['rows']} | {summary['scored_rows']} | "
            f"{mean_change:.4f} | {summary['cutoff_crossings']} | "
            f"{summary['mean_length_ratio']:.4f} |"
        )
    lines += [
        "",
        "## Bias summary",
        "",
        "| Delta | Rows | Scored | Mean z | Cutoff crossings | Mean NLL | Mean copied tokens |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, summary in cast(dict[str, Any], artifact["bias_summary"]).items():
        lines.append(
            f"| {label} | {summary['rows']} | {summary['scored_rows']} | "
            f"{summary['mean_z']:.4f} | {summary['cutoff_crossings']} | "
            f"{summary['mean_nll']:.4f} | {summary['mean_copied_tokens']:.1f} |"
        )
    lines += ["", artifact["interpretation"]["scope"], ""]
    return "\n".join(lines).encode()
