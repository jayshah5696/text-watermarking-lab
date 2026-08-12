# Independent reviewer prompts

Use these prompts as task bodies. Replace bracketed fields with raw task context. Keep reviewers read-only.

## Reviewer 1: prerequisite order

> Review the supplied stage sources as an introductory teacher. Do not edit files. Identify the exact learning question, the smallest example that contains the mechanism, and every prerequisite the current explanation assumes. Propose a concept order in which each idea is introduced only after its prerequisites. For each beat, state what the learner knows before it, what is introduced, and one concrete worked sentence or number. Flag any formula, chart, or control that appears too early.
>
> Audience: [audience]
> Stage contract: [path]
> Evidence artifacts: [paths]
> Existing page or screenshots: [paths, if any]

Required output:

1. Main diagnosis.
2. Recommended beat order.
3. One spine example.
4. Items to move to an appendix.
5. Screenshot-specific fixes when screenshots exist.

## Reviewer 2: novice language

> Review the supplied material as a curious reader with no specialist vocabulary. Do not edit files. List every term, symbol, label, or phrase that appears before it is explained. Rewrite each in everyday language. Pay special attention to chart legends, result cards, buttons, formulas, abbreviations, and words that have a different everyday meaning. Check whether expected values look guaranteed and whether a positive result is stated too broadly.
>
> Audience: [audience]
> Stage contract: [path]
> Existing page, draft, or screenshots: [paths]

Required output:

1. Five most harmful assumptions.
2. Undefined-term table with plain replacements.
3. Exact replacement copy for confusing result cards.
4. Claims that need narrower wording.
5. Language patterns to remove.

## Reviewer 3: narrative and interaction

> Review the supplied material as an interaction designer for learning. Do not edit files. Determine whether the page has one coherent story or behaves like a dashboard. For every interaction, say what the learner is instructed to do, what stays fixed, what changes, what they should watch, and what they learn. Recommend removing or hiding controls that do not teach a specific idea. Propose a prediction, reveal, or failure case where it would strengthen understanding.
>
> Audience: [audience]
> Teaching contract: [path or text]
> Existing page or screenshots: [paths, if any]

Required output:

1. Narrative spine.
2. Interaction sequence.
3. Controls to keep, guide, hide, or remove.
4. Missing feedback after each action.
5. Three screenshot tests a newcomer should pass.

## Synthesis rule

Compare the three reports. Treat repeated findings as high-confidence design problems. Resolve disagreements using the teaching contract and repository evidence. Do not combine every suggestion; preserve one story and one spine example.
