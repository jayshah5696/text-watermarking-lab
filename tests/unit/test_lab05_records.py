import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pytest

from watermark_lab.lab05_config import config_from_toml_bytes
from watermark_lab.lab05_records import (
    build_selected_trace,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)


def fixture() -> tuple[dict[str, Any], Any]:
    config_bytes = Path("configs/lab_05.toml").read_bytes()
    config = config_from_toml_bytes(config_bytes)
    selected = json.loads(Path("artifacts/lab-05/trace.json").read_text())
    derived = {
        "config",
        "claim_labels",
        "price_snapshot",
        "projections",
        "gate",
        "unavailable_measurements",
    }
    raw = {key: value for key, value in selected.items() if key not in derived}
    raw["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    return raw, config


def test_builds_projection_and_gate_from_remote_records() -> None:
    raw, config = fixture()
    trace = build_selected_trace(raw, config)
    assert trace["projections"][0]["total_generated_tokens"] == 9600
    assert trace["projections"][1]["total_generated_tokens"] == 19200
    assert trace["gate"]["throughput_pass"] is True
    assert trace["gate"]["vram_headroom_pass"] is True
    assert math.isclose(
        trace["projections"][0]["projected_gpu_only_usd"],
        trace["projections"][0]["projected_generation_seconds"] * 0.000222,
    )
    assert trace_to_json_bytes(trace).endswith(b"\n")
    assert b"GPU-only linear projections" in trace_to_markdown_bytes(trace)


def test_rejects_record_order_seed_and_detector_tampering() -> None:
    raw, config = fixture()
    swapped = copy.deepcopy(raw)
    swapped["records"][0], swapped["records"][1] = swapped["records"][1], swapped["records"][0]
    with pytest.raises(ValueError, match="order"):
        build_selected_trace(swapped, config)
    wrong_seed = copy.deepcopy(raw)
    wrong_seed["records"][0]["seed"] += 1
    with pytest.raises(ValueError, match="seed"):
        build_selected_trace(wrong_seed, config)
    wrong_score = copy.deepcopy(raw)
    wrong_score["records"][0]["detector_results"][0]["z_score"] += 1.0
    with pytest.raises(ValueError, match="z score"):
        build_selected_trace(wrong_score, config)


def test_rejects_secret_volume_gpu_and_short_text() -> None:
    raw, config = fixture()
    for field in ("secret_used", "volume_used"):
        changed = copy.deepcopy(raw)
        changed[field] = True
        with pytest.raises(ValueError, match="neither Secret nor Volume"):
            build_selected_trace(changed, config)
    wrong_gpu = copy.deepcopy(raw)
    wrong_gpu["gpu_name"] = "NVIDIA A10"
    with pytest.raises(ValueError, match="GPU or dtype"):
        build_selected_trace(wrong_gpu, config)
    short = copy.deepcopy(raw)
    short["records"][0]["copied_token_ids"] = [1]
    with pytest.raises(ValueError, match="too short"):
        build_selected_trace(short, config)
