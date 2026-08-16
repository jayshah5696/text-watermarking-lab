---
name: stage-visual-lesson
description: Build or revise novice-friendly, self-contained interactive HTML lessons for repository stages, algorithms, experiments, and technical concepts. Use for stage walkthroughs, visual explainers, interactive teaching pages, concept-first explanations, or polished pages that still feel confusing. Ground claims in project evidence, teach through one concrete example, use plain human prose, guide one-variable interactions, run independent reviewer subagents when available, and complete browser QA. Do not use for monitoring dashboards, slide decks, isolated diagrams, or ordinary documentation that does not need an interactive learning sequence.
---

# Stage Visual Lesson

Turn one project stage into a lesson that a curious newcomer can follow without prior statistical, machine-learning, or implementation knowledge.

## Use companion skills

Use `visual-explainer` for the standalone HTML shell, black technical-document visual system, responsive behavior, SVG/diagram patterns, Mermaid reference, and browser-QA rules. Use `humanizer` in its plain register for all learner-facing prose. Read both selected skill files completely before acting.

This skill overrides `visual-explainer` where they differ on teaching sequence, evidence claims, novice comprehension, repository paths, and project authorization boundaries. A lesson may be less dense than a general technical document when explanation needs more room.

If either skill is unavailable, continue with the equivalent rules in this skill and state the fallback briefly.

For an audit, critique, or storyboard-only request, apply the companion skills' design and language rules but remain read-only. Skip their build, open, and delivery actions when those actions would exceed the request.

## Preserve project boundaries

1. Read the repository instructions, status, stage contract, implementation notes, and existing artifacts before changing anything.
2. Treat plans as context, not authorization. Do not run experiments, download dependencies, cross cloud or publishing gates, or alter locked parameters without approval.
3. Prefer existing measured artifacts. Never invent future results or present an illustrative browser simulation as a repository measurement.
4. Label a mapping to a later stage as a preview when that mechanism is not implemented yet.
5. Preserve the project's claim language. Keep narrow statements narrow.

## Build the teaching contract

Read [teaching-contract.md](references/teaching-contract.md) and complete it from repository evidence before drafting HTML.

Choose exactly one spine question and one spine example. The example must be small enough to calculate or trace by hand while still containing the stage's full mechanism.

If the stage question or intended learner cannot be inferred safely, ask one focused question. Otherwise proceed with a stated assumption.

## Create an evidence ledger

Record the source path for every measured number, fixed parameter, algorithm rule, and limitation used in the page. Label substantive claims using the repository's claim convention when one exists. Otherwise use:

- `measured`: produced by a checked project artifact;
- `derived`: calculated from documented inputs;
- `external`: supported by a cited primary source;
- `opinion`: an explicitly framed teaching or design judgment.

Cross-check every chart value and worked calculation against this ledger before delivery.

When a configured limit differs from an observed value, display both. Typical examples are a token
cap versus achieved length, requested rows versus completed rows, and a cutoff versus the measured
score. Never draw a configured maximum as if it were measured output.

For evidence-bearing token colors, use selected artifact fields. Record and preserve token position,
ID, decoded piece, eligibility, and checker result. Reconcile displayed token states with the
published aggregate count. In this project, green means keyed membership only. It does not mean
truth, quality, authorship, or model origin.

## Run three independent reviews

For a new substantial lesson or a confusing existing lesson, spawn three read-only reviewer subagents in parallel when subagents are available. Read [reviewer-prompts.md](references/reviewer-prompts.md) and assign:

1. prerequisite and pedagogy order;
2. novice language and undefined jargon;
3. narrative and interaction design.

Give reviewers raw sources: the stage contract, relevant artifact, current HTML or screenshots, and intended audience. Do not give them the desired answer or another reviewer's conclusions. Ask them not to edit files.

Synthesize areas of agreement. Do not paste three disconnected reviews into the page.

If capacity prevents all three reviews, continue with the completed reviews and record the missing review as a validation boundary. Do not block the lesson solely on subagent availability.

## Storyboard before HTML

Read [lesson-pattern.md](references/lesson-pattern.md). Write a short beat-by-beat storyboard before coding. Make sure it works as plain text.

Use this default progression, adapting it to the stage:

1. state the narrow real-world goal;
2. define the main component in everyday language;
3. replace the full system with the smallest faithful toy;
4. let the learner predict or observe the toy;
5. follow one complete worked example;
6. show natural variation, ambiguity, or failure;
7. name the formal concept after it is understood;
8. introduce the decision rule or algorithm;
9. change one variable at a time;
10. repeat to reveal a distribution or pattern when useful;
11. map every toy component back to the real system;
12. show repository-backed results;
13. finish with limits and an optional technical appendix.

Do not start HTML until each beat answers “why does the learner need this now?”

## Write for a newcomer

- Define a term before showing it in a result, chart, button, or formula.
- Show concrete numbers before symbolic notation.
- Convert every important score into a complete sentence.
- Use plain labels first. Add the formal term afterward in parentheses when it helps.
- Explain expected values as averages across repetitions, never promises for one run.
- Keep one unfamiliar idea per visual block.
- Prefer literal headings over atmospheric slogans.
- Keep technical lineage and implementation details in an optional appendix until they help the main story.
- Explain what a positive result means and what it cannot establish.

Avoid dashboard language such as “move the knobs,” “operating point,” or unexplained “flagged,” “null,” and variable names. Avoid decorative metaphors that hide the operation being taught.

## Design teaching interactions

Every interaction must include:

1. a concrete instruction;
2. what remains fixed;
3. what changes;
4. what the learner should watch;
5. a plain-language interpretation after the change.

Start with presets or a prescribed experiment. Hide free-form sliders and advanced parameters until the related concepts have been taught. Do not expose four unfamiliar controls at once.

Use interaction to reveal causality, randomness, tradeoffs, or failure cases. Do not add controls merely to make the page feel interactive.

Use animation for a deterministic process that would otherwise make the learner click through a
fixed sequence. Autoplay at a readable pace, include Pause and Replay, retain manual Previous and
Next controls for inspection, and pause after direct learner interaction. Disable autoplay when the
browser requests reduced motion.

Keep interaction when the learner predicts an outcome, changes one input, compares alternatives, or
inspects recorded cases. Do not require repeated clicks merely to advance a fixed explanation.

Keep one recorded example as the teaching spine. After the learner understands it, show the full
preregistered cohort through an overview chart and selectable rows. Do not replace the cohort with
only the strongest or cleanest example. A lesson does not require a positive result. Preserve null,
identical, adverse, and below-cutoff rows. If the cohort contains a positive result, show it beside
the full cohort and a relevant counterexample.

## Build the page

Create one responsive standalone HTML page with code-native visuals such as HTML/CSS, inline SVG, or canvas. Reuse existing project visual conventions only when they support comprehension.

Use the `visual-explainer` dark technical-document system by default: true black background, near-white primary text, dark-gray secondary surfaces, and a controlled blue/cyan/green/yellow/coral/violet palette. Keep colors semantically stable across the lesson and never rely on color alone. Use quiet tracks and dividers so labels, values, and the teaching sequence remain primary.

Avoid generic dashboard cards, oversized hero sections, gradients, glassmorphism, decorative backgrounds, and other visual ornament that does not teach. Preserve generous enough type size, spacing, and explanatory prose for novice comprehension.

Inline CSS and SVG by default. Avoid required external assets. If a remote font, image, or optional library materially improves the lesson, preserve a readable offline fallback, keep the page useful without JavaScript, and report the dependency. A single HTML file with remote dependencies is not offline self-contained.

Generate evidence-bearing browser payloads from the selected artifact when practical. If a
standalone page embeds measured values manually, add structural tests that compare every displayed
measurement with the canonical artifact. Checking only headline values is insufficient.

For Mermaid, follow the installed `visual-explainer` Mermaid reference for theme alignment and accessible zoom/pan/reset controls. Use Mermaid only when automatic graph layout improves the lesson; prefer inline SVG for bespoke pedagogical diagrams.

When the user requests alternatives, render real styled variants in the same page, label them `A`, `B`, `C`, and so on, and arrange them for direct comparison. Do not substitute prose descriptions for unrendered alternatives.

Give explanatory prose enough visual weight. A beautiful chart cannot replace the paragraph that tells a newcomer what the marks mean.

Keep main-path developer details collapsed. Include repository commands, artifact schemas, seeds, and source hashes only when the learner asks for reproducibility or opens a technical appendix.

Write the page to the user's requested path. In this repository, `.agent/diagrams/` is the committed lesson-artifact directory and intentionally overrides `visual-explainer`'s global `~/.agents/diagrams/` default. Use `.agent/diagrams/<project>-<stage>-lesson.html` when the user does not name a file.

## Validate the lesson

Read [validation-rubric.md](references/validation-rubric.md) and complete every applicable check.

At minimum:

1. verify all displayed measurements against project artifacts;
2. open the page in a browser when a GUI browser is available; otherwise run the available rendering/browser-QA equivalent and state that live visual inspection was not performed;
3. test every control and progressive reveal;
4. capture and inspect desktop, mobile, and dark-mode views;
5. check for console errors and horizontal overflow;
6. inspect at least three mid-page screenshots without relying on prior sections;
7. for autoplaying visuals, test Pause, Replay, manual stepping, loop restart, learner takeover,
   reduced-motion behavior, and static fallback;
8. confirm a novice can answer the rubric's comprehension questions from the page alone.

Iterate until the screenshots are understandable without the author explaining them aloud.

## Deliver

Open the final page when a GUI browser is available and link it with an absolute path. In a headless environment, report the rendered/browser-QA equivalent and any missing live inspection. Summarize the teaching spine, interactions, evidence checked, dependencies, and browser coverage. State any unverified boundary. Do not commit or publish unless the user requested it.
