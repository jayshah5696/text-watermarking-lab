# Stage 2 lesson storyboard

## Spine

Use position 4 for the full worked example. Keep the context `[15, 0, 1, 1]`, the public teaching
key, 20 raw scores, five selected IDs, and draw `0.307310772959` fixed. Change only the boost from
0 to 2.

## Beats

1. State the narrow question. Explain that "gently" means all 20 toy choices remain possible.
2. Introduce the 20 numbered options. Word labels are reader aids, not real tokenizer output.
3. Show that a larger score leads to a larger probability after all scores are converted.
4. Lay the probabilities end to end from 0 to 1. Show how draw `0.3073` selects token 1.
5. Reveal the five IDs selected by the fixed key and current four-ID context.
6. Ask the learner whether a +2 boost forces a green result or only raises its chance.
7. Add 2 only to the five selected scores. Keep every other input fixed.
8. Recalculate the probabilities. Show token 2 rising from 12.4% to 31.9%.
9. Place the same draw on the new probability strip. It now selects token 2.
10. Show position 2, where the boost is active but red token 1 still wins.
11. Advance through the four recorded contexts. Mark the outcomes green, red, red, green.
12. Let the checker rebuild each selected set from the observed history and count 2 of 4 hits.
13. State the boundary. The four positions teach mechanics and do not measure a detection rate.
14. Put symbols, exact hashing, full tables, source commit, and config hash in the appendix.

## Guided controls

- Reveal five selected IDs.
- Choose a prediction: force green or raise the chance.
- Switch between no boost and +2 boost.
- Reveal the red outcome from position 2.
- Advance one position at a time through checker replay.
- Open the exact 20-token calculations and reproduction details.

Do not add editable keys, free sliders, random sampling, threshold controls, or separate tabs for
all four positions.
