import math
from pathlib import Path

from watermark_lab.lab07_config import lab07_config_from_toml_bytes
from watermark_lab.lab07_records import (
    RAW_KEYS,
    bootstrap_interval,
    build_stage07_artifact,
    choose_inconvenient_row,
    score_record,
    stage07_json_bytes,
    stage07_markdown_bytes,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIG = lab07_config_from_toml_bytes((ROOT / "configs/lab_07.toml").read_bytes())


def test_stage_07_score_uses_stage_01_formula_and_strict_cutoff() -> None:
    score = score_record(hits=17, trials=39, config=CONFIG)
    assert math.isclose(score["z_score"], 2.6810509484219405, abs_tol=1e-15)
    assert score["prediction"] is False
    assert 0 < score["exact_upper_tail"] < 1


def test_paired_bootstrap_is_deterministic_and_keeps_sign() -> None:
    first = bootstrap_interval((1.0, 2.0, 3.0), replicates=1000, seed=7)
    second = bootstrap_interval((1.0, 2.0, 3.0), replicates=1000, seed=7)
    assert first == second
    assert first[0] > 0
    assert first[1] >= first[0]


def _tokens(token_ids: list[int], green_period: int) -> list[dict[str, object]]:
    return [
        {
            "position": position,
            "token_id": token_id,
            "piece": f"t{token_id}",
            "eligible": position > 0,
            "previous_token_id": token_ids[position - 1] if position > 0 else None,
            "is_green": position % green_period == 0 if position > 0 else None,
        }
        for position, token_id in enumerate(token_ids)
    ]


def _raw_fixture() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    generated_total = 0
    for index in range(24):
        rank = 1000 + index
        text_hash = f"{rank:064x}"
        prompt_ids = list(range(index * 1000, index * 1000 + 50))
        natural_ids = list(range(index * 1000 + 50, index * 1000 + 450))
        control_ids = list(range(index * 2000 + 30_000, index * 2000 + 30_400))
        watermarked_ids = list(range(index * 2000 + 31_000, index * 2000 + 31_400))
        generated_total += 800
        conditions = {
            condition: {
                "condition": condition,
                "status": "ok",
                "copied_text": f"{condition} copied text {rank}",
                "copied_token_ids": token_ids,
                "copied_token_count": len(token_ids),
                "generated_token_ids": token_ids,
                "generated_token_count": len(token_ids),
                "stop_reason": "token_limit",
            }
            for condition, token_ids in (
                ("control", control_ids),
                ("watermarked", watermarked_ids),
            )
        }
        rows.append(
            {
                "selection_rank": rank,
                "dataset_row_index": 2412 + index,
                "url": f"https://example.test/{rank}",
                "timestamp": "2019-04-25T17:52:31Z",
                "text_sha256": text_hash,
                "seed": CONFIG.prompt_seed(rank, text_hash),
                "source_prompt_text": f"prompt {rank}",
                "source_prompt_token_ids": prompt_ids,
                "prompt_roundtrip_ok": True,
                "natural_continuation_token_ids": natural_ids,
                "conditions": conditions,
                "token_evidence": {
                    "control_correct": _tokens(control_ids, 4 if index != 1 else 2),
                    "natural_correct": _tokens(natural_ids, 5),
                    "watermarked_correct": _tokens(watermarked_ids, 2 if index != 1 else 4),
                    "watermarked_comparison": _tokens(watermarked_ids, 4),
                },
            }
        )
    raw: dict[str, object] = {
        "schema_version": 1,
        "source_commit": "a" * 40,
        "config_sha256": "b" * 64,
        "manifest_sha256": CONFIG.manifest_sha256,
        "python_version": "3.12.7",
        "torch_version": CONFIG.torch_version,
        "transformers_version": CONFIG.transformers_version,
        "huggingface_hub_version": CONFIG.huggingface_hub_version,
        "modal_sdk_version": CONFIG.modal_sdk_version,
        "model_revision": CONFIG.model_revision,
        "model_class": CONFIG.model_class,
        "model_safetensors_bytes": CONFIG.model_safetensors_bytes,
        "dataset_file_sha256": CONFIG.dataset_file_sha256,
        "dataset_file_bytes": CONFIG.dataset_file_bytes,
        "gpu_name": "NVIDIA L4",
        "cuda_runtime": "13.0",
        "dtype": "torch.bfloat16",
        "total_vram_bytes": 24_000_000_000,
        "model_download_ns": 1,
        "model_load_ns": 1,
        "runtime_ns": 1,
        "secret_used": False,
        "volume_used": False,
        "generation_call_count": 48,
        "generated_token_id_count": generated_total,
        "rows": rows,
    }
    assert set(raw) == RAW_KEYS
    return raw


def test_full_stage_07_artifact_rebuilds_all_rows_prefixes_and_intervals() -> None:
    artifact = build_stage07_artifact(_raw_fixture(), CONFIG)
    assert len(artifact["selected_rows"]) == 24
    assert artifact["prefix_summary"]["400"]["complete_rows"] == 24
    assert artifact["prefix_summary"]["400"]["cutoff_counts"]["watermarked_correct"] == 23
    assert artifact["teaching_selection"] == {
        "spine_selection_rank": 1000,
        "inconvenient_selection_rank": 1001,
        "inconvenient_reason": "watermarked_not_above_control",
        "inconvenient_prefix": 400,
    }
    assert stage07_json_bytes(artifact).endswith(b"\n")
    markdown = stage07_markdown_bytes(artifact)
    assert b"prefix 400" in markdown
    assert b"selection 1001" in markdown


def test_inconvenient_row_rule_prefers_adverse_control_comparison() -> None:
    rows = [
        {
            "selection_rank": 1000,
            "prefix_scores": {
                "40": {
                    "watermarked_correct": {"z_score": 2.0},
                    "control_correct": {"z_score": 0.0, "prediction": False},
                    "natural_correct": {"z_score": 0.0, "prediction": False},
                    "watermarked_comparison": {"z_score": 0.0},
                }
            },
        },
        {
            "selection_rank": 1001,
            "prefix_scores": {
                "40": {
                    "watermarked_correct": {"z_score": 1.0},
                    "control_correct": {"z_score": 1.5, "prediction": False},
                    "natural_correct": {"z_score": 0.0, "prediction": False},
                    "watermarked_comparison": {"z_score": 0.0},
                }
            },
        },
    ]
    assert choose_inconvenient_row(rows) == (1, "watermarked_not_above_control", 40)
