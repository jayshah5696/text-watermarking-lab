# Text Watermarking Lab

A from-scratch learning lab for deliberate, generation-time text watermarks. The public
teaching implementation is a KGW-style analogue; it does not reproduce or describe
Anthropic's private Claude implementation.

Stage 1 starts with a biased coin, not an LLM. It isolates the detector's statistical
intuition before tokenization or generation is introduced. The eventual detector will
recognize only this project's deliberately embedded watermark profile and key, not arbitrary
AI-written text.

## Current status

Stage 0 provides the reproducible Python 3.12, `uv`, and `just` project foundation. No detector
experiment, model integration, dataset access, cloud configuration, or GPU operation has run.

```console
just --list
just setup
just check
```

After Stage 1 is implemented, `just lab-01` will be the intentional, clean-commit evidence
command. It is not available as publication evidence until the Stage 1 code is committed.

## Scope boundary

The current slice is CPU-only and contains no model, tokenizer, dataset, model SDK, Modal
resource, or GPU code. A positive result in a later watermark stage will mean only “consistent
with this configured watermark and key,” never “AI-written.”

Start with [docs/START_HERE.md](docs/START_HERE.md). Repository rules are in
[AGENTS.md](AGENTS.md), and the live implementation boundary is in [STATUS.md](STATUS.md).

## License

Original repository code, prose, and diagrams are licensed under the MIT License. Third-party
papers, screenshots, datasets, model weights, and quotations are not relicensed by this
repository.
