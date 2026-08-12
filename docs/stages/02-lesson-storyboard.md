# Stage 2 lesson storyboard

## Spine

Open with the hand-authored sentence frame `Jack went up the ___`. It is a concept illustration,
not model output or run data. It gives the learner a familiar reason to care before any ID or hash
appears. Then use recorded position 4 for the entire worked calculation. The learner should always
see which layer they are viewing and which values stay fixed. The measured main path must show
every arrow in:

`history + key → five green IDs → five logits +2 → all probabilities recalculated → fixed draw → chosen token → appended history → checker membership`

## Beats

1. **Begin with an ordinary sentence.** Show `Jack went up the ___` with familiar possible endings.
   State that a model would normally supply the scores, but Stage 2 does not run one. Reveal only
   where a keyed boost would act.
2. **Separate illustration from evidence.** Say that the sentence explains the role of the
   operation. Label the next section `Recorded Stage 2 trace · synthetic scores`. Use IDs as the
   main labels and keep the artifact's optional word tags in Audit view.
3. **Give the measured map.** State that the rule raises five option chances but leaves all 20
   probabilities above zero. Show the full seven-operation causal rail.
4. **Locate position 4.** Start at `[3, 7, 11, 15]`, append recorded choices `0`, `1`, and `1`,
   and visibly arrive at context `[15, 0, 1, 1]`.
5. **Meet one sampler choice.** Show all 20 option IDs and raw logits. Define ID, logit, probability,
   draw, and context in plain language. State that no language model judged whether an option fits.
6. **Run the selector.** Show `20 × 0.25 = 5`, one exact candidate message, all 20 digest prefixes
   in rank order, and a cutoff after rank five. End at green IDs `[2, 5, 6, 10, 11]`.
7. **Apply the only change.** Hold key, context, raw logits, candidate order, green set, and draw
   fixed. Change the boost from 0 to 2. Show each of the five score additions in an aligned ledger.
8. **Convert scores together.** Work ID 2 and ID 1 through stable softmax. Explain why ID 2
   rises from 12.4% to 31.9% and ID 1 falls from 15.1% to 5.3% even though ID 1 stays at logit
   1.7. Show green mass moving from 29.3% to 75.4%.
9. **Use the same draw.** Put draw `0.307311` through two large aligned cumulative rulers. Label
   ID 1's before interval and ID 2's after interval. State that the no-boost choice is one
   same-history comparison, not a second generated sequence.
10. **Show the non-guarantee.** At recorded position 2, show green mass 72.6%, red mass 27.4%, the
   red ID 1 interval `[0.068746, 0.125030)`, and draw `0.112284` inside it.
11. **Append and slide.** Show all four context transitions. Only the choice after the +2 boost is
   appended; the no-boost comparison never enters history.
12. **Replay as the checker.** Given the key, initial context, and observed IDs `[0, 1, 1, 2]`,
    rebuild all four green sets. Keep all positions visible and focus one at a time. Gray out logits,
    probabilities, and draws because checking does not use them.
13. **Derive the score without a verdict.** Show `G=2`, `T=4`, expected hits 1, standard deviation
    0.866025, and `z=1.1547`. State immediately that Stage 2 has no threshold.
14. **Answer again and set the boundary.** Separate measured trace facts, derived arithmetic,
    limitations, and the parts a later approved model stage would replace.

## Main interactions

- Run the selector for position 4; reveal digest ranking and cutoff, not only colored cards.
- Predict whether ID 1's probability can fall while its logit stays fixed.
- Switch one boost control between 0 and 2; synchronize the score ledger, softmax values,
  probability mass, rulers, and chosen token.
- Reveal the recorded position 2 failure on an actual probability ruler.
- Step through checker positions while keeping the four-position overview visible and synchronized.

Do not add editable keys, free sliders, random sampling, thresholds, detection-rate controls, or
tabs that break the position 4 spine.

## Visible calculation contract

- Selector rank prefixes for position 4 begin:
  `11:1f82b78762`, `5:4571366736`, `2:5121a02245`, `6:53b61715fd`,
  `10:56138bc661`; draw the cutoff after the fifth item.
- Stable no-boost total weight: 5.415614 after subtracting maximum 1.9.
- Stable boosted total weight: 3.138616 after subtracting maximum 3.5.
- ID 2 after boost: weight 1; probability `1 / 3.138616 = 0.318612`.
- ID 1 after boost: weight 0.165299; probability `0.165299 / 3.138616 = 0.052666`.
- No-boost intervals near the draw: ID 0 `[0, 0.184651)`, ID 1
  `[0.184651, 0.335831)`, ID 2 `[0.335831, 0.459606)`.
- Boosted intervals near the draw: ID 0 `[0, 0.064327)`, ID 1
  `[0.064327, 0.116993)`, ID 2 `[0.116993, 0.435605)`.

## Appendix only

- Full 20-row exact table.
- Full selector message format and all hash metadata after the ranked demonstration.
- Source commit, config fingerprint, seed, and reproduction commands.
- The exact upstream KGW compatibility warning and future implementation notes.

The main lesson may use a details disclosure for these references, but no disclosure may contain a
reasoning step needed to understand the worked result.
