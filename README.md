# Text Watermarking Lab

A from-scratch learning lab for deliberate, generation-time text watermarks. The public
teaching implementation is a KGW-style analogue; it does not reproduce or describe
Anthropic's private Claude implementation.

Stage 1 starts with a biased coin. Stage 2 uses 20 visible token IDs and a toy keyed selector.
Together they isolate the detector's statistics and the generation step before a model or
tokenizer is introduced. The eventual detector will
recognize only this project's deliberately embedded watermark profile and key, not arbitrary
AI-written text.

## Current status

Stages 0–2 provide the reproducible Python 3.12 foundation, the CPU-only biased-coin detector,
and a deterministic keyed toy-vocabulary trace. Stage 2 evidence was generated from clean
source commit `f7a1690`.

```console
just --list
just setup
just check
just verify-lab-01
just verify-lab-02
```

`just lab-01` is the intentional, clean-commit evidence command. It refuses a dirty worktree,
uses `configs/lab_01.toml`, writes ignored raw rows, and regenerates the selected artifacts.
`just lab-02` follows the same clean-source rule for its deterministic trace.

```console
just lab-01
just verify-lab-01
just lab-02
just verify-lab-02
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
