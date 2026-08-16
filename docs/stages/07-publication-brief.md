# Stage 7 publication brief

> Status: pre-run design. No Stage 7 result is claimed here.

## Article role

Stage 6 showed the checker's background distribution on frozen natural-web text. Stage 7 asks the
core experimental question: when one source prefix feeds control and watermarked Gemma generation,
does correct-key evidence differ from the paired model output, the source continuation, and a
comparison-key replay?

A reader should leave this section able to trace one row through all four checks and explain why
prefix length changes the amount of evidence without turning the cutoff into a truth label.

Narrow pre-run answer:

> The experiment can answer the question only after all 24 frozen rows run once and every matched
> score remains visible. Separation is an outcome, not an exit requirement.

Assume the Stage 6 meaning of `G/T`, z, and strict `z > 3`. Define here: paired seed, score family,
complete-prefix cohort, paired z difference, and bootstrap interval.

## Teaching spine

Use Stage 6 paired-test selection rank `1000`. It was the first prompt frozen for this experiment,
so its role does not depend on a clean or positive result.

Carry these same objects through the section:

1. manifest identity and source hash;
2. exact first 50 Gemma token IDs;
3. one paired seed;
4. control and watermarked generation paths;
5. copied-text token IDs in preserved order;
6. four score-family labels;
7. prefixes at 40, 80, 160, 200, and 400 where supported;
8. concrete `G/T`, ordinary count, ordinary movement, z, and cutoff;
9. three row-level paired z differences; and
10. the row's place in the complete matched cohort.

The operation changed first is the presence of `watermarking_config`. Model, prompt, seed, sampler,
and token cap stay fixed. After generation, hold the recorded text fixed and change only the checked
sequence or key.

The challenging case comes from the predeclared inconvenient-row rule in the Stage 7 contract. It
must sit near the aggregate result. A mean effect cannot hide a row that reverses direction, scores
high under another key, crosses as a negative control, or has the smallest separation margin.

## Fixture selection

- Prompt rows: all Stage 6 paired-test ranks `1000` through `1023`, in manifest order.
- Fixed spine: rank `1000`.
- Prompt content: exact decoded source token IDs `0:50`, after a required ID round trip.
- Conditions: control first, watermarked second, same paired seed.
- Generated-token cap: 400 with normal end-token behavior.
- No prompt, seed, output, or row replacement after observation.
- Every short output stays in the row ledger. Unsupported prefixes are absent, never filled or
  extended.

The first paired-test row was chosen before Stage 7 output existed. Its topical content, sampled
continuation, and score are not reasons for selection.

## Visual plan

### Figure 1: one frozen prompt, two generated paths

Reader question: what exactly is paired?

Keep one 50-token prompt strip at the left. Fork it into control and watermarked Gemma calls. Place
one seed above the fork and one sampler profile below it. Mark the sole condition difference at the
`watermarking_config` boundary. Rejoin neither path after histories diverge.

Marks:

- blue token strip: shared source prompt;
- cyan path: control generation;
- green path: watermarked generation;
- yellow key chip: server-side watermark configuration;
- ordered copied-token strips: recorded outputs.

Draft caption:

> The same frozen 50-token source prefix and paired seed enter two Gemma calls. The watermarked call
> alone receives the keyed generation configuration. Once sampled tokens diverge, each path keeps
> its own history.

Alt text:

> One source prompt forks into control and watermarked Gemma generation. Labels show the shared seed,
> sampler, and 400-token safety cap. Only the watermarked path receives the key profile.

### Figure 2: one recorded row, four questions

Reader question: why four scores?

Use the same spine row and one supported prefix. Arrange four aligned lanes:

- marked text with generation key;
- control text with generation key;
- natural-web text with generation key;
- marked text with comparison key.

Each lane shows source label, key role, `G/T`, z, and the separate cutoff. Keep the copied-token
prefix length identical across lanes.

Draft caption:

> Four matched checks separate key-specific watermark evidence from ordinary Gemma variation,
> natural-web variation, and a comparison-key replay.

Alt text:

> Four aligned score lanes use one row and one copied-token prefix. Each lane names the checked text,
> key role, green-hit count, eligible count, z score, and strict cutoff result.

### Figure 3: evidence along one token history

Reader question: how did evidence change as text accumulated?

Reveal prefix markers at 40, 80, 160, 200, and 400 copied token IDs. Preserve token order and
identity. For each score family, draw z against copied-token length only where the recorded sequence
supports that prefix. Show the cutoff as a rule, not a colored region that implies truth.

Draft caption:

> Each point rechecks a longer prefix of the same recorded continuation. Missing long-prefix points
> mean the copied output ended earlier; they are not zero scores.

Alt text:

> Four score-family lines show z at fixed copied-token prefixes. Some lines stop before 400 tokens
> when generation ended earlier. A horizontal line marks strict z greater than three.

### Figure 4: all 24 rows before the mean

Reader question: does the average hide reversals or overlap?

For one selected prefix, show every row-level paired difference for all three contrasts. Then add the
mean and deterministic 95 percent bootstrap interval. Include the complete-prefix denominator.
Directly label the spine and inconvenient rows.

Draft caption:

> Dots are document-level paired z differences. The larger mark and line show the mean and paired
> bootstrap interval for the complete-prefix cohort. Individual reversals remain visible.

Alt text:

> Three horizontal difference plots compare correct-key watermarked z with model control,
> natural-web control, and comparison-key z. Every frozen row appears as a dot, with a mean and
> interval layered on top.

## Context-free screenshot tests

1. Pairing panel: a newcomer can identify the exact shared inputs and point to the only generation
   difference before either path samples a token.
2. Four-question panel: a newcomer can say what each lane checks and read the score separately from
   the cutoff.
3. Cohort panel: a newcomer can find the complete-prefix denominator, one reversing or inconvenient
   row, the mean paired difference, and the interval without calling it accuracy.

On mobile, the four score lanes may stack, but their prefix, row identity, and shared scale must
remain visible. The paired generation fork may stack vertically only if labels preserve the common
prompt and seed.

## Evidence contract

The raw artifact must retain:

- exact source and manifest identities;
- exact source prompt IDs and decoded prompt text;
- paired seed and call order;
- rendered input and generation settings;
- control and watermarked generated IDs;
- copied text, copied IDs, parser path, stop reason, and achieved lengths;
- generation-key and comparison-key token membership needed for all four families;
- `G/T`, z, exact tail, and strict decision at every supported prefix;
- every-pair primary and distinct-pair diagnostic results;
- complete-prefix membership for each aggregate;
- every row-level paired z difference;
- deterministic bootstrap seeds and intervals;
- fixed spine identity and inconvenient-row rule outcome;
- source commit, exact config SHA-256, package versions, GPU identity, model file identity, dataset
  hash, runtime, and resource-policy fields.

The selected JSON must contain every plotted number. The lesson builder should read this JSON rather
than copy measurements by hand. Structural tests must compare every embedded row score, interval,
denominator, token state, and summary against the selected artifact.

## Expected result before running

The configured logit bias should tend to raise correct-key z on watermarked output as copied-token
length grows. The correct-key watermarked family should tend to exceed the paired model control,
the natural-web continuation, and the comparison-key replay.

That expectation is falsifiable. Individual rows may reverse, controls may cross the cutoff,
comparison-key scores may overlap, watermarked scores may stay below three, and early end tokens may
shrink the long-prefix cohort. Preserve each outcome.

## Allowed claims

Before the run:

- The 24 prompts and source continuations were frozen during Stage 6.
- The contract holds prompt, seed, sampler, model, and cap fixed across each pair.
- Each score family answers a different configured comparison.
- The paired bootstrap will summarize row-level z differences in this frozen cohort.

After the run, measured wording must come only from `artifacts/lab-07/results.json`.

A positive row may be called "consistent with this configured watermark and key." A measured mean
paired difference may be stated for this pinned 24-row experiment with its complete-prefix
sample size and interval.

## Prohibited shortcuts

- "AI detected," "human text," or proof of authorship.
- A cutoff count presented as calibrated accuracy.
- A bootstrap interval presented as a population guarantee.
- A 400-token cap presented as an achieved length.
- A prefix point compared across different row sets without visible denominators.
- Omission of short, failed, adverse, equal, or below-cutoff rows.
- Choosing the cleanest output as the lesson spine.
- Calling C4 verified human writing.
- Claiming quality preservation without a quality evaluation.
- Claiming edit robustness before Stage 8.
- Claiming that this reproduces Claude's private implementation.

## Blog handoff

The completed Stage 7 note must include:

1. the article subsection and narrow question;
2. this pre-run expectation unchanged;
3. artifact paths, source commit, config hash, GPU, call count, runtime, and measured cost fields;
4. the fixed spine row's full worked calculation;
5. the predeclared inconvenient row and selection reason;
6. every complete-prefix denominator and all three paired effects with intervals;
7. captions and alt text for all four figures;
8. allowed and prohibited claims; and
9. this transition into Stage 8:

> The unedited paired result is now frozen. The next experiment may change one editing operation at
> a time and measure how much of the same keyed evidence survives.
