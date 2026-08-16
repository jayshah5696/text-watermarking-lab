# Stage 8 editing and bias trade-off contract

> Status: frozen pre-run contract. This file authorizes no replacement invocation.

## Question

How does ordinary editing change the correct-key evidence in the frozen Stage 7 outputs, and what
changes when generation bias moves from 2 to 1 or 3?

## Continuity from Stage 7

Stage 8 starts with the first twelve marked outputs from Stage 7, selection ranks `1000` through
`1011`. Their copied text, copied token IDs, generation key, tokenizer, and unedited scores stay
fixed. Rank `1000` remains the teaching spine. Rank `1001` remains the inconvenient row.

The first twelve rows are selected by manifest order before any Stage 8 attack result exists. No row,
text, attack result, prompt, or seed may be replaced after observation.

The primary editing comparison uses the first `80` copied token IDs after each edit. All twelve
Stage 7 marked outputs contain at least 153 copied token IDs, so the unedited baseline supports this
prefix. An edited output that contains fewer than 80 copied token IDs remains in the artifact as a
length failure and does not receive an invented score.

## Exact inherited profile

- model and tokenizer: `google/gemma-4-E2B-it`
- revision: `3e22461f65e89153144f8adb70e3b8c2cc9845a7`
- Transformers: `5.14.1`
- PyTorch: `2.13.0`
- generation device: one Modal NVIDIA L4
- detector: green fraction `0.25`, generation key `15485863`, `lefthash`, context width `1`
- cutoff: strict `z > 3`
- sampler: temperature `0.8`, top-k `40`, top-p `0.95`
- normal Gemma end-token behavior: enabled

Stage 8 does not switch to the context-width-four proposal in the early research notes. Doing so
would break continuity with the frozen Stage 7 evidence.

## Deterministic editing fixture

Apply every edit to the complete copied marked text. The detector then re-tokenizes the displayed
result with the pinned Gemma tokenizer. Each transformation records its exact operations.

### 1. Text normalization

Apply these operations in order:

1. Unicode NFKC normalization;
2. replace left and right single quotes with ASCII `'`;
3. replace left and right double quotes with ASCII `"`;
4. replace en dash and em dash with ASCII `-`;
5. replace non-breaking spaces with ordinary spaces; and
6. collapse each whitespace run to one ASCII space and strip its ends.

This is one named transformation. It does not silently run before the other attacks.

### 2. Homoglyph substitution

Run separate `1%` and `5%` conditions. Eligible characters are ASCII letters present in this fixed
mapping:

```text
a -> Cyrillic small a       c -> Cyrillic small es
e -> Cyrillic small ie      i -> Cyrillic small byelorussian-ukrainian i
o -> Cyrillic small o       p -> Cyrillic small er
x -> Cyrillic small ha      y -> Cyrillic small u
A -> Cyrillic capital A     B -> Cyrillic capital Ve
C -> Cyrillic capital Es    E -> Cyrillic capital Ie
H -> Cyrillic capital En    K -> Cyrillic capital Ka
M -> Cyrillic capital Em    O -> Cyrillic capital O
P -> Cyrillic capital Er    T -> Cyrillic capital Te
X -> Cyrillic capital Ha
```

For each row and rate, derive a seed from SHA-256 of
`lab-08|20260814|homoglyph|<rank>|<rate>|<stage7_text_hash>`. Rank eligible character positions by
SHA-256 of the seed and position, then replace the first `round(rate * eligible_count)` positions.
At least one character is changed when the eligible count is nonzero. Record original index, source
and replacement code point, and visible character.

This condition measures tokenizer and Unicode resilience. It is not a semantic paraphrase.

### 3. Word deletion

Run separate `10%` and `30%` conditions. A word is one Unicode non-whitespace run. Derive a seed from
`lab-08|20260814|deletion|<rank>|<rate>|<stage7_text_hash>`, rank word indices by SHA-256, and remove
exactly `round(rate * word_count)` words. Join retained words with one space. Record every removed
index and surface form.

Deletion is allowed to damage grammar or meaning. Such damage stays visible and blocks any claim of
a successful meaning-preserving removal.

### 4. Copy-paste mixing

Run separate `25%` and `50%` conditions. Split the marked and paired control texts into Unicode
non-whitespace runs. The aligned region has `min(marked_words, control_words)` positions. Derive a
seed from `lab-08|20260814|mixing|<rank>|<rate>|<stage7_text_hash>`, rank aligned positions by
SHA-256, and replace exactly `round(rate * aligned_count)` marked words with control words at the
same indices. Retain any marked tail. Join with one space. Record every replaced index and both
surface forms.

This is a deterministic token-source mixture, not a claim that the result preserves one coherent
author or meaning.

## Model paraphrase fixture

Run one unwatermarked Gemma rewrite for each of the same twelve marked texts. The exact user prompt
is:

```text
Rewrite the passage below in fresh wording. Preserve every factual claim, named entity, number, and
qualification. Keep roughly the same length. Return only the rewritten passage.

<passage>
{stage7_marked_copied_text}
</passage>
```

Use a per-row seed derived from SHA-256 of
`lab-08|20260814|paraphrase|<rank>|<stage7_text_hash>`. Use the inherited sampler, no watermark
configuration, and a `400` generated-token safety cap with normal end-token behavior. The output is
never retried or extended.

Record generated IDs, copied text, copied IDs, stop reason, achieved length, generation wall time,
and the exact prompt. A paraphrase passes the automatic preservation screen only when:

- it contains at least 80 copied token IDs;
- its copied-token length ratio to the source is between `0.80` and `1.20`, inclusive;
- every decimal number from the source remains present exactly; and
- cosine similarity between mean final-layer text-model states is at least `0.80`.

The cosine value is a measured model-based proxy, not proof of equal meaning. A separate blinded
manual review records pass, fail, or uncertain for factual claims, named entities, numbers, and
qualifications. The article may call a paraphrase a meaning-preserving removal only when the length
screen, automatic screen, and manual review all pass.

## Bias sweep

Use Stage 7 ranks `1000` through `1007`, selected by manifest order. Reuse each Stage 7 marked output
as the `delta=2` baseline. Generate one new continuation at `delta=1` and one at `delta=3` from the
same exact rendered input and paired Stage 7 seed.

Each new call keeps model, prompt, seed, sampler, end-token behavior, key, green fraction, context
width, and 400-token safety cap fixed. Only watermark bias changes. Call order per row is `delta=1`,
then `delta=3`. No delta-2 generation is repeated.

For all three deltas, record:

- achieved generated and copied lengths;
- correct-key `G`, `T`, z, exact upper tail, and strict decision at copied prefixes 40 and 80 where
  available;
- conditional continuation negative log likelihood under the unmodified Gemma checkpoint;
- repeated adjacent-pair fraction;
- distinct token bigram and trigram fractions; and
- generation wall time for the newly generated conditions.

The Stage 7 delta-2 runtime is retained as a separately measured baseline. Do not imply that these
eight prompts estimate a population quality curve.

## Remote envelope

One Stage 8 invocation may use:

- one NVIDIA L4;
- the already pinned Gemma and tokenizer snapshot;
- exactly 28 generation calls: 12 paraphrases plus 16 bias-sweep calls;
- at most 11,200 generated token IDs;
- no dataset download;
- no Secret, Volume, endpoint, or persistent deployment;
- a 3,600 second timeout; and
- a hard ceiling of USD 5.

The runner receives the selected Stage 7 rows directly. It must verify their source commit,
configuration hash, model revision, row ranks, text hashes, prompts, seeds, and copied texts before
using them.

A failed or canceled invocation does not authorize a retry. Save the operational record and stop.

## Selected evidence

- configuration: `configs/lab_08.toml`
- ignored raw return: `runs/lab-08/modal-result.json`
- manual review: `data/reviews/lab-08-paraphrase.json`
- selected JSON: `artifacts/lab-08/results.json`
- readable ledger: `artifacts/lab-08/results.md`
- signal-loss figure: `artifacts/lab-08/edit_signal_loss.{png,svg}`
- bias trade-off figure: `artifacts/lab-08/bias_tradeoff.{png,svg}`
- local verifier: `scripts/verify_lab_08.py`
- remote command: `just lab-08`
- local command: `just verify-lab-08`

The verifier rebuilds deterministic edits, tokenizer evidence, score records, metric summaries, and
figures from the Stage 7 artifact plus the ignored Stage 8 return. Manual semantic judgments remain
human evidence and are reported as such rather than recomputed.

## Exit gate

Stage 8 closes only when:

- every deterministic attack reproduces exactly;
- all 28 model calls remain present, including short or failed outputs;
- each displayed score reconstructs from recorded token evidence;
- length and meaning screens appear beside any claimed removal;
- the delta sweep keeps all eight rows and all three settings visible;
- `just check` and `just verify-lab-08` pass;
- the blog handoff and claims ledger match the artifact;
- the interactive lesson preserves the Stage 7 row and token continuity; and
- browser QA passes desktop, mobile, dark, reduced-motion, scripts-off, keyboard, console, and
  overflow checks.

Stage 8 does not implement another watermark family, another model, translation, adaptive attacks,
production key security, generic AI detection, or Claude's private implementation.
