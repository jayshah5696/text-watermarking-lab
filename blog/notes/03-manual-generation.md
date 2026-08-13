# Put the score change inside a real generation loop

Stage 2 started with scores that we wrote by hand. Stage 3 keeps the same basic question but gets
the scores from a real causal language model.

The fixture is `mlx-community/LFM2-350M-4bit` at revision
`18dc72abf3b2337f9123cfd6eeeb58dfa7947066`. MLX-LM runs it on the local Apple GPU. The model weights
stay quantized, while the final next-token scores move to float32 before the lesson changes them.

The checkpoint is post-trained for chat. Every fixed passage is placed after this instruction.

> Continue the passage with one short paragraph. Return only the continuation.

The pinned tokenizer then adds its chat control tokens. The artifact records all 36 model-input
tokens for the continuity passage, including the instruction and control tokens. The lesson keeps
the passage visible and puts the extra framing in a disclosure.

An earlier unselected diagnostic omitted the chat template. It produced repetitive text. We fixed
that input error before choosing evidence. The three passages, seeds, keys, green fraction, score
increase, and sampling settings did not change.

## The whole loop

The program performs one small operation at a time.

1. The tokenizer turns the complete model input into token IDs.
2. LFM2 returns one score for every possible next token.
3. The Stage 3 selector uses the previous token ID and public development key to mark exactly 25
   percent of the 65,536 token IDs green.
4. The score-increase path adds 2 to the green scores.
5. Temperature, top-p, and top-k narrow the choices.
6. The program converts the remaining scores to chances and samples one token.
7. It appends that token and repeats with the model cache.

The selector is the lab's `mlx-mix-v1` profile. It uses vectorized 32-bit mixing so MLX can mark the
full vocabulary without a Python loop. It is not a cryptographic design, an upstream LFM2 feature,
or a private vendor method.

The control path and score-increase path start with the same prompt-specific MLX random seed. Their
histories can diverge after a changed probability distribution produces a different token.

## One token in full

The continuity passage is:

> Early one morning Jack went up the hill. At the top he

At the first position, the raw scores are identical in the control and score-increase paths. The
generation key marks `Jack` green. Its score changes from 14.6875 to 16.6875. Temperature 0.8 changes
that to 20.859375. After top-p and top-k, its final chance is 18.5816 percent. The seeded sampler
chooses `Jack`, token ID 30604.

| Token piece | ID | Raw score | Green | Requested increase | Score after increase | Final chance |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| `As` | 2777 | 15.1875 | yes | 2.0 | 17.1875 | 34.7150% |
| `he` | 773 | 14.8125 | yes | 2.0 | 16.8125 | 21.7241% |
| `Jack` | 30604 | 14.6875 | yes | 2.0 | 16.6875 | 18.5816% |
| `The` | 1098 | 13.5000 | yes | 2.0 | 15.5000 | 4.2114% |
| `He` | 3259 | 15.3125 | no | 0.0 | 15.3125 | 3.3315% |

The control path also chooses `Jack` with the same seed, but its chance is 11.6422 percent. One
matching draw does not mean the distributions are equal. The paths diverge on later tokens.

A green token is not guaranteed to survive. A fixed-vector test gives one green candidate a score
of -5, adds 2, and then removes it with top-k. The increase changes its chance before filtering. It
does not force the sampler to keep or choose it.

## Copy and check the continuation

The score-increase continuation begins:

> Jack climbed slowly, his boots sinking slightly into the soft snow-covered earth.

The checker copies the complete 40-token continuation and tokenizes it again. All six continuations
round-trip to the same token IDs in this selected run. The first copied token supplies context and
is not counted. That leaves 39 eligible positions.

At each eligible position, the checker rebuilds the green group from the preceding copied token.
It counts the observed token when that token belongs to the group. The same key used during
generation and the comparison key check the same copied token IDs.

## Measured local results

The 25 percent random baseline averages 9.75 green hits across 39 eligible positions.

| Passage | Score increase | Same-key G/T | Same-key z | Comparison-key G/T | Comparison-key z |
| --- | --- | ---: | ---: | ---: | ---: |
| continuity | off | 8/39 | -0.6472 | 6/39 | -1.3868 |
| continuity | on | 21/39 | 4.1603 | 7/39 | -1.0170 |
| notebook | off | 10/39 | 0.0925 | 14/39 | 1.5717 |
| notebook | on | 26/39 | 6.0093 | 10/39 | 0.0925 |
| library | off | 11/39 | 0.4623 | 10/39 | 0.0925 |
| library | on | 17/39 | 2.6811 | 13/39 | 1.2019 |

With the same key used during generation, the checker counted 21 of 39 eligible copied tokens as
green for the continuity passage. The first copied token supplies context and is not counted. A 25
percent random baseline averages 9.75 green hits here. `z = 4.1603` measures the difference in units
of the usual random spread. Stage 3 has no tested cutoff, so this number does not produce a yes or no
result.

The three score-increase rows have more same-key hits than their paired control rows in this fixed
run. That is measured evidence for this pinned local profile. Three passages cannot measure
detection accuracy, a false-positive rate, prose quality, or a useful cutoff. The comparison key
also matches some tokens by chance.

## Figure handoff

Figure 1 caption: The LFM2 tokenizer turns the fixed instruction, continuity passage, and chat
control tokens into 36 model-input token IDs before the model calculates next-token scores.

Figure 1 alt text: A fixed passage sits inside one user instruction and a chat-template shell. A row
shows tokenizer pieces with IDs. Leading spaces are visible on ordinary word pieces, and special
control pieces are marked separately.

Figure 2 caption: The manual loop adds 2 to green candidate scores before temperature, top-p, and
top-k. A seeded draw chooses one surviving token and the cache carries that token into the next
model call.

Figure 2 alt text: Six numbered panels follow the candidate `Jack` from a model score of 14.6875 to
a green score of 16.6875, through filtering to an 18.5816 percent chance, then into the sampled
history.

Figure 3 caption: Paired paths use the same passage and starting random seed. The checker then
re-tokenizes the copied continuation and compares the same generation key with a separate key.

Figure 3 alt text: Control and score-increase continuations appear above checker cards. The
generation-key result is 21 of 39 with z 4.1603. The comparison-key result is 7 of 39 with z
-1.0170. A note says that Stage 3 has no tested cutoff.

## What Stage 4 must ask

Stage 3 exposes the model call, score change, filters, sampling, cache, and copied-text checker. It
does not show that this lab profile matches a full library adapter. Stage 4 must define a supported
reference profile and test equivalence separately rather than assume it.
