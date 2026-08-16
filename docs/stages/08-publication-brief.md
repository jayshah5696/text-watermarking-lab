# Stage 8 publication brief

> Status: pre-run design. Measured fields remain open until the frozen run verifies.

## Article role

Stage 7 froze unedited marked outputs and found average correct-key separation from three controls.
Stage 8 asks what happens when the visible text changes, and whether a stronger generation bias buys
more detector evidence at a measurable text-model cost.

A reader should leave able to trace one recorded output through one edit, distinguish lost length
from broken watermark context, and read a bias trade-off without treating NLL as human quality.

Narrow pre-run answer:

> Re-tokenize each edited copy, rebuild membership from its new history, then keep only conclusions
> that pass the declared length and meaning checks. For the bias sweep, change delta alone and show
> detector evidence beside model-based quality proxies.

Assume the Stage 7 meaning of copied tokens, `G/T`, z, strict `z > 3`, and paired rows. Define here:
normalization, homoglyph, deletion, mixing, paraphrase, length ratio, semantic proxy, NLL,
repetition, and distinct n-grams.

## Teaching spine

Keep selection rank `1000`, its complete Stage 7 marked copied text, generation key, and 80-token
score. Its exact character string is the starting object. Do not replace it with an authored
sentence or the strongest Stage 8 result.

The first causal trace is one deterministic word deletion:

1. show the original copied characters and Gemma token boundaries;
2. identify the fixed deleted word indices;
3. remove those words and close the gaps;
4. re-tokenize the complete displayed result;
5. preserve token identity only until the first changed token boundary;
6. rebuild every later keyed decision from the edited previous token;
7. compare original and edited `G/T`, z, length ratio, and decision; and
8. state whether the edit preserved enough length and meaning for its result to count as a
   successful removal.

The challenging case stays rank `1001`, carried from Stage 7. It prevents the page from implying
that a watermark must already separate before editing or that a score loss always starts from a
positive row.

## Fixture selection

- deterministic attacks and paraphrase: ranks `1000` through `1011`;
- bias sweep: ranks `1000` through `1007`;
- teaching spine: rank `1000`;
- inconvenient row: rank `1001`;
- primary attack prefix: first 80 copied token IDs after each edit;
- Stage 7 delta-2 outputs are reused, never regenerated;
- no row, prompt, seed, attack, or result replacement after observation.

## Visual plan

### Figure 1: one copied string becomes a new token history

Reader question: why can deleting a few words affect checks after the deleted words?

Keep the Stage 7 spine text at the top. Mark deleted word indices in coral. Under it, show edited
characters, new tokenizer boundaries, and the first boundary mismatch. From that point, split the
old and new token lanes. Green/red membership is attached to exact token IDs and previous IDs, never
copied by visual position.

Caption:

> Deletion changes the visible string. The tokenizer then produces a new ordered token history, so
> the checker rebuilds later keyed decisions from different previous-token contexts.

Alt text:

> Two aligned text and token lanes show one recorded marked passage before and after deterministic
> word deletion. The lanes stop matching at the first changed token boundary. Later keyed checks are
> recomputed on the edited history.

### Figure 2: every edit, every row

Reader question: how much correct-key z remains, and did the edited text still pass the declared
checks?

For each attack, plot all 12 paired z changes from the unedited 80-token baseline. Put zero score
change and the strict cutoff on separate guides. Encode automatic meaning and length pass with
shape and text, not color alone. Homoglyph conditions receive a visible Unicode-warning label.

Caption:

> Each dot is one frozen Stage 7 output after one declared edit. Score loss, retained length, and
> preservation checks stay separate, so damaged or shortened text cannot masquerade as a successful
> meaning-preserving removal.

Alt text:

> Rows of paired z changes for normalization, two homoglyph rates, two deletion rates, two mixing
> rates, and paraphrase. Each point includes a pass, fail, or uncertain preservation marker.

### Figure 3: change delta alone

Reader question: what does a larger generation bias buy on the same eight prompts?

For delta 1, 2, and 3, connect each row's 80-token z where supported. Put NLL change and repetition
on aligned panels with the same row order. Show achieved copied length separately from the 400-token
cap. Display raw points before means.

Caption:

> The same eight frozen prompts and seeds use delta 1, 2, and 3. Detector evidence and model-based
> text proxies are shown together. The proxies do not replace human quality judgment.

Alt text:

> Three aligned panels connect eight prompts across watermark bias values. Panels show correct-key z,
> continuation negative log likelihood, and repetition, with achieved copied lengths labeled.

## Context-free screenshot tests

1. Edit trace: a newcomer can point to the exact edit, first token-boundary change, and why later
   checker states are rebuilt rather than shifted.
2. Attack cohort: a newcomer can read score change, retained length, and meaning-screen status as
   three separate facts.
3. Bias trade-off: a newcomer can identify what stayed fixed, what delta changed, and why NLL is a
   proxy rather than a quality verdict.

## Evidence contract

The selected artifact must retain:

- Stage 7 source commit, config hash, row identities, original copied strings, copied IDs, and
  baseline scores;
- exact deterministic edit operations and seeds;
- edited strings, IDs, token pieces, eligibility, previous IDs, and keyed membership;
- original and edited `G/T`, z, exact tail, decision, lengths, and ratios;
- paraphrase prompt, seed, generated IDs, copied text, stop reason, wall time, embedding similarity,
  number preservation, length screen, and manual review status;
- delta-sweep prompt, seed, setting, generated and copied lengths, scores, NLL, repetition,
  distinct-2, distinct-3, and runtime;
- complete-row denominators and every paired row difference;
- source commit, Stage 8 config hash, package versions, GPU identity, model identity, total calls,
  total generated IDs, runtime, and resource flags.

Any lesson token color must come from this artifact and reconcile with its aggregate count.

## Expected result before running

Normalization may leave many rows close to baseline when tokenization changes little. Homoglyphs,
deletion, mixing, and paraphrase can alter token IDs or histories and may reduce correct-key
watermark evidence. Stronger deletion or mixing may also damage length, grammar, or meaning.

Increasing delta should tend to increase correct-key evidence. It may also raise NLL or repetition
on some prompts. Neither direction is an exit requirement. Keep null, reversed, short, adverse, and
below-cutoff rows.

## Allowed claims

After verification, measured wording may describe this pinned 12-row attack fixture and 8-row bias
sweep. A positive detector result means only "consistent with this configured watermark and key."
A lower post-edit score may be called a successful meaning-preserving removal only when all declared
preservation checks pass.

## Prohibited shortcuts

- "Watermark removed" when the text fails length or meaning checks.
- Calling homoglyph substitution semantic paraphrase.
- Treating NLL, embedding cosine, or n-gram diversity as human quality.
- Treating a 400-token cap as achieved length.
- Omitting short, failed, adverse, or null rows.
- Comparing unmatched row sets under one mean.
- Claiming universal edit robustness or fragility.
- Claiming generic AI detection, authorship, production calibration, another watermark family, or
  Claude's private implementation.

## Blog handoff

The completed note must preserve this expectation, report the exact Stage 7 inputs, give one full
edit trace, show one failed preservation case near any removal claim, list every attack and bias
row, link figures to selected evidence, and end by separating experimental findings from production
security claims.
