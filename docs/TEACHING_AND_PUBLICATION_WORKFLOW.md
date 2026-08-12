# Teaching and publication workflow

## Purpose

The final article is not a wrapper added after the experiments. Each stage must be designed as one
future article section with code and evidence behind it.

Before a stage locks its vocabulary, prompt, seed, configuration, trace schema, or figure shape,
write a short publication brief. The brief comes before implementation so the fixture records the
facts a reader will need and supports a clear visual explanation.

This is a design gate, not permission to run the stage. Repository authorization and external
model, dataset, cloud, GPU, remote, and publishing gates still apply.

## Publication brief required before implementation

Every later stage contract must answer these questions.

### Article role

- Which final article question does this stage answer?
- What should a reader be able to explain after this section?
- What single sentence is the narrow answer?
- Which earlier concept may be assumed, and which new terms must be defined here?

### Teaching spine

- What is the smallest real recorded example that shows the full causal chain?
- Which inputs remain fixed?
- Which one variable or operation changes?
- What exact values must be visible for a reader to reproduce the reasoning?
- What recorded case challenges the most likely mistaken interpretation?

The main path must include the worked calculation and the causal transitions. Do not defer a
reasoning step to a tooltip, closed disclosure, source code, or future section.

### Fixture selection

- Choose labels and prompts that are readable, distinct, short, and safe to publish.
- Choose enough candidates to expose the real mechanism without creating an unreadable visual.
- Keep IDs separate from reader-friendly labels so the explanation can use both.
- Record why a fixed fixture was selected before observing the final result.
- Do not search seeds, prompts, keys, or examples for an impressive outcome unless the search is a
  declared experiment with its own method and evidence.
- Keep surprising, inconvenient, or null outcomes when they are valid. They often provide the
  strongest limitation or failure panel.

Synthetic fixtures should isolate one mechanism. Model-backed fixtures should represent the
approved prompt set and sampling contract rather than imitate a handcrafted toy result.

### Visual plan

Define the visual before choosing the artifact schema.

- Name each required panel and its reader question.
- State which marks encode inputs, transformations, sampled outcomes, and checker results.
- Give every color a single meaning and pair it with text, shape, or pattern.
- Identify the three screenshots that must make sense without the page introduction.
- Write a draft caption and useful alt text for each publication figure.
- State the desktop and mobile comparison that must remain visually possible.

Prefer process arrows, aligned before-and-after views, probability rulers, and state transitions
when they explain causality. Decorative cards, repeated metrics, or generated images must not
replace evidence-bearing diagrams. Use raster illustration only when it adds meaning that HTML,
SVG, plots, or annotated traces cannot express more accurately.

### Evidence contract

The stage artifact must contain every value required by the planned explanation and figures.
At minimum, record:

- inputs and stable identifiers;
- the state before the intervention;
- the exact intervention;
- the state after it;
- randomness or sampling draws;
- the selected output;
- checker or scoring replay;
- source commit and configuration fingerprint; and
- claim type for each substantive conclusion: `external`, `derived`, `measured`, `limitation`, or
  `opinion`.

Published visuals must be generated from or checked against these artifacts. Never copy numbers
into a figure from memory.

### Blog handoff

Before the stage closes, its blog note must provide:

1. the article subsection it supports;
2. expected result written before the run;
3. observed result with artifact paths and source commit;
4. one complete worked example;
5. one failure, counterexample, or important limitation;
6. figure inventory with captions and alt text;
7. allowed claims and prohibited shortcuts; and
8. the transition sentence into the next article section.

The interactive lesson and blog note share one teaching spine. The lesson may add guided controls,
but it must not tell a different causal story from the article.

## Review before locking the fixture

Run three independent read-only reviews against the publication brief and proposed fixture:

- novice pedagogy: prerequisites, beat order, and missing causal steps;
- language: undefined terms, implied reasoning, and claim boundaries; and
- visual interaction: whether each planned panel explains a relationship rather than decorating
  it.

Resolve the reviews before implementation. After evidence exists, changing a locked fixture
requires a scientific or engineering reason, not a desire for a cleaner screenshot.

## Exit gate

A stage is ready to close only when:

- its code and independent verifier pass;
- its selected artifact contains every planned publication value;
- a novice can follow the spine example without filling a reasoning gap;
- the failure case is visible near the claim it limits;
- the three context-free screenshot tests pass on desktop, mobile, and dark mode where applicable;
- the blog handoff links claims to evidence; and
- the stage does not imply results or capabilities reserved for later work.

The final article should then be assembled from these reviewed handoffs and committed evidence,
not reconstructed from memory at the end.
