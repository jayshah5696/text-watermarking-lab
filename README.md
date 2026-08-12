# Text Watermarking Lab

A from-scratch learning lab for deliberate, generation-time text watermarks. The public
teaching implementation is a KGW-style analogue; it does not reproduce or describe
Anthropic's private Claude implementation.

Stage 1 starts with a biased coin, not an LLM. It isolates the detector's statistical
intuition before tokenization or generation is introduced. The eventual detector will
recognize only this project's deliberately embedded watermark profile and key, not arbitrary
AI-written text.

## Current status

Stages 0–1 provide the reproducible Python 3.12 foundation and the CPU-only biased-coin detector.
The Stage 1 evidence run remains pending until its code is committed and the worktree is clean.

```console
just --list
just setup
just check
```

`just lab-01` is the intentional, clean-commit evidence command. It refuses a dirty worktree,
uses `configs/lab_01.toml`, writes ignored raw rows, and regenerates the selected artifacts.

```console
just lab-01
just verify-lab-01
```

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
