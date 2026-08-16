#!/usr/bin/env python3
"""Build or verify Stage 6 evidence without dataset, model, GPU, or cloud access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab06_config import lab06_config_from_toml_bytes
from watermark_lab.lab06_records import (
    RAW_KEYS,
    build_calibration_artifact,
    calibration_json_bytes,
    calibration_markdown_bytes,
    manifest_jsonl_bytes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_06.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-06"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/lab-06-c4.jsonl"))
    parser.add_argument("--raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_bytes = args.config.read_bytes()
        config = lab06_config_from_toml_bytes(config_bytes)
        config_hash = hashlib.sha256(config_bytes).hexdigest()
        json_path = args.artifacts / "calibration.json"
        markdown_path = args.artifacts / "calibration.md"
        if args.raw is not None:
            raw: Any = json.loads(args.raw.read_text())
            artifact = build_calibration_artifact(cast(dict[str, Any], raw), config)
            if artifact["config_sha256"] != config_hash:
                raise ValueError("returned Stage 6 config hash differs")
            args.artifacts.mkdir(parents=True, exist_ok=True)
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_bytes(calibration_json_bytes(artifact))
            markdown_path.write_bytes(calibration_markdown_bytes(artifact))
            args.manifest.write_bytes(manifest_jsonl_bytes(artifact))
        selected: Any = json.loads(json_path.read_text())
        if selected["config_sha256"] != config_hash:
            raise ValueError("selected Stage 6 config hash differs")
        rebuilt = build_calibration_artifact(
            {key: value for key, value in selected.items() if key in RAW_KEYS}, config
        )
        if calibration_json_bytes(rebuilt) != json_path.read_bytes():
            raise ValueError("selected Stage 6 JSON differs from local reconstruction")
        if calibration_markdown_bytes(rebuilt) != markdown_path.read_bytes():
            raise ValueError("Stage 6 Markdown differs from selected JSON")
        if manifest_jsonl_bytes(rebuilt) != args.manifest.read_bytes():
            raise ValueError("Stage 6 manifest differs from selected JSON")
        artifact_text = json_path.read_text().lower()
        for forbidden in ("hf_token", "modal_secret", ".cache/huggingface"):
            if forbidden in artifact_text:
                raise ValueError(f"selected Stage 6 evidence contains forbidden text: {forbidden}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Stage 6 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 6 evidence verified locally; no dataset, model, GPU, or cloud call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
