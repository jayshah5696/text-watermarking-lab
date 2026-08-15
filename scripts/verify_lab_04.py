#!/usr/bin/env python3
"""Regenerate and validate Stage 4 evidence from the pinned local model cache."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from watermark_lab.lab04_config import config_from_toml_bytes
from watermark_lab.lab04_records import trace_from_json_bytes, trace_to_json_bytes


class VerificationError(RuntimeError):
    """A mismatch between Stage 4 source, configuration, and selected evidence."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_04.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-04"))
    return parser.parse_args()


def _run(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise VerificationError(f"{' '.join(command)} failed: {detail}")
    return completed.stdout


def main() -> int:
    arguments = _parse_args()
    try:
        config_bytes = arguments.config.read_bytes()
        config = config_from_toml_bytes(config_bytes)
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        selected_json = (arguments.artifacts / "trace.json").read_bytes()
        selected_markdown = (arguments.artifacts / "annotated_trace.md").read_bytes()
        selected = trace_from_json_bytes(selected_json)
        if selected.config != config:
            raise VerificationError("selected configuration differs from configs/lab_04.toml")
        if selected.config_sha256 != config_sha256:
            raise VerificationError("selected config hash differs from configs/lab_04.toml")
        if trace_to_json_bytes(selected) != selected_json:
            raise VerificationError("selected trace is not in canonical stable JSON form")
        repository = Path(_run(["git", "rev-parse", "--show-toplevel"], cwd=Path.cwd()).strip())
        _run(["git", "cat-file", "-e", f"{selected.source_commit}^{{commit}}"], cwd=repository)
        source_config = _run(
            ["git", "show", f"{selected.source_commit}:configs/lab_04.toml"], cwd=repository
        ).encode()
        if hashlib.sha256(source_config).hexdigest() != selected.config_sha256:
            raise VerificationError("source commit does not contain the selected configuration")

        with tempfile.TemporaryDirectory(prefix="lab-04-verify-") as temporary:
            generated = Path(temporary)
            _run(
                [
                    sys.executable,
                    "labs/04_transformers_reference.py",
                    "--local-files-only",
                    "--source-commit",
                    selected.source_commit,
                    "--artifacts",
                    str(generated),
                ],
                cwd=repository,
            )
            if (generated / "trace.json").read_bytes() != selected_json:
                raise VerificationError("selected trace.json differs from deterministic replay")
            if (generated / "annotated_trace.md").read_bytes() != selected_markdown:
                raise VerificationError("annotated_trace.md differs from deterministic replay")
    except (OSError, TypeError, UnicodeError, ValueError, VerificationError) as error:
        print(f"Stage 4 verification failed: {error}", file=sys.stderr)
        return 1
    print("Stage 4 evidence verified from its config, source commit, and local model cache.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
