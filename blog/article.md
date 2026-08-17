# How does a text watermark work?

I could picture an image watermark. A 4K frame has 8,294,400 pixels. Nudge a handful of color values and the picture can still look the same. A video gives you thousands of those frames.

Plain text seemed different. There is no slightly-more-blue version of the letter `e`. Change a word and you may change the sentence.

So my first question was embarrassingly basic: where would the mark go?

Copy and paste throws away the file wrapper. A model-level mark cannot depend on a hidden PNG layer. It also cannot spray strange characters through the answer and hope nobody notices.

Theo Browne spent part of his video about Claude's announcement on this mismatch. Images and video have lots of nearby values an engineer can alter. Text has a much tighter set of choices.[^theo] His discussion was skeptical, especially about paraphrasing. The image-to-text comparison stuck with me because it points at the real engineering problem.

<!-- interactive: media-slack -->

The opening appears when the model chooses the next token. A language model writes one token, appends it, then chooses another. At many positions, several continuations are reasonable. A secret rule can favor some of them by a small amount.

The copied paragraph has no extra label. The pattern is in the choices the model made.

Someone with the same rule can walk through the text afterward and count how often those favored choices occurred. One choice says almost nothing. A few hundred choices may say more.

Reduced to three lines, the plan looks like this:

```text
generate: favor some acceptable next tokens
check:    rebuild those groups and count the chosen tokens
judge:    compare the count with ordinary chance
```

The code gets more particular later. Before keys, tokenizers, models, and sampling order, there is a smaller problem worth solving cleanly.

## Start with two weighted coins

I first tried to explain the idea with tokens. That dragged in tokenizers, logits, sampling, and keys before the basic statistical trick was clear. So I removed language from the first experiment.

Each token choice became a coin flip. Heads means the source chose from a favored group. Tails means it chose another valid option.

The baseline coin lands heads 25 percent of the time. The nudged coin lands heads 40 percent of the time. Neither coin is fair. The quarter-head baseline matches the favored fraction used later in the text experiment. The 40 percent setting is a teaching bias, not something measured from a language model.

Forty flips are enough to make the difference visible sometimes, but not reliably. The baseline can get lucky. The nudged coin can have a bad run. Their counts can tie or arrive in the wrong order.

<!-- interactive: coin-lab -->

Rerun it a few times and the individual sequences change. The averages do not. The baseline settles near one head in four; the nudged source settles near two in five.

## Follow one batch all the way through

Now keep one batch on the table: 32 heads in 80 flips.

The baseline average is 20. Our batch has 12 extra heads. That sounds high, but the raw difference lacks a scale. Twelve extra heads would be absurd in 20 flips and unremarkable in 20,000.

Under the baseline model, 80-flip batches move by about 3.87 heads around their average. So the observed excess is:

```text
12 extra heads / 3.87 heads of ordinary movement = 3.10
```

That number is the z score. It says the count is 3.10 standard deviations above the baseline average. It is a distance, not the probability that a watermark is present.

A score still does not make a decision. The lab chose a cutoff of 3 before running the experiment. Our 3.10 lands on the other side. Under the exact baseline coin model, 32 or more heads appear in 80 flips about 0.2239 percent of the time. A baseline batch can still do it. Rare and impossible are different words.

The interactive below keeps the same `32`, `80`, `20`, `12`, `3.87`, and `3.10` objects on screen from observation to decision.

<!-- interactive: coin-worked -->

## Add more flips without changing the bias

Now hold the two probabilities fixed and change only the length.

The nudged source accumulates an expected excess of `0.15 x T` heads. Ordinary baseline movement grows as `sqrt(T x 0.25 x 0.75)`. The excess grows in direct proportion to length. The noise grows with its square root.

At 40 flips, the expected excess is 6 heads and ordinary movement is 2.74. At 400 flips, the expected excess is 60 while ordinary movement is 8.66. The same nudge becomes easier to see because the gap outruns the wobble.

<!-- interactive: coin-length -->

One score still tells us little about error. Repeat whole batches and two hills appear. They overlap at short lengths. Moving the cutoff left catches more nudged batches and also catches more baseline batches. Moving it right does the reverse.

<!-- interactive: coin-distribution -->

## The coin was standing in for a token choice

Now return to text.

One coin flip becomes one eligible token position. Heads becomes "the chosen token belonged to the favored set." Counting heads becomes counting favored tokens. The same score can compare that count with the quarter-green baseline.

The analogy has limits. Real token choices depend on their history, repeat, and pass through a tokenizer. The coin experiment assumes independent trials. We will test those assumptions later instead of hiding them.

<!-- interactive: coin-to-token -->

## The first experiment, in code

The repository implementation is intentionally small. `src/watermark_lab/stats.py` owns the statistical operations. `labs/01_biased_coin.py` reads the frozen configuration, simulates both sources, scores every batch, writes the raw rows, summarizes them, and renders the selected figure.

The scorer is six lines of work:

```python
def green_hit_z_score(*, hits: int, trials: int, null_probability: float) -> float:
    expected = trials * null_probability
    variance = trials * null_probability * (1.0 - null_probability)
    return (hits - expected) / math.sqrt(variance)
```

The simulator uses a local seeded random generator. It never touches module-global random state:

```python
def simulate_hit_counts(
    *, trials: int, hit_probability: float, replicates: int, seed: int
) -> tuple[int, ...]:
    generator = random.Random(seed)
    return tuple(
        sum(generator.random() < hit_probability for _ in range(trials)) for _ in range(replicates)
    )
```

The readable lab then runs every configured length under both conditions:

```python
for length in config.lengths:
    for condition in ("null", "biased"):
        probability = _probability(config, condition)
        seed = derive_group_seed(
            base_seed=config.base_seed,
            condition=condition,
            trials=length,
        )
        hit_counts = simulate_hit_counts(
            trials=length,
            hit_probability=probability,
            replicates=config.replicates,
            seed=seed,
        )
        for hits in hit_counts:
            z_score = green_hit_z_score(
                hits=hits,
                trials=length,
                null_probability=config.null_hit_probability,
            )
```

That loop produced 10,000 baseline batches and 10,000 nudged batches at each of five lengths.[^lab01]

| Flips | Nudged batches above cutoff | Baseline batches above cutoff |
| ---: | ---: | ---: |
| 40 | 21.33% | 0.16% |
| 80 | 54.20% | 0.13% |
| 160 | 88.62% | 0.21% |
| 200 | 95.23% | 0.17% |
| 400 | 100.00% | 0.20% |

The null rates wobble rather than falling smoothly. They are finite Monte Carlo estimates. The 100 percent value at 400 means all 10,000 simulated nudged batches crossed under this locked coin setup. It is not a promise about all future batches, much less real model output.

<!-- interactive: coin-results -->

The coin has now done its job. It showed why a weak preference can become measurable and why a cutoff creates both misses and false alarms. It still has no key, no vocabulary, and no way to decide which text choices should count as heads.

## Give the coin a key

The coin experiment supplied hits without explaining where they came from. I needed a rule that could look at one token position and say, repeatably, whether a candidate belonged to the favored group.

I used 20 visible words and one sentence small enough to inspect by hand:

> Early one morning Jack went up the hill.

The program begins with `Early one morning Jack`. For each of the 20 possible next words, it hashes the public teaching key, those four token IDs, and the candidate ID. Sorting the 20 hashes gives a stable ranking. The first five candidates are green.

For this context, the lesson key selects `Early`, `went`, `walked`, `snow`, and `trail`. Some are bad continuations after `Jack`. That is fine. The selector reads token IDs, not grammar. The hand-written starting scores still make awkward words unlikely.

Changing the key changes the ranking. The comparison key selects `the`, `hill`, `path`, `snow`, and `home` for the same context. Five words remain green because the 25 percent fraction stayed fixed. Eight memberships changed.

Now the program adds `2` to the five selected scores and normalizes all 20 into probabilities. `went` rises from 22.85 percent to 46.51 percent. `ran` keeps its score of 1.9, yet its probability falls from 27.91 percent to 7.69 percent because every candidate takes a share of the same total. The odds of a selected word relative to an unchanged word are multiplied by `exp(2)`, about 7.39, before normalization. Its final probability does not simply get multiplied by 7.39.

The saved draw is `0.30`. It selects `walked` from the original distribution and `went` after the increase. The program appends `went`, drops `Early` from the four-token window, and runs the same rule again with `one morning Jack went`.

Four choices finish the sentence: `went`, `up`, `the`, `hill`. The first two were green for their contexts. The last two won despite being outside the selected set. A watermark leans on the sampler. It does not dictate every token.

Checking runs the selection rule in reverse order through the copied sentence. Before `went`, the checker rebuilds the group from `Early one morning Jack`. It repeats that work before `up`, `the`, and `hill`. The checker needs the observed token history, key, tokenizer, context width, green fraction, selector, and counting rule. It never sees the generation scores or random draws.

This sentence produces `G=2` hits across `T=4` checked positions. Random selection predicts one hit, so z is `1.1547`. I assigned no cutoff to this four-position fixture. The comparison key produces zero hits here, although another wrong key could match some positions by chance.

The key printed in the page is for teaching. Anyone can read it, reproduce the sets, and study how to remove or forge the pattern. A service using a symmetric watermark would keep the generation key out of prompts, browser code, model files, and public logs.

<!-- interactive: toy-key -->

## Replace the hand-written scores

The toy sentence answered the mechanism question. It could not tell me how the same score increase behaves inside a language model.

I loaded the pinned `mlx-community/LFM2-350M-4bit` checkpoint and wrote out one autoregressive loop on an Apple GPU.[^lab03] The prompt ended here:

> Early one morning Jack went up the hill. At the top he

The control and marked paths began with the same model state and seed. At the first generated position, the key put `Jack`, token ID `30604`, in the green group.

| Candidate | Raw score | Green | Score after increase | Final marked chance |
| --- | ---: | --- | ---: | ---: |
| `As` | 15.1875 | yes | 17.1875 | 34.7150% |
| `he` | 14.8125 | yes | 16.8125 | 21.7241% |
| `Jack` | 14.6875 | yes | 16.6875 | 18.5816% |
| `The` | 13.5000 | yes | 15.5000 | 4.2114% |
| `He` | 15.3125 | no | 15.3125 | 3.3315% |

`Jack` had an 11.6422 percent chance without the increase and an 18.5816 percent chance with it. The saved draw chose `Jack` in both paths.

That non-event matters. Two probability distributions can return the same token. A later draw eventually split the continuations, after which each path conditioned on its own history. Token-by-token comparison stops being matched at that point.

The marked continuation began:

> Jack climbed slowly, his boots sinking slightly into the soft snow-covered earth.

I copied the continuation, tokenized it again, and scored the copied IDs. The first copied token supplied context, leaving 39 eligible positions. With the generation key, the marked text scored `21/39`, z `4.1603`. The same marked text scored `7/39`, z `-1.0170`, with the comparison key. The paired control scored `8/39`, z `-0.6472`, with the generation key.

All three fixed marked passages had higher same-key counts than their controls. Three examples can prove that the path runs. They cannot estimate accuracy or writing quality.

<!-- interactive: real-token -->

## Operation order changes the sampler

My first loop applied the green score increase before temperature and filtering. Transformers 5.14.1 did the work in another order.[^lab04]

```text
temperature -> top-k -> top-p -> watermark processor -> softmax -> sample
```

The earlier teaching loop used:

```text
watermark increase -> temperature -> top-p -> top-k -> softmax -> sample
```

I replayed both routes on the same 50,257 saved GPT-2 scores. The Transformers route kept 40 candidates after top-k and 19 after top-p. The earlier route kept 11 after top-p. For token ` was`, the final probabilities were 8.642730 percent and 8.825517 percent.

The difference for that token is only 0.18 percentage points. The profile difference is larger. Temperature changes the effective score increase. Filtering can remove a candidate before the watermark reaches it. Recording `delta=2` does not identify the sampler.

A six-token compatibility fixture found another mismatch. It alternated token IDs 373 and 21272, producing five pair occurrences but only two distinct pair values. Both settings of Transformers' `ignore_repeated_ngrams` option returned `3/5`, z `1.8074`, in the pinned version. My explicit distinct-value count returned `1/2`, z `0.8165`.

Those six tokens were a test fixture, not model output. The test taught a blunt lesson: inspect maintained behavior instead of inferring it from an option name.

<!-- interactive: operation-order -->

## Run the same mechanism on Gemma

The watermark core should not know how every model formats a chat. I kept the shared work small: pass a watermark profile into generation, extract copied assistant text, and build the matching checker. A Gemma adapter owned prompt rendering, tokenization, assistant-content extraction, and generated-ID slicing.

The project pinned `google/gemma-4-E2B-it` in BF16 with Transformers 5.14.1 and PyTorch 2.13.0 on one Modal NVIDIA L4.[^lab05] Modal provided the disposable machine. The watermark algorithm did not depend on Modal.

The model downloaded in 36.739 seconds and loaded in 5.782 seconds. Peak reserved memory was 9.682 GiB of the reported 22.034 GiB. The three marked smoke outputs generated between 18.422 and 19.259 tokens per second. Synchronized processor replays took 5.373 to 7.165 milliseconds per complete marked continuation. Those replay timings measure one component under instrumentation, not an end-to-end speed penalty.

The first result was a miss three times over:

| Passage | Copied evidence | z |
| --- | ---: | ---: |
| continuity | `11/26` | `2.0381` |
| notebook | `7/20` | `1.0328` |
| library | `9/22` | `1.7233` |

Each marked output ended after 22 to 28 generated token IDs. The checker had only 20 to 26 eligible positions. I kept the prompts, seeds, keys, and stopping behavior as declared instead of searching for a crossing.

A later natural-length ladder produced 12 marked and 12 paired control outputs. Eight marked rows crossed `z > 3`; no control did. The achieved copied lengths ranged from 200 to 800 tokens. Prompt content and length changed together, so the ladder does not isolate length as the cause.

The committed evidence uses a public key so anyone can verify it. A private service would load key material inside the host process and expose a key version, not the key itself. Browser code cannot conceal a symmetric secret from its user.

<!-- interactive: gemma-path -->

## Score outside text before trusting the cutoff

A crossing looks impressive until the same checker crosses on text that was never watermarked.

I froze 1,000 C4 `realnewslike` continuations for calibration, then reserved the next 24 passing rows for paired generation.[^lab06] Selection followed a pinned validation shard in file order. It required at least 500 Gemma tokens and applied fixed duplicate, list, code, and letter-fraction filters before scoring.

C4 is natural-web text. It is not verified human writing.

With the public Gemma key and all-pair counting, the 1,000 scores had a median of `0.0289`, a 99th percentile of `2.4568`, and a maximum of `3.7286`. Four rows crossed strict `z > 3`.

Those four crossings are false alarms for this declared negative cohort. They do not estimate a rare production rate. A thousand rows cannot validate one-in-100,000 behavior.

The maximum row exposed the counting rule. Counting every adjacent-pair occurrence gave `132/399`, z `3.7286`. Counting each pair value once on the exact same token sequence gave `114/358`, z `2.9904`. The second rule removed 41 observations, including 18 green hits, and moved the row below the cutoff.

I froze that row before scoring and kept it in the article. Fernandez and colleagues had already shown that familiar asymptotic tests can underestimate false positives on short or repetitive text.[^three-bricks] The z formula stays useful because every term is visible. It must travel with the empirical background and repetition policy.

<!-- interactive: calibration -->

## One high score needs three controls

The 24 paired prompts were frozen before generation.[^lab07] Each pair shared its 50-token source prefix, prompt-derived seed, model revision, sampler, and 400 generated-token safety cap. The marked call alone received the watermark configuration. Normal end-token behavior remained active.

A marked correct-key score leaves three easy explanations open. Ordinary Gemma output might score high under that key. Natural text from the source domain might score high. Or the marked text might score similarly under another key.

Rank `1000` gives all four checks at 160 copied tokens:

| Checked text and key | Green hits | Eligible checks | z |
| --- | ---: | ---: | ---: |
| marked text, generation key | 58 | 159 | 3.3424 |
| paired model control, generation key | 47 | 159 | 1.3278 |
| natural-web continuation, generation key | 43 | 159 | 0.5952 |
| marked text, comparison key | 29 | 159 | -1.9688 |

Only the first condition crosses. It is one predeclared example, not an accuracy estimate.

Rank `1001` is just as important. Its marked and control paths shared every token ID through the first 80 copied tokens. Both scored `26/79`, z `1.6239`. The processor changed probabilities. The seeded draws still followed the same early path.

<!-- interactive: four-controls -->

## Read every paired row before the average

All 24 pairs were complete at 80 copied tokens. I plotted each document difference on its own line before calculating a mean.

| Contrast | Mean paired z difference | 95% paired bootstrap interval |
| --- | ---: | ---: |
| paired model control | `1.8296` | `[1.3424, 2.3276]` |
| natural web | `1.7538` | `[1.3100, 2.1977]` |
| comparison-key replay | `2.0461` | `[1.6131, 2.4792]` |

The averages separate cleanly in this cohort. The rows do not. Some differences are small, rank `1001` is exactly zero against its model control, and at least one row points against the mean. Three marked rows crossed `z > 3`; none of the three control families did at this prefix.

The intervals summarize 24 frozen documents. They are not population guarantees.

The matched cohort also shrank with prefix length. Counts at 40, 80, 160, 200, and 400 copied tokens were `24`, `24`, `21`, `17`, and `0`. A 400-token generation cap did not produce a single pair with 400 copied tokens in both generated conditions.

At 200 copied tokens, four of 17 marked rows crossed, along with one natural-web row. Model-control and comparison-key rows had no crossings. Because the documents changed as the prefix grew, that sequence cannot support a clean causal claim about length.

The L4 function made 48 generation calls, returned 12,933 generated token IDs, and ran for 743.1 seconds. Runtime multiplied by the configured L4 rate gives `$0.1650` of GPU time. CPU, memory, image, transfer, and provider overhead sit outside that derived number.

<!-- interactive: cohort -->

## Edits rebuild the checker history

Rank `1000` scored `28/79`, z `2.1436`, at its first 80 copied token IDs. A deterministic 10 percent word deletion scored `25/79`, z `1.3641`. A Gemma paraphrase scored `26/79`, z `1.6239`.[^lab08]

The edit does not peel a label off the text. It changes the string. Tokenization then creates another ordered history, so the checker rebuilds different keyed groups at later positions.

Stage 8 carried the first 12 marked outputs through eight conditions:

| Edit | Mean z change | Mean copied-token length ratio |
| --- | ---: | ---: |
| normalization | `0.0000` | `0.9986` |
| homoglyph 1% | `-0.0217` | `1.0448` |
| homoglyph 5% | `-0.9311` | `1.2183` |
| deletion 10% | `-0.3248` | `0.8980` |
| deletion 30% | `-0.9960` | `0.7021` |
| mixing 25% | `-0.6712` | `1.0012` |
| mixing 50% | `-1.3424` | `1.0088` |
| paraphrase | `-1.7105` | `0.9636` |

Homoglyph substitution swapped ASCII letters for similar-looking Unicode code points. It tested tokenizer sensitivity and expanded token length. It was not a semantic rewrite.

Deletion and mixing could damage grammar or claims. Their lower detector scores say nothing by themselves about meaning preservation.

All 12 paraphrases passed the declared length, decimal-number, and embedding-cosine screens. A non-independent assistant review marked ten pass and two uncertain. Every passed rewrite reduced z, and no paraphrase crossed the cutoff. Embedding cosine and assistant review remain proxies.

Theo's skepticism arrives here. The Declaude explainer reports known-key rewrite tests against open KGW and EXP implementations.[^declaude] Those outside results point in the same direction: recomposition can erase token-history evidence. They do not test Claude's private SynthID configuration or replace this project's measurements.

<!-- interactive: edits -->

## A stronger mark costs something

The default experiment added `delta=2` to green scores. I reused eight frozen prompts and changed delta alone.

| Delta | Mean z | Strict crossings | Mean conditional NLL | Mean repeated-pair fraction |
| ---: | ---: | ---: | ---: | ---: |
| 1 | `0.2923` | `0/8` | `0.5004` | `0.0373` |
| 2 | `2.1761` | `1/8` | `0.5415` | `0.0471` |
| 3 | `2.4684` | `3/8` | `0.5783` | `0.0483` |

Mean z rose with delta. Mean conditional negative log likelihood also rose, meaning the pinned Gemma checkpoint found the outputs more surprising. Repeated adjacent pairs rose as well. Ranks `1004` and `1006` had lower z at delta 3 than at delta 2, so individual paths did not climb monotonically.

NLL and repetition are model-based proxies. They cannot tell us which answer a person would prefer, whether a factual statement remained correct, or whether a story improved. Eight prompts cannot establish a universal setting, and this project did not run an independent human study.

<!-- interactive: delta -->

## Claude uses a SynthID-Text variant

The experiment above is a transparent KGW-style green-list analogue. Claude uses another family.

KGW selects a keyed vocabulary subset, promotes it, and later counts an excess of selected tokens.[^kgw] That is the family implemented here.

SynthID-Text uses keyed Tournament sampling.[^synthid] It samples candidates from the model distribution, lets keyed scoring functions decide tournament winners, and later measures correlation between observed tokens and those functions. The paper describes distortionary and non-distortionary settings, repeated-context masking, and a live quality assessment over nearly 20 million Gemini responses. Entropy and length matter because a model with one plausible continuation gives the sampler little room to encode a preference.

On August 14, Anthropic called Claude's watermark "a version of the SynthID-Text approach." The company says the method changes randomness among acceptable choices, adds no tokens or user identity, showed no practical quality impact in its internal tests, and will eventually have a detection API. It also says exact factual passages, proofreading, and much code carry sparse evidence.[^anthropic-news]

Those are provider claims. Anthropic has not published its tournament settings, key construction, context masking, scorer, threshold, model coverage, or production evaluation data. A KGW delta sweep cannot validate the quality claim for a different sampling intervention.

Other watermark designs make other trades. Fixed partitions avoid rolling-context desynchronization but reuse one partition. Distortion-free schemes map keyed randomness through the model distribution under stated assumptions. Semantic schemes move the unit toward sentences or embeddings. Publicly detectable schemes split secret generation information from public verification. Removal, spoofing, low entropy, calibration, and key management remain engineering problems in every family.

<!-- interactive: field-map -->

## Detection does not settle authorship

The EU transparency requirement helps explain why providers are building marking systems.[^article50] It does not define how a school or employer should judge a person.

A provider-side mark answers a technical question about machine-readable evidence. Authorship concerns who supplied the ideas and accepted responsibility. A policy defines which assistance was allowed. Discipline is a separate decision.

A watermark score cannot perform those jobs.

Anthropic draws a similarly narrow boundary. A detected mark can indicate Claude involvement, according to the company, without showing that Claude wrote every word. Light proofreading may leave too few Claude-chosen tokens. Translation gives the model more choices and may retain more evidence. The mark contains no person, organization, or chat identifier.

Absence says even less. Short answers, exact code, low-entropy facts, old models, a wrong key, or edited passages can all leave little detectable evidence despite model involvement.

Passive classifiers create another risk. Sean Goedecke describes students changing their own prose or recording drafts because they fear false accusations. Turning an uncertain classifier score into proof is a policy failure.

The wording used throughout this project is intentionally narrow:

> Consistent with this configured watermark and key.

## What survived the experiment

For the frozen 24-row Gemma cohort, marked correct-key scores exceeded model-control, natural-web, and comparison-key scores on average at every supported copied prefix. At 80 copied tokens, all 24 rows remained matched and each paired interval stayed above zero. Individual documents still overlapped.

Four of 1,000 natural-web passages crossed the same cutoff under all-pair counting. One crossed under distinct-pair counting. That result prevents the cutoff from masquerading as a truth label.

Most named edits reduced mean correct-key evidence in the 12-row fixture. Ten paraphrases passed the declared automatic and non-independent review screens, and every one of those ten reduced z.

Larger delta raised the eight-row mean z along with NLL and repetition proxies. Two signal paths fell from delta 2 to delta 3.

The work leaves large questions open. It does not provide production calibration, a rare false-alarm rate, human quality judgments, adaptive security, private-key safety, or results for another model, tokenizer, or watermark family. It cannot detect unmarked historical AI text. It says nothing about intent or misconduct, and it does not reveal Claude's production settings.

A text watermark leaves a trail of sampling choices. The matching key and profile can turn a long enough trail into evidence. Short outputs, rebuilt histories, and questions beyond the checker's design weaken that evidence quickly.

## Reproduce the checked evidence

The repository pins Python 3.12 and uses `uv` with a root `justfile`. These commands validate the saved artifacts without launching a model or cloud job:

```console
just setup
just check
just verify-lab-01
just verify-lab-02
just verify-lab-03
just verify-lab-04
just verify-lab-05
just verify-lab-05-examples
just verify-lab-05-lengths
just verify-lab-06
just verify-lab-07
just verify-lab-08
just verify-final-article
```

The model-backed records include revisions, configuration hashes, source commits, achieved lengths, hardware, and runtime. Regeneration would require separate approval and could incur cost. The HTML replays committed evidence only.

## Sources and evidence

[^anthropic-support]: Anthropic, [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content), inspected 2026-08-16. This living support page framed the project before the fuller method announcement.
[^anthropic-news]: Anthropic, [How Claude's text watermark works](https://www.anthropic.com/news/claude-text-watermark), published 2026-08-14. Provider statements about its chosen method, quality, rollout, detection API, code, editing, and user identity are attributed to Anthropic.
[^article50]: European Union, [AI Act Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50), and European Commission, [Code of Practice on Transparency of AI-generated Content](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content). Used as policy motivation, not legal advice or a compliance assessment.
[^theo]: Theo Browne, [Claude watermarks your code now](https://www.youtube.com/watch?v=Be-NqsW-wuk), 2026-08-14, 31:58. Transcript extracted from YouTube caption tracks with `summarize.sh`.
[^computerphile]: Computerphile with Dr Mike Pound, [Ch(e)at GPT?](https://www.youtube.com/watch?v=XZJc1p6RE78), 2023-02-16. Used for green/red-list intuition.
[^sean]: Sean Goedecke, [AI detection tools cannot prove that text is AI-generated](https://www.seangoedecke.com/ai-detection/), 2025-12-05.
[^ghostbuster]: Verma et al., [Ghostbuster: Detecting Text Ghostwritten by Large Language Models](https://arxiv.org/abs/2305.15047), submitted 2023-05-24; NAACL 2024.
[^dnagpt]: Yang et al., [DNA-GPT: Divergent N-Gram Analysis for Training-Free Detection of GPT-Generated Text](https://arxiv.org/abs/2305.17359), submitted 2023-05-27.
[^editlens]: Thai et al., [EditLens: Quantifying the Extent of AI Editing in Text](https://arxiv.org/abs/2510.03154), submitted 2025-10-03.
[^kgw]: Kirchenbauer et al., [A Watermark for Large Language Models](https://arxiv.org/abs/2301.10226), ICML 2023.
[^synthid]: Dathathri et al., [Scalable watermarking for identifying large language model outputs](https://www.nature.com/articles/s41586-024-08025-4), Nature 634, 818-823, 2024.
[^three-bricks]: Fernandez et al., [Three Bricks to Consolidate Watermarks for Large Language Models](https://arxiv.org/abs/2308.00113), version inspected 2023-11-08.
[^declaude]: James Padolsey at NOPE, [How AI text watermarking works](https://declaude.org/watermarking/), inspected 2026-08-17. Its open-model removal measurements are self-reported and are not evidence about Claude.
[^lab01]: Project measurement, `artifacts/lab-01/summary.json`, verified by `just verify-lab-01`.
[^lab03]: Project measurement, `artifacts/lab-03/trace.json`, verified by `just verify-lab-03`.
[^lab04]: Project measurement, `artifacts/lab-04/trace.json`, verified by `just verify-lab-04`.
[^lab05]: Project measurements, `artifacts/lab-05/trace.json`, `examples.json`, and `lengths.json`, verified by the three Stage 5 verifier commands.
[^lab06]: Project measurement, `artifacts/lab-06/calibration.json`, verified by `just verify-lab-06`.
[^lab07]: Project measurement, `artifacts/lab-07/results.json`, verified by `just verify-lab-07`.
[^lab08]: Project measurement, `artifacts/lab-08/results.json`, verified by `just verify-lab-08`.
