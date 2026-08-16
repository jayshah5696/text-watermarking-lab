# Stage 6 natural-web calibration contract

## Authorization and stop rule

The user approved Stage 6 implementation, C4 access, and whichever local or Modal execution path is
best. One detector-only Modal L4 invocation is allowed. It must not load model weights, generate
text, create a Secret or Volume, deploy an endpoint, or start Stage 7. The invocation may download
the pinned 14.6 MiB compressed validation shard and the pinned Gemma tokenizer files. It must stop
after scoring the frozen manifest. A failed or canceled invocation does not authorize a retry.

## Question

What scores does the Stage 5 checker assign to text that was not generated with its key?

Stage 5 showed 12 hand-written prompts with paired model outputs. None of the 12 controls crossed
strict `z > 3`, but 12 prompts cannot describe the natural-web negative distribution. Stage 6 keeps
the checker profile fixed and changes the source of text.

## Pinned sources and profile

- dataset repository: `allenai/c4`
- dataset revision: `1588ec454efa1a09f29cd18ddd04fe05fc8653a2`
- configuration and split: `realnewslike`, `validation`
- validation shard: `realnewslike/c4-validation.00000-of-00001.json.gz`
- compressed shard SHA-256: `42ac859dc1c4d48d165ec602909403e2066ce1d4854149ed70b9ec9cc96dc65f`
- declared validation rows: `13,863`
- tokenizer: `google/gemma-4-E2B-it` at Stage 5 revision
  `3e22461f65e89153144f8adb70e3b8c2cc9845a7`
- detector: Transformers `5.14.1`, CUDA, `lefthash`, context width `1`, green fraction `0.25`,
  public key `15485863`, and strict cutoff `z > 3`
- primary count: every eligible adjacent token pair, matching the Stage 5 result rows
- diagnostic count: each distinct value-based adjacent token pair once

The CUDA device is part of the pinned Transformers pseudorandom profile. CPU scoring is not a
substitute for this artifact.

## Deterministic selection

Iterate the pinned shard in file order. Tokenize exact row text without model special tokens. Apply
the first matching rejection reason in this order:

1. `too_short`: fewer than 500 Gemma tokens;
2. `duplicate_text`: SHA-256 of the exact UTF-8 text already appeared;
3. `obvious_list`: at least eight non-empty lines and at least half begin with a bullet or numbered
   list marker;
4. `code_dump`: at least five code-like non-empty lines and at least 20 percent of non-empty lines
   are code-like;
5. `low_letter_fraction`: Unicode letters are less than 65 percent of non-whitespace characters.

The first 1,000 passing rows form `calibration`. The next 24 form `paired_test`. Stop scanning as
soon as both splits are full. The selected manifest stores dataset row index, URL, timestamp, text
SHA-256, full token count, fixed token ranges, split, and selection rank. It stores no full article
text. The first selected row may include short prompt and continuation excerpts in the selected
evidence for teaching.

For every selected row:

```text
tokens 0..49     future shared prompt
tokens 50..449   natural-web continuation scored in Stage 6
```

The 24 `paired_test` rows are frozen for Stage 7 but are not generated or scored as final test
results here. Calibration is filled first, so the splits are disjoint by construction.

## Scoring and selected evidence

Score only the 400 natural-web continuation token IDs. Do not prepend the 50 prompt tokens. For
each calibration row record all-occurrence `G`, `T`, z, exact binomial upper-tail probability, and
strict decision. Also record value-distinct-pair `G`, `T`, z, exact tail, and decision.

The artifact must include:

- all 1,024 selected manifest rows;
- rejection counts and the last scanned source index;
- all 1,000 calibration score rows;
- empirical count and fraction above the frozen cutoff;
- sorted z quantiles using the nearest-rank index `round(q * (n - 1))` for
  `q = 0.05, 0.50, 0.95, 0.99`;
- the maximum observed z and its manifest identity;
- one complete selected-row token trace with position, ID, decoded piece, eligibility, and keyed
  result, reconciled to the row's aggregate count;
- source commit, exact config hash, package versions, GPU identity, and download hashes.

Do not choose a new cutoff from these scores. The fixed `z > 3` result is an empirical diagnostic.
With 1,000 rows, the smallest non-zero observed fraction is `1/1000`; this cannot validate a
one-in-100,000 false-alarm claim. C4 is natural-web text, not verified human authorship.

## Paths and commands

- config: `configs/lab_06.toml`
- manifest: `data/manifests/lab-06-c4.jsonl`
- selected evidence: `artifacts/lab-06/calibration.json` and `calibration.md`
- ignored raw return: `runs/lab-06/modal-result.json`
- cost command: `just lab-06`
- local verifier: `just verify-lab-06`

The verifier rebuilds the manifest and selected evidence from the raw return, then independently
recomputes every z score, exact tail, decision, quantile, and summary. Unit tests cover selection,
split disjointness, hashes, CUDA-result schema, and fixed scorer vectors.

## Exit gate

Stage 6 closes when the manifest is immutable, all 1,000 negative rows remain visible, selected
files reconstruct locally, the lesson preserves the strongest inconvenient row, and browser QA
passes. No Stage 7 model generation is included.
