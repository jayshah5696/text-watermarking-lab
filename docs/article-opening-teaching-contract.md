# Article opening teaching contract

## Learner

- Intended learner: a technically curious reader who has heard that text can be watermarked but has not studied language-model sampling or statistical tests.
- Safe assumptions: they understand percentages and averages.
- Must be taught here: where a text watermark can live, why media intuition does not transfer cleanly, how a repeated sampling preference becomes countable evidence, what z means, and where the repository code performs each operation.

## One learning question

- Question: How can plain text carry a hidden statistical mark when every visible word matters?
- Why it matters: every later result depends on seeing the mark as a repeated sampling preference rather than metadata or a magic character pattern.
- Plain answer: the generator slightly favors a keyed group of acceptable next tokens, and a checker later asks whether that group appears more often than ordinary chance would explain.

## Learning outcome

After the opening, the reader should be able to explain:

1. why text gives a watermark less room than an image or video;
2. how the 25 percent and 40 percent coins stand in for ordinary and nudged token choices;
3. how `32` heads becomes `z = 3.10`, why the cutoff is separate, and which Python functions compute the result.

## Spine example

- Example: 32 heads in 80 independent flips under a 25 percent baseline.
- Inputs: `T=80`, `G=32`, baseline chance `0.25`, cutoff `3`.
- Result: expected count `20`, excess `12`, usual movement `sqrt(15)=3.8730`, z `3.0984`, exact upper tail `0.2239%`.
- Failure: some baseline batches cross the line and some nudged batches stay below it.

## Controlled exploration

- Fixed first: baseline `0.25`, nudge `0.40`, cutoff `3`, and recorded Stage 1 evidence.
- Changed first: a fresh illustrative 40-flip draw.
- Changed second: length only.
- Changed third: cutoff only, after the score is understood.
- Reader sentence: the persistent excess grows with length faster than ordinary baseline movement, so the two sources become easier to separate, although they still overlap at finite lengths.

## Evidence ledger

| Claim or value | Type | Source | Check |
| --- | --- | --- | --- |
| Images and video have continuous values and redundant samples; text is discrete | external intuition | Theo transcript beats 05:33-20:12; project source notes | attributed to Theo; no security claim |
| Baseline 25 percent, nudge 40 percent, lengths, 10,000 replicates, cutoff 3 | measured configuration | `artifacts/lab-01/summary.json`; `configs/lab_01.toml` | final-article payload test |
| 32/80 gives z 3.0984 and upper tail 0.2239 percent | derived | `src/watermark_lab/stats.py` | direct unit-tested functions |
| Recorded detection and null rates at five lengths | measured | `artifacts/lab-01/summary.json` | complete row comparison |
| Simulation loop and scorer shown in article | implementation | `labs/01_biased_coin.py`; `src/watermark_lab/stats.py` | exact source excerpts reviewed against files |

## Boundaries

- Establishes: behavior of the independent biased-coin teaching model and the code path that produced the selected artifact.
- Does not establish: language-model error rates, real-text independence, production calibration, robustness, or Claude's implementation.
- Later material: keyed vocabulary, real logits, Transformers, Gemma, calibration, paired controls, editing, SynthID, and Claude remain later in the article.
- Authorization: no model, dataset, GPU, cloud, remote, publication, or new evidence generation.

## Output

- Canonical destination: `blog/how-text-watermarks-hide-in-plain-sight.html`.
- Preserve: warm dark technical page, visible grid, stable blue baseline and orange nudge, serif editorial headings, mono values, and one-object continuity from the Stage 1 walkthrough.
- QA: desktop 1440 by 1000, mobile 390 by 844, desktop light 1200 by 900, reduced motion, scripts off, all opening controls, and at least three isolated opening screenshots.
