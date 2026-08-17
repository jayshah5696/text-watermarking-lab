# Stage 9 publication brief

> Status: local assembly complete in draft form. Publication remains unapproved.

## Article role

The final article answers one question: what did the staged open-model experiment establish, and what remains unknown about production watermarking and Claude?

A reader should be able to trace one token from model scores through keyed sampling, rebuild one copied-text score, explain why four controls are needed, and state the result without turning it into generic AI detection.

Narrow answer:

> In one frozen Gemma experiment, correct-key marked scores exceeded three controls on average, while individual rows overlapped and ordinary edits weakened the evidence. The checker recognizes one configured watermark and key, not arbitrary AI writing.

## Teaching spine

Selection rank `1000` remains the spine. Stage 7 chose it before generation. Stage 8 carried its exact copied string through deterministic edits. Stage 9 opens on its unedited, deleted, and paraphrased states, then rewinds to the Stage 3 first-token draw.

The article preserves these objects:

1. the candidate token `Jack`, its token ID, raw score, green membership, and final chance with the score increase off and on;
2. the saved draw, which selects `Jack` in both paths;
3. rank 1000's first 80 copied token IDs and generation-key states;
4. `G=28`, `T=79`, ordinary count `19.75`, ordinary movement `3.8487`, and z `2.1436`;
5. the fixed strict `z > 3` cutoff;
6. four Stage 7 score families at a matched prefix;
7. all 24 paired differences at 80 copied tokens;
8. the same rank 1000 string after deletion and paraphrase; and
9. every Stage 8 attack and bias row before summary values.

Rank `1001` remains the inconvenient row. Stage 6's natural-web crossings remain beside the cutoff discussion.

## Visual plan

### Panel 1: one saved token draw

Reader question: does the watermark force a token?

Show the same candidate table and seed with the score increase off and on. Keep `Jack` fixed as the selected token while its final chance changes.

Caption:

> The watermark changes the sampling distribution. In this saved first draw, `Jack` rises from an 11.6422 percent chance to 18.5816 percent, yet both paths select it.

Alt text:

> Two states of one candidate table show the same five tokens. Green candidates receive a score increase in the marked state. Jack remains the selected token in both states.

### Panel 2: copied text becomes a score

Reader question: where does z come from?

Reveal rank 1000's first 80 copied tokens in order. Reconcile every green state with `28/79`, then display ordinary hits, ordinary movement, and z.

Caption:

> The first copied token supplies context. The checker rebuilds keyed membership for the next 79 tokens, observes 28 green hits, and computes z 2.1436.

Alt text:

> Eighty ordered copied tokens are colored by generation-key membership. A four-part calculation turns 28 green hits among 79 checks into z 2.1436, below the strict cutoff.

### Panel 3: controls and cohort

Reader question: does the marked score beat the alternatives?

Show the four score families for rank 1000, then every document-level paired difference at 80 copied tokens. Add the mean and paired interval only after raw points.

Caption:

> Every dot is one frozen document-level difference. At 80 copied tokens, correct-key marked z exceeded model-control z by mean 1.8296 across 24 complete pairs, with paired bootstrap interval [1.3424, 2.3276].

Alt text:

> Twenty-four paired differences appear around a zero line. Some points overlap zero or move below it. A mean point and interval sit beneath the raw rows.

### Panel 4: edit and bias trade-off

Reader question: what weakens the evidence, and what did stronger embedding cost in the measured proxies?

Keep edit score change, retained length, preservation status, detector z, conditional NLL, and repetition separate.

Caption:

> Named edits usually reduced correct-key evidence in the 12-row fixture. In the eight-row bias sweep, mean z rose with delta while conditional NLL and repetition also rose.

Alt text:

> One chart shows 12 paired score changes for a selected edit. A second connects eight prompts across delta 1, 2, and 3. Text below labels NLL and repetition as model-based proxies.

## External claims

Use primary sources only in the main article:

- Anthropic's current support page for its stated marking plan and undisclosed implementation boundary;
- Kirchenbauer et al. for the green-list mechanism;
- Dathathri et al. for SynthID-Text tournament sampling and production evaluation.

Living provider claims include an inspection date. The article attributes Anthropic's quality statement rather than treating it as this project's result.

## Claim boundary

Allowed wording:

- "consistent with this configured watermark and key";
- "mean paired difference in this frozen 24-row cohort";
- "observed natural-web crossings in this pinned 1,000-row cohort";
- "model-based proxy" for NLL, embedding cosine, and repetition.

Prohibited wording:

- "AI detected" or "human text";
- production accuracy or false-alarm rate;
- universal edit robustness;
- human quality preservation;
- Claude equivalence;
- a 400-token result when zero pairs reached that copied prefix.

## Deliverables and gate

- article source: `blog/article.md`;
- final lesson: `.agent/diagrams/text-watermarking-stage-9-final-lesson.html`;
- builder: `scripts/build_stage_09_lesson.py`;
- verifier: `scripts/verify_stage_09.py`;
- structural evidence tests: `tests/unit/test_stage_09_lesson.py`.

Local assembly does not authorize publication, a pull request, a remote change, or the optional hosted playground.
