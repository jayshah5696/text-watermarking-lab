# Stage 7 paired core experiment

All 24 prompts were frozen during Stage 6. Each generated pair shared one prompt and seed.

| Prefix | Complete rows | Marked correct | Model control | Natural web | Comparison key |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 40 | 24 | 1 | 0 | 0 | 0 |
| 80 | 24 | 3 | 0 | 0 | 0 |
| 160 | 21 | 5 | 0 | 0 | 0 |
| 200 | 17 | 4 | 0 | 1 | 0 |
| 400 | 0 | 0 | 0 | 0 | 0 |

## Paired z differences

- prefix 40, `versus_control`, n=24: mean 1.1248, 95% paired bootstrap [0.6317, 1.6333]
- prefix 40, `versus_natural`, n=24: mean 1.0632, 95% paired bootstrap [0.4931, 1.6949]
- prefix 40, `versus_comparison_key`, n=24: mean 0.9707, 95% paired bootstrap [0.4777, 1.4638]
- prefix 80, `versus_control`, n=24: mean 1.8296, 95% paired bootstrap [1.3424, 2.3276]
- prefix 80, `versus_natural`, n=24: mean 1.7538, 95% paired bootstrap [1.3100, 2.1977]
- prefix 80, `versus_comparison_key`, n=24: mean 2.0461, 95% paired bootstrap [1.6131, 2.4792]
- prefix 160, `versus_control`, n=21: mean 2.5205, 95% paired bootstrap [2.1018, 2.9391]
- prefix 160, `versus_natural`, n=21: mean 2.4071, 95% paired bootstrap [1.9274, 2.8693]
- prefix 160, `versus_comparison_key`, n=21: mean 2.4769, 95% paired bootstrap [1.9885, 2.9827]
- prefix 200, `versus_control`, n=17: mean 2.5134, 95% paired bootstrap [1.9164, 3.1297]
- prefix 200, `versus_natural`, n=17: mean 2.6964, 95% paired bootstrap [1.9452, 3.3512]
- prefix 200, `versus_comparison_key`, n=17: mean 2.5423, 95% paired bootstrap [2.0704, 3.0045]

## Teaching rows

- fixed spine: selection 1000
- inconvenient row: selection 1001 at prefix 80 because `watermarked_not_above_control`

This is one pinned 24-row C4 and Gemma experiment. It does not estimate production accuracy, prove authorship, or detect arbitrary AI text.
