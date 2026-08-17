# Text Watermarking Lab

A from-scratch learning lab for deliberate, generation-time text watermarks. The public
teaching implementation is a KGW-style analogue; it does not reproduce or describe
Anthropic's private Claude implementation.

Stage 1 starts with a biased coin. Stage 2 uses 20 visible token IDs and a toy keyed selector.
Stage 3 puts a separate MLX selector inside an explicit LFM2 350M generation loop. Stage 4 checks
that mental model against the maintained Transformers 5.14.1 watermark path with a pinned GPT-2
fixture on the local CPU. Stage 5 carries the adapter to Gemma 4 E2B in BF16. Stage 6 freezes and
scores a 1,000-row natural-web background. Stage 7 runs 24 frozen paired prompts against three
controls. Stage 8 measures named edits and a delta 1/2/3 bias sweep. Stage 9 assembles the final
article source and one continuous interactive article from those committed results. The detector
recognizes only this project's deliberately embedded watermark profile and key, not arbitrary
AI-written text.

## Current status

Stages 0 through 9 are complete locally. Stage 7 measured 24 frozen paired Gemma prompts. At 80
copied tokens, correct-key marked z exceeded paired model-control z by mean `1.8296`, natural-web z
by `1.7538`, and comparison-key z by `2.0461`; individual rows still overlapped. Stage 8 found mean
z changes of `-0.9960` after 30 percent deletion, `-1.3424` after 50 percent mixing, and `-1.7105`
after paraphrase in its 12-row fixture. Its eight-row bias sweep raised mean z from `0.2923` at
delta 1 to `2.4684` at delta 3 while model-based NLL and repetition proxies also rose. Stage 9 adds
no experiment. It assembles the checked manuscript in [`blog/article.md`](blog/article.md) and the
canonical interactive article in
[`blog/how-text-watermarks-hide-in-plain-sight.html`](blog/how-text-watermarks-hide-in-plain-sight.html).
Nothing has been published.

```console
just --list
just setup
just check
just verify-lab-01
just verify-lab-02
just verify-lab-03
just verify-lab-04
just verify-lab-05
just verify-lab-06
just verify-lab-07
just verify-lab-08
just verify-final-article
```

`just lab-01` is the intentional, clean-commit evidence command. It refuses a dirty worktree,
uses `configs/lab_01.toml`, writes ignored raw rows, and regenerates the selected artifacts.
`just lab-02` follows the same clean-source rule for its deterministic trace.
`just lab-03` downloads the pinned checkpoint when absent, uses the local Apple GPU through MLX,
and records six paired continuations.
`just lab-04` downloads only the approved pinned GPT-2 model and tokenizer when absent, runs six
local CPU continuations, and records the reference order and copied-text detector checks.
`just lab-05` is the explicit cost-incurring Modal command. It is not part of ordinary verification.
`just verify-lab-05` validates the original smoke evidence locally without a model, GPU, network,
or cloud call. `just verify-lab-05-examples` independently validates the selected ten-pair
comparison. `just verify-lab-05-lengths` validates the natural-length and token-color artifact.
`just verify-lab-06` reconstructs the selected manifest and all 1,000 scores without accessing C4,
a model, GPU, network, or cloud. `just verify-lab-07` and `just verify-lab-08` rebuild their selected
evidence locally. `just verify-final-article` rebuilds the continuous HTML article and checks every
embedded evidence payload against committed artifacts. The corresponding model-backed `lab-*`
commands incur
cloud cost and require approval.

```console
just lab-01
just verify-lab-01
just lab-02
just verify-lab-02
just lab-03
just verify-lab-03
just lab-04
just verify-lab-04
just verify-lab-05
just verify-lab-06
just verify-lab-07
just verify-lab-08
just verify-final-article
```

## Scope boundary

The current slice includes one pinned C4 validation shard and compact identifiers, hashes, scores,
and excerpts. It does not republish full articles. There is no hosted endpoint, production secret,
or public deployment. Stage 3 uses one approved local Apple GPU fixture. Stage 4 uses one approved
local CPU fixture. Stage 5 used disposable Modal L4 invocations with no Secret and no persistent
Volume. Stage 6 used detector-only L4 invocations with no model weights or generation calls. Stages 7 and
8 used bounded, approved L4 generation invocations. Stage 9 used no model, dataset, GPU, cloud, or
network operation for experimental evidence. The committed demo key is public for reproducibility
and provides no secrecy. The private-key path defines how a host would
inject process-local key material; it does not claim production key management. Three passages do
not establish accuracy, prose quality, or a generally useful cutoff. A result above a configured
cutoff means only "consistent with this configured watermark and key," never "AI-written."

Start with [docs/START_HERE.md](docs/START_HERE.md). Repository rules are in
[AGENTS.md](AGENTS.md), and the live implementation boundary is in [STATUS.md](STATUS.md).

## License

Original repository code, prose, and diagrams are licensed under the MIT License. Third-party
papers, screenshots, datasets, model weights, and quotations are not relicensed by this
repository.
