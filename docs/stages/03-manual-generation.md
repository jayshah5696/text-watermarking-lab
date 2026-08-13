# Stage 3 implementation contract: manual causal model loop

## Authorization

The user approved the full local Stage 3 slice on 2026-08-12. This approval includes downloading
the model and tokenizer pinned below, installing the locked MLX dependencies, and using the local
Apple GPU for this stage.

This stage must not use a dataset, Modal, secret, new remote, pull request, deployment, or
publishing workflow. It must stop before the Stage 4 library-adapter comparison.

## Question

Where does the watermark sit between a model's next-token scores and token sampling?

## Continuity

Stage 1 counted green hits. Stage 2 showed how a key and recent token history define a green hit in
a 20-token toy vocabulary. Stage 3 keeps the same count, green fraction, bias, and paired random
seed. It replaces the hand-written scores and one-word labels with scores and token IDs from a real
causal language model.

The Stage 2 SHA-256 selector must not be imported. Stage 3 defines a separate, vectorized MLX
selector over the model's full vocabulary. The selector is a portable lab profile, not a
cryptographic construction and not an upstream model feature. Stage 4 may compare the manual loop
with a supported library adapter as a separate profile.

## Locked model and runtime

- Model and tokenizer: `mlx-community/LFM2-350M-4bit`.
- Model and tokenizer revision: `18dc72abf3b2337f9123cfd6eeeb58dfa7947066`.
- MLX-LM: `>=0.31.3,<0.32`, resolved exactly by `uv.lock`.
- MLX: `>=0.31.2,<0.33`, resolved exactly by `uv.lock`.
- Device: the local Apple GPU through MLX.
- Model mode: evaluation with the checkpoint's pinned 4-bit weights.
- Batch size: one.
- The lab may download only the pinned model and tokenizer. The verifier must use the local cache.

LFM2 350M was chosen because the selected checkpoint is small, public, and packaged for native MLX
inference. Its output is not evidence about current model quality or the article's later headline
model. nanoGPT remains a useful teaching reference, but it is training code built around GPT-2 and
PyTorch rather than a newer MLX model fixture.

## Locked prompts and generation settings

`configs/lab_03.toml` must contain these three prompt fixtures in this order.

1. `stage-02-continuity`: `Early one morning Jack went up the hill. At the top he`
2. `notebook`: `The student opened the notebook and wrote down each result because`
3. `library`: `When the neighborhood library lost power, the staff`

The remaining settings are:

- instruction prefix: `Continue the passage with one short paragraph. Return only the continuation.`
  followed by one blank line and the fixed passage;
- input framing: the pinned tokenizer's documented chat template with one user message and a
  generation prompt;
- base seed `20260812`;
- 40 new tokens at most for each continuation;
- stop when the tokenizer emits its end token;
- temperature `0.8`;
- top-k `40`;
- top-p `0.95`;
- green fraction `0.25`;
- watermark bias `2.0`;
- hashing key `15485863`;
- comparison key `15485867`;
- context width `1`;
- five candidates retained in the readable trace.

Derive one seed per prompt by hashing the ASCII text
`lab-03|<base-seed>|<prompt-id>` with SHA-256 and reading the first eight bytes as an unsigned
big-endian integer. Reduce the result to MLX's supported seed range and reinitialize the MLX random
state with that seed for each condition. The control continuations and continuations with the score
increase enabled for one prompt therefore begin with the same random stream, but their token
histories may diverge after the score change alters a sampled token.

For one previous token ID and one public development key, compute a 32-bit mixing score for every
candidate token ID with MLX array operations. Mark exactly `floor(0.25 * vocabulary_size)` candidates
with the lowest mixing scores as green. This is the locked Stage 3 selector. Fixed-vector tests must
pin its membership. The public key is reproducibility metadata, not a production secret.

The author-facing passage stays visible in the lesson. The instruction prefix and control tokens
added by the chat template must appear in a disclosure so the page never implies that the model saw
only the passage. The selected artifact records the complete model-input token IDs and token pieces.

An initial unselected diagnostic fed the post-trained checkpoint raw passage text without its
documented chat template. It produced repetitive continuations. That run exposed a missing input
contract and was discarded before evidence selection. The three passages, seeds, sampling settings,
keys, green fraction, and score increase were not changed.

## Manual loop order

Write the autoregressive loop explicitly for one batch row. At every position:

1. Pass the prompt token IDs through the model and create an MLX key-value cache.
2. Read the logits at the final sequence position.
3. For the score-increase condition, identify the green candidates and add `2.0` to their logits.
4. Divide the logits by temperature `0.8`.
5. Apply top-p filtering at `0.95`.
6. Keep the top `40` remaining logits.
7. Normalize the remaining scores into log probabilities.
8. Sample one token with the condition's seeded MLX random state.
9. Append the token, pass that one new token through the cached model state, and repeat.

This is the locked Stage 3 manual order. The score increase occurs before temperature and sampling
filters, matching the project's algorithm note. A regression test must lock the order. A green token
can still be removed by top-p or top-k after its score increases.

Do not call `mlx_lm.generate()` or its hidden generation loop. A library adapter comparison belongs
to Stage 4.

## Copied-text scoring

The checker must use the same vectorized Stage 3 selector that generation uses.

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

- schema version, source commit, configuration hash, platform, Python, MLX, and MLX-LM versions;
- pinned model and tokenizer identifiers and revisions;
- every prompt, complete model-input token ID and token piece, condition, derived seed, stop reason,
  generated token ID, and decoded continuation;
- copied-text token IDs and their exact-match status;
- same-key and comparison-key `G`, `T`, and z scores;
- for every generation step, the input length, watermark context ID, five leading candidates,
  candidate counts after each filter, selected token ID and text, whether it was green, its score
  before and after the configured increase, and its final sampling probability.

`artifacts/lab-03/annotated_trace.md` must render one full token step from the continuity prompt and
a compact six-row paired summary. It must label the outputs as measured from the pinned local
fixture and state the model, versions, revision, local Apple GPU boundary, and no-calibration caveat.

Both files must use stable UTF-8 serialization, sorted JSON keys, two-space indentation, finite
numbers, and a newline at EOF. They must not contain timestamps or cache paths.

## Public commands

- `just lab-03` downloads the pinned model and tokenizer when absent, refuses a dirty worktree,
  generates all six continuations, and writes the selected evidence.
- `just verify-lab-03` uses only the local model cache, validates the artifact schema and source
  configuration, regenerates the six continuations, and compares both files byte for byte.
- `just check` must not download or run a model. Unit and integration tests must use fixed arrays
  and small fakes.

## Required tests

- fixed seed derivation and configuration validation;
- portable selector, temperature, top-k, and top-p fixed vectors;
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
- no test downloads a model or imports Modal or Datasets; MLX tests use only small local arrays.

## Exit gate

Stage 3 is complete when the manual loop produces and independently verifies paired traces for all
three prompts, a reader can locate the intervention in one token step, and the lesson passes the
Stage Visual Lesson browser checks. Stop before the Stage 4 reference adapter.
