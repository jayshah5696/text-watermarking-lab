# Stage 3 lesson storyboard

## Spine

Keep the first recorded prompt visible through the main path.

`Early one morning Jack went up the hill. At the top he`

The lesson follows the first recorded token with the score increase enabled through generation.
It then adds the second recorded token to complete the first eligible checker step. The same token
labels and IDs must persist through candidate rows, result cards, appended history, and copied-text
checking.

## Beat order

1. Recall the Stage 2 operation. The toy program started with chosen scores, added 2 to selected
   token IDs, and sampled one result.
2. Show the whole loop before opening it. The loop receives token IDs, gets model scores, applies
   the configured increase, filters scores, samples one token, appends it, and repeats.
3. State the Stage 3 question. The reader must locate the score increase inside that loop.
4. Keep the continuity passage fixed and reveal its recorded LFM2 token pieces and IDs. Show the
   fixed instruction and chat-template control tokens in a disclosure.
5. Define the model as code that receives the token history and returns one score for every
   possible next token. Show only the final-position scores.
6. Reveal which candidates are green and add 2 only to their scores.
7. Show temperature, top-p, and top-k in order. Each view keeps the same candidates aligned.
8. Show the locked MLX order. A green token can receive the increase and still be removed by a
   later filter.
9. Convert the final scores to probabilities. Use the recorded seeded sample and append the chosen
   token.
10. Show why the next model call receives a different history after the paired paths diverge.
11. Align the control continuation and the continuation with the score increase enabled for the
    same prompt and seed. State that a
    shared seed does not guarantee matching later draws once probabilities and histories differ.
12. Copy the continuation generated with the increase enabled and tokenize it again. Compare the copied IDs with
    the generated IDs.
13. Mark the first copied token as context only. Rebuild green membership for the second token,
    which is the first eligible checker position. Update Stage 1 `G`, `T`, and z.
14. Keep the text fixed and switch to the comparison key. Explain chance matches without treating either
    score as a decision.
15. Show the compact results for the other two fixed prompts.
16. End with the measured local boundary and the Stage 4 question about equivalence with the full
    library adapters.

## Guided interaction sequence

### Token pieces

Instruction: decide whether every written word will remain one token, then reveal the recorded
pieces. The prompt and tokenizer revision stay fixed. The visible token pieces and IDs change.
Watch how spaces, punctuation, and word boundaries appear. The model and watermark operate on
tokenizer IDs rather than the word labels shown in Stage 2.

### One-token loop

Instruction: advance one recorded operation. The prompt, model, settings, seed, and candidate rows
stay fixed. The visible processing stage changes. Watch the same candidate row across each stage.
The result sentence explains what that operation changed.

### Paired comparison

Instruction: compare the control and watermarked first step. The raw model scores, prompt, settings,
and random seed stay fixed. The watermark score increase changes. Watch the green survivor scores,
their final probabilities, and the sampled result.

### Copied-text checker

Instruction: check the next copied token. The copied text, tokenizer, and checker settings stay
fixed. The observed token and running count change. Watch `G`, `T`, and z update.

### Comparison-key check

Instruction: use the comparison key on the same copied text. The token IDs, green fraction, and formula
stay fixed. Green membership changes. Watch which observed tokens count as hits and read the new
score as a sentence.

## Screenshot tests

The token screenshot must identify the passage, fixed instruction, chat-template boundary, model
revision, token pieces, IDs, and the statement that Stage 2's word labels have become real tokenizer
output.

The loop screenshot must show the numbered order, one aligned candidate, the score before and after
the intervention, the final probability, the sampled token, and the filtered-token failure case.

The checker screenshot must show copied text, re-tokenized IDs, same-key and comparison-key `G`, `T`,
and z, plus the statement that Stage 3 has no calibrated cutoff.

## Appendix

Put the full six-sequence table, model cache command, source commit, configuration hash, package
versions, prompt IDs, seeds, complete candidate snapshots, and repository paths in disclosures.
The reader must not need the appendix to find the intervention or interpret the score.
