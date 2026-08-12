# Repository instructions for Codex

## Read before acting

1. Read `docs/START_HERE.md`.
2. Read the canonical Stage 0–1 handoff named there in full.
3. Read `STATUS.md` and preserve its authorization boundary.
4. Before implementing a later stage, read the matching canonical roadmap and algorithm notes.

Do not treat a planning document as permission to execute it. If the user's current request is review, planning, or setup-only, remain read-only except for the explicitly requested repository metadata.

## Project identity

- This is an educational, reproducible lab for deliberate generation-time text watermarks.
- The public teaching implementation is a KGW-style analogue. Never claim that it reproduces Anthropic's private Claude implementation.
- A positive result means “consistent with this configured watermark and key,” not “AI-written.”
- Build in Lego blocks: one learning question, one readable executable, one falsifiable artifact, and one blog note per stage.

## Locked engineering choices

- Use Python `>=3.12,<3.13` and `uv` for Python installation and execution.
- Use a root `justfile` as the public command surface. Do not add a Makefile.
- Keep linear teaching programs in `labs/`; extract stable typed code into `src/watermark_lab/` only when the handoff calls for it.
- Use conventional commits and keep commits stage-scoped.
- Prefer fixed-vector tests before optimization or framework integration.
- Keep secrets out of the repository.
- Do not edit raw run data by hand. Regenerate compact published artifacts only through documented commands.
- Label substantive claims as `external`, `derived`, `measured`, or `opinion`.

## Authorization gates

The repository is currently authorized only for bootstrap metadata and an idle Codex session. Do not implement Stage 0 or Stage 1 until the user explicitly approves implementation.

Separate approval is always required before any of the following:

- downloading a model, tokenizer, or dataset;
- installing or authenticating Modal;
- creating Modal secrets, Images, Volumes, Apps, Functions, endpoints, or GPU jobs;
- using a local or remote GPU;
- creating or changing a GitHub remote or repository visibility;
- opening a pull request, merging, publishing a package, or publishing the article.

Stages 0–1 must not import Transformers, Torch, Datasets, Modal, MLX, or any model SDK.

## Working method after approval

- Implement only the approved stage and its exit gate.
- Start from the exact contracts in the canonical handoff; do not silently change statistics, schemas, dependencies, commands, or artifact paths.
- Use `apply_patch` for focused file edits.
- Inspect the worktree before editing and preserve unrelated user changes.
- Run the proportionate checks required by the handoff and report what remains unverified.
- Do not manufacture future results or create placeholders for unimplemented model, dataset, attack, cloud, or web stages.

## Stop conditions

Stop and ask when a proposed action crosses an authorization gate, changes a locked decision, creates cloud cost, needs a secret, or would materially expand the current stage.
