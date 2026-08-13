#!/usr/bin/env python3
"""Regenerate and validate Stage 3 evidence from the pinned local model cache."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from watermark_lab.lab03_config import config_from_toml_bytes
from watermark_lab.lab03_records import (
    trace_from_json_bytes,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)
from watermark_lab.lab03_runtime import build_lab03_trace


class VerificationError(RuntimeError):
    """A mismatch between Stage 3 source, configuration, and selected evidence."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_03.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-03"))
    return parser.parse_args()


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=repo, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise VerificationError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout


def main() -> int:
    arguments = _parse_args()
    try:
        config_bytes = arguments.config.read_bytes()
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        config = config_from_toml_bytes(config_bytes)
        selected_json = (arguments.artifacts / "trace.json").read_bytes()
        selected_markdown = (arguments.artifacts / "annotated_trace.md").read_bytes()
        selected = trace_from_json_bytes(selected_json)
        if selected.config != config:
            raise VerificationError("selected configuration differs from configs/lab_03.toml")
        if selected.config_sha256 != config_sha256:
            raise VerificationError("selected config hash differs from configs/lab_03.toml")
        repository = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
        _git(repository, "cat-file", "-e", f"{selected.source_commit}^{{commit}}")
        source_config = _git(
            repository, "show", f"{selected.source_commit}:configs/lab_03.toml"
        ).encode()
        if hashlib.sha256(source_config).hexdigest() != selected.config_sha256:
            raise VerificationError("source commit does not contain the selected configuration")
        recomputed = build_lab03_trace(
            source_commit=selected.source_commit,
            config_sha256=config_sha256,
            config=config,
            local_files_only=True,
        )
        if trace_to_json_bytes(recomputed) != selected_json:
            raise VerificationError("selected trace.json differs from deterministic replay")
        if trace_to_markdown_bytes(recomputed) != selected_markdown:
            raise VerificationError("annotated_trace.md differs from deterministic replay")
    except (
        OSError,
        TypeError,
        UnicodeError,
        ValueError,
        VerificationError,
    ) as error:
        print(f"Stage 3 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 3 evidence verified from its config, source commit, and local model cache.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
