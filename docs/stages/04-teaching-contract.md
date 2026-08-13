# Stage 4 teaching contract

## Learner

- Intended learner: a curious reader who receives only the HTML file. The page links to earlier
  lessons but must make sense without opening them.
- Safe prior knowledge: percentages, token IDs as numbered text pieces, and the idea that a model
  assigns a number to every possible next token.
- Knowledge taught here: why Stage 3 used a hand-written MLX loop, why Stage 4 checks that loop
  against Transformers, how each generation formula changes one recorded score list, how a copied
  continuation becomes detector evidence, and why the complete recipe must stay fixed.

## One learning question

- Question: Stage 3 already generated a watermark with MLX. Why check it against Transformers, and
  which exact details change?
- Project role: Stage 3 exposed the mechanism in code the learner could inspect. Stage 4 checks that
  explanation against one exact maintained library path before the project considers a larger model
  or cloud runtime.
- Plain answer: MLX made the generation loop visible and fast on the local Apple GPU. Transformers
  provides a maintained reference path. Both paths mark green token IDs, change model preference
  numbers, sample a token, and rebuild green hits from copied text. They use different models,
  tokenizers, green-set rules, prompt formatting, devices, and operation orders, so their outputs
  are not interchangeable.

## Learning outcome

After the page, the learner should be able to explain:

1. what Stage 3 was built to teach and why Stage 4 adds a reference implementation;
2. how temperature, top-k, top-p, the watermark addition, and softmax change one saved GPT-2 score
   list, including the exact formulas and operation-order difference;
3. how the checker rebuilds green hits from copied continuation IDs, how the key changes those hits,
   and why repeated equal token transitions need an explicit counting rule.

## Spine example

- Smallest example with the full mechanism: the continuity passage and the first two generated GPT-2
  pieces, ` was` with ID 373 and ` greeted` with ID 21272.
- Starting state: one saved list of 50,257 GPT-2 preference numbers after prompt token ` he`, ID 339;
  generation key 15485863; temperature 0.8; top-k 40; top-p 0.95; watermark addition 2.0; and
  sampling seed 568285428.
- Observable result: Transformers leaves 19 choices and gives ` was` an 8.642730 percent chance.
  Applying the Stage 3 operation order to the same GPT-2 list leaves 11 choices and gives ` was` an
  8.825517 percent chance. Only the Transformers order produced the saved continuation.
- Hand-worked reasoning: substitute ` was` into every formula. Divide its saved preference number
  by 0.8, keep or remove candidates under the two filters, add 2 if it is green and still available,
  then normalize the remaining numbers into chances with softmax.
- Failure or ambiguity: the recorded sampler chose ` was` even though ` saw` had the largest final
  chance among the visible witnesses. A higher chance does not force a choice. The 40-token
  continuity watermark row also falls below the configured detector cutoff. A generated watermark
  can produce insufficient evidence in a short sample.

## Controlled exploration

### First comparison: operation order

- Quantity held fixed: the saved GPT-2 preference list, recent token ID, key, temperature, top-k,
  top-p, added value, and displayed chance scale.
- Single quantity changed: the order of the same operations.
- What visibly changes: the survivor count, selected-token formula, and final chance.
- Sentence afterward: the same operation names do not guarantee the same distribution when their
  order changes.

### Second comparison: passage and condition

- Quantities held fixed: pinned GPT-2 revision, tokenizer, sampling settings, key recipe, token
  limit, and checker formula.
- Single quantity changed first: choose one of three fixed passages, then switch between its saved
  control and watermark continuation.
- What visibly changes: copied text, token pieces, green positions, G, z, and cutoff result.
- Sentence afterward: three examples show variation in this recorded run, not an accuracy estimate.

### Third comparison: bounded live key replay

- Quantities held fixed: one saved continuation, its copied token IDs, Transformers 5.14.1
  `lefthash` rule, context width one, 25 percent green fraction, and all-occurrence counting.
- Single quantity changed: select or enter one of the exact public teaching keys bundled with the
  page.
- What visibly changes: green marks at each eligible position, G, z, and cutoff result. T stays 39.
- Sentence afterward: the key is part of the detector recipe because it changes which token
  transitions count as green.

The browser does not regenerate GPT-2. The key explorer replays exact precomputed detector outcomes
for a bounded public teaching-key range and labels that boundary beside the input.

## Formula contract

Teach each formula only after showing its plain operation.

1. Temperature: `s_i^(temp) = s_i / 0.8`.
2. Top-k: keep the 40 largest finite values and replace the rest with negative infinity.
3. Top-p: convert current values to temporary chances, sort them, and keep the shortest leading
   group whose cumulative chance reaches at least 0.95.
4. Watermark: `s_i^(wm) = s_i + 2 * I[i is green]` for choices that remain available.
5. Final chance: `p_i = exp(s_i) / sum_j exp(s_j)` over choices that remain.
6. Detector baseline: `E[G] = 0.25T`.
7. Detector evidence: `z = (G - 0.25T) / sqrt(T * 0.25 * 0.75)`.

Explain that Stage 3 applied the watermark addition before temperature. For a green survivor, adding
2 before division by 0.8 becomes an addition of 2.5 on the divided score scale. Transformers adds 2
after its filters. The two paths also swap top-k and top-p, so the full difference cannot be assigned
to the addition alone.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| Stage 3 goal, MLX runtime, model, prompt framing, operation order, and measured first-token values | measured configuration | `docs/stages/03-manual-generation.md`; `artifacts/lab-03/trace.json`; `src/watermark_lab/manual_generation.py` | direct contract and artifact comparison |
| Transformers configuration fields and `lefthash` green-set rule | external | Transformers 5.14.1 source in the locked environment and official documentation | source inspection and fixed-vector tests |
| Transformers processor order | external and measured | locked `generation/utils.py`; `artifacts/lab-04/trace.json` | order assertion and `generate()` score equality |
| GPT-2 revision, license, and selected file size | external | Hugging Face model metadata | pinned metadata check |
| First-step formulas, survivor counts, candidate values, chances, and selected token | measured or derived | `artifacts/lab-04/trace.json` | `just verify-lab-04` plus displayed arithmetic checks |
| All six continuation texts, copied IDs, checker counts, and evidence scores | measured | `artifacts/lab-04/trace.json` | byte-for-byte local-cache regeneration |
| Bounded teaching-key replay memberships and counts | derived | copied IDs in `artifacts/lab-04/trace.json`; pinned Transformers detector | regenerate the bundled key table and compare fixed keys |
| Stage 1 z formula agrees with library counts | derived | `src/watermark_lab/stats.py`; `artifacts/lab-04/trace.json` | independent recomputation |
| Repeated-pair mismatch in Transformers 5.14.1 | measured compatibility check | `artifacts/lab-04/trace.json`; locked detector source | fixed alternating-token fixture and explicit value-based count |
| Three prompts do not measure accuracy, quality, or a useful cutoff | opinion and limitation | experiment scope | claim review |

## Boundaries

- This stage establishes one pinned local Transformers adapter and an inspectable comparison with
  the Stage 3 explanation.
- The page's live key replay changes detection only. It does not generate new text and does not show
  what GPT-2 would have sampled under the edited key.
- The Stage 3 and Stage 4 profiles are not equivalent. Model, tokenizer, selector, device, prompt
  formatting, and processor order all changed.
- Three passages do not establish language quality, detection accuracy, a false-alarm rate, a useful
  cutoff, cross-device portability, or production key security.
- Stage 5 model work, Modal, datasets, GPUs, cloud cost, deployment, and publishing remain untested
  and separately gated.
- A score above the configured cutoff means only "consistent with this configured watermark and
  key." It does not prove AI origin, authorship, or use of a private vendor system.

## Continuity rules

- Use the graph-paper visual system, serif headings, numbered sections, fixed-value strips, green
  hatching, orange selected-token marks, blue calculation notes, and rust boundary notes from the
  earlier lessons.
- Add direct links to Stage 1, Stage 2, and Stage 3. State the result of each stage in one sentence
  before Stage 4 begins.
- Keep the continuity passage visible from Stage 3 recap through both GPT-2 tokens and copied-text
  checking.
- Reuse stable visual objects for candidate tokens and copied continuation tokens. Do not redraw
  them as unrelated cards.
- Use one shared chance scale for the two operation orders. Keep raw preference numbers and final
  chances on separately labeled scales.
- Stop generation comparisons after the first sampled histories diverge.
- Use "model preference number" for generation and "watermark evidence score" for detection.
- State that green is an arbitrary key-selected label. It does not mean safe, correct, or higher
  quality.

## Interaction contract

1. Stage rail: select Stage 1, 2, or 3 to see its question, completed result, and link. Stage 4 stays
   visually connected to the rail.
2. MLX-to-Transformers bridge: reveal what Stage 3 exposed by hand, then overlay the matching
   Transformers components. The reader sees why the reference path exists before any formula.
3. Formula microscope: advance one operation at a time. Each step displays the plain instruction,
   symbolic formula, substituted ` was` calculation, persistent candidate rows, full survivor count,
   and one result sentence.
4. Operation-order comparison: predict same or different, then run both order tracks on the same
   saved GPT-2 values. Restore the reference track before revealing the recorded sampled token.
5. Recorded sample: explain that Transformers reset its random generator to seed 568285428 and
   sampled ` was`, then ` greeted`. The artifact records the seed, final chances, and chosen token.
   It does not store one separate random-number draw. Move the same token objects into the
   continuation and checker.
6. Detector construction: move only continuation tokens across a visible boundary. Build the first
   eligible previous-token/current-token check before expanding to all 39 checks. Reveal G and T
   before z and cutoff.
7. Recorded continuation explorer: choose among three passages and control or watermark output.
   Show the full saved text, token strip, same-key and comparison-key results, and cutoff sentence.
8. Live key replay: keep one saved continuation fixed. Change among the bundled exact public keys.
   Recompute visible green marks, G, expected G, z, and the cutoff statement. State that no generation
   occurs in the browser.
9. Repetition lesson: build five adjacent transition occurrences from `A B A B A B`. Group equal
   transitions visually, explain why repeated patterns may not be fresh evidence, then reveal the
   pinned library mismatch and explicit two-pattern count.
10. Evidence map: show verified, derived, and untested claims as a visual flow from source to claim.
    Keep hashes, versions, formulas, and full tables in an optional technical appendix.

Every action must state what stays fixed, what changes, what to watch, and a complete interpretation.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-4-lesson.html`.
- Views: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
- Context-free screenshots: Stage 3 to Stage 4 bridge, formula microscope, continuation and key
  explorer, and repeated-transition explanation.
- Test every control, keyboard focus, reduced motion, static fallback, console output, and horizontal
  overflow.
- Run learner copy through the Humanizer plain register and a final lint audit.
