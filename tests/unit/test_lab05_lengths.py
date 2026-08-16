import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from watermark_lab.lab05_lengths import (
    build_lengths_trace,
    lengths_to_json_bytes,
    lengths_to_markdown_bytes,
)
from watermark_lab.lab05_lengths_config import lengths_config_from_toml_bytes


def fixture() -> tuple[dict[str, Any], Any]:
    examples = json.loads(Path("artifacts/lab-05/examples.json").read_text())
    config_bytes = Path("configs/lab_05_lengths.toml").read_bytes()
    config = lengths_config_from_toml_bytes(config_bytes)
    source = examples["records"]
    records: list[dict[str, Any]] = []
    for index, prompt in enumerate(config.prompts):
        for offset, condition in enumerate(("control", "reference_watermark")):
            base = source[offset]
            ids = list(base["copied_token_ids"])
            evidence = copy.deepcopy(base["detector_results"][0])
            green = evidence["num_green_tokens"]
            tokens = []
            remaining = green
            for position, token_id in enumerate(ids):
                eligible = position > 0
                is_green = eligible and remaining > 0
                remaining -= int(is_green)
                tokens.append(
                    {
                        "position": position,
                        "token_id": token_id,
                        "piece": f"t{position}",
                        "eligible": eligible,
                        "is_green": is_green if eligible else None,
                    }
                )
            records.append(
                {
                    "prompt_id": prompt.id,
                    "prompt_text": prompt.text,
                    "max_new_tokens": prompt.max_new_tokens,
                    "condition": condition,
                    "seed": config.prompt_seed(prompt.id),
                    "generated_token_ids": list(base["generated_token_ids"]),
                    "copied_text": f"fixture {index} {condition}",
                    "copied_token_ids": ids,
                    "stop_reason": "end_token",
                    "evidence": evidence,
                    "token_evidence": tokens,
                }
            )
    raw = {
        "source_commit": examples["source_commit"],
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "gpu_name": "NVIDIA L4",
        "dtype": "torch.bfloat16",
        "secret_used": False,
        "volume_used": False,
        "records": records,
    }
    return raw, config


def test_loads_frozen_length_config() -> None:
    config = lengths_config_from_toml_bytes(Path("configs/lab_05_lengths.toml").read_bytes())
    assert len(config.prompts) == 12
    assert [prompt.max_new_tokens for prompt in config.prompts] == [200] * 4 + [400] * 4 + [800] * 4
    assert config.max_generation_calls == 24


def test_builds_pairs_and_token_color_summary() -> None:
    raw, config = fixture()
    trace = build_lengths_trace(raw, config)
    assert len(trace["pairs"]) == 12
    assert trace["pairs"][0]["control"]["token_evidence"][0]["is_green"] is None
    assert trace["summary"]["maximum_achieved_copied_tokens"] >= 2
    assert lengths_to_json_bytes(trace).endswith(b"\n")
    assert b"Caps are safety limits" in lengths_to_markdown_bytes(trace)


def test_rejects_order_seed_token_and_score_tampering() -> None:
    raw, config = fixture()
    order = copy.deepcopy(raw)
    order["records"][0]["max_new_tokens"] = 400
    with pytest.raises(ValueError, match="order differs"):
        build_lengths_trace(order, config)
    seed = copy.deepcopy(raw)
    seed["records"][0]["seed"] += 1
    with pytest.raises(ValueError, match="seeds differ"):
        build_lengths_trace(seed, config)
    token = copy.deepcopy(raw)
    token["records"][0]["token_evidence"][1]["token_id"] += 1
    with pytest.raises(ValueError, match="identity"):
        build_lengths_trace(token, config)
    score = copy.deepcopy(raw)
    score["records"][0]["evidence"]["z_score"] += 1
    with pytest.raises(ValueError, match="z score"):
        build_lengths_trace(score, config)
