# Stage 3 annotated manual-generation trace

This measured local fixture used the pinned LFM2 model and tokenizer through MLX. It
records where the configured score increase occurs in one explicit loop.

- Source commit: `2f082b7f63853811881c0f23c2d7022e8e5dbc3b`
- Config SHA-256: `694a3d09ea341165cef5061360800e43957d2055993f7140b514ebf07ff3117f`
- Model revision: `mlx-community/LFM2-350M-4bit@18dc72abf3b2337f9123cfd6eeeb58dfa7947066`
- Runtime: Python `3.12.7`, MLX `0.32.0`, MLX-LM `0.31.3` on `macOS-26.6.1-arm64-arm-64bit`

## First recorded token from the continuity prompt

Prompt: `Early one morning Jack went up the hill. At the top he`

The model received 36 token IDs. The previous token ID used by the
green-group calculation was `708`. Top-p kept
105 candidates, and top-k then kept
40 candidates.

| Token piece | ID | Model score | Green | Increase | After increase | After temperature | Final chance | Chosen |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `As` | 2777 | 15.187500 | yes | 2.0 | 17.187500 | 21.484375 | 34.714988% | no |
| `he` | 773 | 14.812500 | yes | 2.0 | 16.812500 | 21.015625 | 21.724084% | no |
| `Jack` | 30604 | 14.687500 | yes | 2.0 | 16.687500 | 20.859375 | 18.581595% | yes |
| `The` | 1098 | 13.500000 | yes | 2.0 | 15.500000 | 19.375000 | 4.211406% | no |
| `He` | 3259 | 15.312500 | no | 0.0 | 15.312500 | 19.140625 | 3.331497% | no |

The seeded sampler chose `Jack` (ID `30604`) with final chance `18.581595%`. The loop appended that ID before asking the model for the next score list.

## Paired local results

| Prompt | Score increase | Tokens | Copied IDs match | Same-key G/T | Same-key z | Comparison-key G/T | Comparison-key z |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `stage-02-continuity` | off | 40 | yes | 8/39 | -0.647150 | 6/39 | -1.386750 |
| `stage-02-continuity` | on | 40 | yes | 21/39 | 4.160251 | 7/39 | -1.016950 |
| `notebook` | off | 40 | yes | 10/39 | 0.092450 | 14/39 | 1.571651 |
| `notebook` | on | 40 | yes | 26/39 | 6.009252 | 10/39 | 0.092450 |
| `library` | off | 40 | yes | 11/39 | 0.462250 | 10/39 | 0.092450 |
| `library` | on | 40 | yes | 17/39 | 2.681051 | 13/39 | 1.201850 |

## Claim boundary

These six continuations show deterministic replay for this pinned local fixture. Three
prompts do not measure detection accuracy or language quality. Stage 3 has no tested
cutoff, and no score proves AI origin, authorship, or use of a private vendor system.
