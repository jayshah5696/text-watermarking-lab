# Stage 4 publication brief

## Article role

This section answers one question. Does a maintained Transformers adapter perform the same
operations that Stage 3 exposed by hand?

The reader may assume that a model assigns preference numbers to possible next tokens and that a key
selects green token IDs. Stage 4 must define the small layer that passes fixed settings to
Transformers and must make operation order visible. It must show why matching visible settings do
not establish equivalence.

The narrow expected answer is one sentence. The reference adapter uses the same causal parts, but
Transformers 5.14.1 orders its filters and watermark processor differently from the Stage 3 loop.

## Teaching spine

Keep the Stage 3 continuity passage:

`Early one morning Jack went up the hill. At the top he`

Use the first two GPT-2 generation positions as the recorded example. Hold the first position's
model preference list, recent token ID, key, temperature, top-k, top-p, and added value fixed.
Process that list in the Transformers order and in the Stage 3 order. Then follow the first two
selected reference tokens into the saved continuation. Token 1 becomes checker context. Token 2 is
the first eligible green-or-red decision.

The main path must make these transitions visible:

1. the same readable passage becomes GPT-2 token IDs;
2. GPT-2 produces one raw score vector;
3. the reference path applies temperature, top-k, top-p, then the score increase;
4. the Stage 3 order places the score increase first and reverses the two filters;
5. the saved reference draw selects one token;
6. the page appends that exact token to the passage and reveals token 2;
7. copied continuation text becomes GPT-2 IDs again;
8. token 1 supplies context and token 2 supplies the first checker decision;
9. the checker reconstructs green hits with the same complete recipe;
10. a different key changes green membership on the same copied IDs;
11. a separate repeated-pair rule changes how much constructed evidence is counted.

The challenge case is exact equivalence. A shared key and score increase can still produce a
different candidate set, chance, sampled path, and detector profile when the selector, tokenizer,
model, device, or processor order changes.

## Fixture selection

The three passages, base seed, prompt seed rule, generation settings, green fraction, score
increase, keys, and context width come unchanged from Stage 3. They were fixed before the Stage 4
model run.

The canonical roadmap named `openai-community/gpt2` for the cheap Transformers fixture, and the
official reference examples use it. Pin revision
`607a30d783dfa663caf39e06633721c8d4cfcd7e`. Use the model card's MIT license and selected
safetensors size as recorded metadata.

GPT-2 receives the passage directly because it has no LFM2 chat template. This is a declared
profile change. Do not hide it to make the two stages look more similar.

Do not change prompts, seeds, settings, key, model revision, or detector policy after seeing the
scores. Keep weak, negative, repetitive, or awkward results.

## Visual plan

### Figure 1: one raw score vector, two operation orders

Keep candidate rows aligned. First build the Transformers order. Then reset the same GPT-2 values
and show the Stage 3 order on the same chance scale. Mark removed choices without deleting their
row. Restore the Transformers state before revealing the saved draw. Use the selected evidence to
show one token chance and the full number of choices left at each step.

Caption draft:

> Both views start from the same GPT-2 scores and settings. Transformers 5.14.1 filters first and
> adds the watermark score increase afterward. Stage 3 used a different order.

Alt text draft:

> Two aligned rows process one set of token candidates. The upper row applies temperature, top-k,
> top-p, and then the watermark increase. The lower row applies the increase first, followed by
> temperature, top-p, and top-k.

### Figure 2: copied continuation only

Show the complete prompt and generated continuation, then move only the continuation pieces into
the checker. Keep prompt tokens visibly outside the checker boundary. Mark token 1 "context only"
and token 2 "first eligible decision." Show the green count and eligible count before z, then give
the complete narrow interpretation sentence. Put padding validation in a separate gray row or the
technical disclosure.

Caption draft:

> The primary detector receives re-tokenized continuation text. It excludes the prompt and padding,
> then reports counts and scores for one exact watermark profile.

Alt text draft:

> A passage is split into a fixed prompt and generated continuation. Only continuation token pieces
> enter a detector box, which returns a green count, eligible count, and z-score.

### Figure 3: one repeated pair, two counting policies

Alternate the first two copied continuation token IDs three times. Keep all pieces fixed. Number
all five adjacent pair occurrences. Run both documented library modes, then list the distinct pair
values explicitly and score each once. State that the constructed sequence is a calculated checker
example, not model output. If the library flag and explicit value count disagree, show the mismatch
as the Stage 4 failure case.

Caption draft:

> The pinned Transformers option did not collapse the repeated value-equal pairs in this fixture.
> Explicitly listing the distinct pair values changed the count from five checks to two.

Alt text draft:

> Six alternating token pieces form five adjacent pairs. One view counts all five pairs. A second
> view counts only the distinct pair patterns.

The three context-free screenshot targets are the order comparison, prompt exclusion, and repeated
pair policy. Desktop keeps candidate rows aligned. Mobile stacks operations but preserves token
identity and numbered order.

## Evidence contract

The selected artifact must record every value required by the three figures. The page and blog note
may use only values from `artifacts/lab-04/trace.json`, values independently derived from that
artifact, and external facts linked to primary sources.

The source commit and configuration hash identify the code and fixed inputs. Package versions,
model revision, device, and serialized watermark profile identify the reference runtime. The
verifier must regenerate selected output from the local model cache.

## Expected result before the run

After the filters, the Transformers watermark step should add 2 to each surviving green token's
model preference number. The checker should rebuild its green counts from copied continuation IDs.
For the saved first generation step, applying the recorded Transformers operations should reproduce
the preference list returned by `generate()`. The alternate Stage 3 order may change available
choices or final chances, but no direction or size is assumed. Some recorded counts may fall near or
below the 25 percent baseline. Three passages cannot estimate detection accuracy.

## Blog handoff requirements

`blog/notes/04-transformers-reference.md` must include the article subsection, the expected result
above, the observed six-row result, one complete first-step order comparison, the repeated-pair
case, the three figure captions and alt text, allowed claims, prohibited claims, and the transition
to Stage 5.

Allowed claims:

- the pinned Transformers version used its recorded maintained processor order;
- the local CPU adapter generated the recorded continuations and detector counts;
- primary detection excluded prompt and padding tokens;
- the Stage 1 z formula reproduced the library z-score from the same counts;
- the pinned library's repeated-pair flag did or did not match an explicit value-based distinct-pair
  count in the fixed fixture.

Prohibited claims:

- the Stage 3 MLX profile and Stage 4 Transformers profile are equivalent;
- three prompts measure detection accuracy, text quality, or a useful cutoff;
- a positive score proves AI origin, authorship, or use of a private vendor system;
- GPT-2 represents current model quality;
- local CPU behavior automatically matches CUDA or another package version.
