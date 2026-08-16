"""Validation and selected-artifact rendering for Stage 7."""

from __future__ import annotations

import json
import math
import random
from collections.abc import Mapping, Sequence
from typing import Any, cast

from watermark_lab.lab07_config import Lab07Config
from watermark_lab.stats import exact_binomial_upper_tail, green_hit_z_score

SCORE_FAMILIES = (
    "watermarked_correct",
    "control_correct",
    "natural_correct",
    "watermarked_comparison",
)
COMPARISONS = {
    "versus_control": "control_correct",
    "versus_natural": "natural_correct",
    "versus_comparison_key": "watermarked_comparison",
}
RAW_KEYS = {
    "schema_version",
    "source_commit",
    "config_sha256",
    "manifest_sha256",
    "python_version",
    "torch_version",
    "transformers_version",
    "huggingface_hub_version",
    "modal_sdk_version",
    "model_revision",
    "model_class",
    "model_safetensors_bytes",
    "dataset_file_sha256",
    "dataset_file_bytes",
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


def score_record(*, hits: int, trials: int, config: Lab07Config) -> dict[str, Any]:
    z = green_hit_z_score(hits=hits, trials=trials, null_probability=config.green_fraction)
    return {
        "num_green_tokens": hits,
        "num_tokens_scored": trials,
        "green_fraction": hits / trials,
        "z_score": z,
        "exact_upper_tail": exact_binomial_upper_tail(
            hits=hits, trials=trials, null_probability=config.green_fraction
        ),
        "z_threshold": config.z_threshold,
        "prediction": z > config.z_threshold,
    }


def _validate_tokens(tokens: Sequence[Mapping[str, Any]], config: Lab07Config) -> tuple[int, int]:
    if len(tokens) < 2:
        raise ValueError("Stage 7 token evidence needs at least two tokens")
    green = 0
    eligible = 0
    for position, token in enumerate(tokens):
        if (
            token.get("position") != position
            or not isinstance(token.get("token_id"), int)
            or not isinstance(token.get("piece"), str)
        ):
            raise ValueError("Stage 7 token identity differs")
        expected_eligible = position >= config.context_width
        if token.get("eligible") is not expected_eligible:
            raise ValueError("Stage 7 token eligibility differs")
        if expected_eligible:
            if not isinstance(token.get("is_green"), bool):
                raise ValueError("eligible Stage 7 token needs a Boolean membership")
            eligible += 1
            green += int(cast(bool, token["is_green"]))
        elif token.get("is_green") is not None:
            raise ValueError("unscored Stage 7 token cannot have membership")
    return green, eligible


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[round(q * (len(ordered) - 1))]


def bootstrap_interval(
    differences: Sequence[float], *, replicates: int, seed: int
) -> tuple[float, float]:
    if not differences:
        raise ValueError("paired bootstrap needs at least one row")
    generator = random.Random(seed)
    count = len(differences)
    means = [
        math.fsum(differences[generator.randrange(count)] for _ in range(count)) / count
        for _ in range(replicates)
    ]
    return _quantile(means, 0.025), _quantile(means, 0.975)


def choose_inconvenient_row(rows: Sequence[Mapping[str, Any]]) -> tuple[int, str, int]:
    candidates: list[tuple[int, int, Mapping[str, Any]]] = []
    for index, row in enumerate(rows):
        prefixes = cast(Mapping[str, Any], row["prefix_scores"])
        supported = sorted(int(prefix) for prefix in prefixes)
        if supported:
            candidates.append((index, supported[-1], row))
    for index, prefix, row in candidates:
        scores = cast(Mapping[str, Any], row["prefix_scores"])[str(prefix)]
        if scores["watermarked_correct"]["z_score"] <= scores["control_correct"]["z_score"]:
            return index, "watermarked_not_above_control", prefix
    for index, prefix, row in candidates:
        scores = cast(Mapping[str, Any], row["prefix_scores"])[str(prefix)]
        if scores["watermarked_comparison"]["z_score"] >= scores["watermarked_correct"]["z_score"]:
            return index, "comparison_key_not_below_correct_key", prefix
    for index, prefix, row in candidates:
        scores = cast(Mapping[str, Any], row["prefix_scores"])[str(prefix)]
        if scores["control_correct"]["prediction"] or scores["natural_correct"]["prediction"]:
            return index, "negative_control_crossed_cutoff", prefix
    if not candidates:
        raise ValueError("no Stage 7 row supports a shared generated prefix")
    index, prefix, _ = min(
        candidates,
        key=lambda item: (
            cast(Mapping[str, Any], item[2]["prefix_scores"])[str(item[1])]["watermarked_correct"][
                "z_score"
            ]
            - max(
                cast(Mapping[str, Any], item[2]["prefix_scores"])[str(item[1])][family]["z_score"]
                for family in (
                    "control_correct",
                    "natural_correct",
                    "watermarked_comparison",
                )
            ),
            cast(int, item[2]["selection_rank"]),
        ),
    )
    return index, "smallest_separation_margin", prefix


def build_stage07_artifact(raw: Mapping[str, Any], config: Lab07Config) -> dict[str, Any]:
    if set(raw) != RAW_KEYS or raw.get("schema_version") != 1:
        raise ValueError("Stage 7 raw schema differs from the exact contract")
    if (
        raw.get("gpu_name") != "NVIDIA L4"
        or raw.get("dtype") != "torch.bfloat16"
        or raw.get("secret_used") is not False
        or raw.get("volume_used") is not False
    ):
        raise ValueError("Stage 7 resource identity differs")
    if raw.get("manifest_sha256") != config.manifest_sha256:
        raise ValueError("Stage 7 manifest hash differs")
    if raw.get("dataset_file_sha256") != config.dataset_file_sha256:
        raise ValueError("Stage 7 dataset hash differs")
    if raw.get("model_revision") != config.model_revision:
        raise ValueError("Stage 7 model revision differs")
    if raw.get("generation_call_count") != config.max_generation_calls:
        raise ValueError("Stage 7 generation call count differs")
    generated_count = raw.get("generated_token_id_count")
    if (
        not isinstance(generated_count, int)
        or not 0 < generated_count <= config.max_generated_token_ids
    ):
        raise ValueError("Stage 7 generated-token count exceeds the contract")

    raw_rows = cast(list[dict[str, Any]], raw.get("rows"))
    if len(raw_rows) != config.paired_rows:
        raise ValueError("Stage 7 requires exactly 24 rows")
    selected_rows: list[dict[str, Any]] = []
    for index, row in enumerate(raw_rows):
        selection_rank = 1000 + index
        if row.get("selection_rank") != selection_rank:
            raise ValueError("Stage 7 row order differs from the frozen manifest")
        text_hash = row.get("text_sha256")
        if not isinstance(text_hash, str) or len(text_hash) != 64:
            raise ValueError("Stage 7 source hash differs")
        if row.get("seed") != config.prompt_seed(selection_rank, text_hash):
            raise ValueError("Stage 7 paired seed differs")
        prompt_ids = cast(list[int], row.get("source_prompt_token_ids"))
        if len(prompt_ids) != config.prompt_tokens or row.get("prompt_roundtrip_ok") is not True:
            raise ValueError("Stage 7 prompt identity differs")
        natural_ids = cast(list[int], row.get("natural_continuation_token_ids"))
        if len(natural_ids) != config.natural_continuation_tokens:
            raise ValueError("Stage 7 natural continuation length differs")
        conditions = cast(dict[str, dict[str, Any]], row.get("conditions"))
        if set(conditions) != {"control", "watermarked"}:
            raise ValueError("Stage 7 conditions differ")
        for condition, record in conditions.items():
            if record.get("condition") != condition or not isinstance(
                record.get("copied_text"), str
            ):
                raise ValueError("Stage 7 condition record differs")
            copied_ids = cast(list[int], record.get("copied_token_ids"))
            if len(copied_ids) != record.get("copied_token_count"):
                raise ValueError("Stage 7 copied length differs")
            if len(copied_ids) < 2 and record.get("status") != "insufficient_copied_tokens":
                raise ValueError("short Stage 7 copied text needs explicit status")
            if len(copied_ids) >= 2 and record.get("status") != "ok":
                raise ValueError("scorable Stage 7 copied text needs ok status")

        prefix_scores: dict[str, Any] = {}
        control_ids = cast(list[int], conditions["control"]["copied_token_ids"])
        watermarked_ids = cast(list[int], conditions["watermarked"]["copied_token_ids"])
        token_evidence = cast(dict[str, list[dict[str, Any]]], row["token_evidence"])
        if set(token_evidence) != {
            "control_correct",
            "natural_correct",
            "watermarked_correct",
            "watermarked_comparison",
        }:
            raise ValueError("Stage 7 token evidence families differ")
        expected_lengths = {
            "control_correct": len(control_ids),
            "natural_correct": len(natural_ids),
            "watermarked_correct": len(watermarked_ids),
            "watermarked_comparison": len(watermarked_ids),
        }
        for family, tokens in token_evidence.items():
            if len(tokens) != expected_lengths[family]:
                raise ValueError("Stage 7 token trace length differs")
            _validate_tokens(tokens, config)

        for prefix in config.prefixes:
            if len(control_ids) < prefix or len(watermarked_ids) < prefix:
                continue
            family_scores: dict[str, Any] = {}
            for family in SCORE_FAMILIES:
                all_tokens = token_evidence[family][:prefix]
                all_hits, all_trials = _validate_tokens(all_tokens, config)
                seen: set[tuple[int, int]] = set()
                distinct_hits = 0
                for position in range(config.context_width, len(all_tokens)):
                    pair = (
                        cast(int, all_tokens[position - 1]["token_id"]),
                        cast(int, all_tokens[position]["token_id"]),
                    )
                    if pair not in seen:
                        seen.add(pair)
                        distinct_hits += int(cast(bool, all_tokens[position]["is_green"]))
                all_score = score_record(hits=all_hits, trials=all_trials, config=config)
                distinct_score = score_record(hits=distinct_hits, trials=len(seen), config=config)
                family_scores[family] = {**all_score, "distinct_pairs": distinct_score}
            prefix_scores[str(prefix)] = family_scores
        selected_rows.append(
            {
                "selection_rank": selection_rank,
                "dataset_row_index": row["dataset_row_index"],
                "url": row["url"],
                "timestamp": row["timestamp"],
                "text_sha256": text_hash,
                "seed": row["seed"],
                "source_prompt_text": row["source_prompt_text"],
                "source_prompt_token_ids": prompt_ids,
                "natural_continuation_token_ids": natural_ids,
                "conditions": conditions,
                "prefix_scores": prefix_scores,
                "token_evidence": token_evidence if index == 0 else None,
            }
        )

    summaries: dict[str, Any] = {}
    for prefix in config.prefixes:
        complete = [row for row in selected_rows if str(prefix) in row["prefix_scores"]]
        prefix_summary: dict[str, Any] = {
            "complete_rows": len(complete),
            "cutoff_counts": {
                family: sum(
                    row["prefix_scores"][str(prefix)][family]["prediction"] for row in complete
                )
                for family in SCORE_FAMILIES
            },
            "comparisons": {},
        }
        for comparison, control_family in COMPARISONS.items():
            differences = [
                row["prefix_scores"][str(prefix)]["watermarked_correct"]["z_score"]
                - row["prefix_scores"][str(prefix)][control_family]["z_score"]
                for row in complete
            ]
            if differences:
                seed = config.bootstrap_seed(prefix, comparison)
                low, high = bootstrap_interval(
                    differences, replicates=config.bootstrap_replicates, seed=seed
                )
                prefix_summary["comparisons"][comparison] = {
                    "row_differences": differences,
                    "mean_difference": math.fsum(differences) / len(differences),
                    "bootstrap_seed": seed,
                    "bootstrap_replicates": config.bootstrap_replicates,
                    "interval_low": low,
                    "interval_high": high,
                }
        summaries[str(prefix)] = prefix_summary

    inconvenient_index, inconvenient_reason, inconvenient_prefix = choose_inconvenient_row(
        selected_rows
    )
    return {
        **dict(raw),
        "config": {
            "base_seed": config.base_seed,
            "model_id": config.model_id,
            "model_revision": config.model_revision,
            "prefixes": list(config.prefixes),
            "temperature": config.temperature,
            "top_k": config.top_k,
            "top_p": config.top_p,
            "green_fraction": config.green_fraction,
            "watermark_bias": config.watermark_bias,
            "generation_key": config.generation_key,
            "comparison_key": config.comparison_key,
            "context_width": config.context_width,
            "z_threshold": config.z_threshold,
            "max_new_tokens": config.max_new_tokens,
        },
        "selected_rows": selected_rows,
        "prefix_summary": summaries,
        "teaching_selection": {
            "spine_selection_rank": 1000,
            "inconvenient_selection_rank": selected_rows[inconvenient_index]["selection_rank"],
            "inconvenient_reason": inconvenient_reason,
            "inconvenient_prefix": inconvenient_prefix,
        },
        "interpretation": {
            "positive": "Consistent with this configured watermark and key.",
            "scope": (
                "This is one pinned 24-row C4 and Gemma experiment. It does not estimate "
                "production accuracy, prove authorship, or detect arbitrary AI text."
            ),
        },
    }


def stage07_json_bytes(artifact: Mapping[str, Any]) -> bytes:
    return (json.dumps(artifact, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def stage07_markdown_bytes(artifact: Mapping[str, Any]) -> bytes:
    lines = [
        "# Stage 7 paired core experiment",
        "",
        (
            "All 24 prompts were frozen during Stage 6. Each generated pair shared one prompt "
            "and seed."
        ),
        "",
        (
            "| Prefix | Complete rows | Marked correct | Model control | Natural web | "
            "Comparison key |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for prefix, summary in cast(dict[str, Any], artifact["prefix_summary"]).items():
        counts = summary["cutoff_counts"]
        lines.append(
            f"| {prefix} | {summary['complete_rows']} | {counts['watermarked_correct']} | "
            f"{counts['control_correct']} | {counts['natural_correct']} | "
            f"{counts['watermarked_comparison']} |"
        )
    lines += ["", "## Paired z differences", ""]
    for prefix, summary in cast(dict[str, Any], artifact["prefix_summary"]).items():
        for name, comparison in summary["comparisons"].items():
            lines.append(
                f"- prefix {prefix}, `{name}`, n={summary['complete_rows']}: mean "
                f"{comparison['mean_difference']:.4f}, 95% paired bootstrap "
                f"[{comparison['interval_low']:.4f}, {comparison['interval_high']:.4f}]"
            )
    teaching = artifact["teaching_selection"]
    lines += [
        "",
        "## Teaching rows",
        "",
        f"- fixed spine: selection {teaching['spine_selection_rank']}",
        (
            f"- inconvenient row: selection {teaching['inconvenient_selection_rank']} at prefix "
            f"{teaching['inconvenient_prefix']} because `{teaching['inconvenient_reason']}`"
        ),
        "",
        artifact["interpretation"]["scope"],
        "",
    ]
    return "\n".join(lines).encode()
