# Stage 2 teaching contract

## Reader and goal

This lesson is for a curious programmer who understands ordinary percentages but has not seen
watermark code.

The reader should learn how the program raises the chances of five selected next words. The reader
should also learn how the checker uses the same setup to find those selections in finished text.

A future match could show that text fits this watermark setup and key. It could not prove that a
model wrote the text. Stage 2 does not make a decision.

## Connect the lesson to Stage 1

Stage 1 treated each position as a coin flip. A green hit was one outcome and a red result was the
other. With a 25 percent baseline, Stage 1 counted `G` hits in `T` trials and calculated a z score.

Stage 2 defines where each hit or miss comes from. Before each checked token, the selector uses the
key and four recent tokens to mark five of 20 candidates green. The checker counts whether the
observed token belongs to that group. It then uses the same Stage 1 formula.

The key and a decision cutoff have separate jobs. The key affects which observed tokens count as
green hits. A cutoff can turn a completed score into a decision after calibration. Stage 2 does not
set a cutoff.

Stage 1 used a 40 percent biased coin as a teaching comparison. Stage 2 does not assume that
`delta=2` creates a 40 percent green hit rate. The hit chance depends on all candidate scores.

## Use one sentence

Use this sentence through the full lesson.

> `Early one morning Jack went up the hill.`

The program starts with four words. It adds `went`, `up`, `the`, and `hill`, one word at a time.
Words stay larger than their token numbers, so the reader does not have to translate anonymous IDs.

We wrote this example and chose its scores and random numbers. No language model generated it. The
example is separate from the fixed token trace that the repository tests use to check the code.

## Explain the key before the first choice

The repository author chose `stage-02-public-demo-key-v1`. The model, prompt, and reader did not
choose it.

SHA-256 turns the key, context, and candidate number into a fixed-length result. The selector sorts
those results. A small change to the input usually gives a different order.

The key is a fixed piece of text. The selector tests each of the 20 candidate words separately. For
each candidate, it combines the key, the four recent token numbers, and that candidate's token
number. It runs the SHA-256 calculation, sorts the 20 results, and marks the first five.

The key is separate from the model weights. The operator can change it without retraining the model.
Changing the model or tokenizer can change token numbers, starting scores, text quality, and hit
rates. Tests and useful cutoffs do not automatically transfer to the new setup.

The operator can also change the key. The selector will usually mark a different set for the same
context. The checker must use the key that the generator used.

For the first context, the lesson key ranks `went` first and marks
`Early, went, walked, snow, trail` green. The comparison key marks
`the, hill, path, snow, home` green. Eight words move between the green and red groups. Both keys
still mark five words because the green fraction stays at 25 percent.

The key changes the input to SHA-256. It does not change SHA-256, the vocabulary, the green
fraction, the score increase, the z score formula, or a later cutoff.

We print this key in the lesson so readers can repeat the calculation. A production system would
normally generate an unpredictable secret. The exact size and format depend on the selected
watermark method and need a security review. The operator should store the secret outside model
files, prompts, browser code, generated text, logs, and public repositories. The operator should
give each secret a public name, limit access, plan key changes, and keep an old secret only while
old text still needs checking.

If the operator puts a shared secret in public browser code, every user can read it. Public checking
would need a service that verifies who may submit text, or another method designed for public
verification. Stage 2 builds neither system.

To rebuild the marked sets and count hits, the checker must match the tokenizer, vocabulary,
selector code, number of recent words, fraction of words that the selector marks, and counting
rule. It does not need the score increase or the random numbers used during generation. The
operator should still record the score increase because it affects the strength of the pattern and
the cutoff that later tests may support. Stage 2 does not include secret storage, access control,
key rotation, or production security work.

## Fixed sentence example

Use these values in the lesson.

- The token vocabulary is
  `Early, one, morning, Jack, went, up, the, hill, walked, ran, road, path, stairs, and, saw, snow, down, home, ., trail`.
- The teaching key is `stage-02-public-demo-key-v1`.
- The selector uses the documented Stage 2 SHA-256 teaching rule.
- The program keeps four recent tokens as context.
- The selector marks five of 20 candidates at each position.
- The program adds `2.0` to each selected score.
- Every unlisted starting score is `-2.2`.
- Each displayed word is one token in this example. A real tokenizer may split a word into several
  tokens. Stage 3 has not tested that part yet.
- The comparison key is `wrong-public-key`. For the first context, the selector marks
  `the, hill, path, snow, home`. The checker finds no hits in this fixed sentence. Another key can
  still match some words by chance.

| Position | Recent words | Higher base scores | Green words | Draw | Chosen word | Hit? |
|---|---|---|---|---:|---|---|
| 1 | Early one morning Jack | went 1.7; walked 1.4; ran 1.9; saw 1.2; and 0.5; home 0.2 | Early, went, walked, snow, trail | 0.30 | went | green |
| 2 | one morning Jack went | up 1.7; down 1.9; home 1.5; and 0.8; road 0.4; . 0.1 | Jack, up, hill, stairs, saw | 0.35 | up | green |
| 3 | morning Jack went up | the 2.2; hill 1.3; road 1.1; path 0.9; stairs 0.7; trail 0.5; . 0.2 | one, went, stairs, snow, trail | 0.13 | the | red |
| 4 | Jack went up the | hill 2.5; road 1.8; path 1.6; stairs 1.4; trail 1.2; down 0.4; . 0.2 | went, road, stairs, saw, trail | 0.06 | hill | red |

At position 1, the sampler picks `walked` with no score increase. The sampler picks `went` after the program
adds 2 to the selected scores. The program uses the same random number, `0.30`, both times. The
chance for `went` rises from 22.85% to 46.51%.

The program does not change the score for `ran`. Its score stays at 1.9, but its chance falls from
27.91% to 7.69%. This happens because the program converts all 20 scores into shares of one total.

The checker finds two green hits in four positions. Random selection would produce one hit on
average. The usual spread is `sqrt(0.75)=0.8660`, so the z score is `1.1547`. These numbers belong
to the example that we wrote by hand. They are not measured results.

## Guided sequence

1. Recall that Stage 1 counted hits and misses, then calculated a z score.
2. State that Stage 2 defines how one token becomes a green hit or red result.
3. Define the key, its owner, and the complete selector input.
4. Keep the first context fixed and switch between the lesson key and comparison key. Show all 20
   candidates, hash prefixes, ranks, and green or red labels.
5. Keep the lesson key fixed. Use one moving four-word window to generate `went`, `up`, `the`, and
   `hill`.
6. Show the full 20-word green and red grid for each completed choice.
7. Keep the text fixed. Let the checker use a teaching key and the toy text to rebuild one group at
   a time.
8. Update `G`, `T`, expected hits, and z after each checked token.
9. State that Stage 2 has no cutoff. Put production practice and the repository trace in optional
   disclosures.

## Interaction contract

- Use a 20-word grid before generation. Keep the context and green fraction fixed. Let the reader
  switch only between the lesson key and comparison key.
- Keep candidate cards in token number order. Show each small token number, hash prefix, rank, and
  green or red label. Animate only cards that move between the green and red groups.
- Use one persistent four-word window and one `Choose next token` control for all four generation
  positions.
- Keep the window width fixed. On each click, move the oldest word out from the left, shift the
  other three words left, and move the sampled word into the rightmost slot.
- Keep the teaching key fixed. Update the selected words, score increase, final chance, random
  number, sampled word, hit result, sentence, and next context after each click.
- Name the context used for the completed choice after the window moves. This prevents the learner
  from attaching the selected set to the next context by mistake.
- Change the same control to `Replay from start` after the fourth choice. Include a separate
  `Start over` control that works from any settled state.
- Use a small inline classic script with no imports, remote libraries, fetch calls, or storage.
  The exact `file://` page must work without an HTTP server.
- Keep a complete four-step record in ordinary HTML. Show it when scripts do not run. Hide it only
  after the interactive runner starts successfully.
- Ignore repeated clicks while the context is moving. Keep focus on the control and report each
  result through an `aria-live` region.
- Follow `prefers-reduced-motion` and update the same states without animation.
- Checking never uses the generation scores, chances, or random numbers.
- The checker accepts a teaching key and text made from the 20 lesson labels. It uses the first four
  tokens as context and checks every later token.
- Use `Start checking` and one repeatable `Check next token` control. Show the rebuilt 20-word grid,
  observed token, hit result, running `G`, running `T`, expected hits, and z score.
- Validate short text, unknown labels, empty keys, non-ASCII keys, and the `|` delimiter in place.
- Never label the checker as an AI detector. It checks only this toy selector and key.
- Keep production sources and the repository test trace in optional disclosures.

Each interactive figure must give an instruction and explain what stays fixed. It must also explain
what changes, what the reader should watch, and what the result means.

## Visual contract

- Use a single reading column with one main figure in each section.
- Keep a sentence strip in every major figure and use familiar words as the dominant labels.
- Show token numbers in small secondary type only.
- Use green hatching plus the word `selected`, orange plus `fixed draw`, and rust plus `red result`.
- Keep the moving four-word window, selected set, sampled result, and sentence visible together.
- Keep three main visual ideas. Show how the key changes which words are green, generation with a moving context,
  and checking with fixed text.
- Number figure captions and state each result in a full sentence.
- Reduce headline scale enough that the first viewport shows the goal, sentence, and boundary.

## Language contract

All learner copy must pass the Humanizer plain register before browser QA.

- Use everyday words and complete sentences.
- Use `selected words`, `score`, `chance`, and `random number` before introducing `logit`,
  `softmax`, or `z score`.
- Name the author, selector, program, or tests as the actor. Do not make the key, context, page,
  trace, or watermark perform an action.
- Do not use em dashes, en dashes, decorative arrows, curly quotes, rhetorical question stacks,
  fragments, colon-led point labels, analogies, or slogan headings.
- Keep one new idea in each visual block. Move production terms and exact implementation details
  into the optional repository appendix.
- Explain an odd selected word beside the selection. State that the selector uses token numbers
  and does not read grammar.
- Run a final anti-AI audit after the copy is complete. Rewrite any remaining templated phrasing
  before delivery.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
|---|---|---|---|
| Sentence, vocabulary, scores, and draws | illustrative | this declared example | fixed lesson test |
| `went` ranks first with hash prefix `01d63f53` under the lesson key | derived illustration | selector input and SHA-256 | fixed hash test |
| Comparison key moves eight words between the green and red groups while keeping five green words | derived illustration | selector plus first sentence context | fixed ranking test |
| Five words selected for each sentence context | derived illustration | selector plus declared example | fixed selector test |
| The four choices are went, up, the, hill | derived illustration | scores, boost, and draws above | sampling replay test |
| Sentence example has two green hits and z=1.1547 | derived illustration | green group check and Stage 1 formula | fixed lesson test |
| Canonical run has two green hits in four positions | derived evidence | `artifacts/lab-02/trace.json` | `just verify-lab-02` |
| Checker finds zero hits with the comparison key on the canonical run | derived evidence | canonical trace and alternate key test | `test_wrong_key_does_not_replay_the_recorded_hits` |
| We make no production security claim for the published teaching key | limitation | Stage 2 contract | scope review |

## Boundaries and QA

Readers can follow repeatable selection from a context and key. They can also follow the score
increase, conversion from scores to chances, sampling, context movement, checking, and matching
settings.

We did not measure language quality, detection accuracy, a decision cutoff, production security,
authorship, AI origin, or compatibility with Anthropic's private system.

Model or tokenizer downloads, datasets, cloud work, GPU work, remotes, deployment, and publishing
still need separate approval.

Save the page at `.agent/diagrams/text-watermarking-stage-2-lesson.html`.

Check the page at 1440 by 1000 in light mode, 390 by 844 in light mode, and 1200 by 900 in dark
mode. Test every control, keyboard use, reduced motion, console output, and horizontal overflow.

Capture the key explanation, worked choice, and checker in separate screenshots. Each screenshot
must make sense without the opening section.
