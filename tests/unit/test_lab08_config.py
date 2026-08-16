from dataclasses import fields
from pathlib import Path

import pytest

from watermark_lab.lab08_config import Lab08Config, lab08_config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/lab_08.toml"


def test_selected_config_is_the_frozen_stage08_fixture() -> None:
    config = lab08_config_from_toml_bytes(CONFIG.read_bytes())
    assert config.attack_selection_ranks == tuple(range(1000, 1012))
    assert config.bias_selection_ranks == tuple(range(1000, 1008))
    assert config.max_generation_calls == 28
    assert config.max_generated_token_ids == 11_200
    assert config.bias_values == (1.0, 2.0, 3.0)


def test_stage08_seed_derivation_is_stable_and_separates_operations() -> None:
    config = lab08_config_from_toml_bytes(CONFIG.read_bytes())
    digest = "a" * 64
    assert config.derive_seed("deletion", 1000, digest, "0.10") == config.derive_seed(
        "deletion", 1000, digest, "0.10"
    )
    assert config.derive_seed("deletion", 1000, digest, "0.10") != config.derive_seed(
        "deletion", 1000, digest, "0.30"
    )
    assert config.paraphrase_seed(1000, digest) != config.paraphrase_seed(1001, digest)


def test_stage08_config_rejects_key_drift_and_unknown_keys() -> None:
    payload = CONFIG.read_text()
    with pytest.raises(ValueError, match="locks attack_prefix"):
        changed = payload.replace("attack_prefix = 80", "attack_prefix = 40")
        lab08_config_from_toml_bytes(changed.encode())
    with pytest.raises(ValueError, match="keys differ"):
        lab08_config_from_toml_bytes((payload + "extra = 1\n").encode())


def test_stage08_config_rejects_wrong_field_types() -> None:
    payload = CONFIG.read_text()
    with pytest.raises(TypeError, match="attack_selection_ranks"):
        changed = payload.replace("attack_selection_ranks = [", 'attack_selection_ranks = ["bad", ')
        lab08_config_from_toml_bytes(changed.encode())
    assert {field.name for field in fields(Lab08Config)}
