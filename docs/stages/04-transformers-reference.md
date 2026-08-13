# Stage 4 implementation contract: Transformers reference adapter

## Authorization

The user approved the full local Stage 4 slice on 2026-08-13. This approval includes adding the
locked PyTorch and Transformers dependencies, downloading the exact GPT-2 model and tokenizer
revision named below, and running the reference path on the local CPU.

This stage must not use a dataset, Modal, a secret, a GPU, a new remote, a pull request, a hosted
service, or a publishing workflow. It must stop before Stage 5.

## Question

Does the Stage 3 mental model match the maintained Transformers watermark implementation?

## Narrow answer expected before the run

The same four ideas remain visible: choose a context-dependent green group, change scores, sample
a token, and reconstruct the green count from copied text. Exact equivalence is not assumed. The
pinned Transformers version applies temperature, top-k, and top-p before its watermark processor,
while Stage 3 applied its score increase before temperature, top-p, and top-k.

## Continuity

Stage 4 keeps the three Stage 3 passage fixtures, prompt-derived seeds, 40-token limit,
temperature `0.8`, top-k `40`, top-p `0.95`, green fraction `0.25`, score increase `2.0`, public
development key `15485863`, comparison key `15485867`, and context width `1`.

The runtime profile changes deliberately:

- Stage 3 used `mlx-community/LFM2-350M-4bit`, MLX, a custom `mlx-mix-v1` selector, and a manual
  sampling loop on the local Apple GPU.
- Stage 4 uses `openai-community/gpt2`, PyTorch, Transformers `WatermarkingConfig`, and
  `WatermarkDetector` on the local CPU.

The lesson must keep the continuity passage visible and explain the profile change before it shows
any score. Stage 4 compares contracts and maintained behavior. It must not claim that the GPT-2
output should match the LFM2 output or that the two selectors choose the same green IDs.

## Locked model, tokenizer, and runtime

- Model and tokenizer: `openai-community/gpt2`.
- Revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
- License recorded by the Hugging Face model card: MIT.
- Download boundary: the selected 548,105,171-byte safetensors file plus tokenizer and config
  files. The unused PyTorch binary must not be downloaded when safetensors is available.
- Transformers: `>=5.14,<5.15`, resolved exactly by `uv.lock`.
- PyTorch: `>=2.8,<3`, resolved exactly by `uv.lock`.
- Device: local CPU for generation and detection.
- Model mode: evaluation with float32 checkpoint weights.
- Batch size: one for selected generation records.
- The lab may download only the pinned model and tokenizer. The verifier must use the local cache.

The model is an implementation fixture. It is not evidence about current model quality.

## Locked reference watermark profile

Construct one `WatermarkingConfig` with:

- `greenlist_ratio=0.25`;
- `bias=2.0`;
- `hashing_key=15485863`;
- `seeding_scheme="lefthash"`;
- `context_width=1`.

Construct the comparison-key detector from the same values except
`hashing_key=15485867`. Generation and primary detection must use the same generation-key
configuration object serialized into the selected artifact.

The public key is reproducibility metadata. It is not a production secret.

## Locked prompt and sampling contract

Use the three Stage 3 passages in the same order:

1. `stage-02-continuity`: `Early one morning Jack went up the hill. At the top he`
2. `notebook`: `The student opened the notebook and wrote down each result because`
3. `library`: `When the neighborhood library lost power, the staff`

GPT-2 is a continuation model, so Stage 4 sends each passage directly without the Stage 3 chat
template or instruction prefix. The page must show this input change beside the model change.

Use the Stage 3 base seed `20260812`. Derive each prompt seed from
`lab-03|<base-seed>|<prompt-id>` exactly as Stage 3 did. Reset the PyTorch CPU random state to the
same prompt seed before the control and reference-watermarked calls. The paths share a first
random stream but may diverge after their sampled token histories diverge.

Each call uses `do_sample=True`, at most 40 new tokens, temperature `0.8`, top-k `40`, top-p
`0.95`, and the tokenizer end token as the pad token. Do not search prompts, seeds, or settings for
a stronger score.

## Maintained processor order

Transformers 5.14.1 builds the selected sampling processor list in this order:

1. temperature;
2. top-k;
3. top-p;
4. `WatermarkLogitsProcessor`;
5. sampling.

Stage 3 used:

1. its custom score increase;
2. temperature;
3. top-p;
4. top-k;
5. sampling.

The Stage 4 adapter must use `model.generate()` for selected outputs. It must not reimplement the
library generation loop. A separate order probe may compose the public Transformers processor
classes on the first recorded raw score tensor. It must assert that the reference-order probe
matches the score tensor returned by `generate()`.

The probe must keep raw scores, context IDs, key, temperature, top-k, and top-p fixed. It changes
only processor order. It records candidate survival counts and the final chance of the selected
reference token. Values from the alternate order are derived diagnostics, not generated output.
Only the reference order produces the saved continuation.

The five visible witness rows are fixed by role, not by visual appeal: the selected token, the
highest-chance other green survivor, the highest-chance red survivor, the highest raw-score green
token removed by the reference filters, and the highest raw-score red token removed by the
reference filters. The artifact must label each role.

## Copied-text detection

Decode each generated continuation, then tokenize that copied text again with the pinned GPT-2
tokenizer. The primary detector input contains only copied continuation IDs. It must exclude the
prompt and any padding.

For each copied continuation, record both repeated-context policies:

- count every eligible context and token pair;
- count each unique pair once with `ignore_repeated_ngrams=True`.

For both policies, record the `WatermarkDetector` token count, green count, green fraction,
z-score, approximate p-value, configured threshold, and Boolean prediction. Transformers 5.14.1
uses `z_score > z_threshold` for that Boolean. Also compute the Stage 1 z formula from the recorded
counts and assert that it matches the library z-score.

With context width one, the first copied continuation token supplies context and is not scored. The
second copied token is the first eligible decision. The selected evidence and final lesson must
carry both tokens through the generation and checker handoff.

Run the same copied IDs through a comparison-key detector and store the same fields. A Boolean is
never sufficient evidence by itself.

The primary narrative uses the all-context generation-key score. The unique-context and
comparison-key scores are limitation checks.

## Repetition and padding fixtures

The artifact must include two fixed validations.

1. Build a repeated-history fixture by alternating the first two copied token IDs from the
   continuity reference output three times. Record the visible pieces, all-context result, and the
   library result with `ignore_repeated_ngrams=True`. Independently list distinct adjacent token-ID
   pairs by value and score each pair once with the same library detector. Do not assume the library
   flag deduplicates until the fixed comparison proves it. This construction rule is fixed before
   the output exists.
2. Left-pad the three prompt encodings with the GPT-2 end token as the pad token. Record the padded
   width, attention-mask token count, and continuation slice boundary. Assert that no pad or prompt
   token enters the primary detector input.

The repeated history is a derived detector fixture. It is not model output.

## Selected evidence

`artifacts/lab-04/trace.json` must contain:

- schema version, source commit, configuration hash, platform, Python, PyTorch, and Transformers
  versions;
- pinned model and tokenizer identifiers, revision, license, selected download size, device, and
  reference watermark profile;
- every prompt, prompt IDs and pieces, condition, seed, generated IDs, decoded continuation,
  copied IDs, and copied-ID match status;
- every generation-key and comparison-key detector result for both repetition policies;
- the continuity first-step raw score, reference processed score, selected token, and final chance;
- the two fixed processor orders and their candidate survival counts;
- the repeated-history and left-padding validations.

`artifacts/lab-04/annotated_trace.md` must render the continuity first-step order comparison, a
compact six-row result table, the repeated-history result, and the prompt-exclusion boundary.

Both files use stable finite UTF-8 serialization with sorted JSON keys, two-space indentation, and
a newline at EOF. They must not contain timestamps, cache paths, or unpublished model output beyond
the six fixed continuations.

## Public commands

- `just lab-04` downloads the pinned model and tokenizer when absent, refuses a dirty worktree,
  generates the six selected records, and writes the selected evidence.
- `just verify-lab-04` uses only the local cache, validates source and configuration, regenerates
  all evidence, and compares both selected files byte for byte.
- `just check` must not download or run a model. Tests use fixed tensors, small fakes, saved vectors,
  or local configuration objects.

## Required tests

- exact model, revision, sampling, and watermark configuration validation;
- fixed prompt seed continuity with Stage 3;
- fixed reference green-list and detector vectors from the pinned Transformers version;
- the reference order probe equals `generate()` scores for a small fake model fixture;
- processor order is temperature, top-k, top-p, then watermark;
- prompt tokens and left padding do not enter primary detection;
- copied text is re-tokenized before detection;
- all-context and unique-context policies can return different eligible counts;
- the constructed repeated history checks whether the library unique-context flag actually changes
  counts and compares it with explicit value-based distinct pairs;
- generation and primary detector configurations match exactly;
- comparison-key results are stored as counts and scores;
- Stage 1 z-score recomputation matches the reference detector;
- paired conditions reset to the same seed;
- deterministic replay returns byte-identical records;
- the lab refuses a dirty worktree;
- the verifier fails after an artifact change;
- no test downloads a model or imports Modal or Datasets.

## Exit gate

Stage 4 is complete when the pinned Transformers adapter generates and independently verifies six
local CPU records, the order probe explains the exact agreement and mismatch with Stage 3, counts
and scores survive copied-text replay, and the continuous lesson passes the Stage Visual Lesson
browser checks. Stop before Stage 5 model, cloud, dataset, GPU, or publishing work.
