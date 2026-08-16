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


def _run_paired(
    config_json: str,
    source_commit: str,
    config_sha256: str,
    expected_generation_calls: int,
) -> str:
    """Run one exact bounded paired Gemma fixture and return raw evidence."""

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
    )

    from watermark_lab.gemma_adapter import Gemma4Adapter
    from watermark_lab.lab05_config import config_from_toml_bytes
    from watermark_lab.stats import green_hit_z_score
    from watermark_lab.transformers_runtime import (
        SamplingProfile,
        WatermarkProfile,
        finalize_generation,
        generation_kwargs,
    )

    config = config_from_toml_bytes(
        config_json.encode(), expected_generation_calls=expected_generation_calls
    )
    if config.modal_gpu != "L4" or config.max_generation_calls != expected_generation_calls:
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
    adapter = Gemma4Adapter(model, processor, "cuda")
    model_config = adapter.model_config
    if model.__class__.__name__ != config.model_class:
        raise RuntimeError("loaded Gemma class differs from the contract")

    generation_profile = WatermarkProfile(
        green_fraction=config.green_fraction,
        bias=config.watermark_bias,
        hashing_key=config.generation_key,
        seeding_scheme=config.seeding_scheme,
        context_width=config.context_width,
    )
    sampling = SamplingProfile(
        max_new_tokens=config.max_new_tokens,
        temperature=config.temperature,
        top_k=config.top_k,
        top_p=config.top_p,
    )

    def time_watermark_processor(
        prompt_ids: tuple[int, ...], generated_ids: tuple[int, ...]
    ) -> tuple[int, int]:
        watermark_processor = generation_profile.to_transformers().construct_processor(
            int(model_config.vocab_size), "cuda"
        )
        scores = torch.zeros((1, int(model_config.vocab_size)), device="cuda", dtype=torch.float32)
        total_ns = 0
        calls = 0
        for index in range(len(generated_ids)):
            context = torch.tensor(
                [prompt_ids + generated_ids[:index]], device="cuda", dtype=torch.long
            )
            scores.zero_()
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            start.record()
            watermark_processor(context, scores)
            end.record()
            torch.cuda.synchronize()
            total_ns += int(start.elapsed_time(end) * 1_000_000)
            calls += 1
        return calls, total_ns

    def evidence(token_ids: tuple[int, ...], key: int, role: str, unique: bool) -> dict[str, Any]:
        detector_profile = WatermarkProfile(
            green_fraction=config.green_fraction,
            bias=config.watermark_bias,
            hashing_key=key,
            seeding_scheme=config.seeding_scheme,
            context_width=config.context_width,
        )
        detector = WatermarkDetector(
            model_config=model_config,
            device="cuda",
            watermarking_config=detector_profile.to_transformers(),
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
        encoded = adapter.encode_prompt(message)
        input_ids = encoded.input_ids
        prompt_ids = tuple(int(value) for value in input_ids[0].tolist())
        seed = config.prompt_seed(prompt.id)
        for condition in ("control", "reference_watermark"):
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.cuda.reset_peak_memory_stats()
            runtime_condition = "watermarked" if condition == "reference_watermark" else "control"
            kwargs = generation_kwargs(
                adapter=adapter,
                encoded=encoded,
                sampling=sampling,
                condition=runtime_condition,
                watermark=generation_profile if runtime_condition == "watermarked" else None,
            )
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            torch.cuda.synchronize()
            wall_start = time.perf_counter_ns()
            start_event.record()
            with torch.inference_mode():
                output = model.generate(**kwargs)
            end_event.record()
            torch.cuda.synchronize()
            wall_ns = time.perf_counter_ns() - wall_start
            gpu_ns = int(start_event.elapsed_time(end_event) * 1_000_000)
            continuation = finalize_generation(
                adapter=adapter,
                encoded=encoded,
                output=output,
                condition=runtime_condition,
            )
            generated = continuation.generated_token_ids
            raw_text = continuation.raw_generated_text
            copied_text = continuation.copied_text
            copied_ids = continuation.copied_token_ids
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
            processor_calls, processor_gpu_ns = (
                time_watermark_processor(prompt_ids, generated)
                if condition == "reference_watermark"
                else (0, 0)
            )
            seconds = wall_ns / 1_000_000_000
            records.append(
                {
                    "prompt_id": prompt.id,
                    "prompt_text": prompt.text,
                    "condition": condition,
                    "seed": seed,
                    "rendered_input": encoded.rendered_text,
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
                    "watermark_processor_calls": processor_calls,
                    "watermark_processor_gpu_ns": processor_gpu_ns,
                    "detector_results": detector_results,
                }
            )
    if len(records) != expected_generation_calls:
        raise RuntimeError(
            f"Stage 5 must return exactly {expected_generation_calls} generation records"
        )
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


def _run_lengths(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Run the frozen natural-length ladder with token-level key membership."""

    import math
    import platform
    import time
    from importlib.metadata import version

    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForMultimodalLM, AutoProcessor

    from watermark_lab.gemma_adapter import Gemma4Adapter
    from watermark_lab.lab05_lengths_config import lengths_config_from_toml_bytes
    from watermark_lab.stats import green_hit_z_score
    from watermark_lab.transformers_runtime import (
        SamplingProfile,
        WatermarkProfile,
        finalize_generation,
        generation_kwargs,
    )

    config = lengths_config_from_toml_bytes(config_json.encode())
    if config.modal_gpu != "L4" or config.max_generation_calls != 24:
        raise RuntimeError("Stage 5 length resource guard rejected the configuration")
    if not torch.cuda.is_available() or "L4" not in torch.cuda.get_device_name(0):
        raise RuntimeError("Stage 5 length ladder requires one NVIDIA L4")
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
        snapshot, local_files_only=True, dtype=torch.bfloat16
    ).to("cuda")
    model.eval()
    torch.cuda.synchronize()
    load_ns = time.perf_counter_ns() - load_start
    adapter = Gemma4Adapter(model, processor, "cuda")
    model_config = adapter.model_config
    profile = WatermarkProfile(
        green_fraction=config.green_fraction,
        bias=config.watermark_bias,
        hashing_key=config.generation_key,
        seeding_scheme=config.seeding_scheme,
        context_width=config.context_width,
    )
    watermark_processor = profile.to_transformers().construct_processor(
        int(model_config.vocab_size), "cuda"
    )

    def score(copied_ids: tuple[int, ...]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        tensor = adapter.token_tensor(copied_ids)
        tokens: list[dict[str, Any]] = []
        for index, token_id in enumerate(copied_ids):
            eligible = index >= config.context_width
            is_green: bool | None = None
            if eligible:
                prefix = tensor[0, index - config.context_width : index]
                green_ids = watermark_processor._get_greenlist_ids(prefix)  # pyright: ignore[reportPrivateUsage]
                is_green = bool((green_ids == token_id).any().item())
            tokens.append(
                {
                    "position": index,
                    "token_id": token_id,
                    "piece": processor.tokenizer.decode(
                        [token_id], clean_up_tokenization_spaces=False
                    ),
                    "eligible": eligible,
                    "is_green": is_green,
                }
            )
        scored = sum(item["eligible"] for item in tokens)
        green = sum(item["is_green"] is True for item in tokens)
        z = green_hit_z_score(hits=green, trials=scored, null_probability=config.green_fraction)
        p_value = 1 - (0.5 * (1 + (1 if z >= 0 else -1) * (1 - math.exp(-2 * z**2 / math.pi))))
        evidence = {
            "num_tokens_scored": scored,
            "num_green_tokens": green,
            "green_fraction": green / scored,
            "z_score": z,
            "independent_z_score": z,
            "p_value": p_value,
            "z_threshold": config.z_threshold,
            "prediction": z > config.z_threshold,
        }
        return evidence, tokens

    records: list[dict[str, Any]] = []
    for prompt in config.prompts:
        encoded = adapter.encode_prompt(config.instruction_prefix + prompt.text)
        seed = config.prompt_seed(prompt.id)
        sampling = SamplingProfile(
            max_new_tokens=prompt.max_new_tokens,
            temperature=config.temperature,
            top_k=config.top_k,
            top_p=config.top_p,
        )
        for condition in ("control", "reference_watermark"):
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.cuda.reset_peak_memory_stats()
            runtime_condition = "watermarked" if condition == "reference_watermark" else "control"
            kwargs = generation_kwargs(
                adapter=adapter,
                encoded=encoded,
                sampling=sampling,
                condition=runtime_condition,
                watermark=profile if runtime_condition == "watermarked" else None,
            )
            torch.cuda.synchronize()
            wall_start = time.perf_counter_ns()
            with torch.inference_mode():
                output = model.generate(**kwargs)
            torch.cuda.synchronize()
            wall_ns = time.perf_counter_ns() - wall_start
            continuation = finalize_generation(
                adapter=adapter, encoded=encoded, output=output, condition=runtime_condition
            )
            evidence, token_evidence = score(continuation.copied_token_ids)
            generated = continuation.generated_token_ids
            records.append(
                {
                    "prompt_id": prompt.id,
                    "prompt_text": prompt.text,
                    "max_new_tokens": prompt.max_new_tokens,
                    "condition": condition,
                    "seed": seed,
                    "generated_token_ids": generated,
                    "copied_text": continuation.copied_text,
                    "copied_token_ids": continuation.copied_token_ids,
                    "stop_reason": "end_token"
                    if generated and generated[-1] == processor.tokenizer.eos_token_id
                    else "token_limit",
                    "generation_wall_ns": wall_ns,
                    "generated_tokens_per_second": len(generated) / (wall_ns / 1e9),
                    "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                    "evidence": evidence,
                    "token_evidence": token_evidence,
                }
            )
    if len(records) != 24:
        raise RuntimeError("length ladder must return exactly twenty-four records")
    result = {
        "schema_version": 1,
        "source_commit": source_commit,
        "config_sha256": config_sha256,
        "python_version": platform.python_version(),
        "torch_version": version("torch"),
        "transformers_version": version("transformers"),
        "model_revision": MODEL_REVISION,
        "vocabulary_size": int(model_config.vocab_size),
        "dtype": str(model.dtype),
        "gpu_name": torch.cuda.get_device_name(0),
        "total_vram_bytes": torch.cuda.get_device_properties(0).total_memory,
        "model_download_ns": download_ns,
        "model_load_ns": load_ns,
        "secret_used": False,
        "volume_used": False,
        "records": records,
    }
    result["remote_total_ns"] = time.perf_counter_ns() - remote_start
    return json.dumps(result, allow_nan=False, sort_keys=True)


@app.function(gpu="L4", timeout=3600, max_containers=1, single_use_containers=True)
def run_smoke(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Run exactly three paired Gemma generations."""

    return _run_paired(config_json, source_commit, config_sha256, 6)


@app.function(gpu="L4", timeout=3600, max_containers=1, single_use_containers=True)
def run_examples(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Run exactly ten paired Gemma examples in one approved invocation."""

    return _run_paired(config_json, source_commit, config_sha256, 20)


@app.function(gpu="L4", timeout=3600, max_containers=1, single_use_containers=True)
def run_lengths(config_json: str, source_commit: str, config_sha256: str) -> str:
    """Run twelve natural-length paired prompts with token-level evidence."""

    return _run_lengths(config_json, source_commit, config_sha256)
