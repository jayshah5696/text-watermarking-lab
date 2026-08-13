from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.lab03_config import config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]


def _payload() -> bytes:
    return (ROOT / "configs/lab_03.toml").read_bytes()


def _replace(old: str, new: str) -> bytes:
    return _payload().decode().replace(old, new).encode()


def test_locked_stage_03_config_loads() -> None:
    config = config_from_toml_bytes(_payload())
    assert config.model_id == "mlx-community/LFM2-350M-4bit"
    assert config.model_revision == "18dc72abf3b2337f9123cfd6eeeb58dfa7947066"
    assert config.temperature == 0.8
    assert config.top_k == 40
    assert config.top_p == 0.95
    assert config.context_width == 1
    assert [prompt.id for prompt in config.prompts] == [
        "stage-02-continuity",
        "notebook",
        "library",
    ]


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b"schema_version = 2\n", ValueError),
        (b"[nested]\nvalue = 1\n", ValueError),
        (b"not valid toml", ValueError),
        (b"\xff", UnicodeError),
    ],
)
def test_config_loader_rejects_bad_documents(payload: bytes, error: type[Exception]) -> None:
    with pytest.raises(error):
        config_from_toml_bytes(payload)


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        ("base_seed = 20260812", "base_seed = true", TypeError),
        ("max_new_tokens = 40", "max_new_tokens = 1", ValueError),
        ("temperature = 0.8", "temperature = 0.0", ValueError),
        ("top_k = 40", "top_k = 0", ValueError),
        ("top_p = 0.95", "top_p = 1.1", ValueError),
        ("green_fraction = 0.25", "green_fraction = 1.0", ValueError),
        ("watermark_bias = 2.0", "watermark_bias = -1.0", ValueError),
        ("comparison_key = 15485867", "comparison_key = 15485863", ValueError),
        ('selector_profile = "mlx-mix-v1"', 'selector_profile = "other"', ValueError),
        ("context_width = 1", "context_width = 2", ValueError),
        ("trace_candidates = 5", "trace_candidates = 41", ValueError),
        ('id = "notebook"', 'id = "stage-02-continuity"', ValueError),
        ('id = "notebook"', "id = 7", TypeError),
        ('text = "The student', 'text = ""\n# The student', ValueError),
    ],
)
def test_config_loader_rejects_invalid_fields(old: str, new: str, error: type[Exception]) -> None:
    with pytest.raises(error):
        config_from_toml_bytes(_replace(old, new))


def test_config_loader_requires_exact_prompt_and_root_keys() -> None:
    with pytest.raises(ValueError, match="config keys differ"):
        config_from_toml_bytes(_replace("[[prompts]]", "unknown = 1\n\n[[prompts]]"))
    with pytest.raises(ValueError, match="prompt 0 keys differ"):
        config_from_toml_bytes(
            _replace(
                'id = "stage-02-continuity"',
                'id = "stage-02-continuity"\nunknown = 1',
            )
        )


def test_config_dataclass_rejects_nonfinite_types_revision_and_prompt_shapes() -> None:
    config = config_from_toml_bytes(_payload())
    with pytest.raises(TypeError, match="real number"):
        replace(config, temperature="hot")
    with pytest.raises(ValueError, match="finite"):
        replace(config, temperature=float("nan"))
    with pytest.raises(ValueError, match="model_revision"):
        replace(config, model_revision="A" * 40)
    with pytest.raises(ValueError, match="exactly three"):
        replace(config, prompts=config.prompts[:2])
    with pytest.raises(ValueError, match="exactly three"):
        replace(config, prompts=list(config.prompts))
    with pytest.raises(TypeError, match="PromptFixture"):
        replace(config, prompts=(config.prompts[0], config.prompts[1], "bad"))


def test_config_parser_rejects_wrong_schema_and_prompt_container(monkeypatch) -> None:
    with pytest.raises(ValueError, match="schema_version"):
        config_from_toml_bytes(_replace("schema_version = 1", "schema_version = 2"))
    parsed = __import__("tomllib").loads(_payload().decode())
    parsed["prompts"] = "bad"
    monkeypatch.setattr("watermark_lab.lab03_config.tomllib.loads", lambda text: parsed)
    with pytest.raises(TypeError, match="array of tables"):
        config_from_toml_bytes(_payload())


def test_config_parser_rejects_non_table_documents_and_prompts(monkeypatch) -> None:
    monkeypatch.setattr("watermark_lab.lab03_config.tomllib.loads", lambda text: [])
    with pytest.raises(TypeError, match="TOML table"):
        config_from_toml_bytes(_payload())
    monkeypatch.undo()
    parsed = __import__("tomllib").loads(_payload().decode())
    parsed["prompts"][0] = "bad"
    monkeypatch.setattr("watermark_lab.lab03_config.tomllib.loads", lambda text: parsed)
    with pytest.raises(TypeError, match="prompt 0"):
        config_from_toml_bytes(_payload())
