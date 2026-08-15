import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from watermark_lab.lab05_config import config_from_toml_bytes
from watermark_lab.lab05_examples import (
    build_examples_trace,
    examples_to_json_bytes,
    examples_to_markdown_bytes,
)


def raw_fixture() -> tuple[dict[str, Any], Any]:
    smoke = json.loads(Path("artifacts/lab-05/trace.json").read_text())
    config_bytes = Path("configs/lab_05_examples.toml").read_bytes()
    config = config_from_toml_bytes(config_bytes, expected_generation_calls=20)
    rows = smoke["records"]
    records: list[dict[str, Any]] = []
    for index, prompt in enumerate(config.prompts):
        for offset, condition in enumerate(("control", "reference_watermark")):
            row = copy.deepcopy(rows[offset])
            row["prompt_id"] = prompt.id
            row["prompt_text"] = prompt.text
            row["condition"] = condition
            row["seed"] = config.prompt_seed(prompt.id)
            row["copied_text"] = f"fixture {index} {condition} continuation"
            records.append(row)
    raw = {
        key: value
        for key, value in smoke.items()
        if key
        not in {
            "config",
            "claim_labels",
            "price_snapshot",
            "projections",
            "gate",
            "unavailable_measurements",
        }
    }
    raw["records"] = records
    raw["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    return raw, config


def test_builds_ten_pairs_with_p_value_definition() -> None:
    raw, config = raw_fixture()
    trace = build_examples_trace(raw, config)
    assert len(trace["pairs"]) == 10
    assert trace["pairs"][0]["control"]["z_score"] == pytest.approx(0.17407765595569785)
    assert "not the probability that the text is watermarked" in trace["interpretation"]["p_value"]
    assert examples_to_json_bytes(trace).endswith(b"\n")
    assert b"p-value" in examples_to_markdown_bytes(trace)


def test_rejects_order_seed_and_score_tampering() -> None:
    raw, config = raw_fixture()
    swapped = copy.deepcopy(raw)
    swapped["records"][0], swapped["records"][1] = (
        swapped["records"][1],
        swapped["records"][0],
    )
    with pytest.raises(ValueError, match="order"):
        build_examples_trace(swapped, config)
    seed = copy.deepcopy(raw)
    seed["records"][0]["seed"] += 1
    with pytest.raises(ValueError, match="seeds"):
        build_examples_trace(seed, config)
    score = copy.deepcopy(raw)
    score["records"][0]["detector_results"][0]["z_score"] += 1
    with pytest.raises(ValueError, match="z score"):
        build_examples_trace(score, config)


def test_rejects_invalid_p_value_and_decision() -> None:
    raw, config = raw_fixture()
    p_value = copy.deepcopy(raw)
    p_value["records"][0]["detector_results"][0]["p_value"] = 2.0
    with pytest.raises(ValueError, match="p-value"):
        build_examples_trace(p_value, config)
    decision = copy.deepcopy(raw)
    decision["records"][0]["detector_results"][0]["prediction"] = True
    with pytest.raises(ValueError, match="strict configured cutoff"):
        build_examples_trace(decision, config)
