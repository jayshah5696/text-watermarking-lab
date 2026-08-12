# Project status

## Current stage

Stages 0–2 complete locally on `jay/lab-02-toy-vocabulary`; awaiting user review.

## Implemented

- Local Git repository with Stage 2 work on `jay/lab-02-toy-vocabulary`.
- Python 3.12 project metadata and locked `uv` environment.
- Root `justfile` command surface and CPU-only CI contract.
- Ruff, Pyright, Pytest, and coverage configuration.
- Project README, MIT license, Codex instructions, claims ledger, and architecture decision.
- Start-here map to the canonical Obsidian research and implementation handoff.
- Biased-coin statistics, immutable result records, readable simulation, and independent verifier.
- Fixed Stage 1 configuration, selected summary, PNG/SVG figure, and evidence-backed blog note.
- Locked Stage 2 toy-vocabulary contract with a separate SHA-256 teaching selector.
- Typed green-set selection, logit bias, stable softmax, visible sampling, and detector replay.
- Deterministic JSON and annotated Markdown trace with an independent verifier.
- Evidence-grounded interactive Stage 2 lesson with guided probability, failure, and replay views.

## Verified

- `uv sync --locked --all-groups` succeeds locally.
- `just check` passes locally with 75 CPU-only tests.
- `just test-cov` passes with 99.38% branch-aware coverage for `stats.py` and `records.py`.
- `just lab-01` generated 100,000 raw simulation rows from source commit
  `e99e9e5f9b8bc426d1cc4e13f874854f8c303475` using config SHA-256
  `bb514264d259086929ef86d15e81fb2f44dfa6d5d1fa0f2b1d65586090ff6df9`.
- `just verify-lab-01` recomputes the selected summary exactly from ignored raw rows and passes.
- Selected evidence is in `artifacts/lab-01/summary.json`,
  `artifacts/lab-01/detection_by_length.png`, and
  `artifacts/lab-01/detection_by_length.svg`.
- The PNG is 1920 by 928 pixels; the SVG omits creation-date metadata.
- No target GitHub remote exists.
- `just check` passes locally with 179 CPU-only tests.
- `just test-cov` passes with 96.48% branch-aware package coverage.
- `just lab-02` generated a four-position trace from source commit
  `f7a1690d28cfb48fc825017891b5d3e82eebdd07` using config SHA-256
  `a342b4d1d347587098763e8f2ff6aa75dd86cbb538dc78200963a631b2a0defa`.
- `just verify-lab-02` recomputes the trace and annotated table exactly and passes.
- Selected Stage 2 evidence is in `artifacts/lab-02/trace.json` and
  `artifacts/lab-02/annotated_trace.md`.
- The interactive lesson passed desktop light, mobile light, and desktop dark browser checks.
  Every control and disclosure was exercised with no console errors or horizontal overflow.

## Not implemented

- Model/tokenizer integration.
- Dataset access or manifests.
- Modal or other hosted compute setup.
- Hosted detector or public playground.

No model- or tokenizer-backed detector experiment has run.

## Approval required next

Stage 3 manual generation-loop planning or implementation. Any model or tokenizer access,
including a download, requires separate explicit approval. Dataset, cloud, GPU, GitHub remote,
publishing, and public deployment remain separate gates.

## Known limitations

- The simulation assumes independent Bernoulli trials; it is not an empirical LLM calibration.
- The `p=0.40` condition is pedagogical and is not derived from an LLM logit bias.
- The selected artifact records local macOS/Python provenance; CI has not run because no GitHub
  remote exists.
- The canonical research material currently lives outside this repository in the user's Obsidian vault.
- The future detector will detect only this project's deliberately embedded watermark profile, not arbitrary AI-generated text.
- The Stage 2 selector is a toy SHA-256 rule. It is not compatible with an upstream KGW
  implementation and is not a production pseudorandom function or key-management design.
- Four generated positions demonstrate mechanics. They do not measure detection rates, text
  quality, or model behavior.
