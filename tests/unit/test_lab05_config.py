from pathlib import Path

import pytest

from watermark_lab.lab05_config import config_from_toml_bytes


def payload() -> bytes:
    return Path("configs/lab_05.toml").read_bytes()


def test_loads_locked_stage_05_config_and_continuity_seeds() -> None:
    config = config_from_toml_bytes(payload())
    assert config.model_revision == "3e22461f65e89153144f8adb70e3b8c2cc9845a7"
    assert [config.prompt_seed(prompt.id) for prompt in config.prompts] == [
        568285428,
        640916431,
        432742284,
    ]
    assert config.max_generation_calls == 6
    assert config.use_volume is False


def test_rejects_model_or_gpu_drift() -> None:
    with pytest.raises(ValueError, match="model_id"):
        config_from_toml_bytes(payload().replace(b"google/gemma-4-E2B-it", b"other/model"))
    with pytest.raises(ValueError, match="modal_gpu"):
        config_from_toml_bytes(payload().replace(b'modal_gpu = "L4"', b'modal_gpu = "A10"'))


def test_rejects_unknown_key_and_non_boolean_resource_policy() -> None:
    with pytest.raises(ValueError, match="keys differ"):
        config_from_toml_bytes(
            payload().replace(b"schema_version = 1\n", b"schema_version = 1\nunknown = 1\n")
        )
    with pytest.raises(TypeError, match="use_volume"):
        config_from_toml_bytes(payload().replace(b"use_volume = false", b"use_volume = 0"))
