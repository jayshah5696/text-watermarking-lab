# Article opening review

## Scope

This pass changed the opening through the Stage 1 code and measured result. Later sections remain available for subsequent visual and prose passes.

## Narrative

The opening no longer starts with project dates, Article 50, a detector taxonomy, or Anthropic's implementation. Its order is now:

1. image and video slack compared with discrete text;
2. the question of where a copied-text mark can live;
3. next-token choice as the hiding place;
4. two weighted coins;
5. one fixed `32/80` calculation;
6. ordinary batch variation;
7. z as a named distance and cutoff as a separate rule;
8. length and overlapping score hills;
9. coin-to-token mapping;
10. actual Stage 1 scorer, simulator, loop, and committed results;
11. transition to the keyed vocabulary.

Anthropic's August 14 SynthID-Text statement now first appears near the end in the method-comparison section. August 11 no longer appears in the reader-facing narrative.

## Visual continuity

The opening retains the same objects instead of replacing them with unrelated charts:

- blue always means the baseline coin;
- orange always means the nudged coin;
- green always marks a counted hit or favored token;
- `32`, `80`, `20`, `12`, `3.87`, and `3.10` persist through the worked example;
- the coin's heads event maps directly to favored-token membership.

The opening now contains seven visual blocks: media slack, weighted flips, worked batch, length, distributions, coin-to-token mapping, and committed results.

## Code fidelity

The article shows abridged but source-faithful excerpts of:

- `green_hit_z_score` from `src/watermark_lab/stats.py`;
- `simulate_hit_counts` from the same module;
- the length/condition simulation and scoring loop from `labs/01_biased_coin.py`.

The exact implementation retains validation and record-writing code outside the excerpts. The article links the project measurement through the Stage 1 source note and keeps all ten committed summary rows in the embedded evidence payload.

## Browser QA

Checked in Chrome:

- desktop dark at 1440 by 1000;
- mobile dark at 390 by 844;
- desktop light at 1200 by 900;
- all 16 opening controls;
- keyboard traversal;
- scripts disabled;
- JavaScript syntax;
- console and page errors;
- horizontal overflow.

Results: zero console errors and zero horizontal overflow. Scripts-off mode retained the prose, code, table, citations, and measured conclusion.

Context-free screenshots inspected for:

- media comparison;
- weighted coins;
- `32/80` worked calculation;
- score hills on desktop and mobile;
- coin-to-token mapping;
- committed Stage 1 curve.

The initial mobile z ruler was too small because a desktop-width object was scaled down. It now uses the mobile width directly and remains legible without horizontal scrolling.

## Verification

- `just verify-final-article`: 8 passed.
- `just check`: 473 passed; Ruff and Pyright clean.
- No model, dataset, GPU, cloud, remote, or publication action was used.
