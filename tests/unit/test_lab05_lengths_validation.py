import copy
from dataclasses import replace
from pathlib import Path

import pytest
from test_lab05_lengths import fixture

from watermark_lab.lab05_lengths import build_lengths_trace
from watermark_lab.lab05_lengths_config import lengths_config_from_toml_bytes


def test_config_rejects_locked_and_prompt_drift() -> None:
    payload = Path("configs/lab_05_lengths.toml").read_bytes()
    with pytest.raises(ValueError, match="model_id"):
        lengths_config_from_toml_bytes(payload.replace(b"google/gemma-4-E2B-it", b"other/model"))
    with pytest.raises(ValueError, match="four prompts"):
        lengths_config_from_toml_bytes(
            payload.replace(b"max_new_tokens = 200\ntext =", b"max_new_tokens = 400\ntext =", 1)
        )
    with pytest.raises(ValueError, match="keys differ"):
        lengths_config_from_toml_bytes(
            payload.replace(b"schema_version = 1\n", b"schema_version = 1\nextra = 1\n")
        )
    with pytest.raises(TypeError, match="use_volume"):
        lengths_config_from_toml_bytes(payload.replace(b"use_volume = false", b"use_volume = 0"))
    with pytest.raises(ValueError, match="blank line"):
        lengths_config_from_toml_bytes(
            payload.replace(
                (
                    b'instruction_prefix = "Continue the passage naturally with a detailed, '
                    b"coherent response. Do not summarize early. Return only the continuation."
                    b'\\n\\n"'
                ),
                b'instruction_prefix = "Continue"',
            )
        )
    with pytest.raises(ValueError, match="twelve unique prompts"):
        lengths_config_from_toml_bytes(
            payload.replace(b'id = "lost-language"', b'id = "generation-ship"')
        )
    with pytest.raises(TypeError, match="non-empty"):
        lengths_config_from_toml_bytes(payload.replace(b'id = "story-map"', b'id = ""'))


def test_config_rejects_bad_prompt_table_and_number_type() -> None:
    payload = Path("configs/lab_05_lengths.toml").read_bytes()
    with pytest.raises(ValueError, match="needs id"):
        lengths_config_from_toml_bytes(
            payload.replace(b'id = "story-map"\n', b'id = "story-map"\nextra_prompt = 1\n')
        )
    with pytest.raises(TypeError, match="top_k"):
        lengths_config_from_toml_bytes(payload.replace(b"top_k = 40", b'top_k = "40"'))
    with pytest.raises(TypeError, match="temperature"):
        lengths_config_from_toml_bytes(
            payload.replace(b"temperature = 0.8", b'temperature = "0.8"')
        )


def test_trace_rejects_resource_provenance_and_counts() -> None:
    raw, config = fixture()
    with pytest.raises(ValueError, match="twenty-four"):
        build_lengths_trace({**raw, "records": raw["records"][:-1]}, config)
    for field, value, match in (
        ("gpu_name", "A10", "GPU or dtype"),
        ("dtype", "torch.float32", "GPU or dtype"),
        ("secret_used", True, "neither Secret nor Volume"),
        ("volume_used", True, "neither Secret nor Volume"),
        ("source_commit", "short", "source_commit"),
        ("config_sha256", "short", "config_sha256"),
    ):
        changed = copy.deepcopy(raw)
        changed[field] = value
        with pytest.raises(ValueError, match=match):
            build_lengths_trace(changed, config)


def test_trace_rejects_token_count_pvalue_and_decision_drift() -> None:
    raw, config = fixture()
    length = copy.deepcopy(raw)
    length["records"][0]["token_evidence"] = length["records"][0]["token_evidence"][:-1]
    with pytest.raises(ValueError, match="length differs"):
        build_lengths_trace(length, config)
    count = copy.deepcopy(raw)
    count["records"][0]["evidence"]["num_green_tokens"] += 1
    with pytest.raises(ValueError, match="detector totals"):
        build_lengths_trace(count, config)
    p_value = copy.deepcopy(raw)
    p_value["records"][0]["evidence"]["p_value"] = 2
    with pytest.raises(ValueError, match="p-value"):
        build_lengths_trace(p_value, config)
    decision = copy.deepcopy(raw)
    decision["records"][0]["evidence"]["prediction"] = True
    with pytest.raises(ValueError, match="strict cutoff"):
        build_lengths_trace(decision, config)


def test_config_dataclass_rejects_non_ladder_call_count() -> None:
    _, config = fixture()
    with pytest.raises(ValueError, match="locks max_generation_calls"):
        replace(config, max_generation_calls=23)
