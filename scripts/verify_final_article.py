#!/usr/bin/env python3
"""Rebuild and verify the continuous final article."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    completed = subprocess.run(args, cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    run(sys.executable, "scripts/build_final_article.py")
    run(sys.executable, "-m", "pytest", "-q", "tests/unit/test_final_article.py")
    print("Final article matches committed Stage 1-8 evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
