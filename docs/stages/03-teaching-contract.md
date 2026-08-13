# Stage 3 teaching contract

## Learner

- Intended learner: a curious programmer who can read percentages and simple code.
- Safe prior knowledge: Stage 1 counted hits and Stage 2 changed toy token chances with a key.
- New knowledge: real tokenization, model logits, sampling filters, the manual autoregressive loop,
  paired generation, and copied-text checking.

## One learning question

- Question: At which step does this MLX loop change candidate scores?
- Project role: it connects the toy selector to actual model scores without hiding the loop inside
  `generate()`.
- Plain answer: in the pinned MLX loop, the program adds 2 to green candidate scores, applies the
  sampling filters, converts the remaining scores to chances, and samples one token.

## Learning outcome

After the page, the learner should be able to explain:

1. how text becomes token IDs and next-token scores;
2. which values the watermark changes and which values stay fixed;
3. why copied text must be tokenized again with the same tokenizer and checked with the same key.

## Spine example

- Smallest generation example: the first recorded token from the continuity prompt with the score
  increase enabled.
- Smallest full round trip: the first two recorded tokens. Token 1 supplies checker context, and
  token 2 is the first token the checker can count.
- Starting inputs: pinned LFM2 revision, fixed instruction and chat template, complete model-input
  token IDs, prompt seed, sampling settings, and the same key used during generation.
- Observable result: one sampled token, its candidate score path, its probability, and its green
  membership.
- Hand reasoning: follow one candidate from raw model score through filters, optional bias,
  softmax probability, seeded sample, and append.
- Failure case: a green token removed by top-k or top-p remains unavailable.

## Controlled exploration

- Held fixed: model, prompt, first-step history, temperature, top-k, top-p, seed, and key profile.
- First change: turn the watermark score increase off and on.
- Visible change: only green survivor scores and the normalized probabilities change before the
  seeded sample.
- Learner sentence: the watermark changes the distribution used by the sampler, so it can change
  the sampled token without forcing one fixed token.

The second guided comparison keeps the copied text fixed and changes only the checker key. The
reader should watch which observed tokens count as hits while `T` and the z score formula stay
fixed.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| Model and tokenizer revision | external configuration | `configs/lab_03.toml` and Hugging Face model API | exact revision in artifact |
| MLX-LM loads and runs the pinned 4-bit LFM2 checkpoint | external configuration | pinned model card and MLX-LM source | revision and versions in artifact |
| Prompt tokens and first-step candidate values | measured | `artifacts/lab-03/trace.json` | `just verify-lab-03` |
| Six paired continuations | measured | `artifacts/lab-03/trace.json` | `just verify-lab-03` |
| Copied-text token match results | measured | `artifacts/lab-03/trace.json` | tokenizer replay in verifier |
| Same-key and comparison-key `G`, `T`, and z | measured | `artifacts/lab-03/trace.json` | scorer replay in verifier |
| A filtered token stays unavailable after watermarking | derived | fixed tensor test | sampling-order regression test |
| Three prompts do not establish accuracy or quality | limitation | Stage 3 contract | scope review |

Replace the measured artifact rows with their exact recorded values after the approved run. Do not
write values into the lesson before the artifact exists.

## Boundaries

- This stage establishes the location and replay of the intervention in one pinned manual loop.
- It does not establish a detector cutoff, accuracy, prose quality, device portability, production
  key security, or model-family generalization.
- Stage 4 library adapter, Stage 5 GPU model, Stage 6 dataset, later attacks, deployment, and
  publishing remain unimplemented.
- Dataset, Modal, secrets, new remotes, pull requests, deployment, and publishing remain gated.
  Local Apple GPU use is approved only for this Stage 3 fixture.

## Continuity rules

- Begin with the Stage 2 running sentence and show the same words becoming LFM2 tokens.
- Keep the author-facing passage separate from the instruction and chat-template control tokens.
  Show the complete model input in a disclosure.
- Show the complete loop first: token IDs, model scores, filters, score increase, probability,
  sample, append, and repeat. Then zoom into the first generated token.
- Keep Stage 1 `G`, `T`, and z labels when the checker returns.
- Preserve green hatching for selected tokens, orange for seeded sampling, and rust for ordinary
  red results.
- State the locked MLX loop order beside the first loop. Do not bury it in an appendix.
- Name the formal terms only after the page shows the concrete score operation.
- Use the recorded first prompt as the single spine. The other two prompts support the result
  pattern and limitations rather than starting new stories.

## Interaction contract

1. `Reveal token pieces` shows the first useful boundaries, then reveals the remaining recorded
   pieces together. The prompt stays fixed.
2. `Show next loop step` moves the recorded first token through model scores, filters, watermarking,
   probabilities, sampling, and append. Only one stage appears per press.
3. `Compare score increase off and on` aligns the recorded control and watermarked first step.
   Model, prompt, settings, and seed stay fixed.
4. `Check copied text` replays the first three eligible copied tokens one at a time, then finishes
   the recorded check in one action. It updates `G`, `T`, and z.
5. `Check the same text with the comparison key` keeps the text fixed and changes only the hashing
   key.

Each interaction must state the action, fixed values, changed value, mark to watch, and a full
sentence interpretation. Advanced configuration belongs in a disclosure. The page must include a
complete non-script fallback and use no remote scripts, fonts, storage, or fetch calls.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-3-lesson.html`.
- Views: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
- Mid-page screenshots: token pieces, one-token loop, and copied-text checker.
- Test every control, keyboard focus, reduced motion, script-off fallback, console output, and
  horizontal overflow.
- Run the learner copy through the Humanizer plain register and its final anti-AI audit.
