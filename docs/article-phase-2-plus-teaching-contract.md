# Article Phase 2 and later teaching contract

## Product

The user is reviewing only `blog/how-text-watermarks-hide-in-plain-sight.html`. The HTML is the product. The Markdown and builder remain internal inputs so the HTML can be rebuilt and checked.

## Reader

A technically curious reader has finished the coin lesson. They understand a hit count, z score, overlap, false alarms, misses, and the mapping from heads to a favored next-token choice. They have not yet seen how the program chooses that favored set or how a checker reconstructs it.

## Learning sequence

The continuation must answer these questions in order.

1. How does a key select favored tokens for one context?
2. How does the score increase change chances without forcing one token?
3. How does the context move after the sampler chooses a token?
4. How can the checker reconstruct the same decisions from copied text?
5. What changes when hand-written scores become real model scores?
6. Why does processor order belong to the watermark profile?
7. What happened when the same mechanism moved to Gemma?
8. How did outside text, paired controls, edits, and a stronger bias change the evidence?
9. How does the public KGW-style experiment differ from SynthID-Text and Claude's disclosed family?

## Stable objects and colors

- The sentence `Early one morning Jack went up the hill` carries the toy mechanism.
- `Jack`, token ID `30604`, carries the real-model score change.
- Rank `1000` carries the paired-control and editing results.
- Blue means unchanged or baseline behavior.
- Green means keyed membership or the correct-key marked condition. It never means truth or authorship.
- Orange means the active draw, operation, or changed input.
- Coral means a cutoff crossing, adverse result, or caution.
- Violet distinguishes outside or comparison conditions.

## Phase 2 spine

Use the declared sentence fixture from `docs/stages/02-teaching-contract.md`, not the anonymous repository trace, for the visible lesson.

- Vocabulary: `Early, one, morning, Jack, went, up, the, hill, walked, ran, road, path, stairs, and, saw, snow, down, home, ., trail`.
- Key: `stage-02-public-demo-key-v1`.
- Comparison key: `wrong-public-key`.
- Context width: four tokens.
- Favored set: five of 20 tokens.
- Score increase: `2.0`.
- First context: `Early one morning Jack`.
- First favored set: `Early, went, walked, snow, trail`.
- Comparison-key set: `the, hill, path, snow, home`.
- First draw: `0.30`.
- Without the increase, the draw selects `walked`.
- With the increase, the same draw selects `went`.
- `went` moves from `22.85%` to `46.51%`.
- `ran` keeps score `1.9` and moves from `27.91%` to `7.69%` after normalization.
- Generated words: `went, up, the, hill`.
- Hit sequence: green, green, red, red.
- Final score: `G=2`, `T=4`, expected `1`, z `1.1547`.
- Comparison-key result: zero hits in the fixed example.
- There is no Stage 2 cutoff.

The committed anonymous trace remains in the evidence payload and source note. It verifies the implementation but must not replace the readable sentence on screen.

## Later evidence ledger

| Visual | Stable object | Evidence |
| --- | --- | --- |
| Real scores | `Jack`, ID `30604` | `artifacts/lab-03/trace.json` |
| Processor order | token ` was`, ID `373`; six-token repeated-pair fixture | `artifacts/lab-04/trace.json` |
| Gemma boundary | three marked smoke rows | `artifacts/lab-05/trace.json` |
| Calibration | all 1,000 natural-web scores and frozen maximum row | `artifacts/lab-06/calibration.json` |
| Four controls | rank `1000`, 160 copied tokens | `artifacts/lab-07/results.json` |
| Cohort | all 24 rank rows at 80 copied tokens | `artifacts/lab-07/results.json` |
| Editing | rank `1000` text plus all 12 paired changes | `artifacts/lab-08/results.json` |
| Bias | all eight prompt paths for delta 1, 2, and 3 | `artifacts/lab-08/results.json` |
| Field comparison | named method families | primary sources cited in the article |

## Interaction rules

- Every control changes one named variable or advances one deterministic operation.
- Every visual says what remains fixed.
- The page keeps relevant objects visible while they change.
- A fixed explanation may autoplay only if it also supports pause, replay, previous, and next. Direct interaction pauses autoplay.
- Charts show row labels or provide an inspectable selected-row readout. Anonymous dots are insufficient.
- The default state must communicate the finding without a click.
- Scripts-off mode keeps the prose, measurements, tables, and limitations.

## Prose rules

Use first person where the author made a choice or reacted to evidence. Keep direct technical sentences. Remove numbered `Interactive N` captions, dashboard phrasing, recap padding, cheap reversals, repeated disclaimers, and generic transitions. No em dashes, curly quotes, decorative arrows, or meta claims about the article.

The public claim stays narrow: `Consistent with this configured watermark and key.`

## Boundaries

- The KGW-style experiment does not reproduce Claude's private implementation.
- C4 is natural-web text, not verified human writing.
- A 400-token cap is not an achieved 400-copied-token result.
- NLL, embedding cosine, repetition, and assistant review are proxies.
- The visible Stage 2 sentence is a declared hand-written fixture. The anonymous trace is the committed code artifact.
- No model, tokenizer, dataset, GPU, cloud, remote, secret, deployment, publication, or new experimental run is authorized.
