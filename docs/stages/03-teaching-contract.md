# Stage 3 teaching contract

## Learner

- Intended learner: a curious reader who receives only the HTML file.
- Safe prior knowledge: percentages, simple bar charts, and the idea that a program can choose one
  item from several possible items.
- Knowledge taught in this page: token IDs, raw model scores, adjusted sampling chances, the
  difference between distribution change and quality loss, copied text checking, and evidence
  limits.

## One learning question

- Question: When this lab adds a watermark, what changes and what stays the same?
- Project role: it connects the Stage 2 score increase to one pinned LFM2 loop while making the
  quality drawback and scientific boundary visible.
- Plain answer: the saved model weights do not change. At one shared history, both paths start from
  the same raw LFM2 scores. The lab copies those scores, adds 2 to green candidates, and samples from
  different chances. Stage 3 did not measure whether that change helped or harmed text quality.

## Learning outcome

After the page, the learner should be able to explain:

1. why the control and score-increase paths have the same first raw score list but different
   sampling chances;
2. why a changed distribution does not prove a noticeable quality loss, and why one readable pair
   cannot prove quality preservation;
3. which Stage 3 claims have measured support and which claims need a larger quality or calibration
   experiment.

## Spine example

- Smallest example containing the full story: the first 20 recorded tokens from the continuity
  prompt, with the first two positions used for the controlled probability comparison.
- Starting state: the same pinned LFM2 revision, complete 36-token input, first-step history, random
  seed, green group, temperature, top-p, and top-k settings.
- Observable result: `Jack` starts at raw score `14.6875` in both paths. Its final chance is
  `11.6422%` with the increase off and `18.5816%` with the increase on. The seeded sampler chooses
  `Jack` in both paths. At position 2, the control chooses `paused` and the score increase run
  chooses `climbed`. Among positions 2 to 20, the saved counts are `5/19` and `11/19`.
- Hand-worked reasoning: Stage 3 adds 2 before temperature 0.8. The relative green-versus-red odds
  boost before filtering is therefore `exp(2 / 0.8) = 12.1825`. Normalization and top-p/top-k still
  determine the final chances.
- Failure or ambiguity: the same draw can select the same token from two different distributions.
  A readable continuation does not measure quality, and a green candidate can still be removed by
  a later filter. After position 2, the histories differ, so later selected probabilities are
  observations inside different histories rather than a controlled before and after comparison.

## Controlled exploration

- Quantity held fixed: model, prompt, first-step history, raw scores, seed, green group, temperature,
  top-p, and top-k.
- Single quantity changed first: the score increase, from 0 to 2.
- What should visibly change: twelve bars rise from 0 to 2 in the persistent 20-token trace. A
  separate first-position detail shows green probability shares rise, unchanged shares fall, and
  top-p keeps a different number of candidates.
- Sentence the learner should be able to say afterward: the lab changed the sampling distribution,
  even though this recorded first draw selected `Jack` in both paths.

The second guided comparison keeps the copied continuation fixed and changes only the checker key.
The reader should watch which token IDs count as green while the copied text, eligible-token count,
and score formula remain fixed.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| Pinned LFM2 and tokenizer revision | external configuration | `configs/lab_03.toml` | exact revision in selected artifact |
| First-step raw scores, candidate chances, filter counts, and chosen token | measured | `artifacts/lab-03/trace.json` | `just verify-lab-03` |
| `Jack` chance changes from `11.6422%` to `18.5816%` | measured | paired continuity records in `artifacts/lab-03/trace.json` | byte-for-byte verifier replay |
| Position 2 chooses `paused` at `4.0225%` and `climbed` at `28.5079%` | measured | paired continuity records in `artifacts/lab-03/trace.json` | byte-for-byte verifier replay |
| Positions 2 to 20 contain `5/19` and `11/19` green selected tokens | measured | selected-token fields in `artifacts/lab-03/trace.json` | direct count of saved green membership |
| Green-versus-red odds boost is `exp(2 / 0.8) = 12.1825` before filtering | derived | `configs/lab_03.toml`; `src/watermark_lab/manual_generation.py` | direct calculation from locked processor order |
| Six paired same-key and comparison-key counts | measured | `artifacts/lab-03/trace.json` | `just verify-lab-03` |
| Copied text reproduces generated token IDs for all six records | measured | `artifacts/lab-03/trace.json` | tokenizer replay in verifier |
| Three prompts do not measure quality, accuracy, or a cutoff | limitation | Stage 3 contract and experiment size | scope review |
| KGW-style score increases trade stronger detection for possible distribution and quality change | external | Kirchenbauer et al.; Fernandez et al. | primary papers linked in page |
| Non-distortionary SynthID preserves a stated distribution on average over watermark randomness | external | Dathathri et al., Nature 2024 | primary paper linked in page |
| SynthID reports no detected quality loss in its tested configuration | external | Dathathri et al., Nature 2024 | production, controlled human, perplexity, and benchmark evaluations |
| SynthID can reduce inter-response diversity and offers a distortionary stronger mode | external | Dathathri et al., Nature 2024 | paper definitions and evaluation |
| Anthropic says Claude marking does not change meaning, quality, or readability | external vendor claim | Anthropic support page | page linked with undisclosed-method warning |

Selected measured values come from source `2f082b7f63853811881c0f23c2d7022e8e5dbc3b` and configuration
SHA-256 `694a3d09ea341165cef5061360800e43957d2055993f7140b514ebf07ff3117f`.

## Scientific claim ladder

1. Strong support: this pinned loop applies the score increase at the recorded location, samples,
   appends, re-tokenizes, and replays from the local cache.
2. Narrow measured result: the score-increase row has more same-key green hits in each of the three
   fixed prompt pairs.
3. Untested here: prose quality, usefulness, diversity, downstream accuracy, and the best bias.
4. Untested here: false-positive rate, true-positive rate, a decision cutoff, other models, other
   devices, and production security.

The HTML must label the first two items as repository evidence and the last two as open questions.
External papers may explain possible controls, but the page must not present their findings as this
repository's measurements.

## Boundaries

- This stage establishes the location and replay of one configured score change in one pinned
  manual loop.
- It does not establish quality preservation, quality loss, detection accuracy, a false-positive
  rate, a cutoff, device portability, production key security, or model-family generalization.
- Lower bias, entropy-aware skipping, longer-text accumulation, blind quality review, NLL,
  repetition/diversity measures, and SynthID-style sampling are research controls or later-stage
  work. Stage 3 did not test them.
- Stage 4 library adapter, datasets, cloud work, new models, deployment, and publishing remain
  separately gated.

## Continuity rules

- The page must stand alone. It may mention Stages 1 and 2 only after explaining the carried concept
  in plain language.
- Keep the continuity prompt visible through tokenization, the paired probability view, generation,
  and copied-text checking.
- Use one aligned before-and-after probability picture as the main visual. Do not scatter the cause
  across separate cards.
- Keep green hatching for candidates selected by the key, orange for the seeded sampled token, blue
  for fixed values, and rust for limitations. Pair every color with text or a pattern.
- Define a probability distribution as the complete set of chances used to choose the next token.
- Introduce `logit`, `z`, KGW, and SynthID only after the visible operation is understood.
- Keep developer details and full citations in two disclosures.

## Interaction contract

1. `Reveal token pieces` shows how the complete input becomes 36 recorded IDs. The prompt and model
   revision stay fixed.
2. `Reveal key-selected positions` keeps the same 20 token columns and adds green membership marks.
3. `Apply the recorded score increase` raises twelve bars from 0 to 2 without changing their unit.
4. `Follow Jack through sampling` opens a first-position probability detail on one shared scale.
5. `Run the saved draw` marks `Jack` in both paths, then reveals the position 2 fork.
6. `Use the +2 tokens as copied text` reuses the same columns and shows the `11/19` running count.
7. The final result extends that count to the recorded `21/39` checker result.
8. `Use comparison key` keeps the copied text fixed and changes only green membership.
9. The quality and research-control sections are explanatory, not adjustable simulations. Stage 3
   has no measured quality curve to drive a slider honestly.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-3-lesson.html`.
- Views: 1440 by 1000 light, 390 by 844 light, and 1200 by 900 dark.
- Context-free screenshots: aligned before/after distribution, SynthID comparison, and scientific
  claim ladder with measured results.
- Test every control, keyboard focus, reduced motion, script-off fallback, console output, and
  horizontal overflow.
- Run all learner copy through the Humanizer plain register and final lint audit.
