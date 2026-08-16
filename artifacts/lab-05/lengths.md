# Stage 5 natural-length evidence ladder

Normal end-token behavior remained active. Caps are safety limits, not achieved lengths.

| Prompt | Cap | Condition | Achieved copied tokens | Stop | G/T | z | p-value | z > 3 |
| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `story-map` | 200 | control | 200 | token_limit | 49/199 | -0.1228 | 0.504776 | no |
| `story-map` | 200 | watermarked | 200 | token_limit | 71/199 | 3.4788 | 0.000225 | yes |
| `field-journal` | 200 | control | 200 | token_limit | 53/199 | 0.5321 | 0.417545 | no |
| `field-journal` | 200 | watermarked | 200 | token_limit | 63/199 | 2.1691 | 0.025008 | no |
| `repair-guide` | 200 | control | 200 | token_limit | 55/199 | 0.8595 | 0.312418 | no |
| `repair-guide` | 200 | watermarked | 200 | token_limit | 67/199 | 2.8240 | 0.003119 | no |
| `festival-history` | 200 | control | 200 | token_limit | 58/199 | 1.3506 | 0.156544 | no |
| `festival-history` | 200 | watermarked | 200 | token_limit | 70/199 | 3.3151 | 0.000458 | yes |
| `coastal-expedition` | 400 | control | 400 | token_limit | 91/399 | -1.0116 | 0.739371 | no |
| `coastal-expedition` | 400 | watermarked | 399 | token_limit | 148/398 | 5.6144 | 0.000000 | yes |
| `city-water-system` | 400 | control | 400 | token_limit | 98/399 | -0.2023 | 0.512862 | no |
| `city-water-system` | 400 | watermarked | 400 | token_limit | 123/399 | 2.6880 | 0.005026 | no |
| `archive-mystery` | 400 | control | 400 | token_limit | 109/399 | 1.0694 | 0.241413 | no |
| `archive-mystery` | 400 | watermarked | 400 | token_limit | 121/399 | 2.4568 | 0.010719 | no |
| `community-radio` | 400 | control | 400 | token_limit | 98/399 | -0.2023 | 0.512862 | no |
| `community-radio` | 400 | watermarked | 400 | token_limit | 158/399 | 6.7346 | 0.000000 | yes |
| `generation-ship` | 800 | control | 768 | token_limit | 191/767 | -0.0625 | 0.501243 | no |
| `generation-ship` | 800 | watermarked | 800 | token_limit | 276/799 | 6.2297 | 0.000000 | yes |
| `river-restoration` | 800 | control | 800 | token_limit | 222/799 | 1.8178 | 0.061000 | no |
| `river-restoration` | 800 | watermarked | 800 | token_limit | 298/799 | 8.0271 | 0.000000 | yes |
| `mountain-clinic` | 800 | control | 614 | token_limit | 173/613 | 1.8422 | 0.057634 | no |
| `mountain-clinic` | 800 | watermarked | 654 | token_limit | 244/653 | 7.2977 | 0.000000 | yes |
| `lost-language` | 800 | control | 793 | token_limit | 207/792 | 0.7385 | 0.353315 | no |
| `lost-language` | 800 | watermarked | 698 | token_limit | 247/697 | 6.3638 | 0.000000 | yes |

Green and red token pieces are stored in `lengths.json`. Green means keyed membership,
not semantic quality. The first copied token is unscored context.

Probability under the configured no-watermark baseline of evidence at least this extreme; not the probability that the text is watermarked.

Twelve varied prompts show natural achieved lengths. They do not isolate a causal length effect or estimate detector accuracy.
