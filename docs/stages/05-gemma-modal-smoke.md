# Stage 5 implementation contract: Gemma 4 Modal smoke test

## Authorization

The user approved the complete Stage 5 slice on 2026-08-15. This approval covers the exact Gemma
model and tokenizer below, a declared Modal Image and App, one Modal L4 GPU smoke session, and use
of the existing `huggingface` Modal Secret only if anonymous access fails.

This stage must not access a dataset, select C4 rows, create an endpoint, deploy a service, run E4B
or another GPU, start the 24-row experiment, change a GitHub remote, open a pull request, merge, or
publish. It stops after six generations and the human review gate.

## Question

What does the same maintained watermark intervention cost on a credible current open model?

## Narrow answer expected before the run

The watermark recipe should move from GPT-2 on a local CPU to Gemma 4 E2B on one CUDA L4 without
changing its green fraction, score increase, keys, context width, sampling settings, or copied-text
checker. Model load, generation speed, processor time, CUDA memory, and detector evidence must be
measured. No direction or size is assumed.

## Continuity

Use the three Stage 4 passage fixtures in the same order:

1. `stage-02-continuity`: `Early one morning Jack went up the hill. At the top he`
2. `notebook`: `The student opened the notebook and wrote down each result because`
3. `library`: `When the neighborhood library lost power, the staff`

Keep base seed `20260812` and the Stage 3/4 derivation
`lab-03|<base-seed>|<prompt-id>`. Keep temperature `0.8`, top-k `40`, top-p `0.95`, green fraction
`0.25`, score increase `2.0`, generation key `15485863`, comparison key `15485867`, `lefthash`,
context width `1`, and strict detector cutoff `z > 3.0`.

Stage 4 and Stage 5 do not share token IDs or CUDA green sets. The model, tokenizer, vocabulary,
device, precision, prompt rendering, and output length change. Continuity means the question,
passages, sampler settings, checker statistic, and paired design remain visible.

## Locked model and runtime

- Model and processor: `google/gemma-4-E2B-it`.
- Revision: `3e22461f65e89153144f8adb70e3b8c2cc9845a7`.
- Recorded model-card license: Apache 2.0.
- Model file: `model.safetensors`, 10,246,621,918 bytes at the locked revision.
- Model class: the pinned Transformers multimodal auto model used for Gemma 4.
- Python: 3.12.
- PyTorch: the exact Linux version resolved by `uv.lock`.
- Transformers: 5.14.1.
- Hugging Face Hub: 1.26.0.
- Modal SDK: 1.5.3.
- Device: exactly one NVIDIA L4 through Modal. Reject another GPU before loading weights.
- Precision: BF16 model weights with no quantization, compile, CPU offload, or silent fallback.
- Batch size: one. Evaluation and inference mode.

Record the CUDA runtime, driver, GPU name, total VRAM, vocabulary size, package versions, model
revision, model file size, source commit, configuration hash, Modal App name, and image metadata.

## Modal resources

- App name: `text-watermarking-lab-05`.
- Image: Python 3.12 Debian plus exact locked Stage 5 runtime dependencies and local
  `watermark_lab` source. Assert package versions inside the container.
- GPU function: one L4, one input at a time, one smoke invocation.
- Secret: anonymous model access is the default. Use existing Modal Secret `huggingface`, which
  supplies `HF_TOKEN`, only if the pinned anonymous download fails. Never print or serialize the
  token or a token fingerprint.
- Volume: none. The first smoke deliberately measures one disposable cold download and creates no
  persistent Stage 5 cache.
- Results: return JSON-compatible data to the local caller. The container filesystem is not an
  evidence store.

The hard Stage 5 cost ceiling is USD 5.00. Current published Modal rates are recorded in the
configuration with source and retrieval date. If client-observed elapsed time or the projection
crosses the ceiling, stop rather than changing the model, GPU, precision, or fixture.

## Locked prompt and generation contract

Gemma 4 Instruct receives one user message:

`Continue the passage with one short paragraph. Return only the continuation.\n\n<passage>`

Render it with the pinned processor's chat template, `add_generation_prompt=True`, and thinking
disabled when the template supports that option. Record the complete rendered text, input IDs, and
input pieces. Generated evidence excludes any reasoning channel and uses the processor's parsed
final response when available; raw generated text and IDs remain in the selected artifact.

For each passage, generate `control` and then `reference_watermark`. Reset the CUDA random state to
the same prompt-derived seed before each condition. Use:

- at most 200 new tokens;
- `do_sample=True`;
- temperature `0.8`;
- top-k `40`;
- top-p `0.95`;
- model end-token and pad-token behavior from the pinned processor and model;
- no prompt, seed, key, or setting search after observing output.

The watermarked call passes one Transformers `WatermarkingConfig` with the locked Stage 4 recipe.
The control call omits it. Transformers owns the generation loop and maintained processor order.

Early end tokens, weak detector evidence, awkward prose, and output-ID round-trip mismatches remain
results. They are not grounds for prompt or seed tuning.

## Copied-text detection

For each condition:

1. obtain the displayed continuation text;
2. tokenize that copied text again with the pinned Gemma processor/tokenizer;
3. exclude prompt and padding IDs;
4. run generation-key and comparison-key detectors on CUDA;
5. record all-occurrence and library `ignore_repeated_ngrams=True` policies;
6. record `G`, `T`, green fraction, z, p-value, threshold, and strict prediction;
7. recompute z with the Stage 1 formula and require agreement.

The primary result is generation key plus all-occurrence counting. The other three results are
compatibility checks. A positive result means only “consistent with this configured watermark and
key.”

## Benchmark definitions

Use `time.perf_counter_ns()` for host intervals and synchronized CUDA events for GPU intervals.
Record the measurement source beside each value.

- `remote_total_ns`: remote user-code entry through completed result assembly.
- `model_download_ns`: pinned snapshot download start through local snapshot availability. Record a
  cache-hit Boolean.
- `model_load_ns`: snapshot available through BF16 model on CUDA in evaluation mode.
- `generation_wall_ns`: synchronized call interval for one `generate()` call.
- `generated_tokens_per_second`: generated copied token count divided by generation wall seconds.
  This includes prompt processing and is not called decode-only speed.
- `watermark_processor_gpu_ns`: total synchronized CUDA event time spent inside the maintained
  watermark processor during one separate instrumented replay. Divide by processor calls for the
  displayed per-call value. Instrumented timing is not used to select the saved continuation.
- memory: allocated and reserved bytes after load, then peak allocated and reserved bytes for each
  condition after resetting peaks.
- headroom: `(total_vram - peak_reserved) / total_vram`.

If first-token latency, Modal queue time, image-build time, or billed cost cannot be measured from
user code, record them as unavailable. Do not infer them from unrelated intervals.

## Cost projection

Lock the rate snapshot to:

- L4 GPU: USD `0.000222` per second;
- CPU: USD `0.0000131` per physical core-second;
- memory: USD `0.00000222` per GiB-second;
- Volume: USD `0.09` per GiB-month, with no Stage 5 Volume used;
- source: `https://modal.com/pricing`;
- retrieved: `2026-08-15`.

Project the 24-row paired run at 200 tokens (`9,600` generated tokens) and 400 tokens (`19,200`
generated tokens) from the slower measured condition throughput. Show the formula. Report a
GPU-only generation projection separately from unmeasured image build, download, model load, CPU,
memory, and storage components. Do not call the GPU-only figure a total bill.

## Quality smoke rubric

Before the run, define one Boolean judgment per row and condition for:

- non-empty final continuation;
- more than one generated content token;
- no immediate end token;
- no obvious short phrase repeated three or more times consecutively;
- readable continuation relation to the fixed passage.

These are smoke checks, not a quality estimate or blinded comparison. Preserve the text regardless
of outcome.

## Selected evidence

`artifacts/lab-05/trace.json` contains:

- stable schema, source commit, configuration hash, and claim labels;
- exact model, processor, revision, file, license, runtime, CUDA, GPU, App, image, secret-use, and
  no-Volume metadata;
- three prompts, rendered inputs, IDs, pieces, paired seeds, conditions, and generation settings;
- raw generated IDs/text, parsed copied continuation, copied IDs, and match status;
- four detector results per continuation;
- raw nanoseconds and bytes for all observable benchmark fields;
- quality smoke judgments;
- measured totals and the two run projections;
- go/no-go checks and explicit unavailable measurements.

`artifacts/lab-05/annotated_trace.md` renders the three paired rows, the continuity timing/memory
story, copied-text detector evidence, and the projection. Stable selected files contain no secret,
cache path, raw Modal log, or mutable timestamp.

Ignored operational output lives below
`runs/lab-05/<source_commit>/<config_sha256>/`. It may contain invocation timing and raw returned
JSON. Selected artifacts must be generated from the returned result, never edited by hand.

## Commands and verification

- `just lab-05` is the only cost-incurring command. It refuses a dirty worktree, validates the
  allowlist, performs at most one six-generation Modal smoke invocation, and writes local evidence.
- `just verify-lab-05` is local, network-free, GPU-free, and cost-free. It validates schema,
  source/config hashes, exact prompt/condition order, paired seeds, settings, token/count
  invariants, Stage 1 z recomputation, finite numbers, cost arithmetic, claim boundaries, and
  byte-for-byte regeneration of annotated Markdown from JSON.
- `just check` never imports Modal during test collection, calls a model, accesses the network, or
  starts cloud work. Tests use config records, arithmetic, saved vectors, and fakes.

There is no hidden remote replay command. Another GPU invocation requires a new explicit approval.

## Go/no-go and stop rule

Recommend later Stage 6/full-run planning only if:

- the exact revision loads as BF16 on one L4 with no fallback or offload;
- all six generations and copied-text checks complete;
- local verification passes;
- peak reserved memory leaves at least 20 percent of total VRAM free;
- the slower watermarked condition reaches at least 2 generated tokens per second;
- no output is empty, ends immediately, or enters an obvious repeated loop;
- both 200- and 400-token projections are shown against the USD 5.00 ceiling.

Positive score separation is not a pass requirement. If memory, speed, runtime correctness, or the
smoke rubric fails, stop and report it. Do not silently use another GPU, quantization, E4B, shorter
settings, or a different prompt. Stage 5 ends after this smoke test regardless of outcome.
