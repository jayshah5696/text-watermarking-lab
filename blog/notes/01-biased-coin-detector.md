# Biased-coin detector

## Question

Why does a small statistical bias become easier to detect as the number of eligible trials
increases?

## Intuition before code

Under an independent null, random variation grows with the square root of the number of trials,
while a persistent excess grows in direct proportion to the number of trials.

## Derivation

For `T` independent trials with null hit probability `gamma`, the expected hit count is
`T * gamma` and its variance is `T * gamma * (1 - gamma)`. The lab standardizes observed hits
with `z = (G - T * gamma) / sqrt(T * gamma * (1 - gamma))` and also calculates an exact
binomial upper tail for fixed tests.

## The smallest implementation

`src/watermark_lab/stats.py` contains the formulas. `labs/01_biased_coin.py` keeps configuration,
simulation, scoring, aggregation, artifact writing, and plotting visible in execution order.

## Expected result before running

The null condition should stay centered near zero. The illustrative `p=0.40` condition should
move farther above the `z=3` threshold as sequence length grows.

## Observed result

Pending Stage 1 evidence run.

## Figure

Pending Stage 1 evidence run.

## What surprised us

Pending Stage 1 evidence run.

## What this establishes

Pending Stage 1 evidence run.

## What this does not establish

The biased condition is not an LLM measurement, and the ideal binomial null is not an empirical
false-positive calibration for real token histories. This lab does not detect arbitrary AI text
or reproduce Claude's private detector.

## Next Lego block

After separate approval, Stage 2 can make the bias deliberate by coloring a tiny toy vocabulary.
