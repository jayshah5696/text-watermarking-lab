# Stage 5 teaching contract

## Learner

- Intended learner: a curious programmer who opens only the HTML file.
- Safe prior knowledge: a token is a numbered text piece; the model produces next-token preference
  numbers; Stage 4's checker turns copied text into a green count and z score.
- Knowledge taught here: why a smoke test comes before a large experiment, what moves into GPU
  memory, what elapsed time and throughput mean, where watermark processor cost appears, how a
  measured rate becomes a bounded cost projection, and why a projection ends at a human gate.

## One learning question

- Question: what does the Stage 4 reference watermark cost when the same recipe runs on Gemma 4
  E2B on one L4?
- Project role: this is the last infrastructure check before any dataset manifest or 24-row run.
- Plain answer before measurement: keep one model, GPU, prompt, seed, sampler, and checker fixed;
  compare control and watermarked generation; measure time and memory; use the slower observed rate
  to size the next run; then stop.

## Learning outcome

After the page, the learner should be able to explain:

1. which Stage 4 settings stay fixed and which Stage 5 profile fields change;
2. the difference among model download, model load, generation time, processor time, throughput,
   GPU memory, and a GPU-only cost projection;
3. why six saved generations can validate a runtime path but cannot measure detector accuracy,
   prose quality, or a total cloud bill.

## Spine example

- Smallest example with the full mechanism: the fixed continuity passage under paired control and
  reference-watermarked Gemma generation on the same L4.
- Starting state: one pinned Gemma revision in BF16, one rendered prompt, one derived seed, one
  sampler profile, one checker profile, and a 200-token cap.
- Observable result: fill only from `artifacts/lab-05/trace.json` after the approved run: generated
  counts, elapsed seconds, tokens per second, peak reserved bytes, watermark processor time, copied
  `G/T`, and z for both branches.
- Hand-worked reasoning: convert raw nanoseconds to seconds; divide generated tokens by generation
  seconds; compute memory headroom; divide 9,600 and 19,200 tokens by the slower measured rate;
  multiply projected seconds by USD 0.000222 per L4 second.
- Failure or ambiguity: a weak score can coexist with a correct runtime path; the watermark can be
  too slow or memory-hungry; an output can end early; GPU-only projected generation charge omits
  other bill components.

## Controlled exploration

### First comparison: runtime bridge

- Held fixed: passage identity, green fraction, bias, keys, sampling settings, context width,
  checker statistic, and paired design.
- Changed: model, tokenizer, vocabulary, device, precision, prompt rendering, and token cap move as
  one declared runtime profile from Stage 4 to Stage 5.
- Watch: which objects keep their meaning and which identifiers cannot transfer.
- Sentence afterward: the recipe continues, but the token IDs and device-specific green sets do
  not.

### Second comparison: watermark off versus on

- Held fixed: exact model, L4, BF16, rendered prompt, seed, temperature, top-k, top-p, and maximum
  length.
- Changed: presence of the maintained watermark processor.
- Watch: generated text, elapsed time, processor calls, peak reserved memory, green count, and z.
- Sentence afterward: one paired smoke measures the local cost and evidence of the intervention; it
  does not estimate an average effect.

### Third comparison: 200 versus 400-token projection

- Held fixed: slower measured throughput and recorded L4 per-second price.
- Changed: projected generated-token total, from 9,600 to 19,200.
- Watch: projected seconds and GPU-only charge double under a linear assumption while fixed load and
  other costs remain excluded.
- Sentence afterward: a projection is arithmetic from one smoke rate, not a measured bill or a
  promise of linear scaling.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| Stage 4 settings, passage, and checker boundary | measured configuration | `configs/lab_04.toml`; `artifacts/lab-04/trace.json` | `just verify-lab-04` and direct comparison |
| Gemma model identity, revision, architecture, vocabulary, and license | external configuration | pinned Hugging Face model card and `configs/lab_05.toml` | exact metadata and file checks in remote result |
| Modal L4, CPU, memory, and Volume price rates | external | `https://modal.com/pricing`, retrieved 2026-08-15 | exact values locked in config and cited in appendix |
| Model download/load, six generations, processor time, memory, and detector evidence | measured | `artifacts/lab-05/trace.json` | local schema/arithmetic verifier and remote invariants |
| Tokens per second, memory headroom, and 200/400 projections | derived | measured Stage 5 fields plus locked formulas | independent local recomputation |
| Six generations do not measure accuracy, quality, or total cost | limitation | Stage 5 scope | claim review |

## Boundaries

- This stage establishes one pinned Gemma 4 E2B BF16 smoke path on one Modal L4 and records its
  measured runtime, memory, copied-text evidence, and bounded projections.
- It does not establish detector accuracy, a false-alarm rate, language quality, robustness,
  model-size generality, CUDA portability, a total Modal invoice, or a useful production cutoff.
- It does not access C4 or any dataset. Stage 6 remains unimplemented.
- It does not run E4B, another GPU, the 24-row experiment, attacks, deployment, or publishing.
- A positive checker result means only “consistent with this configured watermark and key.”

## Continuity rules

- Link and summarize Stages 1 through 4 before Stage 5 begins.
- Keep the continuity passage visible from the Stage 4 bridge through the paired Gemma result and
  copied-text checker.
- Reuse prompt, watermark processor, selected-token stream, checker links, `G/T`, and z as stable
  visual objects.
- State the changed runtime profile before showing a new model output.
- Stop matched token comparison when the two sampled histories differ.
- Keep units attached to every value: seconds, tokens/second, bytes or GiB, and USD per second.
- Use green only for key-selected membership, orange for saved sampled text, blue for measured
  infrastructure, yellow for derived projections, and coral/rust for boundaries or failed gates.
- Use plain labels before “BF16,” “throughput,” “peak reserved memory,” and “projection.”

## Interaction contract

1. Stage rail: reveal the single question and completed result of each prior stage.
2. Recipe handoff: sort profile fields into “kept” and “changed,” then map each changed field to why
   token equality is not expected.
3. Load sequence: advance through container start, pinned files, GPU residency, and ready state.
   Use only measured intervals; mark unavailable platform phases explicitly.
4. Paired continuity run: predict whether watermarking changes time, memory, and checker evidence;
   reveal the saved control and watermark branches from one shared start.
5. Metric microscope: select one metric at a time. Show its raw inputs, arithmetic, unit, and full
   interpretation sentence.
6. Copied-text replay: move only each saved continuation into the same checker recipe. Reveal `G`
   and `T` before z and the cutoff statement.
7. Projection ladder: use the measured slower rate, first for 9,600 tokens and then 19,200. Keep
   price and exclusions fixed. Show the linear assumption beside the result.
8. Human gate: walk through memory, speed, runtime, smoke-rubric, and budget checks. End at review;
   never imply Stage 6 ran.
9. Evidence map and optional technical appendix: source every value and keep hashes, versions, raw
   nanoseconds, raw bytes, full tables, and commands out of the novice main path.

Every action states what stays fixed, what changes, what to watch, and what the observed result
means.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-5-lesson.html`.
- Views: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark, while preserving the earlier
  lessons' visual continuity. If the final lesson follows the newly required black technical system,
  provide an explicit light test surface only for QA and retain semantic colors.
- Context-free screenshots: Stage 4-to-5 recipe bridge, paired continuity timing/memory/checker view,
  and projection plus human gate.
- Test all controls, keyboard focus, reduced motion, scripts-off fallback, console output, and
  horizontal overflow.
- Run learner copy through the Humanizer plain register and final lint audit.
