# Stage 4 teaching contract

## Learner

- Intended learner: a curious reader who receives only the HTML file.
- Safe prior knowledge: percentages, token IDs as numbered text pieces, and the idea that higher
  model preference numbers can change which token a program chooses.
- Knowledge taught here: how a small adapter passes settings into a library, why operation order
  matters, how copied continuation text is checked, how repeated pairs are counted, and why one
  complete recipe must stay fixed.

## One learning question

- Question: When Transformers replaces our hand-written loop, which steps stay the same, and which
  exact details change?
- Project role: it checks the hand-written explanation against one exact Transformers 5.14.1 path
  before the project scales to a larger model or cloud runtime.
- Plain answer expected before the run: Transformers still marks green token IDs, changes model
  preference numbers, chooses a token from the final chances, and rebuilds green hits from copied
  text. Its operation order and complete recipe differ from Stage 3, so the two implementations are
  related but not interchangeable.

## Learning outcome

After the page, the learner should be able to explain:

1. which values stay fixed while the operation order changes;
2. why a shared green fraction, added value, and key do not make two implementations equivalent;
3. why the checker must receive copied continuation tokens, the exact recipe, and an explicit rule
   for repeated previous-token and current-token pairs.

## Spine example

- Smallest example with the full mechanism: the first two generated token pieces from the
  continuity passage under the pinned GPT-2 path. The first token shows the operation order and
  becomes checker context. The second token is the first eligible green-or-red decision.
- Starting state: one complete list of GPT-2 model preference numbers, the final prompt token, the
  fixed key, temperature, top-k, top-p, and one repeatable random starting number.
- Observable result: the selected evidence will record the same model preference list processed in
  Transformers order and Stage 3 order, then carry the two selected reference tokens into the saved
  continuation and the first checker decision.
- Hand-worked reasoning: show how many token choices remain and one candidate chance first. Name the
  formal operations only after the learner sees what each one does.
- Failure or ambiguity: identical visible settings do not imply identical token chances when the
  model, tokenizer, green-set rule, device, prompt formatting, or order differs. Counting every
  occurrence can treat one repeated pair pattern as fresh evidence several times.

## Controlled exploration

- Quantity held fixed: the full GPT-2 model preference list, recent token ID, key, temperature,
  top-k, top-p, and added value.
- Single quantity changed first: the order in which those operations run.
- What should visibly change: the available token choices or final chance for the recorded selected
  token, using evidence generated after the fixed example is locked.
- Sentence the learner should be able to say afterward: both implementations perform the same four
  kinds of work, but exact results depend on the library's operation order and complete recipe.

The second guided comparison keeps copied IDs and the counting rule fixed. It changes only the key.
The final guided comparison uses a separate six-token constructed sequence and changes only whether
the same previous-token and current-token pair is counted again.

## Evidence ledger before the run

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| Transformers configuration fields | external | official Transformers 5.14.1 source and docs | compare source, runtime object, and artifact |
| Transformers operation order | external | `transformers/generation/utils.py` in the locked environment | order assertion and first-step calculation |
| GPT-2 revision, license, and selected file size | external | Hugging Face model metadata | pinned metadata check before download |
| Stage 3 operation order and fixed settings | measured configuration | `docs/stages/03-manual-generation.md`; `configs/lab_03.toml` | direct contract comparison |
| First-step values, choices left, token chance, and selected token | measured or derived | future `artifacts/lab-04/trace.json` | `just verify-lab-04` |
| Checker counts and evidence scores | measured | future `artifacts/lab-04/trace.json` | local-cache regeneration |
| Stage 1 z formula agrees with library counts | derived | `src/watermark_lab/stats.py`; future trace | independent recomputation |
| Three prompts do not measure accuracy, quality, or a useful cutoff | limitation | experiment size and Stage 4 contract | scope review |

Measured page copy must remain pending until the selected artifact exists.

## Boundaries

- This stage establishes one pinned local Transformers adapter and an inspectable comparison with
  the Stage 3 four-step explanation.
- It does not establish equivalence between the MLX and Transformers recipes, language quality,
  detection accuracy, a useful cutoff, cross-device portability, or production key security.
- Stage 5 model work, Modal, datasets, GPUs, cloud cost, deployment, and publishing remain untested
  and separately gated.
- A score above the configured cutoff means only "consistent with this configured watermark and
  key." It does not prove AI origin, authorship, or use of a private vendor system.

## Continuity rules

- Keep the continuity passage visible from model input through the first two generated token pieces
  and copied-text checking.
- Reuse stable visual objects for the same token candidates. Do not redraw them as unrelated cards.
- Use one shared chance scale for the two order views. Do not put model preference numbers and final
  chances on an unlabeled shared axis because they use different units.
- Stop probability comparisons when token histories diverge.
- Keep green hatching for IDs selected by the key, orange for the sampled token, blue for fixed
  values, and rust for limitations.
- Define each operation in plain words before using `WatermarkingConfig`, `lefthash`, z-score, or
  repeated n-gram. Use "model preference number" for generation and "watermark evidence score" for
  detection so the two meanings of score cannot blur together.
- State that green is an arbitrary key-selected label. It does not mean safe, correct, or higher
  quality.

## Interaction contract

1. The opening keeps the passage visible and shows the few changes needed for understanding without
   a control.
2. `Show the library steps one at a time` reveals temperature, keeping the highest 40 choices,
   keeping the smallest high-chance group that reaches 95 percent, and adding 2 to surviving green
   choices. The same candidate rows remain in place.
3. `Apply the same steps in the earlier order` resets the same saved GPT-2 preference numbers and
   changes only operation order. It then restores the Transformers state.
4. `Reveal the recorded token choice` marks the first saved GPT-2 token and appends the same visual
   object to the passage. The page then reveals token 2.
5. `Check only the generated continuation` leaves the prompt outside and reuses both generated token
   pieces. Token 1 is context only. Token 2 is the first eligible decision.
6. `Check the same text with a different key` keeps the original copied IDs and all-pairs counting
   rule fixed and changes only the published key.
7. `Count each distinct pair once` moves to the separate six-token constructed sequence and changes
   only the repeated-pair counting rule.

Each action must state what stays fixed, what changes, what to watch, and a full-sentence result.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-4-lesson.html`.
- Views: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
- Context-free screenshots: the two operation orders on one GPT-2 preference list, copied-text
  checker input with prompt exclusion and the first eligible pair, and repeated-pair policy
  comparison.
- Test every control, keyboard focus, reduced motion, script-off fallback, console output, and
  horizontal overflow.
- Run all learner copy through the Humanizer plain register and final lint audit.
