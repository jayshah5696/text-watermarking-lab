# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Approval-gated detector-only Modal runner for Stage 6."""

from __future__ import annotations

import json

import modal

APP_NAME = "text-watermarking-lab-06"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "huggingface-hub==1.26.0",
        "torch==2.13.0",
        "transformers==5.14.1",
    )
    .add_local_python_source("watermark_lab")
)
app = modal.App(APP_NAME, image=image)


@app.function(gpu="L4", timeout=3600, max_containers=1, single_use_containers=True)
def run_calibration(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Select and score the exact frozen natural-web calibration cohort."""

    import gzip
    import hashlib
    import platform
    import tempfile
    import time
    import urllib.request
    from importlib.metadata import version
    from itertools import pairwise
    from pathlib import Path
    from typing import Any

    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, WatermarkingConfig

    from watermark_lab.dataset import (
        continuation_ids,
        select_rows,
        selection_manifest,
        short_excerpt,
    )
    from watermark_lab.lab06_config import lab06_config_from_toml_bytes
    from watermark_lab.lab06_records import score_record
    from watermark_lab.lab06_scoring import resolve_pair_memberships, score_sequence

    config = lab06_config_from_toml_bytes(config_json.encode())
    if config.max_remote_invocations != 1 or config.modal_gpu != "L4":
        raise RuntimeError("Stage 6 resource guard rejected the configuration")
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != "NVIDIA L4":
        raise RuntimeError("Stage 6 requires one NVIDIA L4")
    if (
        version("torch") != config.torch_version
        or version("transformers") != config.transformers_version
        or version("huggingface-hub") != config.huggingface_hub_version
    ):
        raise RuntimeError("Stage 6 remote package versions differ")

    start_ns = time.perf_counter_ns()
    dataset_url = (
        f"https://huggingface.co/datasets/{config.dataset_id}/resolve/"
        f"{config.dataset_revision}/{config.dataset_file}"
    )
    with tempfile.TemporaryDirectory() as temporary:
        dataset_path = Path(temporary) / "c4-validation.json.gz"
        urllib.request.urlretrieve(dataset_url, dataset_path)
        dataset_bytes = dataset_path.read_bytes()
        if len(dataset_bytes) != config.dataset_file_bytes:
            raise RuntimeError("Stage 6 dataset byte count differs")
        dataset_hash = hashlib.sha256(dataset_bytes).hexdigest()
        if dataset_hash != config.dataset_file_sha256:
            raise RuntimeError("Stage 6 dataset hash differs")

        tokenizer_path = Path(
            snapshot_download(
                repo_id=config.tokenizer_id,
                revision=config.tokenizer_revision,
                allow_patterns=["tokenizer.json", "tokenizer_config.json"],
            )
        )
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)
        tokenizer_files = {
            name: {
                "bytes": (tokenizer_path / name).stat().st_size,
                "sha256": hashlib.sha256((tokenizer_path / name).read_bytes()).hexdigest(),
            }
            for name in ("tokenizer.json", "tokenizer_config.json")
        }

        def rows() -> Any:
            with gzip.open(dataset_path, "rt", encoding="utf-8") as stream:
                for line in stream:
                    yield json.loads(line)

        selections, rejection_counts, last_index = select_rows(rows(), tokenizer, config)
        manifests = [selection_manifest(selection, config) for selection in selections]
        calibration = selections[: config.calibration_rows]
        sequences = [continuation_ids(selection, config) for selection in calibration]
        if any(len(sequence) != config.continuation_tokens for sequence in sequences):
            raise RuntimeError("Stage 6 continuation length differs")

        watermark = WatermarkingConfig(
            greenlist_ratio=config.green_fraction,
            bias=config.watermark_bias,
            hashing_key=config.generation_key,
            seeding_scheme=config.seeding_scheme,
            context_width=config.context_width,
        )
        processor = watermark.construct_processor(int(tokenizer.vocab_size), "cuda")
        stamps = torch.zeros(int(tokenizer.vocab_size), device="cuda", dtype=torch.int32)
        selector_calls = 0

        def selector(previous: int, targets: tuple[int, ...]) -> dict[int, bool]:
            nonlocal selector_calls
            selector_calls += 1
            prefix = torch.tensor([previous], device="cuda", dtype=torch.long)
            green_ids = processor._get_greenlist_ids(  # pyright: ignore[reportPrivateUsage]
                prefix
            )
            stamps[green_ids] = selector_calls
            target_tensor = torch.tensor(targets, device="cuda", dtype=torch.long)
            results = (stamps[target_tensor] == selector_calls).cpu().tolist()
            if selector_calls % 1_000 == 0:
                print(f"resolved {selector_calls} distinct Stage 6 contexts")
            return dict(zip(targets, (bool(result) for result in results), strict=True))

        memberships = resolve_pair_memberships(sequences, selector)
        for sequence in sequences[:1]:
            for previous, target in pairwise(sequence[:9]):
                direct_green = processor._get_greenlist_ids(  # pyright: ignore[reportPrivateUsage]
                    torch.tensor([previous], device="cuda", dtype=torch.long)
                )
                direct_result = bool((direct_green == target).any().item())
                if memberships[(previous, target)] is not direct_result:
                    raise RuntimeError("grouped Stage 6 membership differs from direct reference")
        scores: list[dict[str, Any]] = []
        for selection, sequence in zip(calibration, sequences, strict=True):
            counts = score_sequence(sequence, memberships)
            scores.append(
                {
                    "selection_rank": selection.selection_rank,
                    "dataset_row_index": selection.candidate.row_index,
                    "all_pairs": score_record(
                        hits=counts.all_hits, trials=counts.all_trials, config=config
                    ),
                    "distinct_pairs": score_record(
                        hits=counts.distinct_hits, trials=counts.distinct_trials, config=config
                    ),
                }
            )

        spine_selection = calibration[0]
        spine_sequence = sequences[0]
        token_evidence: list[dict[str, Any]] = []
        for position, token_id in enumerate(spine_sequence):
            eligible = position >= config.context_width
            previous = spine_sequence[position - 1] if eligible else None
            token_evidence.append(
                {
                    "position": position,
                    "token_id": token_id,
                    "piece": tokenizer.decode([token_id], clean_up_tokenization_spaces=False),
                    "eligible": eligible,
                    "previous_token_id": previous,
                    "is_green": memberships[(previous, token_id)] if previous is not None else None,
                }
            )
        source_ids = spine_selection.candidate.token_ids
        spine = {
            "selection_rank": 0,
            "dataset_row_index": spine_selection.candidate.row_index,
            "url": spine_selection.candidate.url,
            "timestamp": spine_selection.candidate.timestamp,
            "text_sha256": spine_selection.candidate.text_sha256,
            "full_token_count": len(source_ids),
            "prompt_excerpt": short_excerpt(source_ids[: config.prompt_tokens], tokenizer),
            "continuation_excerpt": short_excerpt(spine_sequence, tokenizer),
            "prompt_token_ids": source_ids[: config.prompt_tokens],
            "continuation_token_ids": spine_sequence,
            "token_evidence": token_evidence,
        }

    result = {
        "schema_version": 1,
        "source_commit": source_commit,
        "config_sha256": config_sha256,
        "python_version": platform.python_version(),
        "torch_version": version("torch"),
        "transformers_version": version("transformers"),
        "huggingface_hub_version": version("huggingface-hub"),
        "modal_sdk_version": config.modal_sdk_version,
        "gpu_name": torch.cuda.get_device_name(0),
        "cuda_runtime": torch.version.cuda,
        "dataset_file_sha256": dataset_hash,
        "dataset_file_bytes": len(dataset_bytes),
        "dataset_rows_read": last_index + 1,
        "tokenizer_files": tokenizer_files,
        "secret_used": False,
        "volume_used": False,
        "selection": {
            "last_scanned_row_index": last_index,
            "rejection_counts": rejection_counts,
            "manifest": manifests,
        },
        "scores": scores,
        "spine": spine,
        "runtime_ns": time.perf_counter_ns() - start_ns,
    }
    return json.dumps(result, allow_nan=False, sort_keys=True)
