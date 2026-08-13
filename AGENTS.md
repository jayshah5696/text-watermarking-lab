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

Stages 0–3 are implemented and published to the repository. Do not implement Stage 4 or later work
without a new explicit approval.

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
- Use `apply_patch` for focused file edits.
- Inspect the worktree before editing and preserve unrelated user changes.
- Run the proportionate checks required by the handoff and report what remains unverified.
- Do not manufacture future results or create placeholders for unimplemented model, dataset, attack, cloud, or web stages.

## Lesson design gate

These rules apply to every learner-facing HTML lesson, visual explainer, and article figure.

### Required skills and order

1. Use `.agents/skills/stage-visual-lesson/SKILL.md` before drafting the lesson.
2. Use the Humanizer skill in its plain register for every learner-facing sentence. Apply it after
   the causal structure is stable and again before delivery.
3. Complete the teaching contract, evidence ledger, and storyboard before editing HTML.
4. Run the three independent lesson reviews required by the stage visual lesson skill when agents
   are available. Resolve their shared findings before browser QA.

Do not mark these skills as used merely because their files were read. Their checks must change the
storyboard, copy, tests, or browser review when they find a problem.

### One continuous teaching spine

- Use one question, one recorded example, and one set of visual objects from input through result.
- Keep the prompt, token, score, or sample visible while its state changes. Do not replace it with a
  new card and expect the learner to remember the old state.
- Give each visual property one meaning. A bar must keep the same unit and scale while it moves.
- Use one shared axis for a before-and-after comparison. Keep rows in the same order.
- When histories or inputs stop matching, draw the boundary at that exact step. Do not continue a
  matched causal comparison after the boundary.
- Reuse the generated token objects when teaching copied-text checking. The learner should see the
  same objects become checker evidence.
- Move quality discussion, outside research, runtime details, and future work after the local causal
  loop unless one of them is needed to understand the next step.

Use 3Blue1Brown as a visual standard: preserve object identity, animate only the changed property,
label marks directly, and let one transformation happen per beat. Use Andrej Karpathy as a teaching
standard: start from the smallest inspectable program, expose its state and numbers, trace one real
example by hand, and introduce formal language after the operation is visible. Apply these
principles without copying either person's voice or artwork.

### Evidence before visual ambition

- Design the desired chart before locking the trace schema. The artifact must record every value
  needed by the chart.
- Never invent missing candidates, probabilities, or intermediate values to complete a visual.
- If the requested visual needs evidence that the artifact does not contain, stop and ask before
  regenerating a model-backed artifact. Offer a measured alternative that uses the current record.
- Use probability bars only for values from one comparable distribution or from a clearly aligned
  controlled pair. Use a different visual unit after the model histories differ.
- Put the evidence type beside the claim: `measured`, `derived`, `external`, or `opinion`.

### Browser interaction proof

- Start every interaction test from a clean reload.
- After every click, assert the new heading, visible and hidden panels, item counts, numerical text,
  and button state. A successful click command is not proof that the lesson advanced.
- Inspect a screenshot of every progressive state, not only the initial and final pages.
- Add `[hidden] { display: none !important; }` to self-contained lessons when component CSS uses
  `display: grid` or `display: flex`. Confirm that future panels do not leak into earlier states.
- Test Back, Replay, comparison controls, disclosures, keyboard focus, reduced motion, and the
  script-off fallback.
- Test desktop light at about 1440 by 1000, mobile light at about 390 by 844, and desktop dark at
  about 1200 by 900. Check console errors and horizontal overflow in each view.
- A context-free screenshot must state what is fixed, what changed, the unit or scale, and the plain
  interpretation. If the author must explain the screenshot aloud, revise it.

### Learner language gate

- Use short, concrete sentences. Define a term before it appears in a chart, button, or result.
- Remove filler, repeated summaries, dramatic headings, metaphors, and vague teaching phrases such
  as `try this`, `design space`, or `downstream of the fork`.
- Name the actual operation: `starting at token 3, the runs use different histories`.
- Keep one idea per sentence when the concept is new. Use exact numbers instead of vague claims.
- Add learner-copy tests for project-specific forbidden phrases and required claim boundaries.
- Read the final main path aloud. If the prose sounds like a report, dashboard, or generic AI
  explanation, rewrite it before browser QA.

### Lesson exit gate

Passing unit tests is necessary but not sufficient. A lesson is complete only when:

- the artifact, storyboard, HTML, and tests tell the same causal story;
- the same spine example reaches the final interpretation;
- every visual comparison keeps valid units and controlled inputs;
- every interaction state has been clicked, asserted, and visually inspected;
- Humanizer plain-register review passes; and
- the final page states what was measured, what was not measured, and what requires a later stage.

## Stop conditions

Stop and ask when a proposed action crosses an authorization gate, changes a locked decision, creates cloud cost, needs a secret, or would materially expand the current stage.
