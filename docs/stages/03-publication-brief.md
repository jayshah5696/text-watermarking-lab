# Stage 3 publication brief

## Article role

This section answers one question. Where does the watermark enter a real generation loop?

The reader may already understand that Stage 1 counts green hits and Stage 2 selects green token
IDs from recent history. Stage 3 must define tokenizer, model logits, temperature, top-k, top-p,
and a paired continuation. It must show each idea only when the reader needs it.

The narrow answer is one sentence. In the pinned Transformers 5.14.1 flow, the program filters the
model's candidate scores, adds 2 to available green candidates, converts the final scores to
chances, and samples one token.

## Teaching spine

Use the first two recorded tokens of the `stage-02-continuity` continuation with the score increase
enabled as the complete example. Follow the first token through generation in detail. Then show how
it becomes context so the checker can count the second token. Keep the prompt, model revision,
seed, generation settings, and current token history fixed. Compare the score increase off and on
at the first position.

The main figure must show:

1. the prompt text and its actual GPT-2 token pieces;
2. the final-position model scores;
3. the survivors after temperature, top-k, and top-p;
4. which survivors receive a score increase;
5. the sampled token and its final probability;
6. the token appended to the history;
7. the copied continuation re-tokenized for checking;
8. the same-key and comparison-key counts.

The challenge case is the sampling-order boundary. A token removed by top-k or top-p remains
removed even when the watermark key would mark it green. This prevents the reader from assuming
that the score increase can revive every green token.

## Fixture selection

The three prompts were fixed before the model run. The first prompt reuses Stage 2 words so the
reader can compare the hand-authored lesson with real tokenization. The notebook and library
prompts use ordinary publishable prose and give the model different contexts.

Do not change prompts, seeds, settings, or keys to improve prose or detector scores after the run.
Keep early end tokens, awkward output, a weak score, or a comparison-key match when the recorded run
produces one. Those outcomes limit the claim and belong in the evidence.

## Visual plan

### Figure 1: words become token pieces

Show the Stage 2 sentence beside the pinned tokenizer's pieces and IDs for the first Stage 3
prompt. The reader should see that a familiar word may include leading space or split into more
than one token.

Caption draft:

> GPT-2 turns the fixed prompt into token IDs before the model calculates the next-token scores.
> Stage 3 records both the readable text and those IDs.

Alt text draft:

> The continuity prompt appears above a row of GPT-2 token pieces. Each piece has one token ID. A
> note says that the model receives IDs rather than whole words.

### Figure 2: one token through the loop

Use one horizontal sequence with six named stops. Show model scores, temperature and filters,
watermark membership, final chances, the random draw, and the appended token. Use aligned candidate
rows so a learner can follow the same token across the intervention.

Caption draft:

> The program applies the score increase after temperature and filtering. It then samples one
> token and appends that token to the history used for the next model call.

Alt text draft:

> Six connected panels follow one generation position. Candidate tokens receive model scores,
> pass through temperature and two filters, receive an optional watermark increase, become
> probabilities, and produce one sampled token.

### Figure 3: paired paths and copied-text check

Show the control continuation and the continuation with the score increase enabled for the same
prompt and seed. Follow the copied text through re-tokenization and show the same-key and
comparison-key `G`, `T`, and z scores. Put the no-cutoff statement beside the scores.

Caption draft:

> Both paths start with the same prompt and random seed. The intervention changes token chances,
> so later token histories can diverge. The checker scores copied text against one configured key.

Alt text draft:

> Two continuation rows begin from one prompt and seed. A checking row shows copied text becoming
> token IDs, then same-key and comparison-key hit counts. A note says that Stage 3 sets no decision
> cutoff.

The three context-free screenshot targets are the prompt tokenization, the full one-token loop,
and the paired copied-text check. Desktop must preserve aligned candidate rows. Mobile may stack
the same steps but must keep their numbered order and repeated token labels.

## Evidence contract

The lesson and blog note may use only values from `artifacts/lab-03/trace.json` or values derived
and tested from that artifact. The selected artifact must record every input, intervention,
sampling result, copied-text tokenization result, and checker score needed by the three figures.

The source commit and configuration hash identify the code and fixed inputs. Package versions and
the model revision identify the external runtime. The verifier must regenerate every selected
value from the local model cache.

## Expected result before the run

Before the run, we expect the 2.0 increase to raise the total chance assigned to green candidates.
Sampling can still choose other tokens, so three prompts may or may not produce more green hits.
The comparison key may still count some hits by chance. The artifact must record whether copied
text reproduces the generated continuation IDs rather than assume it.

## Blog handoff requirements

`blog/notes/03-manual-generation.md` must include the article subsection, the expected result above,
the observed six-row result, one complete token step, the filtered-green failure case, the three
figure captions and alt texts, allowed claims, prohibited claims, and the transition to Stage 4.

Allowed claims:

- the pinned GPT-2 fixture supplied real next-token scores and token IDs;
- the manual loop used the recorded processor order and seeded sampling settings;
- the recorded paired continuations and checker counts occurred in this local CPU run;
- copied-text checking used the pinned tokenizer and key profile.

Prohibited claims:

- three prompts measure detection accuracy, language quality, or a useful cutoff;
- a positive score proves AI origin, authorship, or use of a private vendor system;
- the GPT-2 fixture represents current model quality;
- the Stage 3 manual checker is already equivalent to the full Transformers adapter;
- CPU results automatically match CUDA or another device's watermark membership.
