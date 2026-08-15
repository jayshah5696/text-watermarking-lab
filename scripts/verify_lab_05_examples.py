#!/usr/bin/env python3
"""Build or verify ten-pair Stage 5 evidence without cloud or model access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab05_config import config_from_toml_bytes
from watermark_lab.lab05_examples import (
    DERIVED_KEYS,
    build_examples_trace,
    examples_to_json_bytes,
    examples_to_markdown_bytes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_05_examples.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-05"))
    parser.add_argument("--raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_bytes = args.config.read_bytes()
        config = config_from_toml_bytes(config_bytes, expected_generation_calls=20)
        config_hash = hashlib.sha256(config_bytes).hexdigest()
        json_path = args.artifacts / "examples.json"
        markdown_path = args.artifacts / "examples.md"
        if args.raw is not None:
            raw: Any = json.loads(args.raw.read_text())
            trace = build_examples_trace(cast(dict[str, Any], raw), config)
            if trace["config_sha256"] != config_hash:
                raise ValueError("returned examples config hash differs")
            args.artifacts.mkdir(parents=True, exist_ok=True)
            json_path.write_bytes(examples_to_json_bytes(trace))
            markdown_path.write_bytes(examples_to_markdown_bytes(trace))
        selected: Any = json.loads(json_path.read_text())
        if selected["config_sha256"] != config_hash:
            raise ValueError("selected examples config hash differs")
        rebuilt = build_examples_trace(
            {key: value for key, value in selected.items() if key not in DERIVED_KEYS}, config
        )
        if examples_to_json_bytes(rebuilt) != json_path.read_bytes():
            raise ValueError("selected examples differ from local reconstruction")
        if examples_to_markdown_bytes(rebuilt) != markdown_path.read_bytes():
            raise ValueError("examples Markdown differs from selected JSON")
        text = json_path.read_text().lower()
        for forbidden in ("hf_token", "modal_secret", ".cache/huggingface"):
            if forbidden in text:
                raise ValueError(f"selected examples contain forbidden text: {forbidden}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Stage 5 examples verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 5 ten-pair evidence verified locally; no cloud or model call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
