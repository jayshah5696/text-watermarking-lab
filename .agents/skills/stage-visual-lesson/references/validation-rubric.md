# Lesson validation rubric

Do not deliver until every applicable critical check passes.

## Evidence

- Every measured value matches the canonical artifact.
- Every derived value can be reproduced from displayed or documented inputs.
- External factual claims cite primary or authoritative sources.
- Illustrative browser simulations are labeled as illustrations.
- The final claim matches the stage boundary.
- No future-stage capability is shown as implemented.

## Narrative

- The page states one learning question near the beginning.
- The detector, algorithm, or component is defined in everyday language.
- One example persists from observation through decision.
- Each formal term appears after its underlying idea.
- Every section answers why the learner needs it now.
- The toy maps explicitly back to the real system.
- The ending states both learned and not yet tested.

## Interaction

- Every control has a learner instruction.
- One main variable changes at a time during guided work.
- The page says what remains fixed.
- The page says what to watch.
- Feedback explains the observed change in a full sentence.
- Random examples visibly vary across reruns.
- Advanced controls appear after guided presets or inside a disclosure.
- A failure case, ambiguity, or tradeoff is shown.

## Novice comprehension

A reader should be able to answer from the page alone:

1. What problem is this stage trying to solve?
2. What does the checker or algorithm receive and return?
3. What is the baseline or ordinary case?
4. What does the main score mean as a sentence?
5. How is the decision cutoff different from the score?
6. What can cause a false alarm or missed signal?
7. Why does changing the guided variable matter?
8. How does the toy correspond to the real system?
9. What does a positive result establish?
10. What has not been tested yet?

If any answer requires jargon not defined on the page, revise the lesson.

## Browser QA

Test at least:

- desktop light mode around 1440 × 1000;
- mobile light mode around 390 × 844;
- desktop dark mode around 1200 × 900.

For each view:

- load without page or console errors;
- confirm document width does not exceed viewport width;
- test every button, slider, preset, disclosure, and progressive reveal;
- verify dynamic text and charts update;
- inspect text contrast, wrapping, labels, legends, and tap targets;
- capture a full-page screenshot.

## Context-free screenshot audit

Capture at least three mid-page sections and inspect them without relying on earlier commentary:

1. the spine example;
2. the main interactive experiment;
3. a result, distribution, or mapping section.

For each screenshot ask:

- Can a newcomer identify what is being shown?
- Are all visible symbols and labels explained nearby?
- Is there a clear action or reading order?
- Does the screenshot state the lesson, not merely display information?

## Delivery

- Open the final HTML for the user.
- Provide an absolute clickable path.
- State evidence sources checked.
- State viewport and interaction coverage.
- Name any unverified boundary.
