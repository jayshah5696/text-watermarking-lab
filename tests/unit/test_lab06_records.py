from pathlib import Path

import pytest

from watermark_lab.lab06_config import lab06_config_from_toml_bytes
from watermark_lab.lab06_records import build_calibration_artifact, score_record


def selected_config():
    return lab06_config_from_toml_bytes(Path("configs/lab_06.toml").read_bytes())


def valid_raw():
    config = selected_config()
    manifests = [
        {
            "dataset_row_index": index,
            "url": f"https://example.test/{index}",
            "timestamp": "2020-01-01T00:00:00Z",
            "text_sha256": f"{index:064x}",
            "full_token_count": 500,
            "split": "calibration" if index < 1000 else "paired_test",
            "selection_rank": index,
            "prompt_token_range": [0, 50],
            "continuation_token_range": [50, 450],
        }
        for index in range(1024)
    ]
    all_pairs = score_record(hits=100, trials=399, config=config)
    distinct_pairs = score_record(hits=100, trials=399, config=config)
    scores = [
        {
            "selection_rank": index,
            "dataset_row_index": index,
            "all_pairs": all_pairs,
            "distinct_pairs": distinct_pairs,
        }
        for index in range(1000)
    ]
    tokens = [
        {
            "position": position,
            "token_id": position,
            "piece": str(position),
            "eligible": position > 0,
            "previous_token_id": position - 1 if position > 0 else None,
            "is_green": (position <= 100) if position > 0 else None,
        }
        for position in range(400)
    ]
    return {
        "schema_version": 1,
        "source_commit": "a" * 40,
        "config_sha256": "b" * 64,
        "python_version": "3.12.0",
        "torch_version": "2.13.0",
        "transformers_version": "5.14.1",
        "huggingface_hub_version": "1.26.0",
        "modal_sdk_version": "1.5.3",
        "gpu_name": "NVIDIA L4",
        "cuda_runtime": "13.0",
        "dataset_file_sha256": config.dataset_file_sha256,
        "dataset_file_bytes": config.dataset_file_bytes,
        "dataset_rows_read": 1024,
        "tokenizer_files": {},
        "secret_used": False,
        "volume_used": False,
        "selection": {
            "last_scanned_row_index": 1023,
            "rejection_counts": {
                "too_short": 0,
                "duplicate_text": 0,
                "obvious_list": 0,
                "code_dump": 0,
                "low_letter_fraction": 0,
            },
            "manifest": manifests,
        },
        "scores": scores,
        "spine": {
            "selection_rank": 0,
            "dataset_row_index": 0,
            "url": "https://example.test/0",
            "timestamp": "2020-01-01T00:00:00Z",
            "text_sha256": "0" * 64,
            "full_token_count": 500,
            "prompt_excerpt": "prompt",
            "continuation_excerpt": "continuation",
            "prompt_token_ids": list(range(50)),
            "continuation_token_ids": list(range(400)),
            "token_evidence": tokens,
        },
        "runtime_ns": 1,
    }


def test_build_calibration_artifact_recomputes_every_summary() -> None:
    artifact = build_calibration_artifact(valid_raw(), selected_config())
    assert artifact["summary"]["calibration_rows"] == 1000
    assert artifact["summary"]["paired_test_rows"] == 24
    assert artifact["summary"]["positive_all_pair_rows"] == 0
    assert artifact["summary"]["maximum_all_pair_selection_rank"] == 0
    assert artifact["summary"]["empirical_resolution"] == 0.001


def test_build_calibration_artifact_rejects_score_and_spine_tampering() -> None:
    raw = valid_raw()
    raw["scores"][25]["all_pairs"]["z_score"] += 1
    with pytest.raises(ValueError, match="z_score differs"):
        build_calibration_artifact(raw, selected_config())

    raw = valid_raw()
    raw["spine"]["token_evidence"][1]["is_green"] = False
    with pytest.raises(ValueError, match="colors differ"):
        build_calibration_artifact(raw, selected_config())


def test_build_calibration_artifact_rejects_split_overlap() -> None:
    raw = valid_raw()
    raw["selection"]["manifest"][1000]["text_sha256"] = raw["selection"]["manifest"][0][
        "text_sha256"
    ]
    with pytest.raises(ValueError, match="overlap"):
        build_calibration_artifact(raw, selected_config())
