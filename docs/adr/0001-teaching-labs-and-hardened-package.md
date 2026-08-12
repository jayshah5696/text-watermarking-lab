# ADR 0001: Teaching labs and a hardened package

- **Status:** Accepted
- **Date:** 2026-08-11

## Decision

Preserve linear teaching programs in `labs/` and place tested, reusable mathematics and result
schemas in `src/watermark_lab/`.

## Reason

Readers should see each algorithm in execution order, while experiments still require reusable,
validated contracts.

## Consequence

A small amount of orchestration may be duplicated. Formulas and result schemas must not be
duplicated.

## Rejected alternatives

- Notebook-only implementation, because hidden state weakens reproducibility.
- Framework-first abstraction, because it obscures the first learning blocks.
- Copying a third-party watermark repository before deriving and testing the detector.
