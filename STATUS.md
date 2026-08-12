# Project status

## Current stage

Stage 1 code implemented; evidence run pending.

## Implemented

- Local Git repository on `jay/lego-watermark-lab`.
- Python 3.12 project metadata and locked `uv` environment.
- Root `justfile` command surface and CPU-only CI contract.
- Ruff, Pyright, Pytest, and coverage configuration.
- Project README, MIT license, Codex instructions, claims ledger, and architecture decision.
- Start-here map to the canonical Obsidian research and implementation handoff.
- Biased-coin statistics, immutable result records, readable simulation, and independent verifier.
- Fixed Stage 1 configuration and pending-evidence blog note.

## Verified

- `uv sync --locked --all-groups` succeeds locally.
- `just check` passes locally without a model, dataset, cloud service, or GPU.
- No target GitHub remote exists.

## Not implemented

- Stage 1 selected summary and figures.
- Model/tokenizer integration.
- Dataset access or manifests.
- Modal or other hosted compute setup.
- Hosted detector or public playground.

No detector experiment has run.

## Approval required next

The clean-commit Stage 1 evidence run under the approved Stage 0–1 slice. Model, tokenizer,
dataset, cloud, GPU, GitHub remote, publishing, and public deployment remain separate gates.

## Known limitations

- Stage 1 code is not scientific evidence until the clean source commit is recorded in generated
  artifacts and those artifacts pass independent recomputation.
- The canonical research material currently lives outside this repository in the user's Obsidian vault.
- The future detector will detect only this project's deliberately embedded watermark profile, not arbitrary AI-generated text.
