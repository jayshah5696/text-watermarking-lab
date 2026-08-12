# Stage 2 annotated toy-vocabulary trace

This deterministic trace uses a 20-item teaching vocabulary. The SHA-256 selector is
a toy rule, not an upstream KGW pseudorandom function or a deployment key system.

- Source commit: `f7a1690d28cfb48fc825017891b5d3e82eebdd07`
- Config SHA-256: `a342b4d1d347587098763e8f2ff6aa75dd86cbb538dc78200963a631b2a0defa`
- Public development key: `stage-02-public-demo-key-v1`
- Green fraction: `0.25` (5 of 20 IDs)
- Relative boost: for one selected token compared with one unchanged token, `exp(2.0) = 7.389056`; final probabilities are recalculated across all 20 options
- Initial context IDs: `[3, 7, 11, 15]`

## Position 1

Context: `[3, 7, 11, 15]`. Green IDs: `[0, 10, 11, 12, 14]`.
The fixed draw is `0.035331837827`. In the same-context no-boost comparison it selects `0:amber`. After the +2 boost it selects `0:amber`.
Checker count so far: `G=1` selected-set hits among `T=1` scored steps; running z-score `1.732050807569` relative to the 25% toy expectation.

| ID | Label | Green | Raw logit | Adjusted logit | Original probability (no boost) | Probability after +2 boost |
|---:|---|:---:|---:|---:|---:|---:|
| 0 | amber | yes | 1.900000 | 3.900000 | 0.184651252585 | 0.515082492784 |
| 1 | birch | no | 1.700000 | 1.700000 | 0.151179659085 | 0.057072767018 |
| 2 | cobalt | no | 1.500000 | 1.500000 | 0.123775436133 | 0.046727229521 |
| 3 | drift | no | 1.300000 | 1.300000 | 0.101338756038 | 0.038257019815 |
| 4 | ember | no | 1.100000 | 1.100000 | 0.082969156047 | 0.031322198643 |
| 5 | fern | no | 0.900000 | 0.900000 | 0.067929399612 | 0.025644447283 |
| 6 | glow | no | 0.700000 | 0.700000 | 0.055615888501 | 0.020995897637 |
| 7 | harbor | no | 0.500000 | 0.500000 | 0.045534438275 | 0.017189987084 |
| 8 | iris | no | 0.300000 | 0.300000 | 0.037280444940 | 0.014073971070 |
| 9 | juniper | no | 0.100000 | 0.100000 | 0.030522646761 | 0.011522792933 |
| 10 | kite | yes | -0.100000 | 1.900000 | 0.024989829569 | 0.069708835051 |
| 11 | linen | yes | -0.300000 | 1.700000 | 0.020459941982 | 0.057072767018 |
| 12 | moss | yes | -0.500000 | 1.500000 | 0.016751183707 | 0.046727229521 |
| 13 | north | no | -0.700000 | -0.700000 | 0.013714709251 | 0.005177524612 |
| 14 | opal | yes | -0.900000 | 1.100000 | 0.011228654234 | 0.031322198643 |
| 15 | pine | no | -1.100000 | -1.100000 | 0.009193244537 | 0.003470598537 |
| 16 | quartz | no | -1.300000 | -1.300000 | 0.007526792023 | 0.002841485753 |
| 17 | river | no | -1.500000 | -1.500000 | 0.006162416101 | 0.002326411771 |
| 18 | stone | no | -1.700000 | -1.700000 | 0.005045359575 | 0.001904704861 |
| 19 | tide | no | -1.900000 | -1.900000 | 0.004130791045 | 0.001559440445 |

## Position 2

Context: `[7, 11, 15, 0]`. Green IDs: `[2, 4, 9, 11, 17]`.
The fixed draw is `0.112284230651`. In the same-context no-boost comparison it selects `0:amber`. After the +2 boost it selects `1:birch`.
Checker count so far: `G=1` selected-set hits among `T=2` scored steps; running z-score `0.816496580928` relative to the 25% toy expectation.

| ID | Label | Green | Raw logit | Adjusted logit | Original probability (no boost) | Probability after +2 boost |
|---:|---|:---:|---:|---:|---:|---:|
| 0 | amber | no | 1.900000 | 1.900000 | 0.184651252585 | 0.068745673364 |
| 1 | birch | no | 1.700000 | 1.700000 | 0.151179659085 | 0.056284196924 |
| 2 | cobalt | yes | 1.500000 | 3.500000 | 0.123775436133 | 0.340499549209 |
| 3 | drift | no | 1.300000 | 1.300000 | 0.101338756038 | 0.037728425473 |
| 4 | ember | yes | 1.100000 | 3.100000 | 0.082969156047 | 0.228243673501 |
| 5 | fern | no | 0.900000 | 0.900000 | 0.067929399612 | 0.025290119900 |
| 6 | glow | no | 0.700000 | 0.700000 | 0.055615888501 | 0.020705798911 |
| 7 | harbor | no | 0.500000 | 0.500000 | 0.045534438275 | 0.016952474336 |
| 8 | iris | no | 0.300000 | 0.300000 | 0.037280444940 | 0.013879512079 |
| 9 | juniper | yes | 0.100000 | 2.100000 | 0.030522646761 | 0.083966155058 |
| 10 | kite | no | -0.100000 | -0.100000 | 0.024989829569 | 0.009303715176 |
| 11 | linen | yes | -0.300000 | 1.700000 | 0.020459941982 | 0.056284196924 |
| 12 | moss | no | -0.500000 | -0.500000 | 0.016751183707 | 0.006236466785 |
| 13 | north | no | -0.700000 | -0.700000 | 0.013714709251 | 0.005105987147 |
| 14 | opal | no | -0.900000 | -0.900000 | 0.011228654234 | 0.004180428702 |
| 15 | pine | no | -1.100000 | -1.100000 | 0.009193244537 | 0.003422645540 |
| 16 | quartz | no | -1.300000 | -1.300000 | 0.007526792023 | 0.002802225160 |
| 17 | river | yes | -1.500000 | 0.500000 | 0.006162416101 | 0.016952474336 |
| 18 | stone | no | -1.700000 | -1.700000 | 0.005045359575 | 0.001878387698 |
| 19 | tide | no | -1.900000 | -1.900000 | 0.004130791045 | 0.001537893775 |

## Position 3

Context: `[11, 15, 0, 1]`. Green IDs: `[8, 12, 15, 16, 19]`.
The fixed draw is `0.156579670594`. In the same-context no-boost comparison it selects `0:amber`. After the +2 boost it selects `1:birch`.
Checker count so far: `G=1` selected-set hits among `T=3` scored steps; running z-score `0.333333333333` relative to the 25% toy expectation.

| ID | Label | Green | Raw logit | Adjusted logit | Original probability (no boost) | Probability after +2 boost |
|---:|---|:---:|---:|---:|---:|---:|
| 0 | amber | no | 1.900000 | 1.900000 | 0.184651252585 | 0.124897002681 |
| 1 | birch | no | 1.700000 | 1.700000 | 0.151179659085 | 0.102257017062 |
| 2 | cobalt | no | 1.500000 | 1.500000 | 0.123775436133 | 0.083720964587 |
| 3 | drift | no | 1.300000 | 1.300000 | 0.101338756038 | 0.068544928385 |
| 4 | ember | no | 1.100000 | 1.100000 | 0.082969156047 | 0.056119840836 |
| 5 | fern | no | 0.900000 | 0.900000 | 0.067929399612 | 0.045947039550 |
| 6 | glow | no | 0.700000 | 0.700000 | 0.055615888501 | 0.037618254293 |
| 7 | harbor | no | 0.500000 | 0.500000 | 0.045534438275 | 0.030799221667 |
| 8 | iris | yes | 0.300000 | 2.300000 | 0.037280444940 | 0.186324433261 |
| 9 | juniper | no | 0.100000 | 0.100000 | 0.030522646761 | 0.020645335685 |
| 10 | kite | no | -0.100000 | -0.100000 | 0.024989829569 | 0.016902971233 |
| 11 | linen | no | -0.300000 | -0.300000 | 0.020459941982 | 0.013838982367 |
| 12 | moss | yes | -0.500000 | 1.500000 | 0.016751183707 | 0.083720964587 |
| 13 | north | no | -0.700000 | -0.700000 | 0.013714709251 | 0.009276547297 |
| 14 | opal | no | -0.900000 | -0.900000 | 0.011228654234 | 0.007594994555 |
| 15 | pine | yes | -1.100000 | 0.900000 | 0.009193244537 | 0.045947039550 |
| 16 | quartz | yes | -1.300000 | 0.700000 | 0.007526792023 | 0.037618254293 |
| 17 | river | no | -1.500000 | -1.500000 | 0.006162416101 | 0.004168221388 |
| 18 | stone | no | -1.700000 | -1.700000 | 0.005045359575 | 0.003412651036 |
| 19 | tide | yes | -1.900000 | 0.100000 | 0.004130791045 | 0.020645335685 |

## Position 4

Context: `[15, 0, 1, 1]`. Green IDs: `[2, 5, 6, 10, 11]`.
The fixed draw is `0.307310772959`. In the same-context no-boost comparison it selects `1:birch`. After the +2 boost it selects `2:cobalt`.
Checker count so far: `G=2` selected-set hits among `T=4` scored steps; running z-score `1.154700538379` relative to the 25% toy expectation.

| ID | Label | Green | Raw logit | Adjusted logit | Original probability (no boost) | Probability after +2 boost |
|---:|---|:---:|---:|---:|---:|---:|
| 0 | amber | no | 1.900000 | 1.900000 | 0.184651252585 | 0.064326600918 |
| 1 | birch | no | 1.700000 | 1.700000 | 0.151179659085 | 0.052666166412 |
| 2 | cobalt | yes | 1.500000 | 3.500000 | 0.123775436133 | 0.318611740096 |
| 3 | drift | no | 1.300000 | 1.300000 | 0.101338756038 | 0.035303187094 |
| 4 | ember | no | 1.100000 | 1.100000 | 0.082969156047 | 0.028903804956 |
| 5 | fern | yes | 0.900000 | 2.900000 | 0.067929399612 | 0.174857830361 |
| 6 | glow | yes | 0.700000 | 2.700000 | 0.055615888501 | 0.143161483133 |
| 7 | harbor | no | 0.500000 | 0.500000 | 0.045534438275 | 0.015862744487 |
| 8 | iris | no | 0.300000 | 0.300000 | 0.037280444940 | 0.012987316740 |
| 9 | juniper | no | 0.100000 | 0.100000 | 0.030522646761 | 0.010633115615 |
| 10 | kite | yes | -0.100000 | 1.900000 | 0.024989829569 | 0.064326600918 |
| 11 | linen | yes | -0.300000 | 1.700000 | 0.020459941982 | 0.052666166412 |
| 12 | moss | no | -0.500000 | -0.500000 | 0.016751183707 | 0.005835577577 |
| 13 | north | no | -0.700000 | -0.700000 | 0.013714709251 | 0.004777766825 |
| 14 | opal | no | -0.900000 | -0.900000 | 0.011228654234 | 0.003911704630 |
| 15 | pine | no | -1.100000 | -1.100000 | 0.009193244537 | 0.003202632878 |
| 16 | quartz | no | -1.300000 | -1.300000 | 0.007526792023 | 0.002622094028 |
| 17 | river | no | -1.500000 | -1.500000 | 0.006162416101 | 0.002146789018 |
| 18 | stone | no | -1.700000 | -1.700000 | 0.005045359575 | 0.001757642189 |
| 19 | tide | no | -1.900000 | -1.900000 | 0.004130791045 | 0.001439035713 |

## Claim boundary

This four-step trace shows how this public teaching key and toy selection rule
change the probabilities of 20 synthetic options. It also shows how a checker using
the same rule recounts selected-set hits. It does not measure language quality, an
LLM watermark, a false-positive rate, or Anthropic's private implementation.
