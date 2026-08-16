# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Approval-gated Stage 8 paraphrase and bias-sweep runner."""

from __future__ import annotations

import json

import modal

APP_NAME = "text-watermarking-lab-08"

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
def run_stage08(
    config_json: str,
    stage7_rows_json: str,
    source_commit: str,
    config_sha256: str,
) -> str:
    """Run the exact 12 paraphrases and 16 delta-sweep generations once."""

    import hashlib
    import math
    import platform
    import time
    from dataclasses import asdict
    from importlib.metadata import version
    from pathlib import Path
    from typing import Any

    import torch
    import torch.nn.functional as functional
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForMultimodalLM, AutoProcessor

    from watermark_lab.attacks import (
        delete_words,
        mix_with_control,
        normalize_text,
        substitute_homoglyphs,
    )
    from watermark_lab.gemma_adapter import Gemma4Adapter
    from watermark_lab.lab08_config import lab08_config_from_toml_bytes
    from watermark_lab.lab08_metrics import (
        distinct_ngram_fraction,
        numbers_preserved,
        repeated_adjacent_pair_fraction,
    )
    from watermark_lab.transformers_runtime import (
        SamplingProfile,
        WatermarkProfile,
        generation_kwargs,
    )

    config = lab08_config_from_toml_bytes(config_json.encode())
    if (
        config.max_remote_invocations != 1
        or config.max_generation_calls != 28
        or config.max_generated_token_ids != 11_200
        or config.modal_gpu != "L4"
        or config.max_cost_usd != 5.0
    ):
        raise RuntimeError("Stage 8 resource guard rejected the configuration")
    if not torch.cuda.is_available() or torch.cuda.get_device_name(0) != "NVIDIA L4":
        raise RuntimeError("Stage 8 requires one NVIDIA L4")
    if (
        version("torch") != config.torch_version
        or version("transformers") != config.transformers_version
        or version("huggingface-hub") != config.huggingface_hub_version
    ):
        raise RuntimeError("Stage 8 remote package versions differ")

    rows: list[dict[str, Any]] = json.loads(stage7_rows_json)
    if [row["selection_rank"] for row in rows] != list(config.attack_selection_ranks):
        raise RuntimeError("Stage 8 input row order differs")
    if any(row["stage7_source_commit"] != config.stage7_source_commit for row in rows):
        raise RuntimeError("Stage 8 input source commit differs")

    start_ns = time.perf_counter_ns()
    download_start = time.perf_counter_ns()
    snapshot = Path(snapshot_download(repo_id=config.model_id, revision=config.model_revision))
    model_download_ns = time.perf_counter_ns() - download_start
    model_file = snapshot / "model.safetensors"
    if not model_file.is_file() or model_file.stat().st_size != config.model_safetensors_bytes:
        raise RuntimeError("Stage 8 model file differs")
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
        raise RuntimeError("Stage 8 model class differs")

    sampling = SamplingProfile(
        max_new_tokens=config.max_new_tokens,
        temperature=config.temperature,
        top_k=config.top_k,
        top_p=config.top_p,
    )
    generation_profile = WatermarkProfile(
        green_fraction=config.green_fraction,
        bias=2.0,
        hashing_key=config.generation_key,
        seeding_scheme=config.seeding_scheme,
        context_width=config.context_width,
    )
    generation_processor = generation_profile.to_transformers().construct_processor(
        int(adapter.model_config.vocab_size), "cuda"
    )

    def seed_all(seed: int) -> None:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    def generate(prompt: str, seed: int, watermark: WatermarkProfile | None) -> dict[str, Any]:
        encoded = adapter.encode_prompt(prompt)
        seed_all(seed)
        kwargs = generation_kwargs(
            adapter=adapter,
            encoded=encoded,
            sampling=sampling,
            condition="watermarked" if watermark is not None else "control",
            watermark=watermark,
        )
        torch.cuda.synchronize()
        wall_start = time.perf_counter_ns()
        with torch.inference_mode():
            output = model.generate(**kwargs)
        torch.cuda.synchronize()
        wall_ns = time.perf_counter_ns() - wall_start
        generated = adapter.generated_ids(output, prompt_length=encoded.prompt_length)
        raw_text = adapter.raw_generated_text(generated)
        copied_text = adapter.copied_text(raw_text, generated, encoded)
        copied_ids = adapter.copied_token_ids(copied_text)
        return {
            "rendered_input": encoded.rendered_text,
            "prompt_token_ids": tuple(int(value) for value in encoded.input_ids[0].tolist()),
            "generated_token_ids": generated,
            "generated_token_count": len(generated),
            "raw_generated_text": raw_text,
            "copied_text": copied_text,
            "copied_token_ids": copied_ids,
            "copied_token_count": len(copied_ids),
            "stop_reason": (
                "end_token"
                if generated and generated[-1] == processor.tokenizer.eos_token_id
                else "token_limit"
            ),
            "generation_wall_ns": wall_ns,
        }

    def final_mean(token_ids: tuple[int, ...]) -> torch.Tensor:
        tensor = adapter.token_tensor(token_ids)
        mask = torch.ones_like(tensor)
        with torch.inference_mode():
            hidden = model.model.language_model(
                input_ids=tensor,
                attention_mask=mask,
                use_cache=False,
                return_dict=True,
            ).last_hidden_state
        return hidden.float().mean(dim=1).squeeze(0)

    def continuation_nll(prompt_ids: tuple[int, ...], copied_ids: tuple[int, ...]) -> float:
        all_ids = prompt_ids + copied_ids
        tensor = adapter.token_tensor(all_ids)
        labels = tensor.clone()
        labels[:, : len(prompt_ids)] = -100
        with torch.inference_mode():
            output = model(input_ids=tensor, attention_mask=torch.ones_like(tensor), labels=labels)
        return float(output.loss.float().item())

    def token_trace(token_ids: tuple[int, ...]) -> list[dict[str, Any]]:
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
                    green_ids = generation_processor._get_greenlist_ids(prefix)  # pyright: ignore[reportPrivateUsage]
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

    call_count = 0
    generated_count = 0
    output_rows: list[dict[str, Any]] = []
    for row in rows:
        rank = int(row["selection_rank"])
        text_hash = hashlib.sha256(row["watermarked_text"].encode()).hexdigest()
        if text_hash != row["watermarked_text_sha256"]:
            raise RuntimeError("Stage 8 copied source hash differs")
        source_ids = tuple(int(value) for value in row["watermarked_token_ids"])
        if tuple(adapter.copied_token_ids(row["watermarked_text"])) != source_ids:
            raise RuntimeError("Stage 8 copied source IDs differ")

        prompt = config.paraphrase_template.format(passage=row["watermarked_text"])
        paraphrase = generate(prompt, config.paraphrase_seed(rank, text_hash), None)
        call_count += 1
        generated_count += paraphrase["generated_token_count"]
        paraphrase_ids = tuple(paraphrase["copied_token_ids"])
        if paraphrase_ids:
            source_vector = final_mean(source_ids)
            candidate_vector = final_mean(paraphrase_ids)
            paraphrase["embedding_cosine"] = float(
                functional.cosine_similarity(source_vector, candidate_vector, dim=0).item()
            )
        else:
            paraphrase["embedding_cosine"] = None
        paraphrase["length_ratio"] = len(paraphrase_ids) / len(source_ids)
        paraphrase["numbers_preserved"] = numbers_preserved(
            row["watermarked_text"], paraphrase["copied_text"]
        )
        paraphrase["prompt"] = prompt
        paraphrase["seed"] = config.paraphrase_seed(rank, text_hash)
        paraphrase["token_evidence"] = token_trace(paraphrase_ids) if paraphrase_ids else []
        paraphrase["automatic_preservation_pass"] = bool(
            len(paraphrase_ids) >= config.attack_prefix
            and config.min_length_ratio <= paraphrase["length_ratio"] <= config.max_length_ratio
            and paraphrase["numbers_preserved"]
            and paraphrase["embedding_cosine"] is not None
            and paraphrase["embedding_cosine"] >= config.similarity_threshold
        )

        attack_records: dict[str, Any] = {}
        attack_edits = [("normalization", normalize_text(row["watermarked_text"]))]
        for rate in config.homoglyph_rates:
            label = f"homoglyph_{int(rate * 100)}"
            seed = config.derive_seed("homoglyph", rank, text_hash, f"{rate:.2f}")
            attack_edits.append(
                (label, substitute_homoglyphs(row["watermarked_text"], rate=rate, seed=seed))
            )
        for rate in config.deletion_rates:
            label = f"deletion_{int(rate * 100)}"
            seed = config.derive_seed("deletion", rank, text_hash, f"{rate:.2f}")
            attack_edits.append(
                (label, delete_words(row["watermarked_text"], rate=rate, seed=seed))
            )
        for rate in config.mixing_rates:
            label = f"mixing_{int(rate * 100)}"
            seed = config.derive_seed("mixing", rank, text_hash, f"{rate:.2f}")
            attack_edits.append(
                (
                    label,
                    mix_with_control(
                        row["watermarked_text"], row["control_text"], rate=rate, seed=seed
                    ),
                )
            )
        for label, edit in attack_edits:
            edited_ids = adapter.copied_token_ids(edit.text)
            attack_records[label] = {
                "text": edit.text,
                "copied_token_ids": edited_ids,
                "copied_token_count": len(edited_ids),
                "length_ratio": len(edited_ids) / len(source_ids),
                "operations": [asdict(operation) for operation in edit.operations],
                "token_evidence": token_trace(edited_ids),
            }
        attack_records["paraphrase"] = paraphrase

        baseline_prompt = adapter.encode_prompt(row["generation_prompt"])
        if baseline_prompt.rendered_text != row["expected_rendered_input"]:
            raise RuntimeError("Stage 8 rendered generation input differs from Stage 7")
        baseline_prompt_ids = tuple(int(value) for value in baseline_prompt.input_ids[0].tolist())
        source_vector = final_mean(source_ids)
        bias_records: dict[str, Any] = {
            "2": {
                "bias": 2.0,
                "seed": int(row["stage7_seed"]),
                "copied_text": row["watermarked_text"],
                "copied_token_ids": source_ids,
                "copied_token_count": len(source_ids),
                "generated_token_count": int(row["stage7_generated_token_count"]),
                "generation_wall_ns": int(row["stage7_generation_wall_ns"]),
                "stop_reason": row["stage7_stop_reason"],
                "conditional_nll": continuation_nll(baseline_prompt_ids, source_ids),
                "repeated_pair_fraction": repeated_adjacent_pair_fraction(source_ids),
                "distinct_2_fraction": distinct_ngram_fraction(source_ids, width=2),
                "distinct_3_fraction": distinct_ngram_fraction(source_ids, width=3),
                "source_embedding_cosine": 1.0,
                "token_evidence": token_trace(source_ids),
                "reused_stage7": True,
            }
        }
        for bias in (1.0, 3.0):
            profile = WatermarkProfile(
                green_fraction=config.green_fraction,
                bias=bias,
                hashing_key=config.generation_key,
                seeding_scheme=config.seeding_scheme,
                context_width=config.context_width,
            )
            record = generate(row["generation_prompt"], int(row["stage7_seed"]), profile)
            call_count += 1
            generated_count += record["generated_token_count"]
            copied_ids = tuple(record["copied_token_ids"])
            record["bias"] = bias
            record["seed"] = int(row["stage7_seed"])
            if len(copied_ids) >= 3:
                record["conditional_nll"] = continuation_nll(
                    tuple(record["prompt_token_ids"]), copied_ids
                )
                record["repeated_pair_fraction"] = repeated_adjacent_pair_fraction(copied_ids)
                record["distinct_2_fraction"] = distinct_ngram_fraction(copied_ids, width=2)
                record["distinct_3_fraction"] = distinct_ngram_fraction(copied_ids, width=3)
                record["source_embedding_cosine"] = float(
                    functional.cosine_similarity(
                        source_vector, final_mean(copied_ids), dim=0
                    ).item()
                )
                record["token_evidence"] = token_trace(copied_ids)
            else:
                record["conditional_nll"] = None
                record["repeated_pair_fraction"] = None
                record["distinct_2_fraction"] = None
                record["distinct_3_fraction"] = None
                record["source_embedding_cosine"] = None
                record["token_evidence"] = []
            record["reused_stage7"] = False
            bias_records[str(int(bias))] = record

        if (
            call_count > config.max_generation_calls
            or generated_count > config.max_generated_token_ids
        ):
            raise RuntimeError("Stage 8 generation ceiling exceeded")
        output_rows.append(
            {
                "selection_rank": rank,
                "stage7_text_sha256": text_hash,
                "attacks": attack_records,
                "bias_generations": bias_records,
            }
        )

    if call_count != config.max_generation_calls or len(output_rows) != len(
        config.attack_selection_ranks
    ):
        raise RuntimeError("Stage 8 did not complete the exact call contract")
    if not math.isfinite(float(generated_count)):
        raise RuntimeError("Stage 8 generated-token count is invalid")
    return json.dumps(
        {
            "schema_version": 1,
            "source_commit": source_commit,
            "config_sha256": config_sha256,
            "stage7_selected_sha256": config.stage7_selected_sha256,
            "python_version": platform.python_version(),
            "torch_version": version("torch"),
            "transformers_version": version("transformers"),
            "huggingface_hub_version": version("huggingface-hub"),
            "modal_sdk_version": config.modal_sdk_version,
            "model_revision": config.model_revision,
            "model_class": model.__class__.__name__,
            "model_safetensors_bytes": config.model_safetensors_bytes,
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
        },
        allow_nan=False,
        sort_keys=True,
    )
