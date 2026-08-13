# Stage 2 lesson storyboard

## One sentence

Keep this sentence visible through the whole lesson.

`Early one morning Jack ____ ____ ____ ____.`

The program adds `went`, `up`, `the`, and `hill` one word at a time. The main lesson uses words.
Small token numbers connect the words to the code. Tests use the repository trace in the optional
appendix.

## Lesson order

1. Recall the Stage 1 count. One position produced a hit or miss. Stage 1 counted `G` hits in `T`
   trials and calculated a z score.
2. State the Stage 2 question. The selector now decides which observed tokens count as hits.
3. Define a token. Explain that we chose the scores and random numbers by hand.
4. Introduce the teaching key. State who chose it, why the code needs it, and which values enter
   the selector.
5. Keep `Early one morning Jack` fixed. Show all 20 candidates with the lesson key. Display small
   token numbers, short hash results, rank, and green or red labels.
6. Change only the key. Keep five of 20 words green and animate the eight cards that change
   between the green and red groups.
7. Restore the lesson key. Show one persistent four-word window and one `Choose next token`
   button.
8. On each press, update the full 20-word grid and show the starting score, score increase, final
   chance, random number, sampled word, and hit result.
9. Move the context for `went`, `up`, `the`, and `hill`. Use `the` and `hill` to show that the sampler
   can choose a red word.
10. Keep the finished text fixed. Let the reader enter a teaching key and toy text.
11. Check one token at a time. Rebuild the 20-word group and update `G`, `T`, expected hits, and z.
12. State that Stage 2 has no cutoff. Explain that the key affects which tokens count as hits before
    the formula runs.
13. Put production key practice, exact test files, commands, and compatibility notes in optional
    disclosures.

## Key comparison interaction

Keep the context `Early one morning Jack`, the 20-word vocabulary, and the 25 percent green
fraction fixed. Provide two controls named `Use lesson key` and `Use comparison key`.

The lesson key marks `Early, went, walked, snow, trail` green. The comparison key marks
`the, hill, path, snow, home` green. Eight words move between the green and red groups. The count
stays at five.

Each card stays in token number order. Show its token number, short hash result, rank, and the word
`green` or `red`. State that the program ranks the full SHA-256 result. The short result is only a
display aid.

## Moving window interaction

Keep one four-word window on screen. The key and window width stay fixed. Each click runs the same
complete operation for the next token.

1. Show the selected words for the current context.
2. Show the sampled word, starting score, score increase, final chance, random number, and hit
   result.
3. Add the sampled word to the sentence.
4. Mark the oldest context word as leaving.
5. Move the remaining words left and bring the sampled word into the rightmost slot.
6. Keep the context used for the completed choice in the result card.
7. Prepare the same control for the next position.

After `hill`, change the control to `Replay from start`. `Start over` restores the first context
from any settled state. Ignore another click while the window is moving.

Use an inline script that works from the direct file path. Keep a full four-step HTML fallback for
scripts-off use. Respect reduced motion. Keep the production sources and repository trace in
optional disclosures.

## Toy checker interaction

Start with the lesson key and `Early one morning Jack went up the hill`. The checker accepts only
the 20 lesson labels. It splits on spaces and matches capital letters exactly.

`Start checking` validates the inputs. `Check next token` repeats the same operation. It uses the
previous four tokens, rebuilds the 20-word group, labels the observed token, and updates the Stage 1
count. The lesson-key result is `G=2`, `T=4`, expected hits `1`, and `z=1.1547`. The comparison-key
result is `G=0`, `T=4`, and `z=-1.1547`.

Stage 2 has no cutoff. The result describes only this toy selector, token mapping, key, and settings.

## Screenshot checks

The key screenshot must show the fixed context, active key, all 20 words, five green words, hash
ranks, and the sentence that explains what stayed fixed.

The first choice screenshot must show the sentence, current four-word window, five selected words,
starting score, score increase, final chance, random number, and sampled word.

The checker screenshot must show the key and text fields, all four results, `G`, `T`, expected hits,
the z score, and the statement that Stage 2 has no cutoff.

## Appendix content

The appendix can include the fixed token number trace, full table with 20 rows, SHA-256 input format,
source commit, configuration fingerprint, seed, commands, and later model notes. The reader must
not need the appendix to understand the sentence.
