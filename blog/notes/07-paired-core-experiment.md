# Compare one marked output with three controls

## Question

Does the configured mark separate from the paired Gemma control, the recorded natural-web
continuation, and the same marked text checked with another key? How does the evidence change as
more copied tokens become available?

## Expected result before running

The configured score increase should tend to raise correct-key z on marked output. That row should
tend to exceed its paired model control, its natural-web continuation, and its comparison-key replay
as copied text grows.

This was an expectation, not a gate. Every frozen row would remain in the result if a control scored
higher, another key overlapped, marked z stayed below three, or generation ended before 400 copied
tokens.

## Frozen experiment

Stage 6 froze 24 C4 `realnewslike` rows before generation. Stage 7 used exact source token IDs 0
through 49 as each shared prompt. Each prompt entered control and watermarked Gemma generation with
the same derived seed, sampler, and 400 generated-token safety cap. The marked call alone received
the configured watermark processor.

The run used `google/gemma-4-E2B-it` revision
`3e22461f65e89153144f8adb70e3b8c2cc9845a7`, BF16, Transformers 5.14.1, PyTorch 2.13.0, and one
Modal NVIDIA L4. It made exactly 48 generation calls in one invocation. No Secret, Volume, endpoint,
replacement prompt, seed search, retry, or end-token suppression was used.

## Observed result

All 24 pairs supported copied-token prefixes 40 and 80. Twenty-one supported 160, and 17 supported
200. No pair supported 400 copied tokens in both generated conditions. The 400 generated-token cap
was therefore never a 24-row, 400 copied-token result.

The correct-key marked score exceeded all three controls on average at every supported prefix. At
80 copied tokens, all 24 pairs remained matched:

- versus paired model control: mean z difference `1.8296`, 95 percent paired bootstrap interval
  `[1.3424, 2.3276]`;
- versus natural-web continuation: mean `1.7538`, interval `[1.3100, 2.1977]`;
- versus comparison-key replay: mean `2.0461`, interval `[1.6131, 2.4792]`.

At 200 copied tokens, 17 complete pairs remained. Mean differences were `2.5134` versus model
control, `2.6964` versus natural web, and `2.5423` versus the comparison key. Their paired bootstrap
intervals were `[1.9164, 3.1297]`, `[1.9452, 3.3512]`, and `[2.0704, 3.0045]`.

Strict cutoff counts also grew with the available prefix, but many marked rows remained below three.
At 40 tokens, one of 24 marked rows crossed. At 80, three of 24 crossed. At 160, five of 21 crossed.
At 200, four of 17 crossed. No paired model control or comparison-key row crossed at any supported
prefix. One natural-web row crossed at 200.

These are measured outcomes for one pinned experiment. They do not estimate production accuracy.

## One complete example

The fixed teaching row was paired-test selection rank `1000`. Stage 6 chose it before Stage 7 output
existed. Its source prefix ended:

```text
Both Pollitt's and Culver's ceremonial beginnings, although vastly different, were appropriate in
that they reflected the personal styles of each man. Wicomico County's government is working
exactly as it was intended - the person occupying the office
```

The control produced 198 copied tokens. The marked path produced 392, so their longest shared
configured prefix was 160.

At 160 copied tokens, the marked path had `G=58` green hits among `T=159` eligible checks. The
configured quarter-green average was `39.75`. Ordinary movement was:

```text
sqrt(159 x 0.25 x 0.75) = 5.4601
```

The recorded standardized distance was:

```text
z = (58 - 39.75) / 5.4601 = 3.3424
```

At the same prefix, model-control z was `1.3278`, natural-web z was `0.5952`, and comparison-key z
was `-1.9688`. The marked row crossed strict `z > 3`; the three controls did not. The narrow reading
is "consistent with this configured watermark and key."

## The inconvenient row

The predeclared rule selected rank `1001`. Its control and marked paths happened to share their
first 80 copied token IDs, so the generation-key scores were identical at that prefix:

```text
control:     26/79, z 1.6239
watermarked: 26/79, z 1.6239
```

The watermark processor had changed token probabilities during generation, but the seeded draws
selected the same early path. This is a useful failure of a common intuition. A changed sampling
distribution does not force a different token on every draw, and short-prefix evidence need not
separate one pair.

## Runtime and cost boundary

The remote function completed in 743.1 seconds, including a 34.8-second model snapshot step and a
5.3-second model load. It returned 12,933 generated token IDs. Multiplying the recorded total
function time by the configured L4 GPU rate of `$0.000222/s` gives `$0.1650` of L4 time. This is a
derived GPU-only amount, not a billed total. It excludes CPU, memory, image build, data transfer,
and provider rounding or overhead.

## Figure handoff

Figure 1 caption: The same frozen 50-token source prefix and paired seed enter two Gemma calls. The
marked call alone receives the watermark profile. Once sampled tokens diverge, each path keeps its
own history.

Figure 2 caption: Four checks on one row distinguish correct-key marked evidence from ordinary
Gemma variation, natural-web variation, and a comparison-key replay.

Figure 3 caption: Each prefix point rechecks a longer prefix of the same recorded output. No pair
supported 400 copied tokens in both generated conditions, so no aggregate 400-token point exists.

Figure 4 caption: Every dot is one document-level paired z difference. Means and intervals summarize
the complete matched cohort without hiding reversals or equal rows.

## Claim boundary

The measured result belongs to one Gemma revision, tokenizer, CUDA pseudorandom profile, public
key pair, sampler, prompt set, and C4 selection. It does not prove authorship, detect arbitrary AI
text, reproduce Claude's private implementation, measure quality, establish a production cutoff,
or show resistance to editing.

A positive row means only "consistent with this configured watermark and key." The paired bootstrap
intervals summarize these frozen documents. They are not population guarantees.

## Next Lego block

The unedited paired result is now frozen. Stage 8 may change one editing operation at a time and
measure how much of the same keyed evidence survives after a new approval.
