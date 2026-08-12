from __future__ import annotations

from pathlib import Path

import pytest

from watermark_lab.lab02_config import config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]


def test_locked_config_loads() -> None:
    config = config_from_toml_bytes((ROOT / "configs/lab_02.toml").read_bytes())
    assert len(config.vocabulary) == 20
    assert config.initial_context == (3, 7, 11, 15)
    assert config.gamma == 0.25
    assert config.delta == 2.0


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b"[nested]\nvalue = 1\n", ValueError),
        (b"schema_version = 2\n", ValueError),
        (b"\xff", UnicodeError),
        (b"not valid toml", ValueError),
    ],
)
def test_config_loader_rejects_bad_documents(payload: bytes, error: type[Exception]) -> None:
    with pytest.raises(error):
        config_from_toml_bytes(payload)


def _replace(source: bytes, old: str, new: str) -> bytes:
    return source.decode().replace(old, new).encode()


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        ("base_seed = 20260811", 'base_seed = "bad"', TypeError),
        ('development_key = "stage-02-public-demo-key-v1"', "development_key = 7", TypeError),
        ("gamma = 0.25", 'gamma = "bad"', TypeError),
        ("delta = 2.0", "delta = -1.0", ValueError),
        ("context_width = 4", "context_width = 0", ValueError),
        ("steps = 4", "steps = 0", ValueError),
        ('  "amber",', "  7,", TypeError),
        ("initial_context = [3, 7, 11, 15]", 'initial_context = [3, "bad", 11, 15]', TypeError),
        ("  1.9,", '  "bad",', TypeError),
    ],
)
def test_config_loader_rejects_invalid_fields(old: str, new: str, error: type[Exception]) -> None:
    source = (ROOT / "configs/lab_02.toml").read_bytes()
    with pytest.raises(error):
        config_from_toml_bytes(_replace(source, old, new))
