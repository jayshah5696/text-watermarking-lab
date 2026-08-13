# Check the hand-written loop against Transformers

Stage 3 exposed each operation in a small generation loop. Stage 4 asks whether the same mental
model survives when a maintained library owns the loop.

The answer is narrow. The same causal parts remain visible: a key selects a green group, model
preference numbers change, a random draw selects a token, and copied text becomes a green count.
The exact recipes are not interchangeable. Transformers 5.14.1 applies temperature, top-k, and
top-p before its watermark processor. Stage 3 applied its score increase before temperature,
top-p, and top-k.

The local CPU fixture is `openai-community/gpt2` at revision
`607a30d783dfa663caf39e06633721c8d4cfcd7e`. It receives each passage directly. Unlike the Stage 3
chat checkpoint, GPT-2 has no instruction wrapper in this run.

## One saved preference list

The continuity passage ends with `he`. Its final token is GPT-2 ID 339. Both order calculations
start from the same 50,257 GPT-2 preference numbers, key, temperature `0.8`, top-k `40`, top-p
`0.95`, and added value `2.0`.

Transformers keeps 40 choices after top-k and 19 after top-p, then applies the watermark change.
The earlier Stage 3 order starts by changing all 50,257 preference numbers, keeps 11 after top-p,
and still has 11 after top-k. On this saved list, the selected piece ` was`, ID 373, has an
`8.642730%` chance in the Transformers order and an `8.825517%` chance in the earlier order. Only
the Transformers order generated the saved continuation.

The recorded draw selects ` was`. The next piece is ` greeted`, ID 21272. These two pieces must
stay together in the explanation: ` was` becomes detector context, and ` greeted` is the first
eligible green-or-red decision.

## Copy only the continuation into the checker

The primary detector receives the copied continuation IDs. It does not receive the prompt or left
padding. Each 40-token continuation therefore has 39 eligible positions when the context width is
one. The Stage 1 count formula reproduces every library z score from the same counts.

| Passage | Condition | Generation-key G/T | z | Comparison-key G/T | z |
| --- | --- | ---: | ---: | ---: | ---: |
| continuity | control | 13/39 | 1.2019 | 12/39 | 0.8321 |
| continuity | watermark | 17/39 | 2.6811 | 12/39 | 0.8321 |
| notebook | control | 12/39 | 0.8321 | 7/39 | -1.0170 |
| notebook | watermark | 21/39 | 4.1603 | 14/39 | 1.5717 |
| library | control | 16/39 | 2.3113 | 10/39 | 0.0925 |
| library | watermark | 22/39 | 4.5301 | 10/39 | 0.0925 |

The configured Boolean uses `z > 3.0`. The continuity watermark row falls below that cutoff even
though the adapter generated it with the watermark. The notebook and library watermark rows rise
above it. With only three passages, neither result estimates detection accuracy or a false-alarm
rate. Falling below the cutoff does not prove that text is human-written or unwatermarked.

## The repeated-pair option did not do what its name suggested

A separate calculated fixture alternates the first two copied IDs three times:

`373, 21272, 373, 21272, 373, 21272`

This makes five adjacent pair occurrences but only two distinct pair values. In the pinned
Transformers run, both `ignore_repeated_ngrams=False` and `True` reported `3/5`, with z `1.8074`.
An explicit value-based list counted one green pair among two distinct pairs, with z `0.8165`.
This sequence is not GPT-2 output. It is a fixed compatibility check showing why an adapter must
test maintained behavior instead of trusting an option name.

## Figure handoff

Figure 1 caption: Both views start from the same GPT-2 preference numbers and settings.
Transformers 5.14.1 filters first and applies the watermark change afterward. The earlier Stage 3
order changes the numbers first.

Figure 1 alt text: Two aligned operation sequences process one saved GPT-2 preference list. The
same five witness tokens stay in place while survival and final chance change.

Figure 2 caption: The primary detector receives re-tokenized continuation text. It excludes the
prompt and padding, uses the first continuation token as context, and starts counting at token 2.

Figure 2 alt text: A fixed prompt remains outside a checker box. The copied continuation enters it,
with token 1 marked context only and token 2 marked first eligible decision.

Figure 3 caption: The pinned repeated-pair option left five checks in this fixture. Explicitly
listing distinct adjacent pair values reduced the count to two.

Figure 3 alt text: Six alternating token pieces make five adjacent pair occurrences but only two
distinct pair patterns.

## Claim boundary

This selected local run can support claims about the pinned model revision, package version,
processor order, copied-text counts, prompt exclusion, and repeated-pair mismatch. It cannot show
that the Stage 3 and Stage 4 profiles are equivalent, that prose quality stayed fixed, or that a
score proves AI origin, authorship, or use of a private system.

Stage 5 must decide its own model and compute boundary before any larger experiment begins.
