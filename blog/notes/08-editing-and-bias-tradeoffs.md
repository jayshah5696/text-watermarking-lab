# Edit the text, then rebuild the evidence

## Question

How does ordinary editing change the correct-key evidence frozen in Stage 7, and what changes when
generation bias moves from 2 to 1 or 3?

## Expected result before running

Normalization might leave scores close to baseline when tokenization changes little. Homoglyphs,
deletion, mixing, and paraphrase could change token IDs or previous-token contexts and reduce
correct-key evidence. Stronger edits could also damage length or meaning.

A larger delta was expected to raise correct-key evidence on average. NLL or repetition could move
against it. Every row would remain visible if the direction reversed.

## Frozen experiment

The editing fixture used Stage 7 ranks 1000 through 1011. Each named edit started from the complete
recorded marked copied text. Every result was re-tokenized with the pinned Gemma tokenizer and
scored at the first 80 copied token IDs with the inherited key and detector profile.

The bias sweep used ranks 1000 through 1007. Delta 2 reused Stage 7. One replacement-approved Modal
L4 invocation generated delta 1 and 3 plus one unwatermarked paraphrase for each attack row. The
successful invocation made 28 generation calls, returned 6,965 generated token IDs, and ran for
599.9 seconds. It used no Secret, Volume, endpoint, or new dataset.

A first invocation failed after model load because the runner applied the sweep to 12 rows instead
of the frozen eight. It returned no result. The subset boundary was fixed, tested, and committed
before the separately approved replacement invocation.

## Observed editing result

At the 80-token prefix, normalization changed no row's z score. Mean paired z change was `0.0000`.
The other mean changes were:

- homoglyph 1 percent: `-0.0217`;
- homoglyph 5 percent: `-0.9311`;
- deletion 10 percent: `-0.3248`;
- deletion 30 percent: `-0.9960`;
- mixing 25 percent: `-0.6712`;
- mixing 50 percent: `-1.3424`; and
- paraphrase: `-1.7105`.

All 12 paraphrases passed the automatic length, number, and embedding-cosine screen. A
non-independent assistant review marked ten pass and two uncertain. The ten passed rewrites all
reduced z. No paraphrase crossed strict `z > 3` after rewriting.

Homoglyph substitution needs separate wording. It changed visually similar Unicode characters and
expanded copied-token length to a mean ratio of `1.0448` at 1 percent and `1.2183` at 5 percent.
That is tokenizer sensitivity, not semantic paraphrase robustness.

Deletion and mixing were not assumed to preserve meaning. The stronger conditions retained mean
copied-token ratios of `0.7021` and `1.0088`, respectively. A lower detector score under those
conditions is an editing result, not a successful meaning-preserving removal claim.

## One complete example

Rank 1000 entered Stage 8 with `28/79`, z `2.1436`, at 80 copied tokens. Ten percent deterministic
word deletion produced a new character string, which re-tokenized into a new history. The first 80
edited IDs scored `25/79`, z `1.3641`. Its paired z change was `-0.7795` and its complete copied-token
length ratio was `0.8929`.

The same row's paraphrase scored `26/79`, z `1.6239`, a change of `-0.5197`. Its copied-token length
ratio was `0.9388`, the embedding cosine was `0.9709`, all decimal numbers were preserved, and the
non-independent manual review passed it.

## Observed bias result

All eight rows supported 80 copied tokens at delta 1, 2, and 3. Mean correct-key z was:

- delta 1: `0.2923` with `0/8` strict crossings;
- delta 2: `2.1761` with `1/8`; and
- delta 3: `2.4684` with `3/8`.

The row-level path was not monotonic. Ranks 1004 and 1006 had lower z at delta 3 than at delta 2.
Mean conditional NLL rose from `0.5004` at delta 1 to `0.5415` at delta 2 and `0.5783` at delta 3.
Mean repeated adjacent-pair fraction rose from `0.0373` to `0.0471` and `0.0483`.

These are model-based proxies on eight frozen prompts. They do not establish human-perceived
quality. Achieved copied length also changed, even though every call shared a 400 generated-token
safety cap.

## Figures

`artifacts/lab-08/edit_signal_loss.png` shows every row's paired score change and retained copied
length for all eight edit conditions.

`artifacts/lab-08/bias_tradeoff.png` connects the same eight prompts across delta 1, 2, and 3 for z,
conditional NLL, and repeated adjacent-pair fraction.

## What this establishes

For these twelve marked Gemma outputs, ordinary edits rebuilt tokenizer histories and usually
reduced correct-key evidence. Ten paraphrases passed the declared automatic and non-independent
manual screens, and all ten reduced z. In the eight-row generation fixture, larger delta increased
mean z and strict crossings, while mean NLL and repetition also increased.

## What this does not establish

The experiment does not measure adaptive security, universal paraphrase robustness, human quality,
production error rates, another tokenizer, another model, private-key safety, another watermark
family, generic AI origin, authorship, or Claude's private implementation. The manual paraphrase
review was performed by the implementation assistant and was not blinded or independent.

A positive detector row means only "consistent with this configured watermark and key."
