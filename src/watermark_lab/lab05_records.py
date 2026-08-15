# pyright: reportUnknownArgumentType=false
"""Selected evidence helpers for the Stage 5 Gemma/Modal smoke test."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any, cast

from watermark_lab.lab05_config import Lab05Config
from watermark_lab.stats import green_hit_z_score


def build_selected_trace(raw: Mapping[str, Any], config: Lab05Config) -> dict[str, Any]:
    """Validate remote evidence and add stable projections and gate results."""

    raw_records = raw.get("records")
    if not isinstance(raw_records, list) or len(raw_records) != 6:
        raise ValueError("Stage 5 needs exactly six records")
    records = cast(list[dict[str, Any]], raw_records)
    expected = [
        (prompt.id, condition)
        for prompt in config.prompts
        for condition in ("control", "reference_watermark")
    ]
    if [(row.get("prompt_id"), row.get("condition")) for row in records] != expected:
        raise ValueError("Stage 5 record order differs from the contract")
    for row in records:
        prompt = next(prompt for prompt in config.prompts if prompt.id == row["prompt_id"])
        if row["prompt_text"] != prompt.text or row["seed"] != config.prompt_seed(prompt.id):
            raise ValueError("prompt identity or paired seed differs")
        if not row["copied_text"] or len(row["copied_token_ids"]) < 2:
            raise ValueError("copied continuation is too short")
        results = row["detector_results"]
        if [(item["key_role"], item["repetition_policy"]) for item in results] != [
            (role, policy) for role in ("generation", "comparison") for policy in ("all", "unique")
        ]:
            raise ValueError("detector result order differs")
        for item in results:
            independent = green_hit_z_score(
                hits=int(item["num_green_tokens"]),
                trials=int(item["num_tokens_scored"]),
                null_probability=config.green_fraction,
            )
            if not math.isclose(float(item["z_score"]), independent, abs_tol=1e-10):
                raise ValueError("detector z score differs from Stage 1")
    if raw["source_commit"] == "" or len(raw["source_commit"]) != 40:
        raise ValueError("source_commit must be a full Git SHA")
    if raw["config_sha256"] == "" or len(raw["config_sha256"]) != 64:
        raise ValueError("config_sha256 must be full SHA-256")
    if raw["gpu_name"] != "NVIDIA L4" or raw["dtype"] != "torch.bfloat16":
        raise ValueError("remote GPU or dtype differs")
    if raw["secret_used"] or raw["volume_used"]:
        raise ValueError("selected Stage 5 run must use neither Secret nor Volume")

    watermarked = [row for row in records if row["condition"] == "reference_watermark"]
    slower_rate = min(float(row["generated_tokens_per_second"]) for row in watermarked)
    projections: list[dict[str, Any]] = []
    for tokens_per_output in (
        config.short_projection_tokens_per_output,
        config.long_projection_tokens_per_output,
    ):
        total_tokens = config.projected_rows * 2 * tokens_per_output
        seconds = total_tokens / slower_rate
        projections.append(
            {
                "tokens_per_output": tokens_per_output,
                "total_generated_tokens": total_tokens,
                "basis_tokens_per_second": slower_rate,
                "projected_generation_seconds": seconds,
                "projected_gpu_only_usd": seconds * config.l4_usd_per_second,
                "excludes": [
                    "image build",
                    "model download",
                    "model load",
                    "CPU",
                    "memory",
                    "storage",
                    "retries",
                    "non-linear scaling",
                ],
            }
        )
    peak_reserved = max(int(row["peak_reserved_bytes"]) for row in records)
    headroom = (int(raw["total_vram_bytes"]) - peak_reserved) / int(raw["total_vram_bytes"])
    runtime_ok = all(row["copied_text"] and len(row["generated_token_ids"]) > 1 for row in records)
    gate = {
        "exact_l4_bf16": raw["gpu_name"] == "NVIDIA L4" and raw["dtype"] == "torch.bfloat16",
        "six_records_complete": len(records) == 6,
        "local_verifier_required": True,
        "vram_headroom_fraction": headroom,
        "vram_headroom_pass": headroom >= config.minimum_vram_headroom_fraction,
        "slowest_watermarked_tokens_per_second": slower_rate,
        "throughput_pass": slower_rate >= config.minimum_tokens_per_second,
        "runtime_smoke_pass": runtime_ok,
        "projection_under_ceiling": all(
            item["projected_gpu_only_usd"] <= config.max_cost_usd for item in projections
        ),
    }
    gate["recommend_next_stage_review"] = all(
        value
        for key, value in gate.items()
        if key.endswith("_pass") or key == "exact_l4_bf16" or key == "six_records_complete"
    )
    return {
        **dict(raw),
        "config": {
            name: (
                [dict(id=prompt.id, text=prompt.text) for prompt in value]
                if name == "prompts"
                else value
            )
            for name, value in (
                (field, getattr(config, field)) for field in config.__dataclass_fields__
            )
        },
        "claim_labels": {
            "runtime_and_detector_values": "measured",
            "projections": "derived",
            "model_and_price_metadata": "external",
            "accuracy_quality_total_bill": "limitation",
        },
        "price_snapshot": {
            "l4_usd_per_second": config.l4_usd_per_second,
            "cpu_usd_per_core_second": config.cpu_usd_per_core_second,
            "memory_usd_per_gib_second": config.memory_usd_per_gib_second,
            "volume_usd_per_gib_month": config.volume_usd_per_gib_month,
            "source": config.price_source,
            "retrieved": config.price_retrieved,
        },
        "projections": projections,
        "gate": gate,
        "unavailable_measurements": [
            "Modal queue time",
            "client-observed cold start",
            "billed cost",
            "first-token latency",
        ],
    }


def trace_to_json_bytes(trace: Mapping[str, Any]) -> bytes:
    return (json.dumps(trace, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def trace_to_markdown_bytes(trace: Mapping[str, Any]) -> bytes:
    records = cast(list[dict[str, Any]], trace["records"])
    lines = [
        "# Stage 5 annotated Gemma Modal smoke trace",
        "",
        "This measured smoke used one pinned Gemma 4 E2B BF16 model on one Modal NVIDIA L4.",
        "It ran three fixed passages with watermarking off and on, then scored copied",
        "continuation text.",
        "",
        f"- Source commit: `{trace['source_commit']}`",
        f"- Config SHA-256: `{trace['config_sha256']}`",
        f"- Model revision: `{trace['model_revision']}`",
        f"- GPU: `{trace['gpu_name']}` with {int(trace['total_vram_bytes']) / 2**30:.3f} GiB",
        f"- Cold model download: {int(trace['model_download_ns']) / 1e9:.3f} s",
        f"- Model load to CUDA: {int(trace['model_load_ns']) / 1e9:.3f} s",
        "",
        "## Six saved continuations",
        "",
        "| Passage | Watermark | Generated | Seconds | tok/s | Peak reserved GiB | "
        "Processor ms | G/T | z |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in records:
        primary = row["detector_results"][0]
        condition = "on" if row["condition"] == "reference_watermark" else "off"
        count = len(row["generated_token_ids"])
        seconds = row["generation_wall_ns"] / 1e9
        rate = row["generated_tokens_per_second"]
        peak_gib = row["peak_reserved_bytes"] / 2**30
        processor_ms = row["watermark_processor_gpu_ns"] / 1e6
        score = f"{primary['num_green_tokens']}/{primary['num_tokens_scored']}"
        lines.append(
            f"| `{row['prompt_id']}` | {condition} | {count} | {seconds:.3f} | "
            f"{rate:.3f} | {peak_gib:.3f} | {processor_ms:.3f} | {score} | "
            f"{primary['z_score']:.4f} |"
        )
    continuity = records[:2]
    lines += ["", "## Continuity passage", ""]
    for row in continuity:
        lines += [
            f"### {'Watermarked' if row['condition'] == 'reference_watermark' else 'Control'}",
            "",
            row["copied_text"],
            "",
        ]
    lines += ["## Bounded projection", ""]
    for projection in cast(list[dict[str, Any]], trace["projections"]):
        lines.append(
            f"- {projection['total_generated_tokens']:,} generated tokens / "
            f"{projection['basis_tokens_per_second']:.3f} tok/s = "
            f"{projection['projected_generation_seconds']:.1f} s, or USD "
            f"{projection['projected_gpu_only_usd']:.4f} of L4 generation time."
        )
    lines += [
        "",
        "These are GPU-only linear projections. They exclude image build, model download,",
        "model load,",
        "CPU, memory, storage, retries, and non-linear scaling.",
        "",
        "## Review gate",
        "",
        f"- Peak-memory headroom: {trace['gate']['vram_headroom_fraction']:.1%} "
        f"({'pass' if trace['gate']['vram_headroom_pass'] else 'fail'})",
        f"- Slowest watermarked throughput: "
        f"{trace['gate']['slowest_watermarked_tokens_per_second']:.3f} tok/s "
        f"({'pass' if trace['gate']['throughput_pass'] else 'fail'})",
        f"- Runtime smoke: {'pass' if trace['gate']['runtime_smoke_pass'] else 'fail'}",
        f"- Projection below USD {trace['config']['max_cost_usd']:.2f}: "
        f"{'pass' if trace['gate']['projection_under_ceiling'] else 'fail'}",
        "",
        "The three watermarked rows remained below the configured z > 3 cutoff. This does not",
        "invalidate the runtime path, and it does not estimate detection accuracy. The smoke stops",
        "for human review.",
        "",
        "A positive score would mean only consistent with this configured watermark and key. Six",
        "generations do not measure quality, accuracy, a false-alarm rate, or a total cloud bill.",
        "",
    ]
    return "\n".join(lines).encode()
