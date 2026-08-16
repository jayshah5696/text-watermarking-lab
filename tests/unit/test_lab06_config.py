from dataclasses import fields, replace
from pathlib import Path

import pytest

from watermark_lab.lab06_config import Lab06Config, lab06_config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/lab_06.toml"


def test_selected_stage_06_config_is_exact_and_locked() -> None:
    config = lab06_config_from_toml_bytes(CONFIG.read_bytes())
    assert config.selected_rows == 1_024
    assert config.dataset_declared_rows == 13_863
    assert config.prompt_tokens == 50
    assert config.continuation_tokens == 400
    assert config.use_huggingface_secret is False
    assert config.use_volume is False
    assert {field.name for field in fields(Lab06Config)} == set(
        __import__("tomllib").loads(CONFIG.read_text())
    )


def test_stage_06_config_rejects_changes_and_wrong_types() -> None:
    config = lab06_config_from_toml_bytes(CONFIG.read_bytes())
    with pytest.raises(ValueError, match="locks green_fraction"):
        replace(config, green_fraction=0.5)
    with pytest.raises(TypeError, match="calibration_rows"):
        lab06_config_from_toml_bytes(CONFIG.read_bytes().replace(b"1000", b'"1000"', 1))
    with pytest.raises(ValueError, match="keys differ"):
        lab06_config_from_toml_bytes(CONFIG.read_bytes() + b"unknown = 1\n")
