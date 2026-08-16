from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.lab07_config import lab07_config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/lab_07.toml"


def test_selected_stage_07_config_is_exact_and_locked() -> None:
    config = lab07_config_from_toml_bytes(CONFIG.read_bytes())
    assert config.prefixes == (40, 80, 160, 200, 400)
    assert config.max_generation_calls == 48
    assert config.max_generated_token_ids == 19_200
    assert config.prompt_seed(
        1000, "765548b4c26fbeabf945527ce731fea576ef5ac35dbf829ac962fe92176821f9"
    ) == config.prompt_seed(
        1000, "765548b4c26fbeabf945527ce731fea576ef5ac35dbf829ac962fe92176821f9"
    )
    assert config.bootstrap_seed(40, "versus_control") != config.bootstrap_seed(
        80, "versus_control"
    )


def test_stage_07_config_rejects_changes_and_wrong_types() -> None:
    config = lab07_config_from_toml_bytes(CONFIG.read_bytes())
    with pytest.raises(ValueError, match="locks generation_key"):
        replace(config, generation_key=1)
    with pytest.raises(TypeError, match="prefixes"):
        lab07_config_from_toml_bytes(CONFIG.read_bytes().replace(b"[40, 80", b'["40", 80'))
    with pytest.raises(ValueError, match="keys differ"):
        lab07_config_from_toml_bytes(CONFIG.read_bytes() + b"unknown = 1\n")
