# Inside a model-level text watermark: an open Gemma experiment

Anthropic says it is adding machine-readable marks to content Claude generates. Its support page describes an imperceptible text watermark applied at the model level. Anthropic says the mark travels with copied text, may persist through some editing, and will have detection documentation later.

The page does not name the algorithm, key system, tokenizer, detector, or evaluation. I cannot inspect a private implementation from a product description. So I built a public analogue that exposes every step.

This project uses a KGW-style watermark. It does not reproduce Claude's system. Its checker answers one narrow question:

> Is this text statistically consistent with this configured watermark and key?

It cannot decide whether arbitrary prose came from AI. It cannot identify an author. It cannot decide whether using a model was allowed.

## Start with the finished string

One recorded Gemma continuation entered the checker with 80 copied tokens. The first token supplied context, leaving 79 checks. The configured key marked 28 of those 79 tokens green. That produced z `2.1436`, below the project's strict `z > 3` cutoff.

Then I edited the same string.

- Deterministic 10 percent word deletion produced `25/79`, z `1.3641`.
- A Gemma paraphrase produced `26/79`, z `1.6239`.

The paraphrase passed the declared length, number, and embedding-cosine screen. A non-independent assistant review also passed it. That review is weak evidence about meaning, not a human study.

The score changed because the visible string changed. The tokenizer then produced a new ordered token history. The checker rebuilt its keyed decisions from that new history. Nothing was hidden in whitespace or attached as file metadata.

To see why this works, rewind to one token.

## The mark lives in the sampler

A causal language model produces one score for every possible next token. Sampling converts those scores into a choice. The watermark changes the scores before that choice.

At each position, the generator combines a key with recent token context. That repeatable rule selects a green subset of the tokenizer vocabulary. The generator adds a fixed value, called `delta`, to the green-token scores. It then runs the configured sampling steps and draws one token.

Adding `delta=2` multiplies the relative odds of an otherwise equal green token by `exp(2)`, about `7.39`, before normalization. The final probability still depends on every starting score and the sampling order.

The Stage 3 teaching fixture makes one draw inspectable. Both paths start from the same model scores and seed. The token `Jack` starts with score `14.6875` and belongs to the green set. Without the increase, its final chance is `11.6422%`. With the increase, its score becomes `16.6875` and its final chance is `18.5816%`.

The saved draw selects `Jack` in both paths.

That detail matters. The watermark changes a distribution. It does not force a special word at every position. Once a later draw differs, each generated path conditions on its own history.

The full loop is short:

1. tokenize the prompt;
2. run the model and take the next-token scores;
3. rebuild green membership from the key and context;
4. increase the green scores;
5. run the pinned sampling transforms and draw a token;
6. append the token and repeat.

Stage 4 checked this mental model against Transformers 5.14.1. The maintained path applied temperature, top-k, top-p, and then its watermark processor. The earlier hand-written loop changed scores before temperature and filtering. Both contain the same causal pieces, but their recipes are not equivalent. Sampling order belongs to the detector profile and the reproducibility record.

The original KGW paper describes this as selecting a randomized green set and softly promoting green tokens during sampling. It then uses a statistical test to detect an excess of green tokens. [Read the primary paper](https://arxiv.org/abs/2301.10226).

## The checker rebuilds the same decisions

The checker receives copied text, the pinned tokenizer, and the matching watermark profile. It does not need Gemma's weights for this KGW-style count.

It tokenizes the copied string. At each eligible position, the prior observed token and key rebuild the green set. The current token either belongs to that set or it does not. Green means keyed membership only. It says nothing about truth or writing quality.

For the 80-token example:

```text
eligible checks T = 79
configured green fraction gamma = 0.25
ordinary green count = 79 x 0.25 = 19.75
ordinary movement = sqrt(79 x 0.25 x 0.75) = 3.8487
observed green count G = 28
z = (28 - 19.75) / 3.8487 = 2.1436
```

The z score states distance from the configured quarter-green average in units of ordinary binomial movement. It is a score, not a verdict. The separate rule in this project calls a row positive only when z is strictly greater than 3.

That clean calculation assumes independent trials. Real token histories repeat and depend on prior tokens. Stage 6 therefore kept both the familiar all-pair count and a distinct-value-pair diagnostic. The choice changed one natural-web row from `132/399`, z `3.7286`, to `114/358`, z `2.9904`. Repetition policy is part of the profile.

## Why more text usually helps

Stage 1 removed language models from the problem. It simulated an independent coin with a null hit probability of `0.25` and a teaching alternative of `0.40`.

At the fixed threshold, simulated biased detection rose from `21.33%` at 40 trials to `100%` at 400. The simulated null condition stayed between `0.13%` and `0.21%`. These are Monte Carlo results for an idealized coin, not LLM error rates.

The intuition is clean. A persistent excess grows in proportion to length. Ordinary random movement grows with the square root of length. More eligible text can make the excess easier to distinguish.

The Gemma experiment was messier. Every pair reached 40 and 80 copied tokens. Twenty-one pairs reached 160, 17 reached 200, and none reached 400 in both generated conditions. Normal end-token behavior stayed enabled. The 400 generated-token setting was a safety cap, not an achieved 400-token paired result.

Because the complete cohort shrank with length, the recorded prefix results do not isolate a causal length effect. They show how evidence accumulated in these outputs.

## One score needs several controls

A high correct-key score can have several easy explanations. The Stage 7 design checked four score families.

1. Marked text with the generation key asks whether keyed generation left correct-key evidence.
2. Paired model-control text with the generation key asks whether ordinary Gemma output scores similarly.
3. The frozen natural-web continuation with the generation key checks the source domain.
4. The same marked text with a comparison key checks whether evidence is tied to this key.

The fixed teaching row at 160 copied tokens scored:

| Checked text and key | Green hits | Eligible checks | z |
| --- | ---: | ---: | ---: |
| marked text, generation key | 58 | 159 | 3.3424 |
| paired model control, generation key | 47 | 159 | 1.3278 |
| natural-web continuation, generation key | 43 | 159 | 0.5952 |
| marked text, comparison key | 29 | 159 | -1.9688 |

That row crossed the configured cutoff only in the first condition. It is one predeclared example, not an accuracy estimate.

The inconvenient row stayed in the article too. Rank `1001` had identical marked and control token IDs through 80 copied tokens. Both scored `26/79`, z `1.6239`. Changed probabilities did not force a different early draw.

## The 24-row paired result

Stage 6 froze 24 C4 `realnewslike` prompts before generation. Each Stage 7 pair shared a prompt, seed, Gemma revision, sampler, and 400 generated-token cap. The marked call alone received the watermark configuration.

At 80 copied tokens, all 24 pairs remained complete. Correct-key marked z exceeded:

- paired model control by mean `1.8296`, with a 95 percent paired bootstrap interval of `[1.3424, 2.3276]`;
- natural web by mean `1.7538`, interval `[1.3100, 2.1977]`;
- comparison-key replay by mean `2.0461`, interval `[1.6131, 2.4792]`.

Those intervals summarize the frozen 24 documents. They are not population guarantees. Three of 24 marked rows crossed strict `z > 3` at this prefix. No paired model-control, natural-web, or comparison-key row crossed at 80. Individual row differences still overlapped and sometimes moved against the mean.

The experiment used one pinned Gemma 4 E2B revision in BF16 on one NVIDIA L4. Its 48 Stage 7 generation calls returned 12,933 generated token IDs. The function ran for 743.1 seconds. Multiplying that time by the configured L4 rate gives `$0.1650` of GPU time. That is not the provider bill; it excludes CPU, memory, image, transfer, and provider overhead.

## A cutoff can still catch outside text

Before paired generation, Stage 6 scored 1,000 frozen natural-web continuations with the same public key and CUDA profile. Four crossed strict `z > 3` under all-pair counting. The median z was `0.0289`, the 99th percentile was `2.4568`, and the maximum was `3.7286`.

C4 is natural-web text, not verified human writing. Four observed crossings in one pinned cohort do not define a production false-alarm rate. One thousand rows cannot validate one-in-100,000 behavior.

A crossing means only "consistent with this configured watermark and key." It does not prove model source or authorship.

## Editing rebuilt the evidence

Stage 8 applied eight named conditions to the first 12 frozen marked outputs. Every deterministic edit started from the complete copied string. The checker then tokenized and scored the edited result.

At the first 80 copied token IDs, mean paired z change was:

| Edit | Rows | Mean z change | Mean copied-length ratio |
| --- | ---: | ---: | ---: |
| normalization | 12 | 0.0000 | 0.9986 |
| homoglyph 1% | 12 | -0.0217 | 1.0448 |
| homoglyph 5% | 12 | -0.9311 | 1.2183 |
| delete 10% | 12 | -0.3248 | 0.8980 |
| delete 30% | 12 | -0.9960 | 0.7021 |
| mix 25% | 12 | -0.6712 | 1.0012 |
| mix 50% | 12 | -1.3424 | 1.0088 |
| paraphrase | 12 | -1.7105 | 0.9636 |

Homoglyph substitution changed Unicode code points that can look similar. It diagnosed tokenizer sensitivity. It was not a semantic paraphrase test.

Deletion and mixing could damage grammar or claims. Their lower scores are editing outcomes, not successful meaning-preserving removals.

All 12 paraphrases passed the automatic length, number, and embedding-cosine screen. The non-independent assistant review marked ten pass and two uncertain. All ten passed rewrites reduced z, and no paraphrase crossed the strict cutoff. Embedding cosine and assistant review do not prove equal meaning.

## A stronger mark changed other measurements

Stage 8 also reused eight frozen prompts and changed delta alone. Delta 2 came from Stage 7. Delta 1 and 3 were new bounded calls.

| Delta | Rows | Mean z | Strict crossings | Mean conditional NLL | Mean repeated-pair fraction |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8 | 0.2923 | 0/8 | 0.5004 | 0.0373 |
| 2 | 8 | 2.1761 | 1/8 | 0.5415 | 0.0471 |
| 3 | 8 | 2.4684 | 3/8 | 0.5783 | 0.0483 |

Mean key-specific evidence rose with delta in this fixture. Mean conditional negative log likelihood and repetition rose too. Two row-level z paths fell from delta 2 to delta 3.

Conditional NLL measures how surprising the pinned Gemma checkpoint finds a continuation. Repetition counts repeated adjacent token pairs. Both are model-based proxies. Neither is a human quality judgment, and the project did not run an independent human evaluation.

There is no universal best delta in these eight rows.

## KGW is the implemented analogue

The project implements one contextual green-list family because it is easy to inspect. The wider field contains different constructions with different promises.

SynthID-Text uses keyed tournament sampling rather than this green-list score increase. The Nature paper studies non-distortionary and distortionary configurations and reports a live quality assessment over nearly 20 million Gemini responses. Those results belong to its tested models, prompts, temperatures, scoring functions, and production system. [Read the SynthID-Text paper](https://www.nature.com/articles/s41586-024-08025-4).

Fixed vocabulary partitions, distribution-preserving sampling, semantic watermarks, and publicly verifiable schemes change the robustness, leakage, quality, and key-management questions. This repository did not implement them.

Anthropic's current support page says its supported Claude text mark does not change meaning, quality, or readability. That is Anthropic's statement. This project did not reproduce or independently validate it. [Read Anthropic's support page](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content).

## What the experiment established

The repository now contains a reproducible path from a biased coin to a keyed toy vocabulary, an explicit model loop, a maintained Transformers adapter, a pinned Gemma run, natural-web controls, paired generation, and editing tests.

For one frozen 24-row Gemma cohort, correct-key marked scores exceeded three controls on average at every supported prefix. At 80 copied tokens, all 24 rows supported the comparison and each paired bootstrap interval stayed above zero.

For the 12-row editing fixture, most named edits reduced mean correct-key evidence. Ten paraphrases passed the declared automatic and non-independent review screens, and all ten reduced z.

For the eight-row bias fixture, a larger delta raised mean z while the measured NLL and repetition proxies also rose.

## What remains unknown

The work does not establish a production detector or a universal cutoff. It does not measure rare false-alarm rates, adaptive attacks, human-perceived quality, another model, another tokenizer, private-key security, or another watermark family.

It cannot detect arbitrary historical AI text. A model must deliberately embed this profile while sampling.

It cannot infer authorship, intent, or policy compliance. Provenance evidence and punishment are separate decisions.

It says nothing about Claude's private algorithm beyond the public problem Anthropic described.

## Reproduce the checked evidence

The environment is pinned for Python `3.12` and `uv`. CPU checks and selected-artifact verification use the root `justfile`.

```console
just setup
just check
just verify-lab-01
just verify-lab-02
just verify-lab-05
just verify-lab-05-examples
just verify-lab-05-lengths
just verify-lab-06
just verify-lab-07
just verify-lab-08
just verify-stage-09
```

Stage 3 and Stage 4 regeneration require their pinned local model caches. The saved Stage 5 through Stage 8 evidence records the model revision, hardware, source commit, configuration hash, achieved lengths, and runtime. Remote generation commands cost money and remain approval-gated.

The final interactive lesson lives at `.agent/diagrams/text-watermarking-stage-9-final-lesson.html`. It embeds no model, external script, font, or network request. Publication remains a separate decision.
