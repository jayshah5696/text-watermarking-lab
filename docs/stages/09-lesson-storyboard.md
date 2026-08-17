# Stage 9 final lesson storyboard

## One question

What did this small open-model watermark experiment establish, and what remains unknown?

## Continuity rule

Open on the exact Stage 8 rank `1000` copied text and its three recorded states: unedited, deterministic 10 percent deletion, and paraphrase. Preserve the rank, character string, token order, generation key, `G/T`, z object, and strict cutoff. The article then rewinds to explain how those objects were created.

Use the same colors as Stages 7 and 8. Blue is copied source text. Green is correct-key membership and evidence. Cyan is the paired model control. Violet is the natural-web control. Yellow is the key and fixed cutoff. Coral marks edits, crossings that need caution, or failed claim gates.

## Beat order

### 1. Reopen the recorded edit

Show rank 1000 at 80 copied tokens:

- unedited `28/79`, z `2.1436`;
- deterministic deletion `25/79`, z `1.3641`;
- paraphrase `26/79`, z `1.6239`.

State that Stage 9 generated no new model text and selected no new row.

Why now: the learner starts with a concrete puzzle instead of a field taxonomy.

### 2. Define the narrow object

Explain that a generation watermark changes token sampling while the model writes. The checker later asks whether copied text is unusually compatible with one key and profile.

Why now: this prevents the learner from confusing a keyed watermark with generic AI detection.

### 3. Rewind to one token choice

Carry Stage 3's first continuity step into a compact candidate table. Both paths start from the same model scores and seed. The score-increase path changes green candidates before filtering and sampling. The saved draw selects `Jack` in both paths even though its chance changes from `11.6422%` to `18.5816%`.

Interaction: toggle the score increase. State every fixed field and the one changed field.

Why now: one matching sampled token disproves the intuition that the watermark forces words.

### 4. Name the generation loop

Place the candidate step in the full order: tokenize, model scores, keyed membership, score change, sampling transforms, draw, append, repeat. Note that Stage 4 pinned the maintained Transformers order rather than assuming it matched the teaching loop.

Why now: the reader has seen the operation before receiving the architecture.

### 5. Build the checker by hand

Return to rank 1000's unedited 80-token prefix. Reveal token decisions in order. Calculate:

```text
ordinary hits = 79 x 0.25 = 19.75
ordinary movement = sqrt(79 x 0.25 x 0.75) = 3.8487
z = (28 - 19.75) / 3.8487 = 2.1436
```

Keep score and cutoff separate. This row remains below strict `z > 3`.

Why now: notation follows the visible count.

### 6. Show why length helps without promising it

Use Stage 1's independent-coin curve to establish the clean statistical intuition. Then show Stage 7's shrinking complete cohorts: 24 at 40 and 80, 21 at 160, 17 at 200, zero at 400. Explain that natural end tokens and changing row sets stop this experiment from isolating a causal length effect.

Why now: the learner can distinguish the mathematical tendency from the recorded cohort.

### 7. Introduce the four controls

For one recorded prefix, change only the checked text or key role:

- marked text, generation key;
- paired model control, generation key;
- natural-web continuation, generation key;
- marked text, comparison key.

Use Stage 7 rank 1000 at 160 tokens for the worked four-way comparison. Then show rank 1001's equal early path.

Why now: a score alone has no useful reference.

### 8. Reveal every paired row before the mean

At 80 copied tokens, display all 24 document-level differences for one selected contrast. Add the mean and paired bootstrap interval only after the dots. Let the learner switch among all three controls while the row set stays fixed.

Why now: overlap and inconvenient rows must remain visible next to the average.

### 9. Put natural-web crossings beside the cutoff

Show Stage 6's `4/1000` all-pair crossings and the maximum row's policy-sensitive change from `132/399`, z `3.7286`, to `114/358`, z `2.9904`, under distinct-pair counting.

Why now: the cutoff cannot become a truth label after a positive paired result.

### 10. Return to the Stage 8 edit

Replay the three rank 1000 states. Explain that the string changes first, tokenization changes second, and keyed checks rebuild third. Keep detector change, length, and meaning screens separate.

Why now: the opening puzzle now has a causal explanation.

### 11. Show all edits and the bias trade-off

Attack tabs show all 12 row changes for one named edit. Delta tabs show all eight z paths and separate NLL and repetition proxies. Preserve non-monotonic rows and the two uncertain paraphrase reviews.

Why now: the reader can inspect the result without treating averages or proxies as verdicts.

### 12. Map the implemented analogue to the wider field

Define KGW-style green lists as the implemented public analogue. Contrast SynthID-Text tournament sampling as literature context only. Attribute Anthropic's statements and list what its public support page does not disclose.

Why now: the learner understands one real mechanism before seeing the map.

### 13. State the answer in two columns

The experiment established a reproducible keyed sampling and checking path plus measured separation on one frozen cohort. It did not establish production accuracy, authorship, generic AI origin, adaptive robustness, or Claude equivalence.

End with reproduction commands and the remaining publication gate.

## Interactions

1. Bias toggle for Stage 3's saved first-token choice.
2. Token replay for rank 1000's 80-token score.
3. Score-family selector for one four-control comparison.
4. Prefix selector for complete-cohort counts.
5. Paired-contrast selector for all 24 row differences.
6. Edit selector for all 12 paired score changes.
7. Delta selector for all eight row paths and proxy summaries.

No free key field, arbitrary text box, attack slider, or unconstrained generation control belongs in the final page.

## Screenshot tests

1. One-token mechanism: identify fixed inputs, changed score increase, changed chance, and the saved sampled token.
2. Checker and controls: calculate rank 1000's score and state why cutoff and comparison controls are separate.
3. Results and limits: identify all 24 row differences, the mean interval, the natural-web crossings, and the narrow positive wording.
4. Editing and trade-off: read score change, length or preservation status, and NLL as separate measurements.
