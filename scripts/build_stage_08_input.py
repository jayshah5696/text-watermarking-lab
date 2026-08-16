#!/usr/bin/env python3
"""Build the exact bounded Stage 8 remote input from selected Stage 7 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab08_config import lab08_config_from_toml_bytes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_08.toml"))
    parser.add_argument("--stage7", type=Path, default=Path("artifacts/lab-07/results.json"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = lab08_config_from_toml_bytes(args.config.read_bytes())
    stage7_bytes = args.stage7.read_bytes()
    if hashlib.sha256(stage7_bytes).hexdigest() != config.stage7_selected_sha256:
        raise ValueError("Stage 7 selected artifact hash differs")
    stage7: dict[str, Any] = json.loads(stage7_bytes)
    if (
        stage7["source_commit"] != config.stage7_source_commit
        or stage7["config_sha256"] != config.stage7_config_sha256
        or stage7["model_revision"] != config.model_revision
    ):
        raise ValueError("Stage 7 selected artifact identity differs")
    rows_by_rank = {row["selection_rank"]: row for row in stage7["selected_rows"]}
    output: list[dict[str, Any]] = []
    for rank in config.attack_selection_ranks:
        row = cast(dict[str, Any], rows_by_rank[rank])
        marked = cast(dict[str, Any], row["conditions"]["watermarked"])
        control = cast(dict[str, Any], row["conditions"]["control"])
        text = cast(str, marked["copied_text"])
        if len(marked["copied_token_ids"]) < config.attack_prefix:
            raise ValueError("Stage 8 attack source is shorter than the fixed prefix")
        generation_prompt = stage7["config"].get("instruction_prefix")
        if generation_prompt is None:
            rendered = cast(str, marked["rendered_input"])
            source_prompt = cast(str, row["source_prompt_text"])
            instruction = (
                "Continue the passage naturally with a detailed, coherent response. "
                "Do not summarize early. Return only the continuation.\n\n"
            )
            generation_prompt = instruction + source_prompt
            if not rendered:
                raise ValueError("Stage 7 rendered input is missing")
        output.append(
            {
                "selection_rank": rank,
                "stage7_source_commit": stage7["source_commit"],
                "text_sha256": row["text_sha256"],
                "stage7_seed": row["seed"],
                "generation_prompt": generation_prompt,
                "expected_rendered_input": marked["rendered_input"],
                "watermarked_text": text,
                "watermarked_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "watermarked_token_ids": marked["copied_token_ids"],
                "control_text": control["copied_text"],
                "stage7_generated_token_count": marked["generated_token_count"],
                "stage7_generation_wall_ns": marked["generation_wall_ns"],
                "stage7_stop_reason": marked["stop_reason"],
            }
        )
    payload = json.dumps(output, allow_nan=False, separators=(",", ":"))
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
