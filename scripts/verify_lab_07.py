#!/usr/bin/env python3
"""Build or verify Stage 7 evidence without dataset, model, GPU, or cloud access."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab07_config import lab07_config_from_toml_bytes
from watermark_lab.lab07_records import (
    RAW_KEYS,
    build_stage07_artifact,
    stage07_json_bytes,
    stage07_markdown_bytes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_07.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-07"))
    parser.add_argument("--raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_bytes = args.config.read_bytes()
        config = lab07_config_from_toml_bytes(config_bytes)
        config_hash = hashlib.sha256(config_bytes).hexdigest()
        json_path = args.artifacts / "results.json"
        markdown_path = args.artifacts / "results.md"
        if args.raw is not None:
            raw: Any = json.loads(args.raw.read_text())
            artifact = build_stage07_artifact(cast(dict[str, Any], raw), config)
            if artifact["config_sha256"] != config_hash:
                raise ValueError("returned Stage 7 config hash differs")
            args.artifacts.mkdir(parents=True, exist_ok=True)
            json_path.write_bytes(stage07_json_bytes(artifact))
            markdown_path.write_bytes(stage07_markdown_bytes(artifact))
        selected: Any = json.loads(json_path.read_text())
        if selected["config_sha256"] != config_hash:
            raise ValueError("selected Stage 7 config hash differs")
        rebuilt = build_stage07_artifact(
            {key: value for key, value in selected.items() if key in RAW_KEYS}, config
        )
        if stage07_json_bytes(rebuilt) != json_path.read_bytes():
            raise ValueError("selected Stage 7 JSON differs from local reconstruction")
        if stage07_markdown_bytes(rebuilt) != markdown_path.read_bytes():
            raise ValueError("Stage 7 Markdown differs from selected JSON")
        required_figures = (
            "separation.png",
            "separation.svg",
            "prefix_effects.png",
            "prefix_effects.svg",
        )
        for name in required_figures:
            figure = args.artifacts / name
            if not figure.is_file() or figure.stat().st_size == 0:
                raise ValueError(f"Stage 7 figure is missing or empty: {name}")
        for name in ("separation.svg", "prefix_effects.svg"):
            if "dc:date" in (args.artifacts / name).read_text():
                raise ValueError(f"Stage 7 SVG contains creation metadata: {name}")
        with tempfile.TemporaryDirectory() as temporary:
            generated = Path(temporary)
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("build_stage_07_figures.py")),
                    "--artifact",
                    str(json_path),
                    "--output",
                    str(generated),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            for name in required_figures:
                if (generated / name).read_bytes() != (args.artifacts / name).read_bytes():
                    raise ValueError(f"Stage 7 figure differs from local reconstruction: {name}")
        artifact_text = json_path.read_text().lower()
        for forbidden in ("hf_token", "modal_secret", ".cache/huggingface"):
            if forbidden in artifact_text:
                raise ValueError(f"selected Stage 7 evidence contains forbidden text: {forbidden}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Stage 7 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 7 evidence verified locally; no dataset, model, GPU, or cloud call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
