# Stage 3 implementation contract: manual causal model loop

## Authorization

The user approved the full local Stage 3 slice on 2026-08-12. This approval includes downloading
the model and tokenizer pinned below and installing the locked CPU dependencies needed to run them.

This stage must not use a dataset, GPU, Modal, secret, new remote, pull request, deployment, or
publishing workflow. It must stop before the Stage 4 `generate()` and `WatermarkDetector` adapter.

## Question

Where does the watermark sit between a model's next-token scores and token sampling?

## Continuity

Stage 1 counted green hits. Stage 2 showed how a key and recent token history define a green hit in
a 20-token toy vocabulary. Stage 3 keeps the same count, green fraction, bias, and paired random
seed. It replaces the hand-written scores and one-word labels with scores and token IDs from a real
causal language model.

The Stage 2 SHA-256 selector must not be imported. Stage 3 uses the pinned Transformers
`WatermarkLogitsProcessor` directly. Stage 4 will compare this manual loop with the library's full
generation and detector adapters.

## Locked model and runtime

- Model and tokenizer: `openai-community/gpt2`.
- Model and tokenizer revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
- Transformers: `>=5.14.1,<5.15`, resolved exactly by `uv.lock`.
- PyTorch: `>=2.13,<2.14`, resolved exactly by `uv.lock`.
- Device: CPU only.
- Model mode: evaluation with inference mode and float32 weights.
- Batch size: one.
- The lab may download only the pinned model and tokenizer. The verifier must use the local cache.

GPT-2 was chosen because it is small, public, and used by the current Transformers watermarking
documentation. Its output is not evidence about current model quality or the article's later
headline model.

## Locked prompts and generation settings

`configs/lab_03.toml` must contain these three prompt fixtures in this order.

1. `stage-02-continuity`: `Early one morning Jack went up the hill. At the top he`
2. `notebook`: `The student opened the notebook and wrote down each result because`
3. `library`: `When the neighborhood library lost power, the staff`

The remaining settings are:

- base seed `20260812`;
- 40 new tokens at most for each continuation;
- stop when GPT-2 emits its end token;
- temperature `0.8`;
- top-k `40`;
- top-p `0.95`;
- green fraction `0.25`;
- watermark bias `2.0`;
- hashing key `15485863`;
- comparison key `15485867`;
- `lefthash` seeding;
- context width `1`;
- five candidates retained in the readable trace.

Derive one seed per prompt by hashing the ASCII text
`lab-03|<base-seed>|<prompt-id>` with SHA-256 and reading the first eight bytes as an unsigned
big-endian integer. Reinitialize a CPU `torch.Generator` with that seed for each condition. The
control continuations and continuations with the score increase enabled for one prompt therefore
receive the same random stream, but
their token histories may diverge after the intervention changes a sampled token.

## Manual loop order

Write the autoregressive loop explicitly for one batch row. At every position:

1. Pass the full prompt and generated token history to the model.
2. Read the logits at the final sequence position.
3. Divide the logits by the temperature.
4. Keep the top 40 logits.
5. Apply top-p filtering at 0.95 to the remaining logits.
6. For the watermarked condition, call the pinned `WatermarkLogitsProcessor`.
7. Convert the resulting scores to probabilities.
8. Sample one token with the condition's seeded CPU generator.
9. Append the sampled token and repeat.

This order matches Transformers 5.14.1. The package source places watermarking after its sampling
processors. It differs from the older algorithm planning note, which placed the watermark before
temperature and filtering. A regression test must lock the order. In particular, watermarking must
not restore a token that top-k or top-p already removed.

Do not call `model.generate()`. Do not call `WatermarkDetector`. Those adapters belong to Stage 4.

## Copied-text scoring

The checker must use the same pinned `WatermarkLogitsProcessor` that generation uses. It may pass
zero scores through the processor and compare the scores before and after the increase to find the
green token IDs without calling private methods.

For each decoded continuation:

1. tokenize the copied text again with the pinned tokenizer;
2. store whether the copied token IDs match the generated continuation IDs;
3. score every eligible copied token with the same key used during generation;
4. score the same copied token IDs with the comparison key;
5. store `G`, `T`, and the Stage 1 z score for both keys.

Exclude the prompt from the copied-text score. With context width one, the first copied token is the
checker context and is not eligible. A score is descriptive evidence for this configured trace. It
is not a calibrated decision.

## Selected evidence

`artifacts/lab-03/trace.json` must contain:

- schema version, source commit, configuration hash, platform, Python, Torch, and Transformers
  versions;
- pinned model and tokenizer identifiers and revisions;
- every prompt, prompt token ID, condition, derived seed, stop reason, generated token ID, and
  decoded continuation;
- copied-text token IDs and their exact-match status;
- same-key and comparison-key `G`, `T`, and z scores;
- for every generation step, the input length, watermark context ID, five leading candidates,
  survivor count, selected token ID and text, whether it was green, its score before and after the
  intervention, and its final sampling probability.

`artifacts/lab-03/annotated_trace.md` must render one full token step from the continuity prompt and
a compact six-row paired summary. It must label the outputs as measured from the pinned local
fixture and state the model, version, revision, CPU boundary, and no-calibration caveat.

Both files must use stable UTF-8 serialization, sorted JSON keys, two-space indentation, finite
numbers, and a newline at EOF. They must not contain timestamps or cache paths.

## Public commands

- `just lab-03` downloads the pinned model and tokenizer when absent, refuses a dirty worktree,
  generates all six continuations, and writes the selected evidence.
- `just verify-lab-03` uses only the local model cache, validates the artifact schema and source
  configuration, regenerates the six continuations, and compares both files byte for byte.
- `just check` must not download or run a model. Unit and integration tests must use fixed tensors
  and small fakes.

## Required tests

- fixed seed derivation and configuration validation;
- temperature, top-k, and top-p fixed vectors;
- top-p keeps the first token that crosses the cumulative cutoff;
- a filtered token remains filtered after watermarking;
- bias zero produces the same sampled IDs as the control path;
- paired conditions start from the same seed;
- deterministic replay returns byte-identical records;
- generated token IDs survive decode and copied-text re-tokenization for the fixed tokenizer test;
- the generation key and comparison key can produce different `G`, `T`, and z results;
- the scorer excludes the first copied token when context width is one;
- the lab refuses a dirty worktree;
- the verifier fails after an artifact change;
- no test downloads a model or imports Modal, Datasets, MLX, or a GPU runtime.

## Exit gate

Stage 3 is complete when the manual loop produces and independently verifies paired traces for all
three prompts, a reader can locate the intervention in one token step, and the lesson passes the
Stage Visual Lesson browser checks. Stop before the Stage 4 reference adapter.
