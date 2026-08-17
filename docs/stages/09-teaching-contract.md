# Stage 9 teaching contract

> Status: local article assembly approved. Publication remains unapproved.

## Learner

- Intended learner: a programmer who is curious about text watermarking but has not read Stages 1 through 8.
- Safe prior knowledge: a language model chooses tokens from scored candidates.
- Knowledge taught here: how a keyed sampling change accumulates into a count, why copied text can be checked without model weights, how controls limit interpretation, and why editing and stronger bias create trade-offs.

## One learning question

- Question: what did this small open-model watermark experiment establish, and what remains unknown?
- Project role: Stage 9 assembles the frozen lessons and evidence without rerunning or selecting results.
- Plain answer: this configured sampler left more correct-key evidence on average in one frozen Gemma cohort, but the evidence overlapped controls, weakened under edits, and says nothing by itself about arbitrary AI origin, authorship, or Claude's private system.

## Learning outcome

After the page, the learner should be able to explain:

1. how one token moves from model scores through keyed sampling and later checker replay;
2. how `G/T`, z, a cutoff, and empirical controls answer different questions; and
3. which conclusions follow from the 24-row paired experiment and which do not.

## Spine example

- Smallest example containing the full mechanism: Stage 7 and Stage 8 selection rank `1000`.
- Starting state: its frozen C4 source prefix, paired seed, control and marked generation paths, copied marked text, generation key, and 80-token score.
- Observable result: the marked copy scored `28/79`, z `2.1436`, before Stage 8. Deterministic 10 percent deletion produced `25/79`, z `1.3641`; its paraphrase produced `26/79`, z `1.6239` and passed the declared automatic and non-independent manual screens.
- Hand-worked reasoning: the checker expects `79 * 0.25 = 19.75` green hits, observes 28, divides the excess by `sqrt(79 * 0.25 * 0.75) = 3.8487`, and obtains z `2.1436`.
- Failure or ambiguity: rank `1001` had identical marked and control token IDs through 80 copied tokens. Both scored `26/79`, z `1.6239`. In Stage 6, four of 1,000 natural-web rows crossed the same strict cutoff.

## Controlled exploration

### First change: bias one candidate list

- Quantity held fixed: candidate scores, key, context, sampler settings, and saved draw.
- Single quantity changed first: whether the keyed score increase is present.
- What should visibly change: green candidate chances change; a token is still sampled rather than forced.
- Learner sentence: the watermark changes the probability table during generation, not the finished string afterward.

### Second change: inspect one score family

- Quantity held fixed: rank `1000`, copied prefix length, tokenizer, detector profile, and cutoff.
- Single quantity changed first: checked text or key role.
- What should visibly change: `G/T` and z change while the cutoff stays fixed.
- Learner sentence: each control rules out a different easy explanation for a high score.

### Third change: edit the recorded string

- Quantity held fixed: source row, key, tokenizer, and scoring rule.
- Single quantity changed first: one named edit.
- What should visibly change: token identity, checker history, score, and preservation status remain separate readings.
- Learner sentence: a lower score is useful only when enough of the intended text remains.

## Evidence ledger

| Page claim or value | Type | Source path or URL | Verification method |
| --- | --- | --- | --- |
| biased-coin length curve | measured | `artifacts/lab-01/summary.json` | `just verify-lab-01` and Stage 9 structural test |
| toy score increase multiplies relative odds before normalization | derived | `src/watermark_lab/toy_greenlist.py` | fixed unit tests |
| Stage 3 one-token probabilities and saved draw | measured | `artifacts/lab-03/trace.json` | `just verify-lab-03` |
| maintained processor order and GPT-2 scores | measured | `artifacts/lab-04/trace.json` | `just verify-lab-04` |
| Gemma runtime, memory, and short smoke scores | measured | `artifacts/lab-05/trace.json` | `just verify-lab-05` |
| 1,000-row natural-web background | measured | `artifacts/lab-06/calibration.json` | `just verify-lab-06` |
| 24-row paired effects, intervals, and spine evidence | measured | `artifacts/lab-07/results.json` | `just verify-lab-07` |
| edit changes and bias sweep | measured | `artifacts/lab-08/results.json` | `just verify-lab-08` |
| Anthropic's stated marking plan | external | `https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content` | attribute to Anthropic; inspection date shown |
| KGW mechanism | external | `https://arxiv.org/abs/2301.10226` | primary paper |
| SynthID-Text comparison | external | `https://www.nature.com/articles/s41586-024-08025-4` | primary paper |

## Boundaries

- Establishes: a checked implementation path and measured outcomes for the pinned fixtures in Stages 1 through 8.
- Does not establish: a universal detector, production calibration, authorship, generic AI origin, human-perceived quality, adaptive security, or Claude's private implementation.
- Later-stage ideas that must not be presented as completed: a hosted playground, public verifier, production key management, another watermark family, or deployment.
- Authorization gates that remain in force: publication, GitHub remote changes, model or dataset downloads, GPU or cloud use, endpoints, secrets, and any new experimental run.

## Output

- Article source: `blog/article.md`
- HTML destination: `.agent/diagrams/text-watermarking-stage-9-final-lesson.html`
- Existing conventions preserved: true-black technical document, blue copied text, green correct-key evidence, cyan model control, violet natural-web control, yellow key and cutoff, coral edits and warnings.
- Browser sizes and modes to test: 1440 by 1000 light, 390 by 844 light, 1200 by 900 dark, reduced motion, scripts off, keyboard use, console, and horizontal overflow.
