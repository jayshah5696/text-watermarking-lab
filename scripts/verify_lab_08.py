#!/usr/bin/env python3
"""Build or verify Stage 8 evidence without model, GPU, network, or cloud access."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

from watermark_lab.lab08_config import lab08_config_from_toml_bytes
from watermark_lab.lab08_records import (
    RAW_KEYS,
    build_stage08_artifact,
    stage08_json_bytes,
    stage08_markdown_bytes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_08.toml"))
    parser.add_argument("--stage7", type=Path, default=Path("artifacts/lab-07/results.json"))
    parser.add_argument("--review", type=Path, default=Path("data/reviews/lab-08-paraphrase.json"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-08"))
    parser.add_argument("--raw", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_bytes = args.config.read_bytes()
        config = lab08_config_from_toml_bytes(config_bytes)
        config_hash = hashlib.sha256(config_bytes).hexdigest()
        stage7_bytes = args.stage7.read_bytes()
        if hashlib.sha256(stage7_bytes).hexdigest() != config.stage7_selected_sha256:
            raise ValueError("Stage 7 selected artifact hash differs")
        stage7: Any = json.loads(stage7_bytes)
        review: Any = json.loads(args.review.read_text())
        json_path = args.artifacts / "results.json"
        markdown_path = args.artifacts / "results.md"
        if args.raw is not None:
            raw: Any = json.loads(args.raw.read_text())
            artifact = build_stage08_artifact(
                cast(dict[str, Any], raw),
                cast(dict[str, Any], stage7),
                cast(dict[str, Any], review),
                config,
            )
            if artifact["config_sha256"] != config_hash:
                raise ValueError("returned Stage 8 config hash differs")
            args.artifacts.mkdir(parents=True, exist_ok=True)
            json_path.write_bytes(stage08_json_bytes(artifact))
            markdown_path.write_bytes(stage08_markdown_bytes(artifact))
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("build_stage_08_figures.py")),
                    "--artifact",
                    str(json_path),
                    "--output",
                    str(args.artifacts),
                ],
                check=True,
            )
        selected: Any = json.loads(json_path.read_text())
        if selected["config_sha256"] != config_hash:
            raise ValueError("selected Stage 8 config hash differs")
        rebuilt = build_stage08_artifact(
            {key: value for key, value in selected.items() if key in RAW_KEYS},
            cast(dict[str, Any], stage7),
            cast(dict[str, Any], review),
            config,
        )
        if stage08_json_bytes(rebuilt) != json_path.read_bytes():
            raise ValueError("selected Stage 8 JSON differs from local reconstruction")
        if stage08_markdown_bytes(rebuilt) != markdown_path.read_bytes():
            raise ValueError("Stage 8 Markdown differs from selected JSON")
        figures = (
            "edit_signal_loss.png",
            "edit_signal_loss.svg",
            "bias_tradeoff.png",
            "bias_tradeoff.svg",
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("build_stage_08_figures.py")),
                    "--artifact",
                    str(json_path),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            for name in figures:
                if (output / name).read_bytes() != (args.artifacts / name).read_bytes():
                    raise ValueError(f"Stage 8 figure differs from local reconstruction: {name}")
        artifact_text = json_path.read_text().lower()
        for forbidden in ("hf_token", "modal_secret", ".cache/huggingface"):
            if forbidden in artifact_text:
                raise ValueError(f"selected Stage 8 evidence contains forbidden text: {forbidden}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"Stage 8 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 8 evidence verified locally; no model, GPU, network, or cloud call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
