# Check the checker on natural-web text

## Question

What scores does the unchanged Stage 5 checker assign to text that was not generated with its key?

## Expected result before running

The 1,000 frozen C4 continuations should produce scores centered near zero under the configured
quarter-green baseline. Some rows could cross strict `z > 3`. No crossing was required, and no
cutoff, row, key, or filter would be changed after scoring.

The all-pair result was the primary Stage 5-compatible count. Counting each distinct value-pair once
was frozen as a repetition diagnostic before the run.

## Frozen source and profile

The manifest comes from `allenai/c4`, `realnewslike`, validation, at revision
`1588ec454efa1a09f29cd18ddd04fe05fc8653a2`. The compressed validation shard contains 13,863 rows
and has SHA-256 `42ac859dc1c4d48d165ec602909403e2066ce1d4854149ed70b9ec9cc96dc65f`.

Selection walked the shard in file order. Rows needed at least 500 Gemma tokens and had to pass the
fixed duplicate, list, code, and letter-fraction checks. The first 1,000 passing rows filled
calibration. The next 24 were frozen for later paired generation. Score did not influence either
split.

The checker retained the Stage 5 Gemma tokenizer revision, CUDA pseudorandom behavior, public key
`15485863`, green fraction `0.25`, `lefthash`, context width one, and strict `z > 3` cutoff. Stage 6
loaded no model weights and generated no text.

## Observed result

The selector scanned 2,479 source rows. It rejected 1,451 as shorter than 500 Gemma tokens and four
as obvious lists. The other fixed filters rejected zero rows before both splits filled.

Under all-pair counting, four of 1,000 calibration rows crossed strict `z > 3`. The median z was
`0.0289`, the 95th percentile was `1.8787`, and the 99th percentile was `2.4568`. The maximum was
`3.7286`.

Under distinct-pair counting, one of 1,000 rows crossed. Its median z was `-0.0594`, the 95th
percentile was `1.6136`, and the 99th percentile was `2.1360`.

These are empirical counts for one pinned natural-web cohort and key. They are not production
false-alarm rates.

## One complete example

The first accepted row was C4 dataset row 0, an eWeek page with SHA-256
`13b538ab00534c6039e05ce324e00a3163c44134ad9ac8515047e3d002209c68`. It contained 988 Gemma
tokens. Tokens 0 through 49 became the frozen future prompt. Tokens 50 through 449 became the
natural-web continuation scored now.

The 400-token continuation supplied 399 eligible adjacent-pair checks. Under a quarter-green
baseline, the ordinary average is `399 * 0.25 = 99.75` hits. The row had 81 hits. Its ordinary
movement is `sqrt(399 * 0.25 * 0.75) = 8.6494`. Therefore:

```text
z = (81 - 99.75) / 8.6494 = -2.1678
```

Counting each distinct value-pair once gave `77/337`, z `-0.9121`. The selected JSON stores all 400
token positions, IDs, decoded pieces, eligibility values, and keyed decisions for this row.

## The inconvenient result

Selection 558, dataset row 1,383, crossed the frozen all-pair cutoff with `132/399`, z `3.7286`.
It entered the manifest before scoring and remains in every figure.

The same token sequence produced `114/358`, z `2.9904`, when each repeated value-pair counted once.
Forty-one repeated observations disappeared, including 18 green hits. This does not make one rule
universally correct. It demonstrates that repetition policy changes the evidence and must belong to
the detector profile.

The all-pair crossing means only "consistent with this configured watermark and key." It does not
prove AI origin, model source, or authorship. Within the declared negative cohort, it is an
empirical false alarm.

## Figure handoff

Figure 1 caption: One pinned C4 document keeps its token order while the first 50 tokens become a
future shared prompt and the next 400 become the natural-web continuation scored in Stage 6.

Figure 1 alt text: A 500-token strip is divided into 50 prompt tokens and 400 scored continuation
tokens, with remaining document tokens left unused.

Figure 2 caption: Every dot is one frozen natural-web continuation checked with the public Stage 5
key. Four of 1,000 all-pair scores crossed the unchanged strict cutoff.

Figure 2 alt text: One thousand z scores cluster around zero. Four coral points lie above the
horizontal z equals three cutoff. The maximum is 3.7286.

Figure 3 caption: The maximum row changes from `132/399`, z `3.7286`, to `114/358`, z `2.9904`, when
repeated value-pairs stop adding observations.

Figure 3 alt text: Side-by-side score panels show the same natural-web token sequence above the
cutoff under all-pair counting and just below it under distinct-pair counting.

## Claim boundary

Allowed claims concern this pinned corpus, selector, tokenizer, public key, CUDA profile, and
recorded results. C4 is natural-web text, not verified human text. One thousand rows resolve
observed counts in steps of one per thousand. They cannot validate one-in-100,000 behavior.

The experiment does not establish a production cutoff, general web behavior, human authorship,
text quality, edit robustness, or paired model separation. The first approved Modal function
completed but lost its returned JSON after a missing local output directory. The user approved one
exact replacement invocation. The replacement used the same clean source commit and configuration,
loaded no model weights, and made zero generation calls.

## Next Lego block

With the negative reference frozen, the next experiment can generate paired model continuations
without changing the prompts after seeing the baseline. Stage 7 remains unimplemented and needs a
new approval.
