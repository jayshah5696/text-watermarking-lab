from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, check=False, capture_output=True, text=True)


def _fixture_repository(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repository = tmp_path / "repository"
    repository.mkdir()
    for directory in ("configs", "labs", "src"):
        shutil.copytree(ROOT / directory, repository / directory)
    environment = os.environ.copy()
    assert _run(["git", "init", "-b", "test"], cwd=repository, env=environment).returncode == 0
    assert (
        _run(
            ["git", "config", "user.name", "Stage 4 Test"], cwd=repository, env=environment
        ).returncode
        == 0
    )
    assert (
        _run(
            ["git", "config", "user.email", "stage4@example.invalid"],
            cwd=repository,
            env=environment,
        ).returncode
        == 0
    )
    assert _run(["git", "add", "."], cwd=repository, env=environment).returncode == 0
    assert (
        _run(["git", "commit", "-m", "test fixture"], cwd=repository, env=environment).returncode
        == 0
    )
    for name in tuple(environment):
        if name.startswith("COV_CORE_") or name == "COVERAGE_PROCESS_START":
            environment.pop(name)
    environment["PYTHONPATH"] = str(repository / "src")
    return repository, environment


def test_lab_refuses_dirty_worktree_before_model_access(tmp_path: Path) -> None:
    repository, environment = _fixture_repository(tmp_path)
    (repository / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
    result = _run(
        [
            sys.executable,
            "labs/04_transformers_reference.py",
            "--local-files-only",
            "--artifacts",
            str(tmp_path / "artifacts"),
        ],
        cwd=repository,
        env=environment,
    )
    assert result.returncode != 0
    assert "dirty Git worktree" in result.stderr
