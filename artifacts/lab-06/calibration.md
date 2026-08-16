# Stage 6 natural-web calibration

The unchanged Stage 5 checker scored 1,000 frozen C4 realnewslike continuations.
C4 is natural-web text, not verified human authorship.

## Selection

- source rows scanned: 2479
- calibration rows: 1000
- frozen paired-test rows: 24
- rejected `code_dump`: 0
- rejected `duplicate_text`: 0
- rejected `low_letter_fraction`: 0
- rejected `obvious_list`: 4
- rejected `too_short`: 1451

## Recorded score distribution

- all-pair rows above strict z > 3: 4/1000
- distinct-pair rows above strict z > 3: 1/1000
- all-pair z quantiles, q05 / median / q95 / q99: -1.8209 / 0.0289 / 1.8787 / 2.4568
- first selected row: 81/399, z -2.1678
- maximum row: selection 558, dataset row 1383, 132/399, z 3.7286

The observed fraction describes this frozen sample and profile. It is not a production false-alarm rate.

One thousand rows can resolve observed counts in steps of 1/1000 and cannot validate one-in-100,000 behavior.
