# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Approval-gated Stage 7 paired Gemma runner."""

from __future__ import annotations

import json

import modal

APP_NAME = "text-watermarking-lab-07"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "huggingface-hub==1.26.0",
        "librosa==0.11.0",
        "torch==2.13.0",
        "torchvision==0.28.0",
        "transformers==5.14.1",
    )
    .add_local_python_source("watermark_lab")
)
app = modal.App(APP_NAME, image=image)


@app.function(gpu="L4", timeout=3600, max_containers=1, single_use_containers=True)
def run_core(
    config_json: str,
    paired_manifest_json: str,
    source_commit: str,
    config_sha256: str,
) -> str:
    """Run the exact 24-row, 48-call paired core fixture once."""

    import gzip
    import hashlib
    import platform
    import tempfile
    import time
    import urllib.request
    from importlib.metadata import version
    from pathlib import Path
    from typing import Any

    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForMultimodalLM, AutoProcessor

    from watermark_lab.gemma_adapter import Gemma4Adapter
    from watermark_lab.lab07_config import lab07_config_from_toml_bytes
    from watermark_lab.transformers_runtime import (
        SamplingProfile,
        WatermarkProfile,
        generation_kwargs,
    )

    config = lab07_config_from_toml_bytes(config_json.encode())
    if (
        config.max_remote_invocations != 1
        or config.max_generation_calls != 48
        or config.max_generated_token_ids != 19_200
        or config.modal_gpu != "L4"
        or config.max_cost_usd != 5.0
    ):
        raise RuntimeError("Stage 7 resource guard rejected the configuration")
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != "NVIDIA L4":
        raise RuntimeError("Stage 7 requires one NVIDIA L4")
    if (
        version("torch") != config.torch_version
        or version("transformers") != config.transformers_version
        or version("huggingface-hub") != config.huggingface_hub_version
    ):
        raise RuntimeError("Stage 7 remote package versions differ")

    paired = json.loads(paired_manifest_json)
    if len(paired) != 24 or [row["selection_rank"] for row in paired] != list(range(1000, 1024)):
        raise RuntimeError("Stage 7 paired manifest differs")

    start_ns = time.perf_counter_ns()
    dataset_url = (
        f"https://huggingface.co/datasets/{config.dataset_id}/resolve/"
        f"{config.dataset_revision}/{config.dataset_file}"
    )
    with tempfile.TemporaryDirectory() as temporary:
        dataset_path = Path(temporary) / "c4-validation.json.gz"
        urllib.request.urlretrieve(dataset_url, dataset_path)
        dataset_bytes = dataset_path.read_bytes()
        dataset_hash = hashlib.sha256(dataset_bytes).hexdigest()
        if (
            len(dataset_bytes) != config.dataset_file_bytes
            or dataset_hash != config.dataset_file_sha256
        ):
            raise RuntimeError("Stage 7 dataset bytes differ")

        download_start = time.perf_counter_ns()
        snapshot = Path(snapshot_download(repo_id=config.model_id, revision=config.model_revision))
        model_download_ns = time.perf_counter_ns() - download_start
        model_file = snapshot / "model.safetensors"
        if not model_file.is_file() or model_file.stat().st_size != config.model_safetensors_bytes:
            raise RuntimeError("Stage 7 model file differs")
        load_start = time.perf_counter_ns()
        processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
        model = AutoModelForMultimodalLM.from_pretrained(
            snapshot, local_files_only=True, dtype=torch.bfloat16
        ).to("cuda")
        model.eval()
        torch.cuda.synchronize()
        model_load_ns = time.perf_counter_ns() - load_start
        adapter = Gemma4Adapter(model, processor, "cuda")
        if model.__class__.__name__ != config.model_class:
            raise RuntimeError("Stage 7 model class differs")

        generation_profile = WatermarkProfile(
            green_fraction=config.green_fraction,
            bias=config.watermark_bias,
            hashing_key=config.generation_key,
            seeding_scheme=config.seeding_scheme,
            context_width=config.context_width,
        )
        comparison_profile = WatermarkProfile(
            green_fraction=config.green_fraction,
            bias=config.watermark_bias,
            hashing_key=config.comparison_key,
            seeding_scheme=config.seeding_scheme,
            context_width=config.context_width,
        )
        sampling = SamplingProfile(
            max_new_tokens=config.max_new_tokens,
            temperature=config.temperature,
            top_k=config.top_k,
            top_p=config.top_p,
        )
        generation_processor = generation_profile.to_transformers().construct_processor(
            int(adapter.model_config.vocab_size), "cuda"
        )
        comparison_processor = comparison_profile.to_transformers().construct_processor(
            int(adapter.model_config.vocab_size), "cuda"
        )

        source_rows: dict[int, dict[str, str]] = {}
        wanted = {row["dataset_row_index"] for row in paired}
        with gzip.open(dataset_path, "rt", encoding="utf-8") as stream:
            for row_index, line in enumerate(stream):
                if row_index in wanted:
                    source_rows[row_index] = json.loads(line)
                if len(source_rows) == len(wanted):
                    break
        if len(source_rows) != 24:
            raise RuntimeError("Stage 7 source rows are missing")

        def token_trace(
            token_ids: tuple[int, ...], watermark_processor: Any
        ) -> list[dict[str, Any]]:
            tensor = adapter.token_tensor(token_ids)
            tokens: list[dict[str, Any]] = []
            cache: dict[tuple[int, int], bool] = {}
            for position, token_id in enumerate(token_ids):
                eligible = position >= config.context_width
                previous = token_ids[position - 1] if eligible else None
                is_green: bool | None = None
                if previous is not None:
                    pair = (previous, token_id)
                    if pair not in cache:
                        prefix = tensor[0, position - config.context_width : position]
                        green_ids = watermark_processor._get_greenlist_ids(prefix)  # pyright: ignore[reportPrivateUsage]
                        cache[pair] = bool((green_ids == token_id).any().item())
                    is_green = cache[pair]
                tokens.append(
                    {
                        "position": position,
                        "token_id": token_id,
                        "piece": processor.tokenizer.decode(
                            [token_id], clean_up_tokenization_spaces=False
                        ),
                        "eligible": eligible,
                        "previous_token_id": previous,
                        "is_green": is_green,
                    }
                )
            return tokens

        output_rows: list[dict[str, Any]] = []
        call_count = 0
        generated_count = 0
        for manifest_row in paired:
            source = source_rows[manifest_row["dataset_row_index"]]
            digest = hashlib.sha256(source["text"].encode()).hexdigest()
            full_ids = tuple(
                int(value)
                for value in processor.tokenizer.encode(source["text"], add_special_tokens=False)
            )
            if (
                digest != manifest_row["text_sha256"]
                or len(full_ids) != manifest_row["full_token_count"]
            ):
                raise RuntimeError("Stage 7 source identity differs from the manifest")
            prompt_ids = full_ids[: config.prompt_tokens]
            natural_ids = full_ids[
                config.prompt_tokens : config.prompt_tokens + config.natural_continuation_tokens
            ]
            prompt_text = processor.tokenizer.decode(prompt_ids, clean_up_tokenization_spaces=False)
            roundtrip = tuple(
                int(value)
                for value in processor.tokenizer.encode(prompt_text, add_special_tokens=False)
            )
            if roundtrip != prompt_ids:
                raise RuntimeError("Stage 7 source prompt does not round-trip")
            encoded = adapter.encode_prompt(config.instruction_prefix + prompt_text)
            seed = config.prompt_seed(manifest_row["selection_rank"], digest)
            conditions: dict[str, Any] = {}
            for condition in ("control", "watermarked"):
                torch.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                runtime_condition = condition
                kwargs = generation_kwargs(
                    adapter=adapter,
                    encoded=encoded,
                    sampling=sampling,
                    condition=runtime_condition,
                    watermark=generation_profile if condition == "watermarked" else None,
                )
                torch.cuda.synchronize()
                wall_start = time.perf_counter_ns()
                with torch.inference_mode():
                    output = model.generate(**kwargs)
                torch.cuda.synchronize()
                wall_ns = time.perf_counter_ns() - wall_start
                generated = adapter.generated_ids(output, prompt_length=encoded.prompt_length)
                raw_generated_text = adapter.raw_generated_text(generated)
                copied_text = adapter.copied_text(raw_generated_text, generated, encoded)
                copied = adapter.copied_token_ids(copied_text)
                call_count += 1
                generated_count += len(generated)
                if (
                    call_count > config.max_generation_calls
                    or generated_count > config.max_generated_token_ids
                ):
                    raise RuntimeError("Stage 7 generation ceiling exceeded")
                parser_path = (
                    "structured_or_fallback" if copied_text else "insufficient_copied_tokens"
                )
                conditions[condition] = {
                    "condition": condition,
                    "status": "ok" if len(copied) >= 2 else "insufficient_copied_tokens",
                    "rendered_input": encoded.rendered_text,
                    "generated_token_ids": generated,
                    "generated_token_count": len(generated),
                    "raw_generated_text": raw_generated_text,
                    "copied_text": copied_text,
                    "copied_token_ids": copied,
                    "copied_token_count": len(copied),
                    "copied_ids_match_generated": copied == generated,
                    "parser_path": parser_path,
                    "stop_reason": (
                        "end_token"
                        if generated and generated[-1] == processor.tokenizer.eos_token_id
                        else "token_limit"
                    ),
                    "generation_wall_ns": wall_ns,
                }
            control_ids = tuple(conditions["control"]["copied_token_ids"])
            watermarked_ids = tuple(conditions["watermarked"]["copied_token_ids"])
            output_rows.append(
                {
                    "selection_rank": manifest_row["selection_rank"],
                    "dataset_row_index": manifest_row["dataset_row_index"],
                    "url": manifest_row["url"],
                    "timestamp": manifest_row["timestamp"],
                    "text_sha256": digest,
                    "full_token_count": len(full_ids),
                    "seed": seed,
                    "source_prompt_text": prompt_text,
                    "source_prompt_token_ids": prompt_ids,
                    "prompt_roundtrip_ok": True,
                    "natural_continuation_token_ids": natural_ids,
                    "conditions": conditions,
                    "token_evidence": {
                        "control_correct": token_trace(control_ids, generation_processor),
                        "natural_correct": token_trace(natural_ids, generation_processor),
                        "watermarked_correct": token_trace(watermarked_ids, generation_processor),
                        "watermarked_comparison": token_trace(
                            watermarked_ids, comparison_processor
                        ),
                    },
                }
            )

    if call_count != 48 or len(output_rows) != 24:
        raise RuntimeError("Stage 7 did not complete the exact call contract")
    result = {
        "schema_version": 1,
        "source_commit": source_commit,
        "config_sha256": config_sha256,
        "manifest_sha256": config.manifest_sha256,
        "python_version": platform.python_version(),
        "torch_version": version("torch"),
        "transformers_version": version("transformers"),
        "huggingface_hub_version": version("huggingface-hub"),
        "modal_sdk_version": config.modal_sdk_version,
        "model_revision": config.model_revision,
        "model_class": model.__class__.__name__,
        "model_safetensors_bytes": config.model_safetensors_bytes,
        "dataset_file_sha256": dataset_hash,
        "dataset_file_bytes": len(dataset_bytes),
        "gpu_name": torch.cuda.get_device_name(0),
        "cuda_runtime": torch.version.cuda,
        "dtype": str(model.dtype),
        "total_vram_bytes": torch.cuda.get_device_properties(0).total_memory,
        "model_download_ns": model_download_ns,
        "model_load_ns": model_load_ns,
        "runtime_ns": time.perf_counter_ns() - start_ns,
        "secret_used": False,
        "volume_used": False,
        "generation_call_count": call_count,
        "generated_token_id_count": generated_count,
        "rows": output_rows,
    }
    return json.dumps(result, allow_nan=False, sort_keys=True)
