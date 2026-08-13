# Stage 2 publication brief

## Purpose

The article section explains how the program raises the chances of selected next words. It then
shows how a checker finds the same selections in finished text.

Open with the Stage 1 connection. Stage 1 received an abstract hit or miss at each position. Stage
2 shows how the key and recent token history create that result. The checker keeps the Stage 1
values `G`, `T`, the 25 percent baseline, and the z score formula.

The key and cutoff have separate jobs. The key affects which observed tokens count as green hits.
A cutoff can turn a completed score into a decision after calibration. Stage 2 does not set one.

Keep one sentence through the full explanation.

> `Early one morning Jack went up the hill.`

We wrote this example and chose its scores and random numbers. A model did not generate it. These
values are an illustration. The repository keeps a separate fixed trace for code tests.

## Required explanation of the key

The repository author chose `stage-02-public-demo-key-v1`. The model and prompt did not choose it.

SHA-256 turns the key, context, and candidate number into a fixed-length result. The selector sorts
those results. A small change to the input usually gives a different order.

The selector combines the key with the previous four token numbers and each candidate number. It
runs this SHA-256 calculation and selects five of 20 words. The checker can repeat the same work
later.

Changing the key changes the SHA-256 inputs and usually changes their ranking. It does not change
SHA-256, the 25 percent green fraction, the score increase, the z score formula, or a later cutoff.
For the first context, eight words move between the green and red groups when the key changes. Both
keys still select five words.

We print the key in the lesson so readers can reproduce the result. A production operator would
normally generate an unpredictable secret and keep it in protected server storage. The operator
would use a separate public name to identify the secret. The final key size and format depend on
the chosen watermark method and need a security review.

To rebuild the marked sets and count hits, the checker must match the key, token numbering,
selection rule, number of recent words, fraction of words that the selector marks, and counting
rule. It does not need the score increase or the random numbers used during generation. The
operator should still record the score increase because it affects the strength of the pattern and
the cutoff that later tests may support.

The key is separate from the model weights. The operator can change it without retraining the model.
Changing the model or tokenizer can change token numbers, starting scores, text quality, and hit
rates. Tests and useful cutoffs do not automatically transfer to the new setup.

If the operator puts a shared secret in public browser code, every user can read it. Public checking
needs a service that verifies who may submit text, or another method designed for public
verification. Stage 2 builds neither system.

## Figure 1

Show the Stage 1 bridge and the 20-word key comparison.

The figure keeps `Early one morning Jack`, the vocabulary, and the 25 percent fraction fixed. Two
key controls recolor the 20 candidate cards. Each card includes its token number, short hash result,
rank, and green or red label.

Caption text:

> Changing only the key changes the hash ranking and which five words are green. It does not change
> the group size, the Stage 1 formula, or a later decision cutoff.

Alt text:

> Twenty word cards remain in token number order. Five are green and fifteen are red. Controls for
> the lesson key and comparison key move eight words between the green and red groups while the context remains Early one
> morning Jack.

## Figure 2

Use one persistent four-word window for all four generation choices.

The figure keeps the current window, full 20-word green and red grid, sampled word, starting score,
score increase, final chance, random number, and running sentence together. Each press moves the
oldest word out and places the sampled word on the right.

Caption text:

> The program keeps the key fixed while the four-word context moves. Each press shows the selected
> words and the sampled result for that position.

Alt text:

> Four word cards show Early, one, morning, and Jack. Went enters from the right while Early leaves
> from the left. The selected set, score change, chance, random number, and running sentence appear
> below the window.

## Figure 3

Show the teaching key, toy text field, repeatable checker control, and Stage 1 count.

The checker rebuilds the full selected set before each observed word. The final count is 2 hits in
4 positions. The expected count is 1, the z score is 1.1547, and Stage 2 has no cutoff. The
comparison key finds zero hits in this fixed example.

Caption text:

> The checker turns four observed tokens into the Stage 1 values G and T. The key affects which
> tokens count as hits. The z score formula does not use the key.

Alt text:

> A key field and text field appear above four checked results. Went and up are green. The and hill
> are red. Cards show G equals 2, T equals 4, expected hits equals 1, and z equals 1.1547. A sentence
> says that Stage 2 has no cutoff.

## Fixed illustration values

- The first selected set is `Early, went, walked, snow, trail`.
- `Went` ranks first under the lesson key with displayed hash prefix `01d63f53`.
- The comparison key selects `the, hill, path, snow, home` for the first context. Eight words change
  green or red label, and both keys select five words.
- `Went` rises from 22.85% to 46.51% after the program adds 2 to its score.
- `Ran` keeps score 1.9 while its chance falls from 27.91% to 7.69%.
- Before the score increase, 0.30 falls in the range for `walked`. After the increase, it falls in the range for `went`.
- The generated words are `went, up, the, hill`.
- `Went` and `up` are green hits. `The` and `hill` are red results.
- Four checked positions have 2 hits and z score 1.1547.
- The checker finds zero hits with the comparison key `wrong-public-key` in this fixed example. Another key can
  still match words by chance.

Tests in `tests/unit/test_stage_02_lesson.py` recalculate these values.

## Repository appendix

The unchanged file `artifacts/lab-02/trace.json` remains the code test record. It uses fixed token
numbers and includes source and configuration information. The command `just verify-lab-02`
recalculates it.

Keep the test trace out of the sentence walkthrough. Its labels do not form language, and we did
not rename its results to create the sentence.

## Claims the article can make

- The selector chooses five of 20 candidates for each context.
- Adding 2 raises the odds of a selected word against an unchanged word by `exp(2)` before the
  program converts the scores to chances.
- A score increase does not force the sampler to pick a selected word.
- The checker can rebuild the selected sets from observed history when it has the matching setup.
- The key affects the z score by changing which observed tokens count as green hits. It does not appear in the formula.
- Repository tests use the fixed trace to check the Stage 2 implementation.

## Claims the article cannot make

- The sentence is model output or evidence of language quality.
- The article cannot claim that the printed teaching key protects a secret.
- The SHA-256 lesson rule matches an upstream KGW implementation.
- Two hits in four positions measure detection accuracy or support a decision.
- The score identifies the writer, proves that AI wrote the text, or describes a private vendor
  system.

Stage 3 would replace the chosen scores with scores from an approved model and tokenizer. That work
still needs separate approval.
