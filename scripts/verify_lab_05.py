#!/usr/bin/env python3
"""Validate selected Stage 5 evidence without network, model, GPU, or Modal work."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab05_config import config_from_toml_bytes
from watermark_lab.lab05_records import (
    build_selected_trace,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_05.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-05"))
    parser.add_argument(
        "--raw", type=Path, help="build selected artifacts from one returned Modal JSON file"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_bytes = args.config.read_bytes()
        config = config_from_toml_bytes(config_bytes)
        config_hash = hashlib.sha256(config_bytes).hexdigest()
        if args.raw is not None:
            raw: Any = json.loads(args.raw.read_text())
            trace = build_selected_trace(cast(dict[str, Any], raw), config)
            if trace["config_sha256"] != config_hash:
                raise ValueError("returned config hash differs")
            args.artifacts.mkdir(parents=True, exist_ok=True)
            (args.artifacts / "trace.json").write_bytes(trace_to_json_bytes(trace))
            (args.artifacts / "annotated_trace.md").write_bytes(trace_to_markdown_bytes(trace))
        selected: Any = json.loads((args.artifacts / "trace.json").read_text())
        if selected["config_sha256"] != config_hash:
            raise ValueError("selected config hash differs")
        rebuilt = build_selected_trace(
            {
                key: value
                for key, value in selected.items()
                if key
                not in {
                    "config",
                    "claim_labels",
                    "price_snapshot",
                    "projections",
                    "gate",
                    "unavailable_measurements",
                }
            },
            config,
        )
        if trace_to_json_bytes(rebuilt) != (args.artifacts / "trace.json").read_bytes():
            raise ValueError("selected trace does not match local recomputation")
        if trace_to_markdown_bytes(rebuilt) != (args.artifacts / "annotated_trace.md").read_bytes():
            raise ValueError("annotated trace does not match selected JSON")
        text = (args.artifacts / "trace.json").read_text().lower()
        for forbidden in ("hf_token", "huggingface/token", ".cache/huggingface", "modal_secret"):
            if forbidden in text:
                raise ValueError(f"selected evidence contains forbidden text: {forbidden}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Stage 5 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 5 selected evidence verified locally; no cloud or model call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
