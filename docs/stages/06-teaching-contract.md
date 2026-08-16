# Stage 6 teaching contract

## Learner

- Intended learner: a programmer who followed the Stage 5 generated-token lesson but has not
  calibrated a statistical checker on outside text.
- Safe prior knowledge: a key rebuilds green membership; `G/T` becomes z; `z > 3` is the frozen
  lab decision.
- Taught here: why a formula is not a field measurement, how a negative reference set is frozen,
  what an empirical false alarm is, and what sample size cannot establish.

## One learning question

- Question: what scores does the Stage 5 checker assign to text that was not generated with its
  key?
- Project role: Stage 5 showed that the keyed generator can create a signal. Stage 6 checks how the
  same score behaves when the generator is absent.
- Plain answer: freeze outside text before looking at scores, run the unchanged checker on every
  selected continuation, keep every high and low result, and report the observed distribution with
  its sample-size limit.

## Learning outcome

After the page, the learner should be able to explain:

1. why `z > 3` and an empirical fraction answer different questions;
2. how one C4 row becomes a 50-token future prompt and a 400-token natural-web continuation;
3. why 1,000 natural-web rows can reveal ordinary variation but cannot certify a rare production
   false-alarm rate.

## Spine example

- Smallest full example: the first selected calibration row, carried from dataset metadata through
  filtering, token split, keyed token checks, `G/T`, z, and the frozen cutoff.
- Starting state: one pinned row and the unchanged Stage 5 tokenizer, public key, green fraction,
  and CUDA checker.
- Observable result: the recorded all-occurrence score and its place in the full 1,000-row cohort.
- Hand reasoning: ordinary count is `0.25 * T`; ordinary movement is
  `sqrt(T * 0.25 * 0.75)`; z is observed excess divided by that movement.
- Counterexample: the maximum-z natural-web row remains visible beside the spine row, whether or
  not it crosses three.

## Controlled exploration

- Held fixed first: the exact 1,000 recorded z scores and the frozen cutoff.
- Changed first: how many manifest rows are revealed, from one to 12 to 100 to 1,000.
- Watch: the visible distribution stabilizes and rare-looking rows can appear without changing
  source labels.
- Learner sentence: a score is one row's distance from the configured average; calibration asks how
  often such distances occur in a declared outside corpus.

The second guided comparison holds text and key fixed, then counts every adjacent pair versus each
distinct value pair once. It reconnects Stage 6 to the repetition issue exposed in Stage 4.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| dataset revision, fields, row count, and license | external | pinned C4 dataset card and repository | downloaded shard hash and source metadata |
| manifest sizes, filter counts, z values, and empirical fractions | measured | `artifacts/lab-06/calibration.json` | `just verify-lab-06` |
| z and exact binomial tail | derived | Stage 1 functions | independent reconstruction for every row |
| Stage 5 profile values | checked configuration | Stage 5 and Stage 6 TOML | strict config parser and tests |
| 1,000 cannot validate one-in-100,000 behavior | derived limitation | manifest size | resolution shown as counts, not extrapolation |

## Boundaries

- Establishes: the recorded score distribution for one pinned natural-web sample under one public
  key and profile.
- Does not establish: human authorship, general web behavior, deployed false-positive rate,
  production cutoff, quality, attack robustness, or Stage 7 separation.
- Positive wording: "consistent with this configured watermark and key."
- Stage 7 generation remains unimplemented.

## Output

- HTML: `.agent/diagrams/text-watermarking-stage-6-lesson.html`
- Story continuity: begin with Stage 5's `0/12` controls, keep the same `G/T -> z -> cutoff` objects,
  then replace hand-written prompts with a frozen natural-web cohort.
- QA: desktop 1440 by 1000, mobile 390 by 844, dark 1200 by 900, reduced motion, keyboard,
  scripts-off, and all controls.
