from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from watermark_lab.lab02_records import trace_from_json_bytes

ROOT = Path(__file__).resolve().parents[2]


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, check=False, capture_output=True, text=True)


def _fixture_repository(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repository = tmp_path / "repository"
    repository.mkdir()
    for directory in ("configs", "labs", "scripts", "src"):
        shutil.copytree(ROOT / directory, repository / directory)
    assert _run(["git", "init", "-b", "test"], cwd=repository).returncode == 0
    assert _run(["git", "config", "user.name", "Stage 2 Test"], cwd=repository).returncode == 0
    assert (
        _run(["git", "config", "user.email", "stage2@example.invalid"], cwd=repository).returncode
        == 0
    )
    assert _run(["git", "add", "."], cwd=repository).returncode == 0
    assert _run(["git", "commit", "-m", "test fixture"], cwd=repository).returncode == 0
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith("COV_CORE_") or name == "COVERAGE_PROCESS_START":
            environment.pop(name)
    environment["PYTHONPATH"] = str(repository / "src")
    return repository, environment


def test_lab_is_reproducible_and_verifier_detects_tampering(tmp_path: Path) -> None:
    repository, environment = _fixture_repository(tmp_path)
    artifacts = tmp_path / "artifacts"
    lab_command = [
        sys.executable,
        "labs/02_toy_greenlist.py",
        "--artifacts",
        str(artifacts),
    ]
    first = _run(lab_command, cwd=repository, env=environment)
    assert first.returncode == 0, first.stderr
    assert "deterministic toy selector" in first.stdout
    selected_json = (artifacts / "trace.json").read_bytes()
    selected_markdown = (artifacts / "annotated_trace.md").read_bytes()
    trace = trace_from_json_bytes(selected_json)
    assert len(trace.steps) == 4
    assert b"## Position 4" in selected_markdown

    second = _run(lab_command, cwd=repository, env=environment)
    assert second.returncode == 0, second.stderr
    assert (artifacts / "trace.json").read_bytes() == selected_json
    assert (artifacts / "annotated_trace.md").read_bytes() == selected_markdown

    verifier = [
        sys.executable,
        "scripts/verify_lab_02.py",
        "--artifacts",
        str(artifacts),
    ]
    verified = _run(verifier, cwd=repository, env=environment)
    assert verified.returncode == 0, verified.stderr

    data = json.loads(selected_json)
    data["steps"][0]["sample_draw"] += 0.01
    (artifacts / "trace.json").write_text(json.dumps(data), encoding="utf-8")
    tampered_json = _run(verifier, cwd=repository, env=environment)
    assert tampered_json.returncode != 0

    (artifacts / "trace.json").write_bytes(selected_json)
    (artifacts / "annotated_trace.md").write_text("tampered\n", encoding="utf-8")
    tampered_markdown = _run(verifier, cwd=repository, env=environment)
    assert tampered_markdown.returncode != 0


def test_lab_refuses_dirty_git_worktree(tmp_path: Path) -> None:
    repository, environment = _fixture_repository(tmp_path)
    (repository / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
    result = _run(
        [
            sys.executable,
            "labs/02_toy_greenlist.py",
            "--artifacts",
            str(tmp_path / "artifacts"),
        ],
        cwd=repository,
        env=environment,
    )
    assert result.returncode != 0
    assert "dirty Git worktree" in result.stderr
