# Stage 8 lesson review passes

Independent reviewer sessions were unavailable in the current harness. The implementation assistant
ran three separate read-only passes using the repository reviewer prompts. This is a validation
boundary, not a substitute for independent review.

## Pass 1: prerequisite and pedagogy order

### Main diagnosis

The main risk is jumping from an edit label to a lower z score. That skips the mechanism the learner
needs: visible characters change, the tokenizer emits a new ordered history, and the key rebuilds
membership from new adjacent IDs.

### Beat order

1. Restore the exact Stage 7 rank 1000 string and 80-token score.
2. Cross out one fixed deleted word before naming an attack.
3. Re-tokenize old and edited strings.
4. Stop matching objects at the first token mismatch.
5. Replay keyed checks and calculate edited z.
6. Add length and meaning gates.
7. Compare all attacks and all rows.
8. Return to generation and change delta alone.
9. Define NLL and repetition before the bias result.

The formula, cohort plot, and bias controls belong after one complete edit trace.

## Pass 2: novice language and claim boundary

### Harmful assumptions

- "Deletion 10%" does not tell a reader which words were removed.
- "Tokenization changed" needs an exact first mismatch.
- "Semantic similarity" can sound like proof of equal meaning.
- "NLL" can sound like a general quality score.
- "Watermark removed" can hide destroyed content or insufficient length.

### Plain replacements

- Use "first 80 copied token IDs" before "attack prefix."
- Use "ordinary quarter-green average" before the z formula.
- Define NLL as "how surprising Gemma finds the recorded continuation, averaged per predicted
  token. Lower is less surprising to this checkpoint."
- Call embedding cosine a "model-based wording similarity check."
- State "correct-key score fell" unless all declared removal gates pass.

Positive wording remains "consistent with this configured watermark and key." The page must state
that manual review was performed by the implementation assistant and was not independent.

## Pass 3: narrative and interaction

### Narrative spine

The page should behave like one inspection session. Start with the same recorded string from Stage 7.
Reveal deterministic deletions, let the learner inspect the first tokenizer mismatch, replay the
checker, and then widen to the cohort. The delta sweep is a second experiment and needs a clear
reset to generation-time inputs.

### Interaction sequence

1. Deletion autoplay with Pause, Replay, Previous, and Next.
2. Original/edited token-lane toggle fixed at the first mismatch.
3. Attack tabs in prescribed order with one result sentence after each action.
4. Row selector only after the attack sequence is understood.
5. Delta tabs that fade all fixed call fields and leave bias visible.
6. Raw eight-row lines before aggregate means.

### Controls to remove or hide

Do not expose free deletion percentages, arbitrary text entry, a key field, or an unconstrained delta
slider. They turn the lesson into a dashboard and can produce claims outside the artifact.

### Screenshot tests

- Edit trace must show the exact removed words, old/new token mismatch, and score calculation in one
  viewport.
- Attack cohort must show score change, length ratio, and preservation status as separate readings.
- Bias view must show fixed prompt/seed/sampler, changed delta, row lines, and the NLL proxy warning.
