#!/usr/bin/env python3
"""Stage 3: expose the score increase inside a manual MLX generation loop."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from watermark_lab.lab03_config import config_from_toml_bytes
from watermark_lab.lab03_records import trace_to_json_bytes, trace_to_markdown_bytes
from watermark_lab.lab03_runtime import build_lab03_trace

CAVEAT = (
    "These six continuations verify a pinned local MLX loop. Three prompts do not measure "
    "detection accuracy or language quality, and Stage 3 has no tested cutoff."
)


class LabError(RuntimeError):
    """An actionable Stage 3 precondition failure."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_03.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-03"))
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="fail instead of downloading the pinned model and tokenizer",
    )
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
            "refusing to generate the Stage 3 trace from a dirty Git worktree; commit, ignore, "
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
        trace = build_lab03_trace(
            source_commit=source_commit,
            config_sha256=hashlib.sha256(config_bytes).hexdigest(),
            config=config,
            local_files_only=arguments.local_files_only,
        )
        arguments.artifacts.mkdir(parents=True, exist_ok=True)
        (arguments.artifacts / "trace.json").write_bytes(trace_to_json_bytes(trace))
        (arguments.artifacts / "annotated_trace.md").write_bytes(trace_to_markdown_bytes(trace))
    except (LabError, OSError, TypeError, UnicodeError, ValueError) as error:
        print(f"Stage 3 lab failed: {error}", file=sys.stderr)
        return 1

    print("prompt                increase  tokens  copied IDs  same-key G/T   z")
    for record in trace.records:
        score = record.generation_key_score
        print(
            f"{record.prompt_id:<21} "
            f"{'off' if record.condition == 'control' else 'on':<8} "
            f"{len(record.generated_token_ids):>6}  "
            f"{'match' if record.copied_ids_match else 'differ':<10} "
            f"{score.green_hits:>2}/{score.eligible_tokens:<3} {score.z_score:>8.3f}"
        )
    print(CAVEAT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
