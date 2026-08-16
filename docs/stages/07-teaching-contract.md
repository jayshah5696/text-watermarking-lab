# Stage 7 teaching contract

> Status: proposed before the model-backed run. Measured fields remain pending until the approved artifact exists.

## Learner

- Intended learner: a programmer who followed Stage 6 and understands `G/T`, z, the strict cutoff,
  and why outside-text calibration comes before the core experiment.
- Safe prior knowledge: the key rebuilds token membership; control and watermarked generation can
  share a prompt and seed; Stage 6 froze 24 prompts before model generation.
- Knowledge taught here: why four controls answer different objections, how paired generation
  removes prompt identity as a comparison difference, how prefixes reveal accumulating evidence,
  and why an interval on 24 rows is still a small-cohort summary.

## One learning question

- Question: does the configured mark separate from all three useful controls, and how does evidence
  change as more copied tokens become available?
- Project role: Stage 6 measured background scores on natural-web text. Stage 7 finally places the
  marked output beside its paired model control, its source continuation, and its wrong-key replay.
- Plain answer: use each frozen 50-token prompt twice with one seed, score the two generated paths
  and two independent checks, then compare matched prefixes without dropping inconvenient rows.

## Learning outcome

After the page, the learner should be able to explain:

1. what each of the four score families tests and why no single control can replace the others;
2. how one frozen row becomes a same-prompt, same-seed pair and then five copied-token prefixes;
3. how to read a row-level z difference and its paired bootstrap interval without calling it
   accuracy or a production guarantee.

## Spine example

- Smallest complete example: Stage 6 paired-test selection rank `1000`, carried from the frozen C4
  source through the exact 50-token prompt, paired Gemma generation, copied-text tokenization, four
  keyed checks, prefix scores, and the full-cohort comparison.
- Starting state: one manifest identity, one exact 50-token source prefix, one paired seed, the
  pinned Gemma runtime, the generation key, the comparison key, and the unchanged strict cutoff.
- Observable result: pending the one approved Stage 7 run. The row remains the spine whether its
  outputs stop early, cross the cutoff, or fail to separate.
- Hand-worked reasoning: at one supported prefix, show the watermarked row's concrete `G` and `T`,
  compute ordinary hits `0.25T`, compute ordinary movement, derive z, then subtract the three
  matched control z values one at a time.
- Failure or ambiguity: apply the predeclared inconvenient-row rule from the Stage 7 contract. Show
  the chosen row beside the fixed spine and the full 24-row cohort.

## Controlled exploration

### First comparison: one score family at a time

- Held fixed: selected row, copied prefix, tokenizer, green fraction, generation key profile, and
  cutoff.
- Changed: the checked sequence or key role.
- Watch: each control removes a different alternative explanation.
- Learner sentence: the model control checks whether ordinary Gemma output scores high, the
  natural-web continuation checks the source domain, and the comparison key checks whether the
  marked text carries key-specific evidence.

### Second comparison: prefix length

- Held fixed: row identity, complete copied token history, key profile, and score formula.
- Changed: reveal the first 40, 80, 160, 200, then 400 copied token IDs where available.
- Watch: `G`, `T`, and z update along one unchanged history. The 80-token view is the same row with
  40 more tokens, not a new sample.
- Learner sentence: a prefix curve shows how evidence accumulated in these recorded outputs; it
  does not promise a monotonic rise on every row.

### Third comparison: row to cohort

- Held fixed: one prefix and one score contrast.
- Changed: show the spine row, the inconvenient row, then every complete matched row.
- Watch: the mean paired difference and interval come from row-level differences, while individual
  rows can move in the opposite direction.
- Learner sentence: the interval summarizes uncertainty across these frozen documents, not the
  detector's accuracy on all text.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| 24 prompts were frozen before generation | measured Stage 6 fact | `data/manifests/lab-06-c4.jsonl` | `just verify-lab-06` |
| paired-test rank `1000` is the fixed lesson spine | derived design choice | Stage 7 contract and Stage 6 manifest | manifest identity test |
| control and watermarked calls share prompt and seed | checked implementation contract | proposed `configs/lab_07.toml`; Stage 7 raw records | config tests and verifier |
| exact prefix set is 40, 80, 160, 200, 400 copied token IDs | locked configuration | Stage 7 contract | config and artifact schema tests |
| each four-family `G/T`, z, exact tail, and decision | measured | pending `artifacts/lab-07/results.json` | `just verify-lab-07` |
| paired mean z differences and 95 percent bootstrap intervals | derived from measured rows | pending Stage 7 artifact | independent deterministic bootstrap rebuild |
| any token color used in the lesson | measured | pending fixed-spine token trace | position, ID, piece, eligibility, membership, and total reconciliation |
| positive wording is narrow | project claim rule | `AGENTS.md`; Stage 7 contract | lesson text test |

## Boundaries

- Establishes: measured separation, or lack of separation, among four fixed score families on one
  24-row paired C4/Gemma experiment under one watermark profile and key pair.
- Does not establish: generic AI detection, human authorship, production false-alarm or true-positive
  rates, text quality, attack resistance, another model or tokenizer, another key, another device,
  or a universal cutoff.
- A positive result means only: "consistent with this configured watermark and key."
- Prefixes are available only where copied output reaches the declared length. Every aggregate must
  show its complete matched denominator.
- Stage 8 editing attacks remain unimplemented.
- Publishing, a GitHub remote, an endpoint, and any replacement cloud invocation remain separate
  approval gates.

## Output

- HTML destination: `.agent/diagrams/text-watermarking-stage-7-lesson.html`
- Continuity: open on Stage 6's frozen 24-row drawer. Carry one row's 50 blue prompt tokens into two
  Gemma paths. Keep the prompt strip, row label, generated token order, green-hit marks, z object,
  and strict cutoff visually stable while the learner changes only the checked family or prefix.
- Visual colors: blue for the shared prompt and model data path; green for correct-key marked
  evidence; cyan for model control; violet for natural-web control; yellow for the comparison key;
  coral only for cutoff crossings or the declared failure panel.
- Browser targets: 1440 by 1000 light, 390 by 844 light, 1200 by 900 dark, reduced motion,
  scripts-off fallback, keyboard use, every control, console, and horizontal overflow.
