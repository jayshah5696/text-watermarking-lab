# Measure the reference path on Gemma and one L4

## Question

What does the Stage 4 reference watermark cost when the same recipe runs on Gemma 4 E2B on a
cloud GPU?

## Expected result before running

The exact Gemma revision should load in BF16 on one NVIDIA L4 and finish six generations. The
watermark processor should add measurable per-token work. The copied-text checker should reproduce
its counts with the same CUDA profile. No assumption was made about score separation, speed
penalty, memory headroom, early endings, or prose quality.

## Fixed profile

The run used `google/gemma-4-E2B-it` at revision
`3e22461f65e89153144f8adb70e3b8c2cc9845a7`, Transformers 5.14.1, PyTorch 2.13.0, BF16, and one
Modal NVIDIA L4. It retained the three earlier passages, prompt-derived seeds, temperature `0.8`,
top-k `40`, top-p `0.95`, green fraction `0.25`, bias `2.0`, generation key `15485863`, comparison
key `15485867`, `lefthash`, and context width one.

Modal supplied the image and GPU. It was not part of the watermark algorithm. The run used no
Hugging Face secret and no persistent Volume.

## Observed result

The disposable container downloaded the pinned model in 36.739 seconds and loaded it onto CUDA in
5.782 seconds. The L4 exposed 22.034 GiB of memory. Peak reserved memory reached 9.682 GiB, leaving
56.1 percent headroom.

| Passage | Watermark | Generated tokens | Seconds | Tokens/s | Processor ms | Generation-key G/T | z |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| continuity | off | 13 | 3.850 | 3.376 | 0.000 | 3/11 | 0.1741 |
| continuity | on | 28 | 1.520 | 18.422 | 7.165 | 11/26 | 2.0381 |
| notebook | off | 18 | 0.954 | 18.869 | 0.000 | 4/16 | 0.0000 |
| notebook | on | 22 | 1.173 | 18.747 | 5.373 | 7/20 | 1.0328 |
| library | off | 30 | 1.873 | 16.018 | 0.000 | 8/28 | 0.4364 |
| library | on | 24 | 1.246 | 19.259 | 5.898 | 9/22 | 1.7233 |

The first control call includes one-time CUDA warm-up behavior and should not be used to infer a
watermark speedup. The three watermarked rows ran from 18.422 to 19.259 generated tokens per second.
The separate instrumented replay measured 5.373 to 7.165 milliseconds total inside the watermark
processor across each complete watermarked continuation. Forced CUDA synchronization perturbs that
measurement, so it is a component timing rather than a throughput benchmark.

All six outputs produced readable continuations related to their fixed passages. That is a smoke
observation, not a language-quality estimate.

## One complete continuity example

The fixed passage was:

> Early one morning Jack went up the hill. At the top he

The control continued:

> saw the entire valley bathed in a soft, ethereal glow.

The watermarked branch continued:

> saw the entire valley bathed in the soft, ethereal glow of the rising sun, a breathtaking
> spectacle that made him pause in his ascent.

Only the copied continuation entered the checker. The control produced 3 green hits among 11
eligible tokens, giving z `0.1741`. The watermarked continuation produced 11 green hits among 26,
giving z `2.0381`. The comparison key produced `6/26`, or z `-0.2265`, on the same watermarked text.

The generated branches had different lengths and sampled histories. Their token positions should
not be aligned after divergence.

## The inconvenient result

None of the three watermarked continuations crossed the configured strict `z > 3` cutoff. Their z
scores were `2.0381`, `1.0328`, and `1.7233`.

That does not invalidate the runtime path. The outputs ended after 22 to 28 generated token IDs,
leaving only 20 to 26 eligible copied-text decisions. Stage 1 already showed why short passages
provide limited evidence. Six outputs cannot estimate a detection rate, and the project did not
search for stronger prompts, keys, seeds, or endings after seeing this result.

## Bounded projection

Use the slowest measured watermarked rate, `18.422` generated tokens per second.

For 24 paired rows at 200 tokens per output:

```text
9,600 tokens / 18.422 tokens per second = 521.1 seconds
521.1 seconds * $0.000222 per L4 second = $0.1157
```

For 24 paired rows at 400 tokens per output:

```text
19,200 tokens / 18.422 tokens per second = 1,042.2 seconds
1,042.2 seconds * $0.000222 per L4 second = $0.2314
```

These are linear GPU-generation projections. They exclude image build, model download, model load,
CPU, memory, storage, retries, and non-linear scaling. They are not a Modal invoice.

## Review gate

The exact pinned revision loaded in BF16 on the required L4. All six generation and copied-text
records completed. The local verifier reproduced detector arithmetic and projections. Peak-memory
headroom was 56.1 percent, above the fixed 20 percent floor. Slowest watermarked throughput was
18.422 tokens per second, above the fixed 2 token-per-second floor. Both GPU-only projections
remained below the USD 5 ceiling.

The runtime smoke therefore passes its preregistered gate and is ready for human review. This does
not authorize Stage 6 or the larger run.

## Figure handoff

Figure 1 caption: Stage 5 carries the Stage 4 watermark recipe from GPT-2 on a CPU to pinned Gemma 4
E2B in BF16 on one L4. The model, tokenizer, vocabulary, device, prompt rendering, and length change,
so token equality is neither expected nor tested.

Figure 1 alt text: A fixed passage and watermark recipe move from a GPT-2 CPU fixture to a Gemma 4
L4 smoke test. Kept settings and changed runtime fields appear in separate groups.

Figure 2 caption: Both continuity branches begin with the same rendered prompt and random seed.
After their sampled histories diverge, the comparison continues in measured time, memory, and
copied-text detector evidence.

Figure 2 alt text: One passage splits into control and watermarked Gemma generation. Each branch
shows saved text, generated-token count, elapsed time, tokens per second, peak reserved memory, and
green-hit score.

Figure 3 caption: The larger-run projection uses the slower measured watermarked rate and the
published L4 price. It estimates GPU generation only and lists excluded costs beside the result.

Figure 3 alt text: A measured rate of 18.422 tokens per second feeds arithmetic for 9,600 and 19,200
generated tokens, ending at 521.1 and 1,042.2 seconds and GPU-only charges of $0.1157 and $0.2314.

## Claim boundary

Allowed claims concern this pinned run: model identity, one L4, BF16, measured download and load,
six saved outputs, generation wall time, component processor timing, peak reserved memory,
copied-text counts, and arithmetic projections.

The run does not establish detector accuracy, quality preservation, a deployed cutoff, a total
cloud bill, cross-GPU portability, model-size generality, Claude equivalence, or Stage 6 results. A
positive score would mean only “consistent with this configured watermark and key.”

## Next Lego block

Stage 6 would freeze a natural-web calibration manifest before scoring any dataset text. That work
requires separate approval and has not started.
