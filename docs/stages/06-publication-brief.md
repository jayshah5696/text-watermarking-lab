# Stage 6 publication brief

## Article role

Stage 5 proved that the pinned Gemma generation path can carry the configured mark. Stage 6 asks
what the same checker does when no marked generator is involved. The section must make the move
from a theoretical tail to an observed negative distribution concrete.

Narrow answer:

> In one frozen sample of 1,000 C4 natural-web continuations, the unchanged checker produced the
> recorded distribution. That distribution describes this sample and key; it does not certify a
> production false-alarm rate.

## Teaching spine and fixture

Carry the first accepted row through source identity, exact text hash, deterministic filters, Gemma
tokenization, the `50 + 400` split, green-hit counting, z, exact upper tail, and cohort position.
The fixture is selected by order before scoring. It is not chosen because its result looks clean.

Keep the maximum-z row beside it. A natural-web row above the cutoff is the important failure panel,
not an embarrassment to hide. If no row crosses, show the maximum anyway and state the empirical
resolution.

## Figures

### Figure 1: one document becomes two experimental objects

Show one ordered 500-token strip. Mark the first 50 as the future shared prompt and the next 400 as
the natural-web continuation scored now. Preserve token order and scale.

Caption: "Stage 6 scores the recorded web continuation. It freezes the 50-token prefix for the
paired generation stage but does not run a model."

### Figure 2: selection funnel

Show source rows scanned, each fixed rejection reason, 1,000 calibration rows, and the next 24
paired-test rows. Counts come only from selected evidence.

Caption: "A deterministic filter fills calibration first and then freezes 24 disjoint prompts.
Scores cannot influence which rows enter either split."

### Figure 3: every negative score

Plot all 1,000 z scores in manifest order with the strict `z > 3` line. Directly label the spine row
and maximum row. Include a compact distribution view and observed count above the cutoff.

Caption: "Each point is one pinned natural-web continuation checked with the public Stage 5 key.
The observed fraction is a property of this sample, profile, and selection rule."

### Figure 4: repeated-pair diagnostic

For the spine and maximum rows, align all-occurrence and distinct-pair counts. Explain that the
primary Stage 5-compatible result counts every pair; the diagnostic prevents identical value pairs
from being treated as fresh observations more than once.

## Evidence contract

The JSON must carry every plotted value, exact source/config fingerprints, all manifest identities,
all score rows, the full token evidence for the spine row, summary quantiles, and selection counts.
The HTML test must derive or compare every displayed measurement with this artifact.

## Claims

Allowed:

- The pinned C4 validation shard declares 13,863 natural-web rows.
- The deterministic rule selected 1,000 calibration and 24 disjoint paired-test rows.
- The measured scores and observed cutoff count describe this frozen cohort.
- C4 natural-web text is not verified human text.

Prohibited:

- The observed fraction is the detector's production false-positive rate.
- Every selected row was human-written.
- A row above the cutoff proves AI origin, model source, or authorship.
- Stage 6 validates Stage 7 separation or attack robustness.

## Blog handoff

The final note must include the pre-run expectation, observed cohort without row removal, worked
spine calculation, maximum-z case, figure captions, source and artifact paths, allowed claims, and
the transition: "With the negative reference frozen, the next experiment can generate paired model
continuations without changing the prompts after seeing the baseline."
