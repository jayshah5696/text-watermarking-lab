# Color a toy vocabulary

## Article handoff

This note supports the final article section “The secret green-list coin.” The publication brief
in `docs/stages/02-publication-brief.md` defines the three required figures, their captions and alt
text, the position 4 teaching spine, the position 2 failure panel, and the claims this trace can
support.

## Question

How can a key change the chance of picking a token without forcing one fixed output?

## Intuition before code

The sampler starts with 20 possible token IDs. Each ID already has a score called a logit. A
higher logit gives that token a larger chance after the scores are normalized.

The toy selector uses the public development key and the four most recent token IDs to choose
five green IDs. It adds 2.0 to those five logits. The other 15 logits stay unchanged. The sampler
still draws from all 20 choices, so a red token can still win.

## The smallest implementation

The selector hashes one exact ASCII string for every candidate ID. It sorts the SHA-256 results
and colors the five lowest IDs green. This rule gives us stable vectors that tests can freeze.

The rule belongs only to this teaching stage. Later model work must use a pinned upstream
implementation instead of treating this selector as KGW compatibility.

## Expected result before running

Adding 2.0 to a green logit should multiply its odds against an unchanged red logit by
`exp(2)`, about 7.389, before normalization. It should raise green probability without making a
green sample certain.

Changing the context should also change the green set. A detector with the same key should be
able to rebuild each set from the generated history.

## Observed result

The trace generated token IDs `[0, 1, 1, 2]`. At each of those four generated contexts, reusing
the same draw without the boost would have selected `[0, 0, 0, 1]`. These are four one-step
comparisons. They are not a separately generated no-boost sequence.

The sampled token was green at positions 1 and 4. Two of the four toy choices therefore belonged
to their step's boosted set. Under the 25% toy expectation, that gives a running z-score of
about 1.155. Stage 2 defines no threshold, so this is not a detection decision and does not
estimate a detection rate.

## Follow one position

At position 4, the recent context was `[15, 0, 1, 1]`. The toy rule selected IDs
`[2, 5, 6, 10, 11]` as green. Token 2 started with logit 1.5. The bias raised it to 3.5, and its
probability rose from about 0.124 to 0.319 after normalization.

The recorded draw was about 0.3073. The unadjusted distribution mapped that draw to token 1. The
adjusted distribution mapped the same draw to token 2. The detector rebuilt the green set from
the context and counted token 2 as a hit.

## What surprised us

In this four-step trace, the boost changed three one-step comparison choices. Two of the
resulting choices were still outside the boosted set. Raising green odds changes the full list
of probabilities. It does not force every draw into the green set.

## What this establishes

The trace shows the complete Stage 2 toy mechanism. A context and public key select five IDs. The sampler
raises only those logits, normalizes all 20 choices, and records a draw. The detector can replay
the same context rule and count the chosen token.

## What this does not establish

The lab contains no tokenizer or language model. It does not measure language quality, false
positive rates, detector power, or model behavior. Its public key and SHA-256 rule provide
reproducibility for teaching. They do not provide production security.

## Next stage

Stage 3 would place the same conceptual step between real model logits and token sampling. That
stage needs separate approval because it introduces a model and tokenizer. Its prompt fixture,
paired trace, visual diagram, and blog evidence should be designed together before any prompt,
seed, model revision, or trace schema is locked.
