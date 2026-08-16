# Stage 7 lesson storyboard

> Status: proposed for user approval before implementation or HTML. Measured result beats remain
> blank until the one approved Stage 7 run finishes.

## One question

Does the configured mark separate from the paired model output, the recorded natural-web
continuation, and the same marked text checked with another key? How does that evidence change as
more copied tokens become available?

## Continuity rule

Open where Stage 6 stopped. Keep the drawer of 24 frozen paired-test rows on screen. Pull out the
first row, selection rank `1000`. Do not introduce a cleaner prompt or a hand-written example.

The same objects persist through the page:

- row label `1000` and its source hash;
- the first 50 Gemma source-token IDs as one blue ordered strip;
- one paired seed;
- control and watermarked copied-token strips;
- green-hit count `G`, eligible count `T`, z, and the separate strict cutoff;
- one fixed horizontal score scale; and
- prefix stops at 40, 80, 160, 200, and 400 copied token IDs where the row supports them.

When a token strip grows, existing tokens keep their identity, order, color, unit, and position.
When control and watermarked histories first differ, stop aligning later tokens as matched objects.
They share an input and seed, not a common sampled history after divergence.

## Visual language

Preserve Stage 6's black technical-document layout, readable prose, quiet surfaces, and direct
labels.

- blue: frozen prompt and shared model inputs;
- cyan: unwatermarked Gemma control;
- green: watermarked output checked with the generation key;
- violet: recorded natural-web continuation;
- yellow: comparison-key replay and the cutoff rule;
- coral: a cutoff crossing or declared inconvenient result;
- gray: unsupported prefix, unscored context, or information not yet revealed.

Never use green for truth or quality. Every color also has a text label and stable lane position.

## Beat order

### 1. Reopen the Stage 6 drawer

Show the final Stage 6 object: 24 rows frozen before model generation. Rank `1000` slides into the
work area. Its 50-token prompt band and 400-token recorded continuation band preserve the Stage 6
scale.

Why now: the learner must see that Stage 7 did not choose prompts after seeing outputs.

Learner knows afterward: this row entered the experiment because of manifest order, not its future
score.

### 2. State the one question in ordinary words

Put four empty result lanes beside the row:

1. marked Gemma text, right key;
2. ordinary Gemma text, right key;
3. recorded web continuation, right key;
4. marked Gemma text, another key.

Do not show scores yet. Label each lane with the objection it tests.

Why now: the learner needs a reason for four checks before seeing four numbers.

Learner knows afterward: one control cannot answer all three alternative explanations.

### 3. Inspect the exact shared input

Expand the first 50 source tokens with position, ID, and decoded piece. Show the required decode and
re-encode identity check. Place the fixed instruction before the decoded prefix and reveal the
complete chat-rendered input in a disclosure.

Why now: "same prompt" should be inspectable, not asserted.

Learner knows afterward: both calls receive the same source prefix and chat framing.

### 4. Freeze everything except one argument

Show two short, exact generation-call snippets side by side. Keep model, rendered input, paired seed,
temperature `0.8`, top-k `40`, top-p `0.95`, and the 400-token safety cap aligned. Highlight the one
extra field in the marked call:

```python
watermarking_config = profile.to_transformers()
```

Interaction: `Compare calls` fades every identical line and leaves the one changed argument.

Why now: the causal intervention fits on one screen.

Learner knows afterward: the pair changes one generation-time input. No text is marked after
sampling.

### 5. Let the two histories run, then stop matching tokens

Animate both recorded outputs from the same prompt and seed. Pause at their first differing copied
token. Keep the common prompt stationary. After divergence, route each token strip into its own
history lane and state that the model now sees different prior tokens.

Controls: Play, Pause, Previous, Next, Replay. Reduced motion starts paused.

Why now: paired inputs do not imply token-by-token paired outputs once sampling paths split.

Learner knows afterward: the experiment pairs rows, while each generated continuation keeps its own
autoregressive history.

### 6. Establish the copied-text boundary

For each generated lane, remove prompt IDs and chat-control IDs. Extract assistant content, display
the exact copied text, and re-tokenize it. Show configured cap and achieved copied length as separate
values. If the row ended early, keep the shorter strip and label unsupported later prefixes.

Interaction: `Show copied boundary` toggles annotations, not data.

Why now: every later score must use the text a reader can copy.

Learner knows afterward: a 400-token safety cap does not guarantee 400 copied tokens.

### 7. Check one concrete prefix by hand

Select the first supported prefix in the fixed order, starting at 40 copied token IDs. Use the
marked-text, generation-key lane. Reveal token membership one position at a time. The first copied
token supplies context. Every later token shows position, ID, piece, previous ID, eligibility, and
keyed result.

Calculate with recorded numbers:

```text
ordinary hits = 0.25 x T
ordinary movement = sqrt(T x 0.25 x 0.75)
z = (G - ordinary hits) / ordinary movement
```

Only after the concrete division, name z as standardized distance. Draw the strict `z > 3` cutoff
as a separate ruler mark.

Why now: the learner should understand one score before comparing four.

Learner knows afterward: score measures distance from the configured quarter-green baseline; the
cutoff applies a decision rule afterward.

### 8. Ask the same row four different questions

Fill the four result lanes at the same copied-token prefix. Change one object at a time:

- marked copied text to control copied text;
- control text to the natural-web continuation;
- generation key to the comparison key while restoring marked text.

Each action states what stays fixed, what changes, and the resulting sentence. Do not animate all
four values simultaneously.

Interaction: four prescribed tabs in the order above. Advanced free selection remains hidden until
all four have been viewed.

Why now: the score families are now concrete checks, not legend jargon.

Learner knows afterward: model control, source control, and key control test different causes for a
high score.

### 9. Grow one recorded history

Return to the spine row. Reveal prefixes at 40, 80, 160, 200, and 400 copied token IDs where
available. Existing token objects remain in place. Extend the strip to the right and update `G`,
`T`, z, and all four score lanes.

Before each reveal, invite a prediction: higher, lower, or unchanged z for the next prefix. Do not
score the prediction. After reveal, state that z can dip even when longer text tends to add evidence
across marked outputs.

Interaction: prescribed prefix buttons. Unsupported lengths stay disabled with the exact achieved
length beside them.

Why now: the learner can distinguish accumulated token history from a fresh sample.

Learner knows afterward: a prefix curve records how evidence changed on one fixed output. It need
not rise at every step.

### 10. Show the declared inconvenient row

Apply the fixed rule from the experiment contract and state which clause selected the row. Show it
beside the spine at the same longest jointly supported prefix. Preserve any reversal, wrong-key
competition, negative-control crossing, short output, or weak margin.

Interaction: `Spine row` and `Inconvenient row` switch the row while preserving lane order, scale,
key labels, and prefix rule.

Why now: the learner sees the failure before any mean compresses the cohort.

Learner knows afterward: a useful aggregate may coexist with overlap, reversals, and misses.

### 11. Reveal every frozen row

Start with the fixed spine and inconvenient row highlighted. Then reveal all complete matched rows
for one prefix. Plot row-level differences for:

```text
marked right-key z - model-control right-key z
marked right-key z - natural-web right-key z
marked right-key z - marked comparison-key z
```

Keep zero visible. A dot to the left means the row moved against the expected direction. State the
complete-prefix denominator before showing the mean.

Interaction: select one contrast at a time. The row cohort and prefix stay fixed.

Why now: the learner reads raw variation before the summary.

Learner knows afterward: every dot is a paired document difference, not a token or a probability.

### 12. Add the mean and interval last

Place the arithmetic mean on top of the row dots. Build the deterministic paired bootstrap in three
visible steps:

1. resample row labels with replacement;
2. keep each row's two matched values together;
3. recompute the mean 10,000 times and mark the middle 95 percent.

Show one small authored resampling illustration first, labeled illustration. Then show only measured
Stage 7 interval values from the artifact.

Interaction: one autoplaying deterministic resample explanation with Pause, Replay, Previous, and
Next. The 10,000-run artifact distribution does not rerun in the browser.

Why now: interval notation appears after the learner knows what was resampled.

Learner knows afterward: the interval describes uncertainty across these 24 frozen documents. It is
not accuracy or a population guarantee.

### 13. Present the measured result ledger

Show every prefix in a compact table. For each prefix and contrast include:

- complete matched row count;
- mean paired z difference;
- 95 percent bootstrap interval;
- score-family cutoff counts; and
- links to selectable rows.

Show missing long-prefix rows as missing because copied output ended, never as zero. Keep all 24
rows available in a disclosure with copied text and score details.

Why now: the main story has supplied enough vocabulary to read the full result.

Learner knows afterward: aggregate values depend on a visible matched denominator.

### 14. Translate the result into one narrow sentence

Use measured artifact values and allow an adverse or ambiguous conclusion. The sentence template is:

> In this pinned 24-row Gemma experiment, [measured direction and interval] at [prefix and complete
> denominator]. Individual rows [measured overlap or reversal fact].

Follow with the fixed positive wording where relevant:

> Consistent with this configured watermark and key.

Place the prohibited interpretations beside it: generic AI detection, authorship, Claude's private
implementation, production rates, quality preservation, and edit resistance.

Why now: the learner has seen the mechanism, rows, and summary needed to judge the claim.

### 15. Hand the same objects to Stage 8

Freeze the unedited copied-token strips and their scores. Preview one future edit arrow without
showing an attack result. State that Stage 8 may change one editing operation at a time after a new
approval.

Why now: continuity proceeds through the recorded outputs rather than switching to a new demo.

Learner knows afterward: Stage 7 measures unedited separation. Editing robustness remains open.

## Guided interactions

### Compare generation calls

- Instruction: press `Compare calls`.
- Fixed: model, prompt, seed, sampler, cap, and call order.
- Changed: presence of the keyed generation configuration.
- Watch: every identical line fades.
- Feedback: the keyed logits processor acts during token choice in one call.

### Follow the sampled histories

- Instruction: play to the first differing copied token, then step manually.
- Fixed: recorded outputs and shared prompt.
- Changed: revealed generation position.
- Watch: the two paths stop sharing history after their first different token.
- Feedback: later logits are conditioned on different histories.

### Ask four questions

- Instruction: inspect marked, model-control, natural-web, then comparison-key evidence.
- Fixed: row and copied-token prefix.
- Changed: checked sequence or key, one at a time.
- Watch: source label, key label, `G/T`, z, and cutoff result.
- Feedback: each lane removes one alternative explanation.

### Grow the prefix

- Instruction: predict, then reveal 40, 80, 160, 200, and 400 where supported.
- Fixed: row, token order, copied history, and profiles.
- Changed: number of copied token IDs included.
- Watch: existing tokens remain while `G`, `T`, and z update.
- Feedback: longer prefixes add observations; one row's z can still move either way.

### Read every paired difference

- Instruction: choose one contrast, then reveal all complete matched rows.
- Fixed: prefix, cohort, and zero line.
- Changed: comparison contrast.
- Watch: dots on either side of zero, spine row, inconvenient row, denominator, mean, and interval.
- Feedback: the summary does not erase overlap or reversals.

## Main path and appendix

Keep on the main path:

- frozen-row identity;
- exact shared prompt and one changed call argument;
- path divergence;
- copied-text boundary and achieved length;
- one hand calculation;
- four controls;
- one prefix curve;
- inconvenient row;
- all row-level differences before mean and interval;
- narrow measured conclusion.

Move to disclosures:

- full chat-rendered string;
- all token IDs outside the selected teaching trace;
- package versions, source commit, config hash, dataset and model hashes;
- bootstrap seeds and implementation;
- exact binomial tails;
- distinct-pair diagnostic;
- runtime, GPU memory, and cost;
- all 24 copied-text records.

## Evidence placeholders that block HTML completion

Do not fill these until `artifacts/lab-07/results.json` exists and verifies:

- spine generated text, copied IDs, stop reasons, and token colors;
- first divergence position;
- all four score-family values;
- supported prefixes per row;
- inconvenient-row identity and reason;
- complete-prefix denominators;
- row-level paired differences;
- means and bootstrap intervals;
- cutoff counts, runtime, and cost.

No illustrative number may occupy a measured result slot.

## Screenshot tests

1. Generation screenshot: a newcomer can identify the exact shared prompt, paired seed, fixed
   sampler fields, safety cap, and single changed generation argument.
2. Four-question screenshot: a newcomer can explain what each score lane tests, identify the copied
   prefix, and read z separately from strict `z > 3`.
3. Cohort screenshot: a newcomer can find the complete matched denominator, dots on either side of
   zero, fixed spine, declared inconvenient row, mean, and paired bootstrap interval.

## Review synthesis and current validation boundary

The design was checked against the three repository reviewer prompts in one local pass because the
current harness exposes no independent reviewer session and workflow fan-out was not requested.
The repeated risks were:

- introducing four scores before explaining their jobs;
- aligning sampled tokens after histories diverge;
- calling the 400-token cap an achieved length;
- hiding short outputs by changing row sets without a denominator;
- showing an interval before explaining row-level paired differences; and
- letting the aggregate hide reversals or negative-control crossings.

The beat order above resolves those risks. Independent reviewer validation remains pending before
HTML implementation. Browser QA also remains pending because no HTML exists yet.
