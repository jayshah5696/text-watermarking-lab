# Stage 4 annotated Transformers reference trace

This measured local fixture used the pinned GPT-2 model and Transformers watermark
adapter on the CPU. It compares one saved score list with the earlier Stage 3 order.

- Source commit: `20b4860e0d64ca116b173bc42f971d50eb0fef95`
- Config SHA-256: `d9367ca271399011703d3e7c150b6646b6612b034fa485026b33d14e49e48ded`
- Model revision: `openai-community/gpt2@607a30d783dfa663caf39e06633721c8d4cfcd7e`
- Runtime: Python `3.12.7`, PyTorch `2.13.0`,
  Transformers `5.14.1` on `macOS-26.6.1-arm64-arm-64bit`

## One saved score list under two orders

The previous token was ` he` (ID `339`).
Transformers kept 19 choices. The earlier order kept
11 choices. The saved reference token
` was` (ID `373`) had chance
`8.642730%` under the Transformers order and
`8.825517%` under the earlier order.

| Witness | Token piece | ID | Green | Raw preference | Reference chance | Earlier-order chance | Saved choice |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| selected | ` was` | 373 | yes | -125.554153 | 8.642730% | 8.825517% | yes |
| green survivor | ` saw` | 2497 | yes | -123.788116 | 78.591889% | 80.254054% | no |
| red survivor | ` found` | 1043 | no | -125.462326 | 1.311924% | 0.812551% | no |
| green filtered | ` fell` | 3214 | yes | -127.748337 | 0.000000% | 0.568309% | no |
| red filtered | ` took` | 1718 | no | -127.842186 | 0.000000% | 0.000000% | no |

Only the Transformers order produced the saved continuation. The earlier-order values
are calculations on the same saved GPT-2 score list.

## Six copied-continuation results

| Prompt | Watermark | Tokens | Copied IDs | Generation key G/T | z | Comparison key G/T | z |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `stage-02-continuity` | off | 40 | match | 13/39 | 1.201850 | 12/39 | 0.832050 |
| `stage-02-continuity` | on | 40 | match | 17/39 | 2.681051 | 12/39 | 0.832050 |
| `notebook` | off | 40 | match | 12/39 | 0.832050 | 7/39 | -1.016950 |
| `notebook` | on | 40 | match | 21/39 | 4.160251 | 14/39 | 1.571651 |
| `library` | off | 40 | match | 16/39 | 2.311251 | 10/39 | 0.092450 |
| `library` | on | 40 | match | 22/39 | 4.530052 | 10/39 | 0.092450 |

## Detector boundaries

For the continuity reference row, the first copied token ` was` supplies
context. The second token ` greeted` is the first eligible decision. The
generation-key result is 17/39 | 2.681051. The comparison-key result is
12/39 | 0.832050.

The derived alternating sequence has six tokens and five adjacent occurrences.
The library's all-pairs mode gives 3/5 | 1.807392. Its documented
unique-pair option also gives 3/5 | 1.807392 in this pinned run.
Listing the two distinct value pairs explicitly gives 1/
2 | 0.816497. GPT-2 did not generate this
constructed sequence.

The primary checker received no prompt or padding tokens.

## Claim boundary

These records verify one pinned local Transformers profile. Three prompts do not
measure detection accuracy or language quality. A score above the configured cutoff
means only
consistent with this configured watermark and key. It does not prove AI origin,
authorship, or use of a private vendor system.
