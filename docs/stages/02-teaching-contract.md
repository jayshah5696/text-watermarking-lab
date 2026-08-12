# Stage 2 teaching contract

## Learner

- Intended learner: a curious programmer who has seen probabilities but not watermark code.
- Safe assumption: they know that software can choose among numbered options.
- Teach here: logits, softmax probabilities, keyed green membership, one visible draw, and replay.

## One learning question

- Question: How can a key change token choice without forcing one fixed output?
- Why it matters: Stage 3 will apply this operation to logits from a real language model.
- Plain answer: in this 20-option toy sampler, the fixed development key, the previous four IDs,
  and the teaching rule select five options for a boost. No option is removed.

## Learning outcome

After the page, the learner should be able to explain:

1. how the same key, context, settings, and rule reproduce five green IDs;
2. why adding 2.0 raises green odds without guaranteeing a green sample;
3. how the detector reconstructs membership from the generated history.

## Spine example

- Smallest full example: position 4 from the selected Stage 2 trace.
- Inputs: context `[15, 0, 1, 1]`, 20 fixed logits, five green IDs, and draw `0.307310772959`.
- Result: the plain probabilities choose token 1, while the biased probabilities choose green
  token 2.
- Hand reasoning: token 2 rises from logit 1.5 to 3.5 and from probability 0.124 to 0.319.
- Check against a common mistake: positions 2 and 3 show that receiving no boost does not prevent
  a token from being chosen.

## Controlled exploration

- Hold fixed: context, key, logits, green fraction, and visible draw.
- Change first: switch the logit bias between 0 and 2.
- Watch: token 2's probability and the selected token under the same draw.
- Learner sentence: adding the bias changed the probability intervals, so the same draw selected
  a different token.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
|---|---|---|---|
| Five of 20 IDs are green | derived | `configs/lab_02.toml`; `trace.json` | `just verify-lab-02` |
| Position 4 green IDs are `[2, 5, 6, 10, 11]` | derived | `artifacts/lab-02/trace.json` | exact replay |
| Token 2 probability changes from 0.123775 to 0.318612 | derived | `artifacts/lab-02/trace.json` | exact replay |
| The same draw changes the choice from ID 1 to ID 2 | derived | `artifacts/lab-02/trace.json` | exact replay |
| For one boosted token versus one unchanged token, `exp(2)` is about 7.389 | derived | `toy_greenlist.py`; fixed test | `just check` |
| Final trace has two green hits in four positions | derived | `artifacts/lab-02/trace.json` | `just verify-lab-02` |
| The published teaching key and toy rule provide no secrecy or production security | opinion | Stage 2 contract | scope review |

## Boundaries

- Establishes: deterministic keyed membership, logit bias, sampling, and detector replay.
- Does not establish: model quality, a calibrated detection rate, or production security.
- Later preview only: real model logits, tokenization, upstream KGW behavior, and copied-text tests.
- Gates still active: models, tokenizers, datasets, cloud, GPU, remote, and publishing.

## Output

- Destination: `.agent/diagrams/text-watermarking-stage-2-lesson.html`.
- Preserve: the Stage 1 lesson's paper-like palette and plain claim boundary where useful.
- Browser checks: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
