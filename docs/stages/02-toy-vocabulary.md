# Stage 2 implementation contract: toy vocabulary

## Authorization

This stage is approved for local CPU-only implementation. It must not download or import a
model, tokenizer, dataset, model SDK, or cloud package. It must not use a GPU, create a remote,
publish an artifact, or claim compatibility with Anthropic or an upstream KGW implementation.

## Question

How can a key gently change token choice without forcing a fixed sentence?

## Locked default

- The vocabulary contains the 20 labels in `configs/lab_02.toml`, with IDs 0 through 19.
- The green fraction is `gamma=0.25`, so each context selects exactly five IDs.
- The green logit bias is `delta=2.0`.
- The context contains the four most recent IDs.
- The public development key is `stage-02-public-demo-key-v1`.
- The sampler uses `random.Random(20260811)` and records each draw.
- The trace generates four positions from initial context `[3, 7, 11, 15]`.
- Raw logits remain fixed across positions so the learner can isolate the green-set change.

## Toy selector

For every candidate token ID, hash this exact ASCII string with SHA-256:

```text
lab-02|v1|<development-key>|<comma-separated-context-ids>|<candidate-token-id>
```

Sort candidates by the 32 digest bytes and then by token ID. The five lowest candidates are
green. Return the selected IDs in ascending numeric order.

This is a teaching rule. Later model work must use and pin its approved upstream implementation.
Nothing may import this selector as a reference KGW pseudorandom function.

## Generation and replay

At each position:

1. Select the green IDs from the current four-ID context.
2. Add `delta` only to the green logits.
3. Compute stable softmax probabilities before and after the bias.
4. Use one visible random draw for both the plain counterfactual and the biased sample.
5. Append only the biased sample to the generated history.
6. Rebuild the green set from the observed history and update `G`, `T`, and the Stage 1 z-score.

The plain token is a same-context counterfactual. It is not a separate generated control sequence.

## Evidence and exit gate

`just lab-02` must refuse a dirty Git worktree and write deterministic `trace.json` and
`annotated_trace.md` files under `artifacts/lab-02/`. `just verify-lab-02` must rebuild both
files, verify the exact configuration bytes at the recorded source commit, and fail on a mismatch.

Stage 2 is complete when a reader can follow every green-set decision, probability, random draw,
sampled token, and detector score by hand. Stop before Stage 3 model or tokenizer integration.

The final-blog role, figure inventory, captions, alt text, allowed claims, and decision to preserve
the locked fixture are recorded in [`02-publication-brief.md`](02-publication-brief.md).
