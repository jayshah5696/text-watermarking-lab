"""Validation and selected-artifact rendering for Stage 6."""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any, cast

from watermark_lab.lab06_config import Lab06Config
from watermark_lab.stats import exact_binomial_upper_tail, green_hit_z_score

RAW_KEYS = {
    "schema_version",
    "source_commit",
    "config_sha256",
    "python_version",
    "torch_version",
    "transformers_version",
    "huggingface_hub_version",
    "modal_sdk_version",
    "gpu_name",
    "cuda_runtime",
    "dataset_file_sha256",
    "dataset_file_bytes",
    "dataset_rows_read",
    "tokenizer_files",
    "secret_used",
    "volume_used",
    "selection",
    "scores",
    "spine",
    "runtime_ns",
}


def score_record(*, hits: int, trials: int, config: Lab06Config) -> dict[str, Any]:
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


def _validate_measurement(value: Mapping[str, Any], config: Lab06Config) -> dict[str, Any]:
    hits = value.get("num_green_tokens")
    trials = value.get("num_tokens_scored")
    if isinstance(hits, bool) or not isinstance(hits, int):
        raise TypeError("green count must be an integer")
    if isinstance(trials, bool) or not isinstance(trials, int):
        raise TypeError("scored count must be an integer")
    expected = score_record(hits=hits, trials=trials, config=config)
    for key, expected_value in expected.items():
        actual = value.get(key)
        if isinstance(expected_value, float):
            if not isinstance(actual, (int, float)) or not math.isclose(
                float(actual), expected_value, rel_tol=0, abs_tol=1e-12
            ):
                raise ValueError(f"Stage 6 {key} differs from independent calculation")
        elif actual != expected_value:
            raise ValueError(f"Stage 6 {key} differs from independent calculation")
    return expected


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[round(q * (len(ordered) - 1))]


def build_calibration_artifact(raw: Mapping[str, Any], config: Lab06Config) -> dict[str, Any]:
    if set(raw) != RAW_KEYS:
        raise ValueError("Stage 6 raw keys differ from the exact contract")
    if raw["schema_version"] != 1:
        raise ValueError("Stage 6 raw schema differs")
    if raw["gpu_name"] != "NVIDIA L4":
        raise ValueError("Stage 6 requires one NVIDIA L4")
    if raw["secret_used"] is not False or raw["volume_used"] is not False:
        raise ValueError("Stage 6 uses neither Secret nor Volume")
    if raw["dataset_file_sha256"] != config.dataset_file_sha256:
        raise ValueError("Stage 6 dataset hash differs")
    if raw["dataset_file_bytes"] != config.dataset_file_bytes:
        raise ValueError("Stage 6 dataset byte count differs")
    source_commit = raw["source_commit"]
    config_hash = raw["config_sha256"]
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise ValueError("source_commit must be a full Git SHA")
    if not isinstance(config_hash, str) or len(config_hash) != 64:
        raise ValueError("config_sha256 must be full SHA-256")

    selection = cast(dict[str, Any], raw["selection"])
    manifests = cast(list[dict[str, Any]], selection.get("manifest"))
    if len(manifests) != config.selected_rows:
        raise ValueError("Stage 6 manifest must contain 1,024 rows")
    expected_splits = ["calibration"] * config.calibration_rows + [
        "paired_test"
    ] * config.paired_test_rows
    if [row.get("split") for row in manifests] != expected_splits:
        raise ValueError("Stage 6 split order differs")
    if [row.get("selection_rank") for row in manifests] != list(range(config.selected_rows)):
        raise ValueError("Stage 6 selection ranks differ")
    if any(not isinstance(row.get("dataset_row_index"), int) for row in manifests):
        raise ValueError("Stage 6 source row indices differ")
    source_indices = cast(list[int], [row["dataset_row_index"] for row in manifests])
    text_hashes = [row.get("text_sha256") for row in manifests]
    if len(set(source_indices)) != len(source_indices) or len(set(text_hashes)) != len(text_hashes):
        raise ValueError("Stage 6 selected splits overlap")
    if source_indices != sorted(source_indices):
        raise ValueError("Stage 6 manifest is not in dataset order")
    for row in manifests:
        if row.get("prompt_token_range") != [0, config.prompt_tokens] or row.get(
            "continuation_token_range"
        ) != [config.prompt_tokens, config.prompt_tokens + config.continuation_tokens]:
            raise ValueError("Stage 6 manifest token ranges differ")
        if not isinstance(row.get("full_token_count"), int) or row["full_token_count"] < 500:
            raise ValueError("Stage 6 selected row is too short")
        if not isinstance(row.get("url"), str) or not isinstance(row.get("timestamp"), str):
            raise ValueError("Stage 6 manifest source metadata differs")
        if not isinstance(row.get("text_sha256"), str) or len(row["text_sha256"]) != 64:
            raise ValueError("Stage 6 text hash differs")

    scores = cast(list[dict[str, Any]], raw["scores"])
    if len(scores) != config.calibration_rows:
        raise ValueError("Stage 6 requires exactly 1,000 calibration scores")
    all_z: list[float] = []
    distinct_z: list[float] = []
    for index, row in enumerate(scores):
        manifest = manifests[index]
        if (
            row.get("selection_rank") != index
            or row.get("dataset_row_index") != manifest["dataset_row_index"]
        ):
            raise ValueError("Stage 6 score identity differs from manifest")
        all_measurement = _validate_measurement(cast(dict[str, Any], row["all_pairs"]), config)
        distinct_measurement = _validate_measurement(
            cast(dict[str, Any], row["distinct_pairs"]), config
        )
        if all_measurement["num_tokens_scored"] != config.continuation_tokens - 1:
            raise ValueError("all-pair score must use 399 eligible tokens")
        if distinct_measurement["num_tokens_scored"] > all_measurement["num_tokens_scored"]:
            raise ValueError("distinct-pair score cannot have more trials")
        all_z.append(all_measurement["z_score"])
        distinct_z.append(distinct_measurement["z_score"])

    spine = cast(dict[str, Any], raw["spine"])
    if (
        spine.get("selection_rank") != 0
        or spine.get("dataset_row_index") != manifests[0]["dataset_row_index"]
    ):
        raise ValueError("Stage 6 spine must be the first selected calibration row")
    tokens = cast(list[dict[str, Any]], spine.get("token_evidence"))
    if len(tokens) != config.continuation_tokens:
        raise ValueError("Stage 6 spine needs all 400 continuation tokens")
    pair_counts: Counter[tuple[int, int]] = Counter()
    all_hits = 0
    distinct_outcomes: dict[tuple[int, int], bool] = {}
    for position, token in enumerate(tokens):
        expected_eligible = position >= config.context_width
        if (
            token.get("position") != position
            or not isinstance(token.get("token_id"), int)
            or not isinstance(token.get("piece"), str)
            or token.get("eligible") is not expected_eligible
        ):
            raise ValueError("Stage 6 spine token identity differs")
        if not expected_eligible:
            if token.get("previous_token_id") is not None or token.get("is_green") is not None:
                raise ValueError("unscored Stage 6 token has keyed evidence")
            continue
        previous = tokens[position - 1]["token_id"]
        target = token["token_id"]
        if token.get("previous_token_id") != previous or not isinstance(
            token.get("is_green"), bool
        ):
            raise ValueError("Stage 6 spine keyed evidence differs")
        pair = (previous, target)
        pair_counts[pair] += 1
        all_hits += int(token["is_green"])
        if pair in distinct_outcomes and distinct_outcomes[pair] != token["is_green"]:
            raise ValueError("identical Stage 6 pair has inconsistent membership")
        distinct_outcomes[pair] = token["is_green"]
    first_score = scores[0]
    if (all_hits, sum(pair_counts.values())) != (
        first_score["all_pairs"]["num_green_tokens"],
        first_score["all_pairs"]["num_tokens_scored"],
    ):
        raise ValueError("Stage 6 spine colors differ from all-pair totals")
    if (sum(distinct_outcomes.values()), len(distinct_outcomes)) != (
        first_score["distinct_pairs"]["num_green_tokens"],
        first_score["distinct_pairs"]["num_tokens_scored"],
    ):
        raise ValueError("Stage 6 spine colors differ from distinct-pair totals")

    max_index = max(range(len(scores)), key=lambda index: all_z[index])
    positive = sum(row["all_pairs"]["prediction"] for row in scores)
    positive_distinct = sum(row["distinct_pairs"]["prediction"] for row in scores)
    rejection_counts = cast(dict[str, int], selection.get("rejection_counts"))
    if set(rejection_counts) != {
        "too_short",
        "duplicate_text",
        "obvious_list",
        "code_dump",
        "low_letter_fraction",
    } or any(value < 0 for value in rejection_counts.values()):
        raise ValueError("Stage 6 rejection counts differ")
    last_index = selection.get("last_scanned_row_index")
    if not isinstance(last_index, int) or last_index != source_indices[-1]:
        raise ValueError("Stage 6 scan boundary differs")
    if raw["dataset_rows_read"] != last_index + 1:
        raise ValueError("Stage 6 rows-read count differs")

    summary = {
        "source_rows_scanned": last_index + 1,
        "rejection_counts": rejection_counts,
        "calibration_rows": config.calibration_rows,
        "paired_test_rows": config.paired_test_rows,
        "positive_all_pair_rows": positive,
        "positive_all_pair_fraction": positive / config.calibration_rows,
        "positive_distinct_pair_rows": positive_distinct,
        "positive_distinct_pair_fraction": positive_distinct / config.calibration_rows,
        "all_pair_z_quantiles": {
            "q05": _quantile(all_z, 0.05),
            "median": _quantile(all_z, 0.50),
            "q95": _quantile(all_z, 0.95),
            "q99": _quantile(all_z, 0.99),
        },
        "distinct_pair_z_quantiles": {
            "q05": _quantile(distinct_z, 0.05),
            "median": _quantile(distinct_z, 0.50),
            "q95": _quantile(distinct_z, 0.95),
            "q99": _quantile(distinct_z, 0.99),
        },
        "maximum_all_pair_z": all_z[max_index],
        "maximum_all_pair_selection_rank": max_index,
        "maximum_all_pair_dataset_row_index": scores[max_index]["dataset_row_index"],
        "empirical_resolution": 1 / config.calibration_rows,
    }
    return {
        **dict(raw),
        "config": {
            "dataset_id": config.dataset_id,
            "dataset_revision": config.dataset_revision,
            "dataset_config": config.dataset_config,
            "dataset_split": config.dataset_split,
            "tokenizer_id": config.tokenizer_id,
            "tokenizer_revision": config.tokenizer_revision,
            "green_fraction": config.green_fraction,
            "generation_key": config.generation_key,
            "seeding_scheme": config.seeding_scheme,
            "context_width": config.context_width,
            "z_threshold": config.z_threshold,
            "prompt_tokens": config.prompt_tokens,
            "continuation_tokens": config.continuation_tokens,
        },
        "summary": summary,
        "interpretation": {
            "source": "C4 realnewslike is natural-web text, not verified human authorship.",
            "positive": "Consistent with this configured watermark and key.",
            "scope": (
                "The observed fraction describes this frozen sample and profile. It is not a "
                "production false-alarm rate."
            ),
            "resolution": (
                "One thousand rows can resolve observed counts in steps of 1/1000 and cannot "
                "validate one-in-100,000 behavior."
            ),
        },
    }


def calibration_json_bytes(artifact: Mapping[str, Any]) -> bytes:
    return (json.dumps(artifact, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def manifest_jsonl_bytes(artifact: Mapping[str, Any]) -> bytes:
    rows = cast(dict[str, Any], artifact["selection"])["manifest"]
    return b"".join(
        (json.dumps(row, allow_nan=False, sort_keys=True) + "\n").encode() for row in rows
    )


def calibration_markdown_bytes(artifact: Mapping[str, Any]) -> bytes:
    summary = cast(dict[str, Any], artifact["summary"])
    scores = cast(list[dict[str, Any]], artifact["scores"])
    maximum_index = cast(int, summary["maximum_all_pair_selection_rank"])
    maximum: dict[str, Any] = scores[maximum_index]
    first: dict[str, Any] = scores[0]
    lines = [
        "# Stage 6 natural-web calibration",
        "",
        "The unchanged Stage 5 checker scored 1,000 frozen C4 realnewslike continuations.",
        "C4 is natural-web text, not verified human authorship.",
        "",
        "## Selection",
        "",
        f"- source rows scanned: {summary['source_rows_scanned']}",
        f"- calibration rows: {summary['calibration_rows']}",
        f"- frozen paired-test rows: {summary['paired_test_rows']}",
    ]
    for reason, count in summary["rejection_counts"].items():
        lines.append(f"- rejected `{reason}`: {count}")
    lines += [
        "",
        "## Recorded score distribution",
        "",
        f"- all-pair rows above strict z > 3: {summary['positive_all_pair_rows']}/1000",
        (f"- distinct-pair rows above strict z > 3: {summary['positive_distinct_pair_rows']}/1000"),
        (
            "- all-pair z quantiles, q05 / median / q95 / q99: "
            f"{summary['all_pair_z_quantiles']['q05']:.4f} / "
            f"{summary['all_pair_z_quantiles']['median']:.4f} / "
            f"{summary['all_pair_z_quantiles']['q95']:.4f} / "
            f"{summary['all_pair_z_quantiles']['q99']:.4f}"
        ),
        (
            f"- first selected row: {first['all_pairs']['num_green_tokens']}/"
            f"{first['all_pairs']['num_tokens_scored']}, z {first['all_pairs']['z_score']:.4f}"
        ),
        (
            f"- maximum row: selection {summary['maximum_all_pair_selection_rank']}, "
            f"dataset row {maximum['dataset_row_index']}, "
            f"{maximum['all_pairs']['num_green_tokens']}/"
            f"{maximum['all_pairs']['num_tokens_scored']}, "
            f"z {maximum['all_pairs']['z_score']:.4f}"
        ),
        "",
        artifact["interpretation"]["scope"],
        "",
        artifact["interpretation"]["resolution"],
        "",
    ]
    return "\n".join(lines).encode()
