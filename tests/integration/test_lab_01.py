from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

from watermark_lab.records import summary_from_json_bytes

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_IMPORT_ROOTS = {"datasets", "mlx", "modal", "torch", "transformers"}


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, check=False, capture_output=True, text=True)


def _fixture_repository(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repository = tmp_path / "repository"
    repository.mkdir()
    for directory in ("configs", "labs", "scripts", "src"):
        shutil.copytree(ROOT / directory, repository / directory)
    (repository / "configs/lab_01.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                "base_seed = 20260811",
                "lengths = [4, 8]",
                "replicates = 20",
                "null_hit_probability = 0.25",
                "alternative_hit_probability = 0.40",
                "z_threshold = 3.0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    assert _run(["git", "init", "-b", "test"], cwd=repository).returncode == 0
    assert _run(["git", "config", "user.name", "Stage 1 Test"], cwd=repository).returncode == 0
    assert (
        _run(["git", "config", "user.email", "stage1@example.invalid"], cwd=repository).returncode
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
    runs = tmp_path / "runs"
    artifacts = tmp_path / "artifacts"
    lab_command = [
        sys.executable,
        "labs/01_biased_coin.py",
        "--runs-dir",
        str(runs),
        "--artifacts",
        str(artifacts),
    ]
    first = _run(lab_command, cwd=repository, env=environment)
    assert first.returncode == 0, first.stderr
    assert "biased-coin demonstration under independent trials" in first.stdout
    selected = (artifacts / "summary.json").read_bytes()
    summary = summary_from_json_bytes(selected)
    raw_directory = runs / summary.source_commit / summary.config_sha256
    assert (raw_directory / "metadata.json").is_file()
    assert (raw_directory / "simulations.jsonl").is_file()

    second = _run(lab_command, cwd=repository, env=environment)
    assert second.returncode == 0, second.stderr
    assert (artifacts / "summary.json").read_bytes() == selected

    svg = (artifacts / "detection_by_length.svg").read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "dc:date" not in svg
    assert "creation" not in svg.lower()
    with Image.open(artifacts / "detection_by_length.png") as image:
        assert image.width > 0 and image.height > 0

    verifier_command = [
        sys.executable,
        "scripts/verify_lab_01.py",
        "--runs-dir",
        str(runs),
        "--artifacts",
        str(artifacts),
    ]
    verified = _run(verifier_command, cwd=repository, env=environment)
    assert verified.returncode == 0, verified.stderr

    data = json.loads(selected)
    data["rows"][0]["mean_z"] += 0.01
    (artifacts / "summary.json").write_text(json.dumps(data), encoding="utf-8")
    tampered = _run(verifier_command, cwd=repository, env=environment)
    assert tampered.returncode != 0


def test_lab_refuses_dirty_git_worktree(tmp_path: Path) -> None:
    repository, environment = _fixture_repository(tmp_path)
    (repository / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
    result = _run(
        [
            sys.executable,
            "labs/01_biased_coin.py",
            "--runs-dir",
            str(tmp_path / "runs"),
            "--artifacts",
            str(tmp_path / "artifacts"),
        ],
        cwd=repository,
        env=environment,
    )
    assert result.returncode != 0
    assert "dirty Git worktree" in result.stderr


def test_stage_1_source_has_no_model_dataset_or_cloud_imports() -> None:
    imported_roots: set[str] = set()
    for directory in (ROOT / "src", ROOT / "labs", ROOT / "scripts"):
        for path in directory.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported_roots.add(node.module.split(".", 1)[0])
    assert imported_roots.isdisjoint(FORBIDDEN_IMPORT_ROOTS)
