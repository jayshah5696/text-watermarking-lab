#!/usr/bin/env python3
"""Stage 2: expose keyed green-list sampling with a 20-token toy vocabulary."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from watermark_lab.lab02_config import config_from_toml_bytes
from watermark_lab.lab02_records import (
    build_lab02_trace,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)

CAVEAT = (
    "This is a deterministic toy selector with a public development key, not an upstream "
    "KGW implementation, a security design, or an LLM measurement."
)


class LabError(RuntimeError):
    """An actionable problem with a Stage 2 generation precondition."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_02.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-02"))
    return parser.parse_args()


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=repo, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise LabError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout.strip()


def _clean_source_commit(repo: Path) -> str:
    dirty = _git(repo, "status", "--porcelain", "--untracked-files=normal")
    if dirty:
        raise LabError(
            "refusing to generate the Stage 2 trace from a dirty Git worktree; commit, ignore, "
            "or remove the listed changes first:\n" + dirty
        )
    return _git(repo, "rev-parse", "HEAD")


def main() -> int:
    arguments = _parse_args()
    try:
        config_bytes = arguments.config.read_bytes()
        config = config_from_toml_bytes(config_bytes)
        repository = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
        source_commit = _clean_source_commit(repository)
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        trace = build_lab02_trace(
            source_commit=source_commit,
            config_sha256=config_sha256,
            config=config,
        )
        arguments.artifacts.mkdir(parents=True, exist_ok=True)
        (arguments.artifacts / "trace.json").write_bytes(trace_to_json_bytes(trace))
        (arguments.artifacts / "annotated_trace.md").write_bytes(trace_to_markdown_bytes(trace))
    except (LabError, OSError, TypeError, UnicodeError, ValueError) as error:
        print(f"Stage 2 lab failed: {error}", file=sys.stderr)
        return 1

    print("position  context         green IDs         draw          plain  biased  G/T   z")
    for step in trace.steps:
        print(
            f"{step.position:>8}  {list(step.context)!s:<15} "
            f"{list(step.green_token_ids)!s:<17} {step.sample_draw:>12.9f}  "
            f"{step.baseline_token_id:>5}  {step.sampled_token_id:>6}  "
            f"{step.green_hits}/{step.eligible_tokens:<3} {step.z_score:>7.3f}"
        )
    print(CAVEAT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
