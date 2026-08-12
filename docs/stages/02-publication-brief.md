# Stage 2 publication brief

## Article role

- Final article section: “The secret green-list coin.”
- Reader question: How can a key raise some next-token chances without forcing one result?
- Reader outcome: explain the complete chain from recent token IDs through temporary green
  membership, a +2 logit boost, shared normalization, one draw, and checker replay.
- Narrow answer: the context and public teaching key select five of 20 candidates; adding 2 to
  those five logits changes every normalized probability, but all 20 candidates remain possible.

## Narrative and evidence fixtures

The final section needs two visibly different layers.

- **Narrative illustration:** `Jack went up the ___` with ordinary possible endings. This is
  hand-authored and exists only to show where the watermark operation sits in a language system.
  Its in-figure label must say `Concept illustration · not model output or run data`.
- **Recorded mechanism fixture:** the locked 20-option Stage 2 trace. This supplies every numeric
  claim and remains unchanged. IDs are the primary public labels; the synthetic word tags appear
  only in reproduction or audit material.

The bridge sentence is: “The sentence shows where the operation would sit in real text generation.
The recorded experiment below measures only the operation itself.”

## Why the locked fixture remains suitable

The evenly spaced raw logits isolate keyed membership and logit-bias mechanics. The vocabulary
labels are artifact metadata, not a sentence. Their semantic content must not be interpreted as
generated prose or model behavior.

The recorded trace already supplies the final article's necessary contrast:

- Position 4 is the teaching spine. With context `[15, 0, 1, 1]` and draw
  `0.307310772959`, the no-boost comparison selects ID 1, while the +2 sampler selects green ID 2.
- Position 2 is the failure panel. The green candidates hold about 72.6% of probability, yet draw
  `0.112284` selects red ID 1.
- All four positions show the rolling context and allow the checker to reproduce the pattern
  green, red, red, green.

Changing labels, seed, key, or logits now only to improve the story would invalidate the selected
artifact and risk outcome-driven fixture selection. Keep the locked trace. If a future scientific
question requires another fixture, specify that question and selection method before running it.

## Required article figures

### Figure 0: where the watermark acts

- Panels: `Jack went up the ___`; several plausible next words; a temporary keyed subset; model
  scores entering before the boost; sampling after the boost.
- Visible label: `Hand-authored concept illustration · not model output or run data`.
- Caption draft: “A generation-time watermark acts after a model has scored possible next tokens
  and before one token is sampled. Stage 2 does not run that model; the sentence only locates the
  operation.”
- Alt text draft: “The unfinished sentence Jack went up the blank sits beside familiar endings
  such as hill, road, stairs, and path. A watermark layer marks a temporary subset for a score
  boost before sampling.”

### Figure A: one keyed token choice

- Panels: recent context and key; digest ranking with rank-five cutoff; selected score additions;
  shared softmax calculation; aligned cumulative probability rulers; fixed draw; selected token.
- Caption draft: “At recorded position 4, the public teaching key and recent IDs select five
  temporary green candidates. Adding 2 to their logits expands ID 2's cumulative interval across
  the same draw, changing the sampled option from ID 1 in the no-boost comparison to ID 2.”
- Alt text draft: “A seven-step diagram follows context IDs 15, 0, 1, 1 through a SHA-256 ranking,
  five green IDs, a plus-two score boost, and two aligned probability rulers. An orange draw at
  0.3073 falls in ID 1 before the boost and ID 2 after it.”

### Figure B: preference is not a guarantee

- Panels: position 2 context and green set; green mass 72.6% versus red mass 27.4%; cumulative
  ruler; draw 0.112284 inside red ID 1's interval.
- Caption draft: “The +2 rule raises total green probability without forcing a green option. At
  position 2, the recorded draw still lands in red ID 1.”
- Alt text draft: “A probability mass chart gives green candidates 72.6 percent and red candidates
  27.4 percent. A cumulative ruler places draw 0.112284 inside red ID 1.”

### Figure C: generation versus checking

- Panels: four rolling contexts; observed IDs `[0, 1, 1, 2]`; rebuilt green set at each position;
  hit pattern green, red, red, green; `G=2`, `T=4`; running z-score 1.1547 with no threshold.
- Caption draft: “The checker needs the public key, selection rule, initial context, and observed
  IDs. It rebuilds membership without the generator's logits, probabilities, or random draws.”
- Alt text draft: “Four rows show the context window shifting through observed tokens 0, 1, 1,
  and 2. The checker marks the first and fourth tokens green and ends with two hits in four checked
  positions.”

## Values required from evidence

The committed `artifacts/lab-02/trace.json` contains:

- initial context, per-position context, public key, `gamma`, and `delta`;
- raw and adjusted logits;
- original and boosted probabilities;
- each recorded draw and its no-boost comparison token;
- each actual +2 token and green membership;
- running `G`, `T`, and z-score; and
- source commit and configuration fingerprint.

The digest prefixes in Figure A are derived by replaying the documented selector for the recorded
position 4 context. Published figure values must continue to match `just verify-lab-02`.

## Allowed claims

- The locked toy rule selects five of 20 IDs per context.
- Adding 2 multiplies one green token's odds relative to one unchanged red token by
  `exp(2) ≈ 7.389` before shared normalization.
- In recorded position 4, the same draw selects ID 1 without the boost and ID 2 after it.
- The checker reconstructs two green hits among four observed positions for this trace.

## Claims to avoid

- The vocabulary represents language-model output or natural language quality.
- The toy SHA-256 selector is compatible with an upstream KGW implementation.
- Two hits in four positions estimate detection accuracy or produce a detection verdict.
- A result proves AI authorship, Claude behavior, secrecy, or production security.

## Transition to Stage 3

Stage 2 supplies every operation except the source of the logits and token IDs. A separately
approved Stage 3 would replace the synthetic scores and labels with one real model and tokenizer
while preserving the visible location of the intervention between model logits and sampling.
