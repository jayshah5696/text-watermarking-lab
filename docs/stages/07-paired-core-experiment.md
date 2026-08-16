# Stage 7 paired core experiment contract

> Status: draft for user approval. This file defines a proposed run. It does not authorize the run by itself.

## Question

Does the configured watermark separate from a paired model control, the recorded natural-web continuation, and the same watermarked text checked with another key? How does that evidence change as more copied tokens become available?

## Continuity from Stage 6

Stage 6 froze 24 `paired_test` rows before generation. Each row already has:

- one C4 source identity and text hash;
- the first 50 Gemma token IDs reserved as a shared prompt;
- the next 400 Gemma token IDs reserved as the natural-web continuation; and
- a fixed position in `data/manifests/lab-06-c4.jsonl`.

Stage 7 must use all 24 rows in manifest order. It must not replace a row, edit a prompt, search a seed, or change stopping behavior after observing output.

## Exact model and runtime

- model and tokenizer: `google/gemma-4-E2B-it`
- revision: `3e22461f65e89153144f8adb70e3b8c2cc9845a7`
- model class: `Gemma4ForConditionalGeneration`
- precision: BF16
- Transformers: `5.14.1`
- PyTorch: `2.13.0`
- device: one Modal NVIDIA L4
- watermark profile: green fraction `0.25`, bias `2.0`, `lefthash`, context width `1`
- generation key: `15485863`
- comparison key: `15485867`
- cutoff: strict `z > 3`
- sampling: temperature `0.8`, top-k `40`, top-p `0.95`
- maximum generated token IDs per call: `400`
- normal Gemma end-token behavior: enabled

The generated-token cap is a safety limit. It is not an achieved length. The artifact must record generated length, copied-text length, and stop reason for every call.

## Prompt construction

For each paired-test row:

1. retrieve the exact pinned C4 row;
2. verify its source index, UTF-8 SHA-256, and full Gemma token count against the Stage 6 manifest;
3. take exact source token IDs `0:50`;
4. decode them with the pinned Gemma tokenizer;
5. re-encode the decoded text without special tokens and require the same 50 IDs;
6. prepend the fixed instruction:

```text
Continue the passage naturally with a detailed, coherent response. Do not summarize early. Return only the continuation.

```

7. render the resulting user message with the pinned Gemma chat template and `enable_thinking=false`.

A failed round-trip check stops the invocation. It does not permit a replacement prompt or retry.

## Seeds and call order

The base seed is `20260813`.

For each row, derive one paired seed by hashing the UTF-8 string:

```text
lab-07|20260813|<selection_rank>|<text_sha256>
```

with SHA-256 and reading the first eight digest bytes as an unsigned big-endian integer.

For every row, reset CPU and CUDA random generators to that seed before each condition. Run the control first and the watermarked condition second. The two calls differ only in the presence of `watermarking_config`.

The remote function makes exactly 48 generation calls in manifest order:

```text
24 rows x [control, watermarked]
```

No failed, empty, short, or below-cutoff generation may be replaced. A short copied continuation remains a recorded row with only the prefixes it supports.

## Copied-text boundary

Primary detection scores the text a reader can copy:

1. slice generated IDs after the rendered prompt;
2. parse only assistant `content`;
3. fall back to special-token-free decoding if the structured parser cannot return text;
4. re-tokenize the displayed copied text without special tokens; and
5. score those copied token IDs without prompt, padding, chat-control, or response-control IDs.

The raw record stores generated IDs, copied text, copied IDs, parser path, stop reason, and whether copied IDs equal generated IDs after end-token handling.

If copied text contains fewer than two token IDs, preserve the row as `insufficient_copied_tokens`. Do not abort the other frozen rows.

## Four score families

At every supported copied-token prefix, record:

1. `watermarked_correct`: watermarked Gemma continuation, generation key;
2. `control_correct`: paired control continuation, generation key;
3. `natural_correct`: recorded natural-web continuation, generation key;
4. `watermarked_comparison`: the same watermarked continuation, comparison key.

Primary scoring counts every eligible adjacent token pair, matching Stages 5 and 6. Also record each distinct value-pair once as a diagnostic. The primary figures and effect sizes use every-pair counts.

For each score, store `G`, `T`, green fraction, z, exact binomial upper tail, strict decision, key role, repetition policy, copied-prefix length, and source identity.

A positive decision means only:

> Consistent with this configured watermark and key.

It does not establish AI origin, model source, authorship, or intent.

## Prefix rule

The fixed copied-token prefixes are:

```text
40, 80, 160, 200, 400
```

A prefix labeled `N` contains the first `N` copied token IDs. With context width one, it supplies `T = N - 1` eligible checks. This matches the earlier 40-token fixtures that produced 39 checks and the Stage 6 400-token continuation that produced 399 checks.

Natural-web continuations support all five prefixes. A generated condition supports a prefix only when its copied text contains at least `N` token IDs.

For aggregate matched comparisons at prefix `N`, include a row only when both its control and watermarked copied continuations support `N`. Use that same complete-prefix cohort for all four score families. Report the cohort size. Do not impute missing prefixes or compare different row sets under one label.

## Effect sizes and intervals

For each prefix, compute three paired effects on the complete-prefix cohort:

```text
watermarked_correct z - control_correct z
watermarked_correct z - natural_correct z
watermarked_correct z - watermarked_comparison z
```

The reported effect is the arithmetic mean of the row-level paired z differences.

Compute a deterministic 95 percent paired bootstrap interval with 10,000 document-level resamples. Sample row indices with replacement, keep each row's paired values together, and use the 2.5th and 97.5th percentile values at nearest-rank index `round(q * (n - 1))`.

Derive each bootstrap seed from SHA-256 of:

```text
lab-07-bootstrap|20260813|<prefix>|<comparison-name>
```

using the first eight digest bytes as an unsigned big-endian integer.

Also report every row-level score, the score-family cutoff counts, and the complete-prefix denominator. The bootstrap intervals summarize these 24 frozen rows. They do not turn the cohort into a population accuracy estimate.

## Predeclared teaching rows

The teaching spine is paired-test selection rank `1000`, the first row frozen for Stage 7. It remains the spine regardless of its generated text, score, stopping point, or decision.

The lesson may also mark one inconvenient row, chosen after the run by this fixed rule at the longest prefix supported by both generated conditions:

1. first row where `watermarked_correct <= control_correct`;
2. otherwise first row where `watermarked_comparison >= watermarked_correct`;
3. otherwise first row where either negative control crosses strict `z > 3`;
4. otherwise the row with the smallest `watermarked_correct - max(control_correct, natural_correct, watermarked_comparison)` margin;
5. break ties by lower Stage 6 selection rank.

This rule searches only the frozen 24-row cohort, reports the reason, and never hides the other rows.

## Token evidence

The ignored raw return must contain enough keyed membership evidence to reconstruct every score locally. For each sequence and key role, preserve token position, token ID, decoded piece, eligibility, previous token ID, and green membership.

The selected artifact keeps compact scores for all rows and the complete token trace for the fixed spine row. Any lesson token colors must come from this selected trace and reconcile exactly with displayed `G/T` totals.

Green means keyed membership only. It does not mean truth, quality, authorship, or model origin.

## Selected artifacts

Proposed paths:

- configuration: `configs/lab_07.toml`
- ignored raw return: `runs/lab-07/modal-result.json`
- selected result: `artifacts/lab-07/results.json`
- readable result ledger: `artifacts/lab-07/results.md`
- separation figure: `artifacts/lab-07/separation.png` and `.svg`
- prefix-effect figure: `artifacts/lab-07/prefix_effects.png` and `.svg`
- verifier: `scripts/verify_lab_07.py`
- evidence command: `just lab-07`
- local verification: `just verify-lab-07`

The verifier must rebuild selected JSON, Markdown, and both figures from the ignored raw return. It must independently recompute every count, z score, exact tail, decision, complete-prefix cohort, paired difference, bootstrap interval, and teaching-row choice.

## Remote authorization envelope

The proposed evidence run uses:

- one Modal invocation;
- one NVIDIA L4;
- exactly 48 generation calls;
- at most 19,200 generated token IDs;
- one download of the already pinned C4 validation shard;
- one download of the already pinned Gemma model and tokenizer snapshot;
- no Secret;
- no Volume;
- no endpoint;
- no persistent App or Function deployment;
- no dataset or prompt substitution;
- a hard ceiling of USD 5;
- a 3,600 second function timeout.

The function must check the GPU identity, package versions, model file size, dataset file size and hash, manifest identities, call ceiling, token ceiling, and cost ceiling before generation.

A failed or canceled invocation does not authorize another invocation. Preserve the operational record and ask the user before any retry.

## Stop rule

Stop after one raw return has been saved locally. Do not rerun a short row, continue an early-ending row, change a seed, tune a key, alter the bias, suppress end tokens, replace a prompt, start Stage 8 attacks, deploy an endpoint, or publish results.

## Exit gate

Stage 7 closes only when:

- all 24 frozen prompt identities validate;
- all 48 generation records remain present, including failures or short outputs;
- all available row-level prefix points remain visible;
- every selected value reconstructs locally from the raw return;
- the figures regenerate byte-for-byte where their format permits stable bytes;
- the fixed spine and predeclared inconvenient-row rule are honored;
- `just check` and `just verify-lab-07` pass;
- the blog handoff and claims ledger use measured values from the artifact;
- the interactive lesson passes evidence, continuity, accessibility, and browser QA; and
- negative or ambiguous results remain publishable without a replacement run.
