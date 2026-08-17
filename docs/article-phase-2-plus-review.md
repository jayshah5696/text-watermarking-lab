# Article Phase 2 and later review

## Scope

This pass rebuilt the canonical HTML from `Give the coin a key` through the method-family comparison. The HTML remains the reading product. Markdown and the Python builder remain editable inputs.

## Visual continuity

The later article now carries a small set of recorded objects instead of switching to anonymous dashboard widgets.

- `Early one morning Jack went up the hill` carries keyed selection, the fixed draw, context movement, and checker replay.
- `Jack`, token ID `30604`, carries the first real-model probability change.
- ` was`, token ID `373`, carries the processor-order comparison.
- rank `1000` carries the four controls and editing example.
- rank `1001` stays visible as the equal marked/control path.

Green means keyed membership or the marked correct-key condition. Blue marks an unchanged or control path. Orange marks the active operation or selected teaching row. Coral marks adverse movement, a false alarm, or a caution. Labels and positions accompany every color.

## Replaced visual blocks

The original later figures were replaced rather than reskinned.

1. The anonymous Stage 2 trace became the declared Jack sentence fixture with exact SHA-256 ranking, score changes, fixed draws, context movement, and checker replay.
2. The Stage 3 table became paired candidate bars and a persistent Jack readout with copied-text outcomes.
3. Processor order became two stable operation rails plus a separate repeated-pair fixture.
4. The Gemma boundary became one request packet with an explicit key boundary, the three short misses, and the later ladder limitation.
5. Calibration became a sorted 1,000-row background with four visible crossings and a same-text counting-rule transformation.
6. The four controls now remain equally legible, followed immediately by rank 1001.
7. The 24-row cohort now gives each selection rank its own line. The matched-prefix counts remain beside it.
8. Editing keeps the rank 1000 text and score visible while every one of the 12 paired changes appears on a labeled row.
9. The delta figure labels important paths and places mean z, conditional NLL, and repeated-pair fraction side by side.
10. The method comparison uses one generation/checking/conclusion frame and leaves Claude's undisclosed settings visibly unresolved.

## Prose pass

The manuscript from Phase 2 onward was rewritten in a direct first-person research voice. It removes numbered interactive captions, dashboard instructions, repetitive setup and recap lines, and several cheap negative reversals. Exact values, inconvenient rows, citations, provider attribution, and narrow claim language remain.

The visible article contains no em dash, en dash, curly quote, decorative arrow, `Interactive N` caption, placeholder, or external runtime dependency.

## Evidence

`tests/unit/test_final_article.py` compares the embedded payload with the canonical Stage 1 through Stage 8 artifacts. Added checks cover:

- the declared Stage 2 sentence fixture, keys, hash prefix, choices, and hit pattern;
- complete Stage 3 continuation text and all three displayed detector scores;
- every Stage 7 selection rank used to label the cohort;
- all prior full-payload checks for calibration, prefixes, editing, and delta.

## Browser QA

Checked with Chrome at:

- desktop dark, 1440 by 1000;
- desktop light, 1200 by 900;
- mobile dark, 390 by 844.

Results:

- 17 figure elements rendered;
- 67 controls rendered;
- 64 enabled controls exercised in each complete traversal, with disabled state controls covered in their enabled states during isolated figure passes;
- zero console or page errors;
- zero horizontal overflow;
- dark background `rgb(0, 0, 0)` with `background-image: none`;
- light background `rgb(247, 247, 245)` with `background-image: none`;
- JavaScript passed `node --check`;
- scripts-off mode retained prose, code, measurements, tables, citations, and sources;
- all seven Markdown tables rendered as semantic HTML tables on desktop and as labeled record cards
  below 600 pixels, with no clipped, empty, unlabeled, or horizontally hidden body cells.

Desktop and mobile screenshots were inspected for every Phase 2 and later figure. The mobile processor-order result was corrected after a six-pixel overflow was found.

## Repository verification

- `just verify-final-article`: 8 passed.
- `just check`: Ruff clean, Pyright clean, 473 tests passed.
- `git diff --check`: clean.

No model, tokenizer, dataset, GPU, cloud, remote, secret, publication, or deployment action was used.
