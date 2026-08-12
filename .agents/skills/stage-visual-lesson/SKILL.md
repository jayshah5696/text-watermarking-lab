---
name: stage-visual-lesson
description: Build or revise novice-friendly, self-contained interactive HTML lessons for repository stages, algorithms, experiments, and technical concepts. Use for stage walkthroughs, visual explainers, interactive teaching pages, concept-first explanations, or polished pages that still feel confusing. Ground claims in project evidence, teach through one concrete example, use plain human prose, guide one-variable interactions, run independent reviewer subagents when available, and complete browser QA. Do not use for monitoring dashboards, slide decks, isolated diagrams, or ordinary documentation that does not need an interactive learning sequence.
---

# Stage Visual Lesson

Turn one project stage into a lesson that a curious newcomer can follow without prior statistical, machine-learning, or implementation knowledge.

## Use companion skills

Use `visual-explainer` to build the self-contained HTML and follow its visual and browser-QA rules. Use `humanizer` in its plain register for all learner-facing prose. Read both selected skill files completely before acting.

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

## Build the page

Create a responsive, self-contained HTML page with code-native visuals such as HTML/CSS, SVG, or canvas. Reuse existing project visual conventions only when they support comprehension.

Avoid required external assets. If remote fonts or optional libraries improve the page, preserve a readable offline fallback and report the dependency.

Give explanatory prose enough visual weight. A beautiful chart cannot replace the paragraph that tells a newcomer what the marks mean.

Keep main-path developer details collapsed. Include repository commands, artifact schemas, seeds, and source hashes only when the learner asks for reproducibility or opens a technical appendix.

Write the page to the user's requested path. In this repository, store stage lessons under `.agent/diagrams/` so the teaching artifact can be reviewed and committed with the stage. Use `.agent/diagrams/<project>-<stage>-lesson.html` when the user does not name a file.

## Validate the lesson

Read [validation-rubric.md](references/validation-rubric.md) and complete every applicable check.

At minimum:

1. verify all displayed measurements against project artifacts;
2. open the page in a browser;
3. test every control and progressive reveal;
4. capture and inspect desktop, mobile, and dark-mode views;
5. check for console errors and horizontal overflow;
6. inspect at least three mid-page screenshots without relying on prior sections;
7. confirm a novice can answer the rubric's comprehension questions from the page alone.

Iterate until the screenshots are understandable without the author explaining them aloud.

## Deliver

Open the final page and link it with an absolute path. Summarize the teaching spine, interactions, evidence checked, and browser coverage. State any unverified boundary. Do not commit or publish unless the user requested it.
