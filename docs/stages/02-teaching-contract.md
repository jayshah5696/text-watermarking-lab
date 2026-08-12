# Stage 2 teaching contract

## Learner

- Intended learner: a curious programmer who has seen basic probability but has not seen
  watermark code.
- Safe assumption: they know that software can choose among numbered options.
- Teach in the main path: candidate IDs, logits as scores, softmax as shared normalization,
  cumulative sampling, context-dependent green membership, the +2 logit boost, the rolling
  context window, and checker replay.

## One learning question

- Question: How can a key raise some token chances without forcing one fixed output?
- Why it matters: a later approved stage would place the same conceptual operation between real
  model logits and token sampling.
- Plain answer: the current four IDs and the public teaching key reproducibly select five of 20
  candidates. Adding 2 to those five logits changes all 20 final probabilities, but none becomes
  zero. One draw still decides the next token.

## Two-layer teaching design

The lesson must not ask one fixture to do two different jobs.

1. **Hand-authored concept illustration, not run data.** Open with
   `Jack went up the ___` and several ordinary endings. Use this only to show where a watermark
   would act after a language model has supplied next-token scores. State in the first viewport
   that Stage 2 did not run a model and did not generate the sentence.
2. **Recorded Stage 2 trace with synthetic scores.** Use the locked 20-option artifact for every
   numerical claim, selector result, probability, draw, context transition, and checker count.
   Present IDs as the primary labels. The optional word tags belong in the audit table because
   their meanings never affect the experiment.

Bridge the layers explicitly: the illustration locates the operation in ordinary text; the
recorded trace measures that operation by itself. Never relabel observed IDs after the run or
search keys and seeds for a sentence-shaped outcome.

## Learning outcome

After the page, the learner should be able to explain the complete chain:

1. context and key select five temporary green IDs;
2. only those five logits receive +2;
3. softmax recalculates all 20 probabilities together;
4. one draw selects the interval that contains it;
5. the chosen token enters history; and
6. the checker later rebuilds membership from that observed history.

## Spine example

- Begin with the human question: after `Jack went up the`, words such as `hill`, `road`, `stairs`,
  and `path` could plausibly come next. A watermark changes some chances before sampling; it does
  not edit the words already written.
- Follow position 4 from the selected Stage 2 trace without switching examples mid-calculation.
- Locate it in history: initial context `[3, 7, 11, 15]` followed by generated IDs `[0, 1, 1]`
  produces the current context `[15, 0, 1, 1]`.
- Fixed inputs: public key, 20 candidates and raw logits, context `[15, 0, 1, 1]`, green fraction
  0.25, and draw `0.307310772959`.
- Selector result: five green IDs `[2, 5, 6, 10, 11]`.
- One changed input: boost amount 0 versus 2.
- No-boost result: ID 1 owns interval `[0.184651, 0.335831)`, so the draw selects ID 1.
- With-boost result: ID 2 moves from logit 1.5 to 3.5 and from probability 0.123775 to
  0.318612. It owns `[0.116993, 0.435605)`, so the same draw selects ID 2.
- Checker result: ID 2 belongs to the rebuilt green set, so position 4 adds one green hit.

## Main-path calculations

The learner must not need an appendix to connect one state to the next.

- Green-set size: `20 × 0.25 = 5`.
- Selector: show one exact candidate message, visible digest prefixes in rank order, and the cutoff
  after rank five.
- Score change: `ID 2: 1.5 + 2.0 = 3.5`; `ID 1: 1.7 + 0 = 1.7`.
- Stable softmax after the boost: subtract maximum 3.5; the adjusted weights total 3.138616;
  ID 2 gets `1 / 3.138616 = 0.318612`; ID 1 gets
  `0.165299 / 3.138616 = 0.052666`.
- Shared normalization: explicitly explain why ID 1's probability falls even though its logit
  stays 1.7.
- Green probability mass: 0.292770 before the boost and 0.753624 after it. Red candidates retain
  0.246376 after the boost.
- Sampling boundaries: label the first three cumulative intervals before and after the boost and
  place the same draw across both rulers.
- Context transition: show “drop the oldest ID, append the chosen token” for every recorded step.
- Checker inputs: key, selection rule, initial context, and observed IDs `[0, 1, 1, 2]`. State that
  logits, probabilities, and random draws are not needed for replay.
- Final score: derive `G=2`, `T=4`, and `z=1.1547`, then state that Stage 2 has no decision
  threshold and produces no verdict.

## Controlled exploration

- Selector control
  - Instruction: run the selector for position 4.
  - Fixed: key, context, candidates, and green fraction.
  - Changes: the digest ranking and rank-five cutoff become visible.
  - Watch: exactly five candidates cross the cutoff.
  - Interpretation: green is temporary membership for this context.
- Prediction control
  - Instruction: predict whether unchanged ID 1 can lose probability.
  - Fixed: ID 1's raw logit.
  - Changes: five other logits receive +2 and the shared denominator grows.
  - Watch: ID 1 stays at logit 1.7 while its probability falls.
  - Interpretation: softmax couples every final probability.
- Bias control
  - Instruction: switch the boost from 0 to 2.
  - Fixed: key, context, raw logits, green IDs, candidate order, and draw.
  - Changes: five adjusted logits, all normalized probabilities, and the chosen interval.
  - Watch: ID 2's interval grows across draw 0.307311.
  - Interpretation: the same draw can select a different token without any token being forced.
- Failure reveal
  - Instruction: inspect recorded position 2.
  - Fixed: vocabulary, +2 rule, and sampling method.
  - Changes: context, green set, and recorded draw.
  - Watch: draw 0.112284 lands in red ID 1 although green mass is 72.6%.
  - Interpretation: a preference is not a guarantee.
- Checker replay
  - Instruction: advance through the observed IDs.
  - Fixed: public key, selection rule, and observed sequence.
  - Changes: context, rebuilt green set, membership result, and running count.
  - Watch: green, red, red, green becomes `G=2`, `T=4`.
  - Interpretation: the checker tests observed membership and never resamples.

## Visual system

- Keep a persistent causal rail:
  `context + key → green set → logits +2 → softmax → draw → append → checker`.
- Use blue for original values, green outline and hatching for temporary green membership, solid
  green additions for +2, orange only for the fixed draw, and rust/gray for observed red results.
- Pair every color with a word or pattern.
- Use large aligned probability rulers with visible cumulative boundaries. Do not rely on hover
  titles.
- Show state transitions with arrows. Cards may contain explanations but must not replace the
  causal connections.
- Keep all four checker positions visible; interaction focuses one position instead of unlocking
  otherwise missing content.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
|---|---|---|---|
| Five of 20 IDs are green | derived | `configs/lab_02.toml`; `trace.json` | `just verify-lab-02` |
| Position 4 digest order selects IDs `[2, 5, 6, 10, 11]` | derived | selector rule; position 4 context | fixed selector replay |
| ID 2 probability changes from 0.123775 to 0.318612 | derived | `artifacts/lab-02/trace.json` | exact replay |
| Green mass changes from 0.292770 to 0.753624 | derived | `artifacts/lab-02/trace.json` | sum selected probabilities |
| The same draw changes the choice from ID 1 to ID 2 | derived | `artifacts/lab-02/trace.json` | cumulative interval replay |
| Position 2 selects red ID 1 while green mass is 72.6% | derived | `artifacts/lab-02/trace.json` | exact replay |
| Final trace has two green hits in four positions | derived | `artifacts/lab-02/trace.json` | `just verify-lab-02` |
| Published key and toy rule provide no production security | limitation | Stage 2 contract | scope review |

## Boundaries

- Establishes: deterministic context-dependent membership, logit bias, shared normalization,
  cumulative sampling, context movement, and checker replay.
- Does not establish: language quality, detection accuracy, a decision threshold, production
  security, authorship, or compatibility with Anthropic's private implementation.
- Later preview only: real model logits, tokenizer IDs, an approved upstream selector, and copied
  text tests.
- Gates still active: models, tokenizers, datasets, cloud, GPU, remote, and publishing.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-2-lesson.html`.
- Browser checks: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
- The first viewport must show `Jack went up the ___`, familiar candidates, and the visible label
  `Hand-authored concept illustration · not run data`.
- The recorded section must be visibly labelled `Recorded Stage 2 trace · synthetic scores`.
- No main-path visual may present `amber birch birch cobalt` as prose. Use IDs in the measured
  history, candidate list, score ledger, probability rulers, context flow, and checker.
- Mid-page screenshots: selector ranking, aligned probability comparison, and checker replay must
  each be understandable without the hero.
- Exercise every control in sequence and after reset. Check keyboard focus, reduced motion, console
  errors, and horizontal overflow.
