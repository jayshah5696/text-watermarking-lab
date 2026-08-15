from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from watermark_lab.lab04_config import REFERENCE_ORDER, STAGE_03_ORDER, config_from_toml_bytes

ROOT = Path(__file__).resolve().parents[2]


def _payload() -> bytes:
    return (ROOT / "configs/lab_04.toml").read_bytes()


def _replace(old: str, new: str) -> bytes:
    return _payload().decode().replace(old, new).encode()


def test_locked_stage_04_config_loads() -> None:
    config = config_from_toml_bytes(_payload())
    assert config.model_id == "openai-community/gpt2"
    assert config.model_revision == "607a30d783dfa663caf39e06633721c8d4cfcd7e"
    assert config.model_safetensors_bytes == 548_105_171
    assert config.device == "cpu"
    assert config.reference_processor_order == REFERENCE_ORDER
    assert config.stage_03_processor_order == STAGE_03_ORDER
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
        ('model_id = "openai-community/gpt2"', 'model_id = "gpt2"', ValueError),
        ("607a30d783dfa663caf39e06633721c8d4cfcd7e", "A" * 40, ValueError),
        ('model_license = "mit"', 'model_license = "other"', ValueError),
        ("model_safetensors_bytes = 548105171", "model_safetensors_bytes = 0", ValueError),
        ('device = "cpu"', 'device = "mps"', ValueError),
        ("base_seed = 20260812", "base_seed = true", TypeError),
        ("max_new_tokens = 40", "max_new_tokens = 1", ValueError),
        ("temperature = 0.8", "temperature = 0.0", ValueError),
        ("top_k = 40", "top_k = 0", ValueError),
        ("top_p = 0.95", "top_p = 1.1", ValueError),
        ("green_fraction = 0.25", "green_fraction = 1.0", ValueError),
        ("watermark_bias = 2.0", "watermark_bias = -1.0", ValueError),
        ("comparison_key = 15485867", "comparison_key = 15485863", ValueError),
        ('seeding_scheme = "lefthash"', 'seeding_scheme = "selfhash"', ValueError),
        ("context_width = 1", "context_width = 2", ValueError),
        ("trace_candidates = 5", "trace_candidates = 41", ValueError),
        ('"temperature", "top_k"', '"top_k", "temperature"', ValueError),
        ('id = "notebook"', 'id = "stage-02-continuity"', ValueError),
        ('text = "The student', 'text = ""\n# The student', ValueError),
    ],
)
def test_config_loader_rejects_invalid_fields(old: str, new: str, error: type[Exception]) -> None:
    with pytest.raises(error):
        config_from_toml_bytes(_replace(old, new))


def test_config_loader_requires_exact_keys_and_prompt_tables() -> None:
    with pytest.raises(ValueError, match="config keys differ"):
        config_from_toml_bytes(_replace("[[prompts]]", "unknown = 1\n\n[[prompts]]"))
    with pytest.raises(ValueError, match="prompt 0 keys differ"):
        config_from_toml_bytes(
            _replace(
                'id = "stage-02-continuity"',
                'id = "stage-02-continuity"\nunknown = 1',
            )
        )


def test_config_dataclass_rejects_nonfinite_and_bad_shapes() -> None:
    config = config_from_toml_bytes(_payload())
    with pytest.raises(TypeError, match="real number"):
        replace(config, temperature="hot")
    with pytest.raises(ValueError, match="finite"):
        replace(config, z_threshold=float("nan"))
    with pytest.raises(ValueError, match="exactly three"):
        replace(config, prompts=config.prompts[:2])
    with pytest.raises(TypeError, match="ReferencePrompt"):
        replace(config, prompts=(config.prompts[0], config.prompts[1], "bad"))
    with pytest.raises(ValueError, match="Transformers processor order"):
        replace(config, reference_processor_order=STAGE_03_ORDER)
    with pytest.raises(ValueError, match="Stage 3 comparison order"):
        replace(config, stage_03_processor_order=REFERENCE_ORDER)


def test_config_parser_rejects_wrong_containers(monkeypatch: pytest.MonkeyPatch) -> None:
    parsed = __import__("tomllib").loads(_payload().decode())
    parsed["prompts"] = "bad"
    monkeypatch.setattr("watermark_lab.lab04_config.tomllib.loads", lambda text: parsed)
    with pytest.raises(TypeError, match="array of tables"):
        config_from_toml_bytes(_payload())
    monkeypatch.undo()
    monkeypatch.setattr("watermark_lab.lab04_config.tomllib.loads", lambda text: [])
    with pytest.raises(TypeError, match="TOML table"):
        config_from_toml_bytes(_payload())
    monkeypatch.undo()
    parsed = __import__("tomllib").loads(_payload().decode())
    parsed["prompts"][0] = "bad"
    monkeypatch.setattr("watermark_lab.lab04_config.tomllib.loads", lambda text: parsed)
    with pytest.raises(TypeError, match="prompt 0"):
        config_from_toml_bytes(_payload())


def test_config_parser_rejects_schema_and_non_array_order() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        config_from_toml_bytes(_replace("schema_version = 1", "schema_version = 2"))
    with pytest.raises(TypeError, match="must be an array"):
        config_from_toml_bytes(
            _replace(
                'reference_processor_order = ["temperature", "top_k", "top_p", "watermark"]',
                'reference_processor_order = "temperature"',
            )
        )
