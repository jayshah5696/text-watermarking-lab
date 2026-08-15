# Text Watermarking Lab

A from-scratch learning lab for deliberate, generation-time text watermarks. The public
teaching implementation is a KGW-style analogue; it does not reproduce or describe
Anthropic's private Claude implementation.

Stage 1 starts with a biased coin. Stage 2 uses 20 visible token IDs and a toy keyed selector.
Stage 3 puts a separate MLX selector inside an explicit LFM2 350M generation loop. Stage 4 checks
that mental model against the maintained Transformers 5.14.1 watermark path with a pinned GPT-2
fixture on the local CPU. Together they connect the detector statistic, keyed membership, real
model scores, sampling, operation order, and copied-text checking. The detector recognizes only
this project's deliberately embedded watermark profile and key, not arbitrary
AI-written text.

## Current status

Stages 0 through 4 provide the reproducible Python 3.12 foundation, the biased-coin detector, a
deterministic toy-vocabulary trace, paired local MLX continuations, and a pinned Transformers
reference adapter.
Stage 4 evidence was generated from clean source commit `20b4860` with the pinned
`openai-community/gpt2` revision.

```console
just --list
just setup
just check
just verify-lab-01
just verify-lab-02
just verify-lab-03
just verify-lab-04
```

`just lab-01` is the intentional, clean-commit evidence command. It refuses a dirty worktree,
uses `configs/lab_01.toml`, writes ignored raw rows, and regenerates the selected artifacts.
`just lab-02` follows the same clean-source rule for its deterministic trace.
`just lab-03` downloads the pinned checkpoint when absent, uses the local Apple GPU through MLX,
and records six paired continuations.
`just lab-04` downloads only the approved pinned GPT-2 model and tokenizer when absent, runs six
local CPU continuations, and records the reference order and copied-text detector checks.

```console
just lab-01
just verify-lab-01
just lab-02
just verify-lab-02
just lab-03
just verify-lab-03
just lab-04
just verify-lab-04
```

## Scope boundary

The current slice has no dataset, Modal resource, hosted endpoint, production secret, or public
deployment. Stage 3 uses one approved local Apple GPU fixture. Stage 4 uses one approved local CPU
fixture. Three passages do not establish accuracy, prose quality, or a generally useful cutoff. A
result above the configured Stage 4 cutoff means only "consistent with this configured watermark
and key," never "AI-written."

Start with [docs/START_HERE.md](docs/START_HERE.md). Repository rules are in
[AGENTS.md](AGENTS.md), and the live implementation boundary is in [STATUS.md](STATUS.md).

## License

Original repository code, prose, and diagrams are licensed under the MIT License. Third-party
papers, screenshots, datasets, model weights, and quotations are not relicensed by this
repository.
