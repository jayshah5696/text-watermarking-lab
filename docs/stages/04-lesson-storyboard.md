# Stage 4 lesson storyboard

## One question

Stage 3 already generated a watermark with MLX. Why check it against Transformers, and which exact
details change?

Stage 3 used an explicit loop so the learner could inspect every step. Stage 4 keeps that explanation
but checks it against one exact maintained Transformers path. The causal parts match. The full
recipes and outputs do not.

## One recorded story

Keep this passage visible from the Stage 3 bridge through detection:

`Early one morning Jack went up the hill. At the top he`

Stage 3 continues it with LFM2 and selects `Jack` first. Stage 4 sends the passage directly to GPT-2
and selects ` was`, then ` greeted`. The page must explain the changed model, tokenizer, prompt
framing, selector, device, and operation order before showing those different outputs.

The first saved GPT-2 score list is the generation microscope. The first two GPT-2 pieces are the
detector microscope. After those are understood, the page expands to all six recorded continuations
and a bounded exact key replay.

## Visual system

- Reuse the warm graph-paper field, dark serif headings, small green section numbers, cream work
  surfaces, and flat colored explanation bands from Stages 1 to 3.
- Use green hatching only for membership under the current key. Use orange for the recorded sampled
  token, blue for fixed inputs and formulas, and rust for a failed assumption or scope boundary.
- Draw the generation process as a continuous horizontal score track on desktop and a vertical track
  on mobile. Candidate tokens never change row identity.
- Draw detector checks as visible links between adjacent token pieces. The link carries the previous
  ID into the green-set rule and points at the current ID.
- Keep formulas large enough to read. Substitute the recorded numbers directly under each symbol.
- Make each main screenshot understandable without reading the previous section.

## Beat order

1. Show a four-stage rail. Stage 1 supplies the count and z score. Stage 2 supplies the keyed green
   set. Stage 3 puts the mechanism inside an explicit MLX generation loop. Stage 4 asks whether a
   maintained Transformers path performs the same kinds of operation.
2. Keep the Stage 3 passage on screen. Show the recorded Stage 3 first token `Jack`, the manual order,
   and the goal of using MLX. MLX gave direct control of the loop on the local Apple GPU. It made
   scores, filters, sampling, cache, and checking inspectable.
3. State why Stage 4 exists. A teaching implementation can be internally consistent and still differ
   from the library a later experiment will use. The reference check tests contracts, order, copied
   IDs, and counts before scale increases.
4. Overlay the two paths. Keep shared ideas aligned and mark declared changes separately. Do not
   compare output quality or imply equivalent token IDs.
5. Introduce the saved GPT-2 score list after prompt token ` he`, ID 339. Explain that GPT-2 supplies
   50,257 model preference numbers. Show five fixed witness rows and label them as a sample from the
   complete list.
6. Show temperature as arithmetic. For ` was`, substitute
   `-125.5542 / 0.8 = -156.9427`. Explain that only differences among the numbers affect the final
   chances.
7. Show top-k as ranking. Keep the 40 largest values. Fade removed candidate marks but leave their
   rows in place.
8. Show top-p as cumulative chance. Animate a running total over the current 40 choices and stop at
   the first group reaching 95 percent. The reference path leaves 19 choices.
9. Show the green rule after the filters. The key and previous token mark 12,564 of 50,257 vocabulary
   IDs green, but only green choices still present can receive 2. For ` was`, show
   `-156.9427 + 2 = -154.9427`.
10. Show softmax. Use the final survivors to turn preference numbers into chances. Substitute the
    selected-token numerator and recorded denominator result, then show 8.642730 percent.
11. Ask whether the same score list will produce the same chance under the Stage 3 order. Record the
    prediction before revealing the alternate calculation.
12. Run the earlier order on the same GPT-2 list. For ` was`, show
    `(-125.5542 + 2) / 0.8 = -154.4427`. Then apply top-p before top-k. Eleven choices remain and the
    chance is 8.825517 percent. State that only order changed in this calculation.
13. Restore the Transformers order. State that the program reset its random generator to seed
    568285428, then reveal the recorded sampled token. Mark ` was` orange and append the same object
    to the passage. Point out that ` saw` had a larger chance among the visible witnesses, so the
    highest chance did not force the recorded choice. Reveal ` greeted` next. The artifact records
    the seed and chosen token, not one separate random-number draw.
14. Move only the saved continuation across a clear checker boundary. Leave the prompt and padding
    outside. Decode and re-tokenize the continuation, then show that all copied IDs match.
15. Build the first detector check from two tokens. ` was`, ID 373, supplies context. The exact
    generation key and `lefthash` rule choose the green set for that context. ` greeted`, ID 21272,
    is the first current token the checker can score.
16. Expand the same links across all 40 copied pieces. Count 17 green links among 39. Show the ordinary
    average `0.25 * 39 = 9.75` before introducing z.
17. Substitute the complete detector formula:
    `(17 - 9.75) / sqrt(39 * 0.25 * 0.75) = 2.6811`. Read it as a sentence. Then show the strict
    cutoff `z > 3.0` and the insufficient-evidence result.
18. Open the recorded continuation explorer. Choose continuity, notebook, or library. For each,
    switch between the saved control and watermark output. Keep the prompt, full continuation,
    token count, copied-ID status, green strip, G, z, comparison key, and cutoff sentence together.
19. Open the live key replay after the recorded examples are clear. Fix one saved continuation.
    Change among the exact public teaching keys bundled with the page. Repaint all 39 eligible links
    and recompute G, expected G, z, and cutoff. State the finite key range and that the browser is
    replaying detection, not generation.
20. Introduce repetition using plain language. One-token context means each check is an adjacent
    transition. Build `A B A B A B` and label the five occurrences `AB, BA, AB, BA, AB`. Ask how many
    different transition patterns exist. Group equal links to reveal two patterns.
21. Explain why the count matters. Counting every occurrence treats three copies of `AB` as three
    pieces of evidence. Counting each distinct pattern once treats them as one pattern. Then reveal
    the pinned Transformers 5.14.1 mismatch: both library settings returned 3/5, while the explicit
    value-based count returned 1/2. This is a compatibility finding, not model output.
22. End with an evidence map. Connect selected claims to their source artifact or implementation.
    Separate measured local behavior, derived browser replay, external library facts, and untested
    claims. Keep raw hashes and full result tables in disclosures.

## Interaction sequence

### Stage rail

- Instruction: select an earlier stage to see the question it answered.
- Fixed: project goal and continuity passage.
- Changed: the visible stage summary.
- Watch: each stage adds one missing mechanism.
- Result: Stage 4 checks the Stage 3 explanation rather than replacing its learning value.

### Formula microscope

- Instruction: advance one operation and read the numeric substitution.
- Fixed: saved GPT-2 list, previous token, key, settings, candidate rows, and scale.
- Changed: one operation at a time.
- Watch: the selected token's number, availability, survivor count, and chance.
- Result: each formal term names a visible operation the learner has already performed.

### Operation-order comparison

- Instruction: predict same or different, then apply the earlier order to the same saved values.
- Fixed: all numbers and settings.
- Changed: operation order only.
- Watch: 19 choices versus 11, and 8.642730 percent versus 8.825517 percent.
- Result: identical operation names and settings do not guarantee identical final chances.

### Detector construction

- Instruction: move only continuation pieces into the checker and build the first adjacent check.
- Fixed: saved text, GPT-2 tokenizer, generation key, context width one, and all-occurrence rule.
- Changed: readable text becomes token IDs and links become counts.
- Watch: the prompt remains outside, token 1 is context, and token 2 is the first eligible decision.
- Result: checking reconstructs evidence from copied continuation IDs, not hidden generation state.

### Recorded continuation explorer

- Instruction: choose one passage, then compare its saved control and watermark outputs.
- Fixed: pinned runtime and detector recipe.
- Changed: recorded passage and condition.
- Watch: text, green positions, G, z, and cutoff result vary together.
- Result: the three fixed examples show both strong and weak evidence, not an accuracy rate.

### Live key replay

- Instruction: keep one saved continuation fixed and select a bundled public key.
- Fixed: copied IDs, tokenizer, green fraction, selector, context width, counting rule, and formula.
- Changed: key only.
- Watch: T remains 39 while green positions, G, z, and the cutoff result change.
- Result: the detector key is part of the complete recipe. The browser does not regenerate text.

### Repeated-transition lesson

- Instruction: count five transition occurrences, then group equal transition values.
- Fixed: six token pieces, order, key, and checker formula.
- Changed: whether equal transitions count again.
- Watch: five occurrence markers collapse to two pattern markers.
- Result: an option name is not evidence that a library version performs the intended value-based
  grouping. The explicit check found a mismatch.

## Main path and appendix

Keep on the main path:

- Stage 1 to 4 continuity and Stage 3's MLX goal;
- plain operation, formula, numeric substitution, and visible result for every generation step;
- the two processor orders and their measured difference;
- the first two GPT-2 tokens and complete detector construction;
- all six recorded continuations through an explorer;
- bounded live key replay;
- repeated-transition explanation and compatibility mismatch;
- measured conclusion and limits.

Move to disclosures:

- package versions, model revision, file size, source commit, config hash, and platform;
- full prompt token pieces and full copied ID arrays;
- p-values and implementation class names;
- full six-row table for copying;
- official source links and reproduction commands.

## Screenshot tests

1. Bridge screenshot: a newcomer can say why Stage 3 used MLX, why Stage 4 adds Transformers, what
   stayed conceptually the same, and what profile parts changed.
2. Formula screenshot: a newcomer can follow ` was` through one visible operation, read the formula
   substitution, identify the complete-list survivor count, and distinguish a preference number from
   a final chance.
3. Detector screenshot: a newcomer can see the prompt outside, token 1 as context, token 2 as the
   first scored token, and the path from 17/39 to z 2.6811 to the below-cutoff sentence.
4. Key explorer screenshot: a newcomer can identify the fixed copied text, selected public key,
   changed green positions, stable T, recomputed z, finite key range, and no-generation boundary.
5. Repetition screenshot: a newcomer can count five transition occurrences, identify two distinct
   transition values, and explain the recorded 3/5 versus explicit 1/2 mismatch.
