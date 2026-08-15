# Stage 5 publication brief

## Article role

This section answers one question: what changes when the Stage 4 reference recipe moves from a
small local CPU fixture to Gemma 4 E2B on a cloud L4?

The reader may assume that Transformers owns the maintained generation loop and that copied text
becomes `G`, `T`, and z. Stage 5 must define BF16, GPU memory, model load, generation throughput,
watermark processor time, and a cost projection in everyday language.

The narrow expected answer is one sentence: the same sampling intervention can run on a larger
current model, but its time and memory cost must be measured because Gemma's 262K-token vocabulary
makes the maintained full-vocabulary green-list step real work.

## Teaching spine

Keep the continuity passage:

`Early one morning Jack went up the hill. At the top he`

Use its paired Gemma row as the recorded story. Keep the passage, seed, L4, BF16 model, generation
settings, and checker recipe fixed. Change only whether the reference watermark processor is
present. Follow both branches only while their inputs and histories match; after the first sampled
difference, compare aggregate time, memory, copied text, and checker evidence rather than aligning
unrelated tokens.

The main path must make these transitions visible:

1. Stage 4's GPT-2/CPU fixture hands the complete recipe to Stage 5.
2. A Modal container supplies one L4; Modal is outside the watermark algorithm.
3. The pinned Gemma files move into GPU memory once.
4. The same rendered prompt and seed begin the control and watermark calls.
5. The watermark processor creates a keyed green group and changes surviving scores at every token.
6. The page measures elapsed generation time and peak reserved GPU memory for each branch.
7. Copied continuation text returns to the same configured checker.
8. The slower measured speed projects the 24-row run at 200 and 400 tokens.
9. A human gate decides whether later dataset and full-run work is justified.

The challenge case is a weak or slow watermark row. It remains evidence. Six generations cannot
measure accuracy or quality, and a projected GPU charge is not a Modal invoice.

## Fixture selection

The three passages, seed rule, sampling settings, keys, green fraction, bias, context width, and
checker formula were selected before the Stage 5 run. They come from Stages 3 and 4.

The 200-token cap is fixed before evidence because a 40-token row cannot estimate the proposed
200-token run, while 400 tokens would double the smoke without resolving the Stage 6 dataset gate.
Do not tune prompts, seeds, keys, or settings after seeing output.

The exact model revision is
`google/gemma-4-E2B-it@3e22461f65e89153144f8adb70e3b8c2cc9845a7`. Record the model card and
Apache 2.0 license. The model is an open-model experiment fixture, not a stand-in for Claude or
proof of model quality.

## Visual plan

### Figure 1: the recipe crosses a runtime boundary

Keep the Stage 4 objects aligned on the left: passage, processor order, key profile, copied-text
checker, `G/T`, and z. Move them across a visible boundary to Gemma 4, BF16, and one L4. Mark model,
tokenizer, vocabulary, device, prompt rendering, and length as changed profile fields.

Caption draft:

> Stage 5 keeps the maintained watermark recipe and paired passages. It changes the model,
> tokenizer, device, precision, prompt rendering, and output length, so token-for-token equality is
> neither expected nor tested.

Alt text draft:

> A fixed passage and watermark recipe move from GPT-2 on a CPU to Gemma 4 E2B on an L4. Stable
> settings are separated from changed runtime and model fields.

### Figure 2: one paired passage through time and memory

Use a shared start. Branch to control and watermark calls. Display generated token count, wall time,
tokens per second, peak reserved memory, and processor time from the selected artifact. Stop token
alignment when histories differ. Bring both copied outputs into matched checker boxes.

Caption draft:

> Both branches begin from the same rendered prompt and random seed. Once sampled histories differ,
> the comparison continues in measured time, memory, and copied-text detector evidence.

Alt text draft:

> One prompt splits into control and watermarked generation on the same L4. Each branch shows time,
> speed, memory, copied continuation, and detector count.

### Figure 3: smoke measurement to bounded projection

Start with the slower measured condition. Show tokens per second as an observed rate, then multiply
the 9,600- and 19,200-token run sizes into projected seconds and GPU-only charges at the recorded L4
rate. List excluded costs beside the result.

Caption draft:

> The projection uses the slower measured condition and Modal's recorded L4 rate. It estimates GPU
> generation time only; image build, download, model load, CPU, memory, and storage are separate or
> unavailable.

Alt text draft:

> A measured token rate feeds two arithmetic paths for a 9,600-token and 19,200-token run. Each path
> ends in projected time and GPU-only cost with exclusions listed.

Context-free screenshots must cover the Stage 4-to-5 bridge, paired continuity row, and projection
with its exclusions. Desktop keeps the paired branches side by side. Mobile stacks them while
retaining shared-start identity and units.

## Evidence contract

The selected artifact records every value required by these figures. The page and blog note may use
only `artifacts/lab-05/trace.json`, values independently derived from it, and external facts linked
to primary sources.

Every substantive claim receives one label:

- `measured`: produced by the selected Modal smoke;
- `derived`: arithmetic from recorded values;
- `external`: model-card, Transformers, or Modal documentation;
- `opinion` or `limitation`: teaching judgment and scope boundary.

Do not copy timings, memory, detector values, or costs from terminal output or memory.

## Expected result before the run

The exact Gemma revision should load in BF16 on one L4 and finish six generations. The watermark
processor should add measurable per-token work. The copied-text checker should reproduce its counts
with the same CUDA profile. No assumption is made about score separation, speed penalty, memory
headroom, early endings, or prose quality.

## Blog handoff requirements

`blog/notes/05-gemma-modal-smoke.md` must include:

1. the article subsection and expected result above;
2. exact model, runtime, App, device, and rate snapshot;
3. the measured six-row smoke result;
4. one complete continuity timing/memory/checker example;
5. one inconvenient result or limitation;
6. the two projected run sizes with formulas and exclusions;
7. figure captions and alt text;
8. allowed and prohibited claims;
9. the explicit human go/no-go result;
10. the transition to Stage 6 without implying that dataset work has started.

Allowed claims are limited to this pinned run: observed load, speed, processor timing, memory,
copied-text evidence, and derived projections. Prohibited claims include detection accuracy,
quality preservation, a total cloud bill, GPU portability, a deployed false-positive rate, a
universal model-scale cost, Claude equivalence, or Stage 6 readiness without the recorded gate.
