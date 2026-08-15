# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOptionalSubscript=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Approval-gated Modal L4 runner for the Stage 5 Gemma smoke test."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

APP_NAME = "text-watermarking-lab-05"
MODEL_ID = "google/gemma-4-E2B-it"
MODEL_REVISION = "3e22461f65e89153144f8adb70e3b8c2cc9845a7"
MODEL_BYTES = 10_246_621_918

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
def run_smoke(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Run exactly three paired Gemma generations and return selected raw evidence."""

    import math
    import platform
    import time
    from importlib.metadata import version

    import torch
    from huggingface_hub import snapshot_download
    from transformers import (
        AutoModelForMultimodalLM,
        AutoProcessor,
        WatermarkDetector,
        WatermarkingConfig,
    )

    from watermark_lab.lab05_config import config_from_toml_bytes
    from watermark_lab.stats import green_hit_z_score

    config = config_from_toml_bytes(config_json.encode())
    if config.modal_gpu != "L4" or config.max_generation_calls != 6:
        raise RuntimeError("Stage 5 resource guard rejected the configuration")
    if not torch.cuda.is_available():
        raise RuntimeError("Stage 5 requires CUDA")
    gpu_name = torch.cuda.get_device_name(0)
    if "L4" not in gpu_name:
        raise RuntimeError(f"Stage 5 requires an L4, received {gpu_name!r}")
    if (
        version("torch") != config.torch_version
        or version("transformers") != config.transformers_version
    ):
        raise RuntimeError("remote locked package versions differ")

    remote_start = time.perf_counter_ns()
    download_start = time.perf_counter_ns()
    snapshot = Path(snapshot_download(repo_id=MODEL_ID, revision=MODEL_REVISION))
    download_ns = time.perf_counter_ns() - download_start
    model_file = snapshot / "model.safetensors"
    if not model_file.is_file() or model_file.stat().st_size != MODEL_BYTES:
        raise RuntimeError("pinned Gemma model file differs from the contract")

    load_start = time.perf_counter_ns()
    processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
    model = AutoModelForMultimodalLM.from_pretrained(
        snapshot,
        local_files_only=True,
        dtype=torch.bfloat16,
    ).to("cuda")
    model.eval()
    torch.cuda.synchronize()
    model_load_ns = time.perf_counter_ns() - load_start
    model_config = model.config.get_text_config()
    if model.__class__.__name__ != config.model_class:
        raise RuntimeError("loaded Gemma class differs from the contract")

    profile = dict(
        greenlist_ratio=config.green_fraction,
        bias=config.watermark_bias,
        hashing_key=config.generation_key,
        seeding_scheme=config.seeding_scheme,
        context_width=config.context_width,
    )

    def evidence(token_ids: tuple[int, ...], key: int, role: str, unique: bool) -> dict[str, Any]:
        watermark_config = WatermarkingConfig(**{**profile, "hashing_key": key})
        detector = WatermarkDetector(
            model_config=model_config,
            device="cuda",
            watermarking_config=watermark_config,
            ignore_repeated_ngrams=unique,
        )
        tensor = torch.tensor([token_ids], device="cuda", dtype=torch.long)
        result = detector(tensor, z_threshold=config.z_threshold, return_dict=True)
        scored = int(result.num_tokens_scored[0])
        green = int(result.num_green_tokens[0])
        z = float(result.z_score[0])
        independent = green_hit_z_score(
            hits=green, trials=scored, null_probability=config.green_fraction
        )
        if not math.isclose(z, independent, abs_tol=1e-10):
            raise RuntimeError("Stage 1 and Transformers z scores differ")
        return {
            "key_role": role,
            "repetition_policy": "unique" if unique else "all",
            "num_tokens_scored": scored,
            "num_green_tokens": green,
            "green_fraction": float(result.green_fraction[0]),
            "z_score": z,
            "independent_z_score": independent,
            "p_value": float(result.p_value[0]),
            "z_threshold": config.z_threshold,
            "prediction": bool(result.prediction[0]),
        }

    records: list[dict[str, Any]] = []
    allocated_after_load = torch.cuda.memory_allocated()
    reserved_after_load = torch.cuda.memory_reserved()
    for prompt in config.prompts:
        message = config.instruction_prefix + prompt.text
        messages = [{"role": "user", "content": message}]
        rendered = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        encoded = processor(text=rendered, return_tensors="pt")
        input_ids = encoded["input_ids"].to("cuda")
        attention_mask = encoded["attention_mask"].to("cuda")
        prompt_ids = tuple(int(value) for value in input_ids[0].tolist())
        seed = config.prompt_seed(prompt.id)
        for condition in ("control", "reference_watermark"):
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.cuda.reset_peak_memory_stats()
            kwargs: dict[str, Any] = {
                "attention_mask": attention_mask,
                "do_sample": True,
                "max_new_tokens": config.max_new_tokens,
                "temperature": config.temperature,
                "top_k": config.top_k,
                "top_p": config.top_p,
                "pad_token_id": processor.tokenizer.pad_token_id
                or processor.tokenizer.eos_token_id,
            }
            if condition == "reference_watermark":
                kwargs["watermarking_config"] = WatermarkingConfig(**profile)
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            torch.cuda.synchronize()
            wall_start = time.perf_counter_ns()
            start_event.record()
            with torch.inference_mode():
                output = model.generate(input_ids=input_ids, **kwargs)
            end_event.record()
            torch.cuda.synchronize()
            wall_ns = time.perf_counter_ns() - wall_start
            gpu_ns = int(start_event.elapsed_time(end_event) * 1_000_000)
            generated = tuple(int(value) for value in output[0, input_ids.shape[1] :].tolist())
            raw_text = processor.decode(generated, skip_special_tokens=False)
            try:
                copied_text = str(processor.parse_response(raw_text, prefix=input_ids[0]))
            except Exception:
                copied_text = processor.decode(generated, skip_special_tokens=True)
            copied_ids = tuple(
                int(value)
                for value in processor.tokenizer.encode(copied_text, add_special_tokens=False)
            )
            if len(copied_ids) < 2:
                raise RuntimeError(f"{prompt.id}/{condition} produced fewer than two copied tokens")
            detector_results = [
                evidence(copied_ids, key, role, unique)
                for role, key in (
                    ("generation", config.generation_key),
                    ("comparison", config.comparison_key),
                )
                for unique in (False, True)
            ]
            seconds = wall_ns / 1_000_000_000
            records.append(
                {
                    "prompt_id": prompt.id,
                    "prompt_text": prompt.text,
                    "condition": condition,
                    "seed": seed,
                    "rendered_input": rendered,
                    "prompt_token_ids": prompt_ids,
                    "generated_token_ids": generated,
                    "raw_generated_text": raw_text,
                    "copied_text": copied_text,
                    "copied_token_ids": copied_ids,
                    "copied_ids_match_generated": generated == copied_ids,
                    "stop_reason": "end_token"
                    if generated and generated[-1] == processor.tokenizer.eos_token_id
                    else "token_limit",
                    "generation_wall_ns": wall_ns,
                    "generation_gpu_ns": gpu_ns,
                    "generated_tokens_per_second": len(generated) / seconds,
                    "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                    "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                    "detector_results": detector_results,
                }
            )
    if len(records) != 6:
        raise RuntimeError("Stage 5 must return exactly six generation records")
    total_vram = torch.cuda.get_device_properties(0).total_memory
    result = {
        "schema_version": 1,
        "source_commit": source_commit,
        "config_sha256": config_sha256,
        "python_version": platform.python_version(),
        "torch_version": version("torch"),
        "torchvision_version": version("torchvision"),
        "transformers_version": version("transformers"),
        "huggingface_hub_version": version("huggingface-hub"),
        "modal_sdk_version": "1.5.3",
        "model_class": model.__class__.__name__,
        "model_revision": MODEL_REVISION,
        "model_safetensors_bytes": MODEL_BYTES,
        "vocabulary_size": int(model_config.vocab_size),
        "dtype": str(model.dtype),
        "gpu_name": gpu_name,
        "cuda_runtime": torch.version.cuda,
        "cuda_driver": torch.cuda.driver_version()
        if hasattr(torch.cuda, "driver_version")
        else None,
        "total_vram_bytes": total_vram,
        "allocated_after_load_bytes": allocated_after_load,
        "reserved_after_load_bytes": reserved_after_load,
        "model_download_ns": download_ns,
        "model_load_ns": model_load_ns,
        "secret_used": False,
        "volume_used": False,
        "records": records,
    }
    result["remote_total_ns"] = time.perf_counter_ns() - remote_start
    return json.dumps(result, allow_nan=False, sort_keys=True)
