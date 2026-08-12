# Start here: implementation handoff

This repository is ready for an implementation agent to get oriented, but implementation has not been approved in the current setup task.

## Canonical source material

Read these local Obsidian files in order. They are the source of truth until the relevant material is deliberately vendored into this repository:

1. `/Users/jshah/Documents/Obsidian Vault/Assitant/Projects/text-watermarking/08-implementation-handoff.md`
   - Exact Stage 0–1 file contracts, APIs, statistics, schemas, fixed tests, artifact rules, commit sequence, and definition of done.
2. `/Users/jshah/Documents/Obsidian Vault/Assitant/Projects/text-watermarking/07-implementation-roadmap.md`
   - The Lego-block learning sequence from biased coin through optional hosted demo.
3. `/Users/jshah/Documents/Obsidian Vault/Assitant/Projects/text-watermarking/06-algorithm-nitty-gritty.md`
   - Token length, vocabulary size, green fraction, logit bias, sampling order, detection, model dependence, and reader FAQ.
4. `/Users/jshah/Documents/Obsidian Vault/Assitant/Projects/text-watermarking/05-model-compute-and-assumptions.md`
   - Model choice, Gemma/Modal assumptions, compute gates, and why the algorithm is not tied to one model.
5. `/Users/jshah/Documents/Obsidian Vault/Assitant/Projects/text-watermarking/index.md`
   - Article premise, Claude framing, scope boundary, project map, and success criteria.

Supporting research, source notes, experiment design, blog outline, and visual assets live beside those files.

## Completed first slice

The first approved implementation contained only:

- Stage 0: reproducible Python/`uv`/`just` repository foundation.
- Stage 1: a CPU-only biased-coin detector with no LLM, model, tokenizer, dataset, cloud service, or GPU.

The first learning question is:

> Why does a small statistical bias become easier to detect as the number of eligible tokens increases?

The handoff is deliberately complete enough that an engineer should not need to make product, architecture, statistics, tooling, or publishing decisions.

## Stage 2 contract

After the user approved the next local teaching block, its exact contract was vendored into
[`docs/stages/02-toy-vocabulary.md`](stages/02-toy-vocabulary.md). That document governs the
toy selector, trace, tests, evidence, and stop boundary. The external roadmap remains context,
not permission for Stage 3 or any model work.

## Current next approval

Stages 0–2 are complete locally. Stage 3 would introduce a real model and tokenizer, so it needs
a separate explicit approval. Model or tokenizer access, downloads, datasets, Modal, GPUs,
GitHub remotes, and publishing remain separate gates.

The next implementation agent must read the matching roadmap and algorithm notes, then prepare or
review a Stage 3 implementation contract before any model work begins. A planning document does
not grant that approval.
