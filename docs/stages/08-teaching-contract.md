# Stage 8 teaching contract

> Status: pre-run. Result fields remain empty until selected evidence verifies.

## Learner

- Intended learner: a programmer who followed Stage 7 and can read copied-token prefixes, `G/T`, z,
  and the strict cutoff.
- Safe prior knowledge: the checker rebuilds keyed membership from ordered token IDs; Stage 7 froze
  twelve suitable marked outputs before Stage 8.
- Knowledge taught here: an edit changes a character string first, tokenization second, and keyed
  checks third; score loss must be separated from length or meaning loss; delta changes the
  sampling distribution during generation rather than editing finished text.

## One learning question

- Question: how does ordinary editing change the frozen watermark evidence, and what does a larger
  generation bias buy?
- Project role: Stage 7 measured unedited separation. Stage 8 tests which evidence survives visible
  changes and whether stronger embedding has measurable costs.
- Plain answer: edit one recorded string, re-tokenize it, replay the checker on the new history, and
  accept a removal claim only when the result still passes length and meaning checks. Then rerun a
  smaller paired generation fixture with delta as the sole changed setting.

## Learning outcome

After the page, the learner should be able to explain:

1. why deleting one word can change later token boundaries and keyed contexts;
2. why a lower z score alone does not prove a useful or meaning-preserving attack; and
3. how to read delta, detector evidence, NLL, repetition, and achieved length without merging them
   into one quality score.

## Spine example

- Smallest complete example: Stage 7 rank `1000`, carried from its exact marked copied text and
  80-token baseline through deterministic 10 percent word deletion, re-tokenization, correct-key
  replay, score comparison, and preservation screen.
- Starting state: the frozen character string, token IDs, generation key, 80-token baseline score,
  and strict cutoff.
- Observable result: pending Stage 8 evidence. The row stays the spine whether z rises, falls, or
  remains unchanged.
- Hand-worked reasoning: name deleted word indices; show the first old/new token mismatch; count
  edited `G/T`; calculate ordinary hits, ordinary movement, and z; then compare length and meaning
  screens.
- Failure or ambiguity: rank `1001` remains visible because its first 80 marked and control token IDs
  were already equal in Stage 7. Add the first edited row that lowers z but fails preservation.

## Controlled exploration

### First interaction: reveal one deletion

- Held fixed: original rank, full copied source, key, tokenizer, deletion seed, and 10 percent rate.
- Changed: reveal the preselected deleted word positions one at a time.
- Watch: the visible string closes, tokenizer boundaries diverge, and later checker contexts rebuild.
- Learner sentence: the checker scores the edited token history, so later states cannot be shifted
  from the old trace.

### Second interaction: compare attacks

- Held fixed: row set, original source, key, detector profile, and 80-token scoring rule.
- Changed: one named attack at a time.
- Watch: z change, copied length ratio, automatic screen, and manual status remain separate.
- Learner sentence: an attack counts as useful only when it changes evidence without failing the
  declared content and length checks.

### Third interaction: compare delta

- Held fixed: eight prompts, per-row seeds, model, sampler, key, green fraction, context rule, and
  token cap.
- Changed: delta 1, 2, then 3.
- Watch: row-level detector z, NLL, repetition, and achieved copied length.
- Learner sentence: a larger delta can buy more key-specific evidence, but this small fixture must
  show any model-proxy cost rather than assuming quality is unchanged.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| ranks 1000 through 1011 were frozen before Stage 8 | measured Stage 7 fact and pre-run selection | `artifacts/lab-07/results.json`; Stage 8 contract | identity checks |
| original rank 1000 copied text, IDs, and 80-token score | measured | Stage 7 artifact | `just verify-lab-07` and Stage 8 cross-check |
| deterministic edit positions and strings | derived | `configs/lab_08.toml`; Stage 8 attack implementation | independent local rebuild |
| every edited token state and score | measured from deterministic text and pinned tokenizer | pending Stage 8 raw and selected artifacts | token reconciliation and local detector replay |
| paraphrase similarity, length ratio, number check, and manual status | measured and human-reviewed | pending Stage 8 artifacts and review file | schema and arithmetic checks; manual provenance retained |
| delta 1 and 3 generations and metrics | measured | pending Stage 8 remote return | selected-artifact reconstruction |
| delta 2 baseline | measured Stage 7 evidence | `artifacts/lab-07/results.json` | cross-artifact identity checks |
| positive wording is narrow | project claim rule | `AGENTS.md`; Stage 8 contract | lesson text test |

## Boundaries

- Establishes: score changes under named edits on twelve frozen outputs and a three-setting bias
  comparison on eight frozen prompts for one pinned Gemma, tokenizer, key, detector, and sampler.
- Does not establish: universal edit robustness, adaptive security, human-perceived quality,
  production calibration, authorship, generic AI origin, another model, another watermark family,
  or Claude's private implementation.
- Homoglyph substitution is a tokenizer diagnostic, not a semantic edit.
- Embedding similarity and NLL are model-based proxies. The page must not call them human judgment.
- A positive result means only "consistent with this configured watermark and key."
- Model/cloud reruns, publication, endpoints, secrets, or additional models remain separate gates.

## Output

- HTML destination: `.agent/diagrams/text-watermarking-stage-8-lesson.html`
- Continuity: open on Stage 7's frozen rank 1000 copied-token strip and score. Preserve its character
  string until an explicit edit acts. Keep unchanged tokens in place only while their identity and
  order match. At the first tokenization mismatch, split old and edited lanes. Keep `G`, `T`, z, and
  the cutoff as the same visual objects while they update.
- Colors: blue for the inherited copied source; green for correct-key membership/evidence; cyan for
  the paired control source used in mixing; violet for paraphrase; yellow for the key/cutoff; coral
  for edits, failed preservation, or warnings; gray for unscored or unavailable evidence.
- Browser targets: 1440 by 1000 light, 390 by 844 light, 1200 by 900 dark, reduced motion,
  scripts-off, keyboard, all controls, console, and overflow.
