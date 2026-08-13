#!/usr/bin/env python3
# pyright: reportArgumentType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Stage 4: compare the manual watermark explanation with Transformers."""

from __future__ import annotations

import argparse
import hashlib
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal, cast

import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

from watermark_lab.hf_adapter import (
    DetectorEvidence,
    ProcessorOrderProbe,
    build_order_probe,
    build_watermark_config,
    derive_reference_seed,
    detector_evidence,
    distinct_pair_evidence,
    make_detector,
)
from watermark_lab.lab04_config import Lab04Config, ReferencePrompt, config_from_toml_bytes
from watermark_lab.lab04_records import (
    ContinuationRecord,
    Lab04Trace,
    PaddingEntry,
    PaddingValidation,
    RepetitionFixture,
    trace_to_json_bytes,
    trace_to_markdown_bytes,
)

CAVEAT = (
    "These six continuations verify one pinned local Transformers profile. Three prompts do not "
    "measure detection accuracy or language quality."
)
MODEL_FILES = (
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "merges.txt",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
)


class LabError(RuntimeError):
    """An actionable Stage 4 precondition failure."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/lab_04.toml"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts/lab-04"))
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="fail instead of downloading the pinned model and tokenizer",
    )
    parser.add_argument("--source-commit", help=argparse.SUPPRESS)
    return parser.parse_args()


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=repo, check=False, capture_output=True, text=True
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise LabError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout.strip()


def _source_commit(repo: Path, override: str | None) -> str:
    if override is not None:
        if len(override) != 40 or any(
            character not in "0123456789abcdef" for character in override
        ):
            raise LabError("source commit override must be a 40-character lowercase Git SHA")
        _git(repo, "cat-file", "-e", f"{override}^{{commit}}")
        return override
    dirty = _git(repo, "status", "--porcelain", "--untracked-files=normal")
    if dirty:
        raise LabError(
            "refusing to generate the Stage 4 trace from a dirty Git worktree; commit, ignore, "
            "or remove the listed changes first:\n" + dirty
        )
    return _git(repo, "rev-parse", "HEAD")


def _token_piece(tokenizer: Any, token_id: int) -> str:
    return cast(
        str,
        tokenizer.decode(
            [token_id],
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
    )


def _encode(tokenizer: Any, text: str) -> tuple[int, ...]:
    return tuple(int(token_id) for token_id in tokenizer.encode(text, add_special_tokens=False))


def _watermark_profile(config: Lab04Config) -> dict[str, object]:
    return {
        "bias": config.watermark_bias,
        "context_width": config.context_width,
        "device": config.device,
        "greenlist_ratio": config.green_fraction,
        "hashing_key": config.generation_key,
        "ignore_repeated_ngrams_primary": False,
        "seeding_scheme": config.seeding_scheme,
        "z_threshold": config.z_threshold,
    }


def _detector_results(
    *,
    detectors: dict[tuple[str, str], Any],
    token_ids: tuple[int, ...],
    config: Lab04Config,
) -> tuple[DetectorEvidence, ...]:
    tensor = torch.tensor([token_ids], dtype=torch.long, device=config.device)
    return tuple(
        detector_evidence(
            detector=detectors[(key_role, policy)],
            token_ids=tensor,
            key_role=cast(Literal["generation", "comparison"], key_role),
            repetition_policy=cast(Literal["all", "unique"], policy),
            green_fraction=config.green_fraction,
            z_threshold=config.z_threshold,
        )
        for key_role in ("generation", "comparison")
        for policy in ("all", "unique")
    )


def _generate_record(
    *,
    model: Any,
    tokenizer: Any,
    detectors: dict[tuple[str, str], Any],
    config: Lab04Config,
    prompt: ReferencePrompt,
    condition: Literal["control", "reference_watermark"],
) -> tuple[ContinuationRecord, ProcessorOrderProbe | None]:
    encoded = tokenizer(prompt.text, add_special_tokens=False, return_tensors="pt")
    input_ids = cast(torch.Tensor, encoded["input_ids"]).to(config.device)
    attention_mask = cast(torch.Tensor, encoded["attention_mask"]).to(config.device)
    prompt_ids = tuple(int(token_id) for token_id in input_ids[0].tolist())
    seed = derive_reference_seed(base_seed=config.base_seed, prompt_id=prompt.id)
    torch.manual_seed(seed)
    generation_arguments: dict[str, object] = {
        "attention_mask": attention_mask,
        "do_sample": True,
        "eos_token_id": int(tokenizer.eos_token_id),
        "max_new_tokens": config.max_new_tokens,
        "output_logits": True,
        "output_scores": True,
        "pad_token_id": int(tokenizer.pad_token_id),
        "return_dict_in_generate": True,
        "temperature": config.temperature,
        "top_k": config.top_k,
        "top_p": config.top_p,
    }
    if condition == "reference_watermark":
        generation_arguments["watermarking_config"] = build_watermark_config(
            config, key=config.generation_key
        )
    with torch.inference_mode():
        output = model.generate(input_ids=input_ids, **generation_arguments)
    generated_tensor = cast(torch.Tensor, output.sequences)[:, input_ids.shape[1] :]
    generated_ids = tuple(int(token_id) for token_id in generated_tensor[0].tolist())
    if not generated_ids:
        raise LabError(f"prompt {prompt.id!r} produced no continuation tokens")
    stop_reason: Literal["end_token", "token_limit"] = (
        "end_token" if generated_ids[-1] == int(tokenizer.eos_token_id) else "token_limit"
    )
    decoded = cast(
        str,
        tokenizer.decode(
            generated_ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
    )
    copied_ids = _encode(tokenizer, decoded)
    if len(copied_ids) < 2:
        raise LabError("copied continuation is too short for context-width-one detection")
    record = ContinuationRecord(
        prompt_id=prompt.id,
        prompt_text=prompt.text,
        condition=condition,
        seed=seed,
        stop_reason=stop_reason,
        prompt_token_ids=prompt_ids,
        prompt_token_pieces=tuple(_token_piece(tokenizer, token_id) for token_id in prompt_ids),
        generated_token_ids=generated_ids,
        decoded_text=decoded,
        copied_token_ids=copied_ids,
        copied_ids_match=generated_ids == copied_ids,
        detector_results=_detector_results(
            detectors=detectors,
            token_ids=copied_ids,
            config=config,
        ),
    )
    probe = None
    if prompt.id == "stage-02-continuity" and condition == "reference_watermark":
        raw_logits = cast(tuple[torch.Tensor, ...], output.logits)
        processed_scores = cast(tuple[torch.Tensor, ...], output.scores)
        probe = build_order_probe(
            raw_scores=raw_logits[0],
            generated_scores=processed_scores[0],
            input_ids=input_ids,
            selected_token_id=generated_ids[0],
            token_text=lambda token_id: _token_piece(tokenizer, token_id),
            config=config,
        )
    return record, probe


def _padding_validation(tokenizer: Any, config: Lab04Config) -> PaddingValidation:
    batch = tokenizer(
        [prompt.text for prompt in config.prompts],
        add_special_tokens=False,
        padding=True,
        return_tensors="pt",
    )
    input_ids = cast(torch.Tensor, batch["input_ids"])
    attention_mask = cast(torch.Tensor, batch["attention_mask"])
    width = int(input_ids.shape[1])
    entries = tuple(
        PaddingEntry(
            prompt_id=prompt.id,
            prompt_token_count=int(attention_mask[index].sum().item()),
            left_padding_count=width - int(attention_mask[index].sum().item()),
            attention_mask_count=int(attention_mask[index].sum().item()),
            continuation_slice_start=width,
        )
        for index, prompt in enumerate(config.prompts)
    )
    return PaddingValidation(
        pad_token_id=int(tokenizer.pad_token_id),
        padding_side="left",
        padded_width=width,
        prompt_tokens_in_detector=0,
        padding_tokens_in_detector=0,
        entries=entries,
    )


def _repetition_fixture(
    *,
    tokenizer: Any,
    detectors: dict[tuple[str, str], Any],
    continuity: ContinuationRecord,
    config: Lab04Config,
) -> RepetitionFixture:
    first, second = continuity.copied_token_ids[:2]
    token_ids = (first, second, first, second, first, second)
    all_results = _detector_results(detectors=detectors, token_ids=token_ids, config=config)
    return RepetitionFixture(
        source_prompt_id=continuity.prompt_id,
        construction="alternate-first-two-copied-ids-three-times",
        token_ids=token_ids,
        token_pieces=tuple(_token_piece(tokenizer, token_id) for token_id in token_ids),
        detector_results=(all_results[0], all_results[1]),
        explicit_distinct_result=distinct_pair_evidence(
            detector=detectors[("generation", "all")],
            token_ids=torch.tensor([token_ids], dtype=torch.long, device=config.device),
            green_fraction=config.green_fraction,
        ),
    )


def build_trace(
    *,
    source_commit: str,
    config_sha256: str,
    config: Lab04Config,
    local_files_only: bool,
) -> Lab04Trace:
    """Load the pinned fixture and generate all selected Stage 4 evidence."""

    model_path = Path(
        snapshot_download(
            repo_id=config.model_id,
            revision=config.model_revision,
            allow_patterns=list(MODEL_FILES),
            local_files_only=local_files_only,
        )
    )
    model_file = model_path / "model.safetensors"
    if not model_file.is_file() or model_file.stat().st_size != config.model_safetensors_bytes:
        raise LabError("the selected safetensors file size differs from the locked model metadata")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        use_safetensors=True,
    ).to(config.device)
    model.eval()

    detectors = {
        (key_role, policy): make_detector(
            config=config,
            model_config=model.config,
            key=config.generation_key if key_role == "generation" else config.comparison_key,
            ignore_repeated_ngrams=policy == "unique",
        )
        for key_role in ("generation", "comparison")
        for policy in ("all", "unique")
    }
    records: list[ContinuationRecord] = []
    order_probe: ProcessorOrderProbe | None = None
    for prompt in config.prompts:
        for condition in ("control", "reference_watermark"):
            record, maybe_probe = _generate_record(
                model=model,
                tokenizer=tokenizer,
                detectors=detectors,
                config=config,
                prompt=prompt,
                condition=condition,
            )
            records.append(record)
            if maybe_probe is not None:
                order_probe = maybe_probe
    if order_probe is None:
        raise LabError("the continuity reference row did not produce an order probe")
    continuity = next(
        record
        for record in records
        if record.prompt_id == "stage-02-continuity" and record.condition == "reference_watermark"
    )
    return Lab04Trace(
        schema_version=1,
        source_commit=source_commit,
        config_sha256=config_sha256,
        python_version=platform.python_version(),
        platform=platform.platform(),
        torch_version=version("torch"),
        transformers_version=version("transformers"),
        config=config,
        watermark_profile=_watermark_profile(config),
        records=tuple(records),
        order_probe=order_probe,
        repetition_fixture=_repetition_fixture(
            tokenizer=tokenizer,
            detectors=detectors,
            continuity=continuity,
            config=config,
        ),
        padding_validation=_padding_validation(tokenizer, config),
    )


def main() -> int:
    arguments = _parse_args()
    try:
        config_bytes = arguments.config.read_bytes()
        config = config_from_toml_bytes(config_bytes)
        repository = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel"))
        source_commit = _source_commit(repository, arguments.source_commit)
        trace = build_trace(
            source_commit=source_commit,
            config_sha256=hashlib.sha256(config_bytes).hexdigest(),
            config=config,
            local_files_only=arguments.local_files_only,
        )
        arguments.artifacts.mkdir(parents=True, exist_ok=True)
        (arguments.artifacts / "trace.json").write_bytes(trace_to_json_bytes(trace))
        (arguments.artifacts / "annotated_trace.md").write_bytes(trace_to_markdown_bytes(trace))
    except (LabError, OSError, TypeError, UnicodeError, ValueError) as error:
        print(f"Stage 4 lab failed: {error}", file=sys.stderr)
        return 1

    print("prompt                watermark  tokens  copied IDs  generation key G/T   z")
    for record in trace.records:
        score = record.detector_results[0]
        print(
            f"{record.prompt_id:<21} "
            f"{'off' if record.condition == 'control' else 'on':<10} "
            f"{len(record.generated_token_ids):>6}  "
            f"{'match' if record.copied_ids_match else 'differ':<10} "
            f"{score.num_green_tokens:>2}/{score.num_tokens_scored:<3} {score.z_score:>8.3f}"
        )
    print(CAVEAT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
