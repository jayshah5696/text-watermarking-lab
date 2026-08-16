# Stage 5 natural-length evidence ladder

## Authorization and stop rule

The user approved one additional bounded Modal L4 invocation. It contains exactly twelve frozen
prompts and twenty-four generation calls: control and watermarked generation for each prompt. It
uses the same pinned Gemma revision, BF16 precision, one L4, paired-seed rule, sampler, watermark
profile, copied-text boundary, and generation-key detector as the existing Stage 5 evidence.

This invocation creates no dataset, Secret, Volume, endpoint, or persistent resource. It must remain
below the existing USD 5 ceiling. It must not rerun, replace prompts, change seeds, suppress EOS, or
alter watermark settings to obtain a score above three.

## Question

How does naturally achieved continuation length change configured-key evidence, and which copied
Gemma token pieces count as green or red under the key?

## Frozen design

Use twelve original long-form continuation prompts, four in each declared cap group:

- maximum 200 generated token IDs;
- maximum 400 generated token IDs;
- maximum 800 generated token IDs.

The cap is a safety boundary, not a target. Normal Gemma end-token behavior remains active. Report
the achieved copied-token length and stop reason for every output. Cap groups must not be described
as measured 200-, 400-, or 800-token outputs unless the model actually reaches those lengths.

The prompts should invite sustained narrative, explanation, procedural writing, and world-building.
Prompt identity and cap are frozen in `configs/lab_05_lengths.toml` before the invocation. No output
is selected, discarded, or extended after observation.

## Token-level evidence

For each copied continuation and the public generation key:

1. tokenize only displayed copied text with the pinned Gemma tokenizer;
2. exclude prompt, padding, chat control, and special response tokens;
3. use the maintained detector's exact context-width-one green-list decision for every eligible
   copied token;
4. record each copied token ID, decoded token piece, zero-based copied position, eligibility, and
   green/red result;
5. require the token-level eligible and green totals to equal the primary detector's `T` and `G`;
6. record z, p-value, and strict `z > 3` decision.

The first copied token supplies context and is labeled unscored. Green means that this key and prior
copied token place the current token in the configured green set. It is not a semantic quality label.
Red means eligible but outside that set. Token colors must be shown for both control and watermarked
outputs.

## Interpretation

A result above three may emerge naturally. It is not a required outcome. If no row crosses the
cutoff, preserve that result. If a row crosses it, state only "consistent with this configured
watermark and key."

The p-value is the configured no-watermark probability of evidence at least this extreme. It is not
the probability that the text is watermarked.

Twelve prompts are a demonstration, not calibration. Prompt content, achieved length, early EOS,
and token dependence vary together. The result does not estimate detector accuracy, a false-alarm
rate, quality preservation, or a causal length effect.

## Selected evidence and verification

- Raw ignored return: `runs/lab-05/lengths-modal-result.json`.
- Selected JSON: `artifacts/lab-05/lengths.json`.
- Selected Markdown: `artifacts/lab-05/lengths.md`.
- Cost-incurring command: `just lab-05-lengths`.
- Local verifier: `just verify-lab-05-lengths`.

The local verifier checks exact prompt/cap/condition order, paired seeds, copied text and token
arrays, token-level count agreement, Stage 1 z recomputation, p-value bounds, strict decision,
resource identity, no Secret/Volume, configuration hash, and byte-for-byte JSON/Markdown rebuild.
