# Use a key to change the chances in one sentence

Stage 2 shows how the program can raise the chance of selected words during generation. It also
shows how a checker can find those selections in finished text.

The lesson uses this sentence.

> Early one morning Jack went up the hill.

We wrote the example and chose its scores and random numbers. A model did not generate it. The
repository tests use a separate fixed trace.

Each displayed word is one token in the lesson vocabulary. A real tokenizer can split one word
into several tokens. Stage 3 has not tested that part yet.

## Connect this step to Stage 1

Stage 1 treated each position as a coin flip. A green hit was one result and a red result was the
other. With a 25 percent baseline, Stage 1 counted `G` hits in `T` trials and calculated a z score.

Stage 2 defines how one observed token becomes a hit or miss. Before each checked token, the
selector uses the key and four recent tokens to mark five of 20 candidates green. The checker then
uses the same Stage 1 count and formula.

The key and a decision cutoff do different work. The key affects which tokens count as hits. A
cutoff can turn a completed score into a decision after calibration. Stage 2 does not set a cutoff.

Stage 1 used a 40 percent biased coin as a teaching comparison. The Stage 2 score increase does not
promise a 40 percent hit rate. Its effect depends on all 20 starting scores.

## Start with scores

The first four words are `Early one morning Jack`. The program needs to choose the next word.

A language model would usually give every possible token a score. A higher score gives a word a
higher chance. The code calls this score a logit. Stage 2 uses scores that we chose by hand because
it does not run a model.

For the first choice, `ran` starts at 1.9. `Went` starts at 1.7, and `walked` starts at 1.4.

## The author chose the key

The repository author chose `stage-02-public-demo-key-v1`. The model and prompt did not choose it.

The generator and checker use a key as part of a repeatable selection rule. The operator stores it
outside the model and can replace it without retraining the model.

SHA-256 turns the key, context, and candidate number into a fixed-length result. The selector sorts
those results. A small change to the input usually gives a different order.

The selector combines the key with the previous four token numbers and one candidate number. It
runs this SHA-256 calculation for all 20 candidates, sorts the results, and selects the first five
words.

For `Early one morning Jack`, the selector chooses `Early`, `went`, `walked`, `snow`, and `trail`.
Some of those words sound wrong after `Jack`. The selector does not read the sentence or judge
grammar. The low starting scores keep the odd words unlikely.

The word `went` has token number 4. Under the lesson key and first context, its hash begins with
`01d63f53`, so it ranks first. The program uses the full 32-byte hash for ranking.

Changing the key changes every SHA-256 input. The comparison key selects `the`, `hill`, `path`,
`snow`, and `home` for the same context. Eight words move between the green and red groups. The
green group still has five words because the 25 percent setting did not change.

The key does not change SHA-256, the starting scores, the score increase, or the Stage 1 formula.

We print the key in the lesson so anyone can repeat the calculation. A production operator would
normally generate an unpredictable secret, keep it in protected server storage, and use a separate
public name to identify it. The final key size and format depend on the chosen watermark method and
need a security review.

## The first choice

The program adds 2 to every selected score. `Went` changes from 1.7 to 3.7. Its chance rises from
22.85% to 46.51%.

`Ran` stays at 1.9 because the selector did not choose it. Its chance still falls from 27.91% to
7.69%. The program converts all 20 scores into shares of one total, so five changed scores affect
every final chance.

The saved random number is 0.30. Before the score increase, 0.30 falls inside the range for
`walked`. After the increase, the same number falls inside the range for `went`. The program adds
`went` to the sentence.

## Finish the sentence

The program removes the oldest context word after each choice. It adds the chosen word at the
other end. The program uses the same key while the four recent words change.

For `one morning Jack went`, the selector chooses `Jack`, `up`, `hill`, `stairs`, and `saw`. The
program adds 2 to their scores. The sampler uses the saved number 0.35 and picks `up`.

For `morning Jack went up`, the selector does not choose `the`. Its starting score is high enough
for the sampler to pick it with the saved number 0.13.

For `Jack went up the`, the selector does not choose `hill`. The sampler still picks it with the saved number 0.06.

The first two words are green hits because they belonged to their selected sets. The last two are
red results because they did not. The score increase makes selected words more likely. Every word
still keeps some chance.

## Check the finished text

The checker reads the finished tokens in order. Before `went`, it reads `Early one morning Jack`
and rebuilds the five selected words. It counts a hit because `went` belongs to that set.

The checker then repeats the same work for `up`, `the`, and `hill`. It needs the observed tokens,
the lesson key, and the matching token numbering and selection settings. It does not need the
generation scores or random numbers.

The selector chooses 5 of 20 words. Under random selection, the expected hit rate is 25%. Four checked positions have
an expected count of 1. The sentence has 2 hits. The usual spread is 0.8660, which gives a z score
of 1.1547.

The key does not appear in that formula. It affects the result earlier by changing which observed
tokens count as green hits.

Stage 2 has no cutoff and makes no detection decision. Later tests would need more text and would
need to set a useful cutoff. A result above that cutoff could show that text matches this watermark
setup and key. It could not identify the writer or prove that AI wrote the text.

## A different key

The selector chooses another set of words when it uses the comparison key `wrong-public-key`. The
checker finds zero hits in these four checked positions. Another key can still match some words by chance, so zero is
only the result of this fixed comparison.

The key is separate from the model weights. The operator can change it without retraining the model.
Changing the model or tokenizer can change token numbers, starting scores, text quality, and hit
rates. Tests and useful cutoffs do not automatically transfer to the new setup.

To rebuild the marked sets and count hits, a checker must match the key, token numbering,
selection rule, number of recent words, fraction of words that the selector marks, and counting
rule. It does not need the score increase or the random numbers used during generation. The
operator should still record the score increase because it affects the strength of the pattern and
the cutoff that later tests may support.

## Production key handling

A production system should keep the secret outside model files, prompts, browser code, generated
text, logs, and public repositories. It should give each secret a public name and record that name
with the other settings.

Only the generator and an approved checker should use the secret. If the operator puts the secret
in public browser code, every user can read it. Public checking therefore needs a service that verifies who may
submit text, or a different
method designed for public verification. Stage 2 builds neither system.

Stage 2 also leaves out secret storage, access control, key rotation, and security testing.

## Repository evidence

We use the ordinary sentence to explain the operation. Repository tests use the separate trace to
check the implementation with fixed token numbers, source information, and configuration
information. The command
`just verify-lab-02` recalculates that trace.

The labels in the test trace do not form a sentence. We wrote the sentence example separately.
The SHA-256 selector belongs to this lesson and does not implement an upstream KGW system or any
private vendor method.

Stage 3 would replace the scores that we chose by hand with scores from an approved model and tokenizer.
That work still needs separate approval.
