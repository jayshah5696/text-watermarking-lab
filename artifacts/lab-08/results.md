# Stage 8 editing and bias trade-offs

## Editing summary

| Edit | Rows | Scored | Mean z change | Cutoff crossings | Mean length ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `normalization` | 12 | 12 | 0.0000 | 2 | 0.9986 |
| `homoglyph_1` | 12 | 12 | -0.0217 | 1 | 1.0448 |
| `homoglyph_5` | 12 | 12 | -0.9311 | 0 | 1.2183 |
| `deletion_10` | 12 | 12 | -0.3248 | 0 | 0.8980 |
| `deletion_30` | 12 | 12 | -0.9960 | 1 | 0.7021 |
| `mixing_25` | 12 | 12 | -0.6712 | 0 | 1.0012 |
| `mixing_50` | 12 | 12 | -1.3424 | 0 | 1.0088 |
| `paraphrase` | 12 | 12 | -1.7105 | 0 | 0.9636 |

## Bias summary

| Delta | Rows | Scored | Mean z | Cutoff crossings | Mean NLL | Mean copied tokens |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8 | 8 | 0.2923 | 0 | 0.5004 | 232.5 |
| 2 | 8 | 8 | 2.1761 | 1 | 0.5415 | 265.8 |
| 3 | 8 | 8 | 2.4684 | 3 | 0.5783 | 271.8 |

This is one pinned 12-row editing fixture and 8-row bias sweep. It does not establish universal robustness, human quality, authorship, or generic AI origin.
