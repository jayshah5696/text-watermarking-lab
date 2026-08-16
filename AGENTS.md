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

Stages 0–5 are implemented locally. Do not implement Stage 6 or later work without a new explicit
approval.

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
- Before locking a later stage's vocabulary, prompts, seeds, trace schema, or figure inputs, write
  its teaching and publication brief using `docs/TEACHING_AND_PUBLICATION_WORKFLOW.md`. Design the
  final explanation, failure case, visual panels, and required evidence before implementation.
- Before a model-backed teaching run, freeze its prompt set, seed rule, generation limits, stopping
  behavior, invocation and generation-call ceilings, resource type, cost ceiling, artifact paths,
  and stop rule. A failed or canceled invocation does not authorize a retry; ask again.
- Distinguish configured limits from measured outcomes. In particular, never present
  `max_new_tokens` as achieved length. Keep normal end-token behavior unless the approved contract
  makes fixed-length generation the experimental variable.
- Do not rerun, replace prompts, search seeds, or change stopping behavior to obtain a positive
  detector result or a cleaner visual. If search is the declared experiment, preregister its search
  space, selection rule, reporting contract, and budget.
- Use `apply_patch` for focused file edits.
- Inspect the worktree before editing and preserve unrelated user changes.
- Run the proportionate checks required by the handoff and report what remains unverified.
- Do not manufacture future results or create placeholders for unimplemented model, dataset, attack, cloud, or web stages.

## Learner-facing lessons

For interactive lessons, visual explainers, and article figures:

1. Use `.agents/skills/stage-visual-lesson/SKILL.md` and the Humanizer skill in its plain register.
2. Complete the teaching contract and storyboard before editing HTML.
3. Carry one recorded example from input through result. Preserve the identity, order, unit, and
   scale of visual objects while they change.
4. Stop matched comparisons when their inputs or histories stop matching.
5. Do not invent values that the recorded artifact does not contain. Ask before regenerating a
   model-backed artifact.
6. If a lesson colors individual tokens by checker state, require selected evidence for each token's
   position, ID, decoded piece, eligibility, and keyed result. Reconcile the token states exactly
   with the published aggregate count.
7. Follow the skill's reviewer, evidence, browser-QA, and delivery gates before calling the lesson
   complete.

Use 3Blue1Brown's object continuity and Andrej Karpathy's inspectable, first-principles teaching as
design standards. Do not copy their voice or artwork.

## Stop conditions

Stop and ask when a proposed action crosses an authorization gate, changes a locked decision, creates cloud cost, needs a secret, or would materially expand the current stage.
