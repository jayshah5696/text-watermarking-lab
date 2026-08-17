#!/usr/bin/env python3
"""Rebuild and verify the local Stage 9 article lesson."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    completed = subprocess.run(args, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    run(sys.executable, "scripts/build_stage_09_lesson.py")
    run(sys.executable, "-m", "pytest", "-q", "tests/unit/test_stage_09_lesson.py")
    print("Stage 9 article lesson matches committed Stage 1-8 evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
