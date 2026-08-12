# Concept-first lesson pattern

## Core sequence

Use this cognitive order:

`familiar object → prediction → visible result → failed intuition → measuring tool → notation → repetition → distribution or pattern → real application`

The exact sections may vary, but do not invert this order without a clear reason.

## The spine example

Choose one example and reuse it across the page. The reader should see the same values move through:

1. raw observation;
2. ordinary or expected state;
3. difference;
4. natural variation or uncertainty;
5. score or algorithm output;
6. decision rule;
7. correct interpretation;
8. one possible failure.

Do not replace the spine example with a new example when introducing notation.

## Naming abstractions

Introduce names only after the underlying operation is visible.

Good order:

1. “The result is 12 above the ordinary average.”
2. “Ordinary runs move by about 3.87.”
3. “The result is 12 ÷ 3.87 = 3.10 usual movements above average.”
4. “This standardized distance is called a z-score.”

Bad order:

1. Display `z = (G - Tγ) / √(Tγ(1-γ))`.
2. Add four sliders for `G`, `T`, `γ`, and the threshold.
3. Expect the learner to discover the meaning.

## Interaction ladder

Progress through four levels:

1. **Repeat:** rerun a familiar random process and observe variation.
2. **Reveal:** expose one calculation or causal step at a time.
3. **Compare:** change one quantity while all others stay fixed.
4. **Explore:** offer free controls only after the guided experiments.

Each control needs adjacent “Try this” and “What to watch” text. Update the interpretation after the learner acts.

## Visual language

- Keep colors semantically stable.
- Reserve warning colors for decisions, errors, or boundaries.
- Label marks directly when possible.
- Explain how a distribution, chart, or diagram was produced before asking the learner to read it.
- Show averages as averages, not exact-looking guaranteed outcomes.
- Keep prose large and readable. Do not let ornamental headings dominate the explanation.
- Prefer code-native visuals for interactive mechanisms.

## Plain language ladder

Use three layers:

1. everyday explanation in the main path;
2. formal name in parentheses after the idea is clear;
3. symbolic formula or implementation in a disclosure or appendix.

Examples:

- “ordinary explanation” before “null hypothesis”;
- “cutoff” before “decision threshold”;
- “ordinary sample marked as a signal” before “false positive”;
- “usual amount of movement” before “standard deviation.”

## Common failure patterns

Reject or revise a page when it:

- opens with a dashboard rather than a question;
- asks the learner to classify something before defining the evidence;
- displays a score before explaining its unit;
- introduces several symbols in one viewport;
- says “move the knobs” without a prescribed experiment;
- uses “more data” without naming what becomes easier to distinguish;
- presents a source label and detector decision as if they cannot disagree;
- treats a positive result as proof of a broader origin claim;
- interrupts the lesson with seeds, hashes, schemas, and file paths;
- uses metaphor where a literal operation would be clearer;
- adds interactivity that has no learning outcome.

## Recommended ending

End with:

1. the project-backed result;
2. the mapping from toy to real mechanism;
3. what was measured;
4. what remains untested;
5. optional math, history, code, and reproducibility details.
