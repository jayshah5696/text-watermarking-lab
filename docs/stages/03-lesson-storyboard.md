# Stage 3 lesson storyboard

## One question

What changes when this lab adds 2 to a key chosen set of token scores?

The saved model stays fixed. The temporary scores and sampling chances change. That change can alter
the chosen text. Stage 3 did not measure whether the writing became better or worse.

## One recorded story

Use the continuity passage for the whole page:

`Early one morning Jack went up the hill. At the top he`

Both recorded runs start with the same complete model input, raw scores, key, sampling settings, and
random seed. One run leaves every raw score alone. The other adds 2 to the green candidates.

## Beat order

1. Keep the passage visible. State the one change and the fixed parts in plain words.
2. Show the first 20 sampled token pieces from the recorded score increase run. Keep each token in
   one fixed column through the rest of the lesson.
3. Reveal which sampled tokens were green at their positions. Then raise those bars from 0 to 2.
   Keep the bar unit fixed as the score added by this lab.
4. Open a separate first-position detail. Show the aligned off and on chances on one shared 0% to
   35% scale. Mark the recorded draw. Both runs choose `Jack`.
5. Append `Jack` to the passage. Show position 2 while both histories are still equal. The chance for
   `climbed` rises from `15.1809%` to `28.5079%`. The control chooses `paused`; the score increase run
   chooses `climbed`.
6. Keep both branches on screen. The main 20-token trace continues along the score increase run.
   State the comparison limit beside it. From position 3 onward, the histories differ. The later
   tokens in the two branches are not a controlled probability comparison at a shared history.
7. Continue the score increase count from `11/19` to `21/39`. Show the `9.75` baseline average and
   z only after the counts are visible. Put the complete control result in the later summary.
8. Ask whether the changed text proves a quality loss. Answer with the evidence boundary. Stage 3
   measured probability changes and selected text. It collected no blind ratings or task scores.
9. Explain why quality can change. The green rule does not read meaning. A strong score increase can
   lower the share of a good candidate outside the green group.
10. Compare Stage 3 with SynthID as a different method. State the averaging condition and the
    reported Gemini quality test. Do not transfer that result to this lab.
11. End with four short evidence labels: measured here, calculated here, found in papers, and not
    tested here.

## Main interaction

### First two positions

- Instruction: press one button to apply the recorded score increase, then press again to run the
  saved draw.
- Fixed: model, complete input, first position history, raw scores, key, random seed, temperature,
  top-p, and top-k.
- Changed: green candidates receive 2 before the sampler makes the final chances.
- Watch: the same probability bars move while the token rows stay fixed.
- Result: `Jack` moves from `11.6422%` to `18.5816%`, but both runs still choose `Jack`.

### First 20 generated tokens

- Instruction: reveal green membership, add 2, then reuse the same token columns for checking.
- Fixed: the saved score increase record, token order, key, and 20 positions.
- Changed: green marks appear, twelve bars rise from 0 to 2, and the checker view excludes Jack from
  its count.
- Watch: the same token objects carry the pattern from generation into checking.
- Result: among positions 2 to 20, the score increase run has `11/19` green choices.

## Evidence rules

- The first position probability chart uses the five named candidates saved in
  `artifacts/lab-03/trace.json` plus one exact aggregate for the other 35 survivors.
- The 20 position chart uses only each recorded selected token, its configured score increase, and
  its saved green membership.
- The page must not turn the later bars into off and on probability comparisons after the histories
  split.
- The quality section says that Stage 3 did not measure quality.
- The SynthID section links the Nature paper and calls it external evidence from another method.

## Screenshot tests

1. The probability screenshot keeps the passage, fixed values, same token rows, old and new chances,
   and the selected `Jack` in one view.
2. The 20 position screenshot shows twelve bars at 2, eight bars at 0, the position 2 split, and the
   `11/19` running count without relying on an earlier section.
3. The final screenshot links that running count to `21/39`, the random baseline average,
   and the statement that Stage 3 has no tested cutoff or quality result.
