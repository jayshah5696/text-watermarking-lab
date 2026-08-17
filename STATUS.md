# Project status

## Current stage

Stages 0 through 9 are assembled locally on `main`. Stage 8 carries the first twelve frozen Stage 7
marked outputs through deterministic normalization, homoglyph, deletion, mixing, and paraphrase
conditions, then compares delta 1, 2, and 3 on the first eight prompts. Stage 9 assembles the final
article source and continuous interactive lesson from committed evidence only. Nothing has been
published. No endpoint, production secret, adaptive attack, or hosted playground has started.

## Implemented

- Local Git repository with Stage 2 work on `jay/lab-02-toy-vocabulary`.
- Python 3.12 project metadata and locked `uv` environment.
- Root `justfile` command surface and CPU-only CI contract.
- Ruff, Pyright, Pytest, and coverage configuration.
- Project README, MIT license, Codex instructions, claims ledger, and architecture decision.
- Start-here map to the canonical Obsidian research and implementation handoff.
- Biased-coin statistics, immutable result records, readable simulation, and independent verifier.
- Fixed Stage 1 configuration, selected summary, PNG/SVG figure, and evidence-backed blog note.
- Locked Stage 2 toy-vocabulary contract with a separate SHA-256 teaching selector.
- Typed green-set selection, logit bias, stable softmax, visible sampling, and detector replay.
- Deterministic JSON and annotated Markdown trace with an independent verifier.
- Evidence-grounded interactive Stage 2 lesson that follows one declared sentence fixture through
  keyed selection, probability change, sampling, context movement, checker replay, and key
  practice, with the separate recorded ID trace kept in a verification appendix.
- The lesson links Stage 2 to the Stage 1 hit count and z score. A 20-word comparison shows how a
  key changes green membership, while the toy checker accepts a teaching key and lesson text.
- Teaching and publication workflow that requires future stage fixtures, evidence schemas,
  visuals, captions, alt text, and blog handoffs to be designed together before implementation.
- Stage 2 publication brief preserving the verified fixture and mapping it to three final-article
  figures.
- Pinned `mlx-community/LFM2-350M-4bit` fixture at revision
  `18dc72abf3b2337f9123cfd6eeeb58dfa7947066`, loaded with MLX-LM on the local Apple GPU.
- Explicit cached next-token loop with a vectorized full-vocabulary selector, float32 score change,
  temperature, top-p, top-k, seeded sampling, append, and repeat.
- Six paired continuations across three fixed passages, copied-text re-tokenization, same-key and
  comparison-key checker results, and deterministic local-cache verification.
- Evidence-grounded Stage 3 blog handoff and interactive lesson that continues the Stage 2 sentence,
  reveals the complete chat-framed model input, follows one token through the loop, and returns to
  the Stage 1 count.
- Pinned `openai-community/gpt2` reference fixture at revision
  `607a30d783dfa663caf39e06633721c8d4cfcd7e`, loaded through Transformers 5.14.1 on the local CPU.
- Thin adapter around `WatermarkingConfig`, `model.generate()`, and `WatermarkDetector`, with a
  separate fixed-vector probe for the maintained processor order.
- Six paired 40-token GPT-2 continuations, copied-text replay, generation-key and comparison-key
  counts, prompt and padding exclusion, and an explicit repeated-pair compatibility fixture.
- Evidence-grounded Stage 4 blog handoff and continuous interactive lesson that keeps the same
  passage and token objects visible through order comparison, saved draw, and detector replay.
- Pinned `google/gemma-4-E2B-it` fixture at revision
  `3e22461f65e89153144f8adb70e3b8c2cc9845a7`, loaded in BF16 through Transformers 5.14.1 on one
  Modal NVIDIA L4.
- Six fixed Gemma smoke continuations across the three Stage 4 passages, copied-text replay,
  generation-key and comparison-key detector evidence, GPU timing, peak memory, and bounded
  200/400-token run projections.
- Reusable Stage 5 Transformers core with explicit watermark and sampling profiles, one generation
  call boundary, copied-text finalization, and matching detector construction.
- Gemma 4 adapter for chat rendering, text-config lookup, generated-ID slicing, strict assistant
  content extraction, copied-text tokenization, and CUDA detector tensors.
- Public-demo and private-environment key policies plus bounded provider-neutral request and response
  records that never serialize the key value.
- Hosting blueprint for a long-lived keyed model process. Modal is one replaceable compute adapter.
- Separately approved ten-pair implementation demonstration: ten frozen prompts, twenty generated
  outputs, paired seeds, copied text, generation-key `G/T`, z, p-value, and strict decisions.
- Natural-length evidence ladder with twelve frozen long-form prompts, four each under 200, 400, and
  800-token safety caps; paired control/watermarked outputs retain normal end-token behavior.
- Token-level copied-text evidence for all 24 ladder outputs: exact Gemma token IDs and pieces,
  unscored context, generation-key green/red membership, detector totals, z, p-value, and decision.
- Stage 5 used bounded disposable cloud invocations with no dataset, Hugging Face Secret,
  persistent Volume, or deployed endpoint.
- Pinned C4 `realnewslike` validation selection with 1,000 calibration rows and the next 24 passing
  rows frozen for later paired generation. The manifest stores identifiers, URLs, timestamps,
  hashes, token counts, and split assignments without republishing complete articles.
- Detector-only Stage 6 scoring on one Modal NVIDIA L4 with the Stage 5 Gemma tokenizer, public key,
  CUDA pseudorandom profile, every-pair primary count, and distinct-value-pair diagnostic.
- Selected Stage 6 JSON, Markdown, manifest, worked token trace, blog handoff, and interactive lesson
  that continue the Stage 5 `G/T`, z, and cutoff story into an outside-text failure case.
- One approved Stage 7 Modal L4 invocation with exactly 48 generation calls across all 24 frozen
  paired-test prompts, using paired seeds, normal end-token behavior, and a 400 generated-token cap.
- Four Stage 7 score families at copied-token prefixes 40, 80, 160, 200, and where jointly available
  400: marked/correct-key, model-control/correct-key, natural-web/correct-key, and
  marked/comparison-key.
- Complete-prefix cohort rules, row-level paired z differences, deterministic 10,000-resample paired
  bootstrap intervals, all-pair primary counts, distinct-pair diagnostics, a fixed spine row, and a
  predeclared inconvenient-row selector.
- Deterministic Stage 8 normalization, 1/5 percent homoglyph substitution, 10/30 percent deletion,
  and 25/50 percent aligned control-text mixing on twelve frozen marked outputs.
- Twelve unwatermarked Gemma paraphrases with copied-text scoring, length and decimal-number checks,
  final-layer mean-state cosine, and a recorded non-independent assistant preservation review.
- Eight-row delta 1/2/3 comparison with delta 2 reused from Stage 7, correct-key 80-token evidence,
  conditional NLL, repeated adjacent pairs, distinct bigrams/trigrams, achieved length, and runtime.
- Final Stage 9 article source assembled from the eight evidence-backed stage notes, with primary
  links for the KGW mechanism, SynthID-Text comparison, and Anthropic's stated marking plan.
- Self-contained Stage 9 interactive lesson that opens on the exact Stage 8 rank 1000 string, rewinds
  to one saved token draw, rebuilds `G/T` and z, reveals all 24 paired differences, and returns to
  every editing and bias row without generating or selecting new evidence.
- Local Stage 9 builder, structural evidence tests, and `just verify-stage-09` command. Publication
  remains a separate authorization gate.

## Verified

- `uv sync --locked --all-groups` succeeds locally.
- `just check` passes locally with 75 CPU-only tests.
- `just test-cov` passes with 99.38% branch-aware coverage for `stats.py` and `records.py`.
- `just lab-01` generated 100,000 raw simulation rows from source commit
  `e99e9e5f9b8bc426d1cc4e13f874854f8c303475` using config SHA-256
  `bb514264d259086929ef86d15e81fb2f44dfa6d5d1fa0f2b1d65586090ff6df9`.
- `just verify-lab-01` recomputes the selected summary exactly from ignored raw rows and passes.
- Selected evidence is in `artifacts/lab-01/summary.json`,
  `artifacts/lab-01/detection_by_length.png`, and
  `artifacts/lab-01/detection_by_length.svg`.
- The PNG is 1920 by 928 pixels; the SVG omits creation-date metadata.
- No target GitHub remote exists.
- `just check` passes locally with 186 CPU-only tests.
- `just test-cov` passes with 96.48% branch-aware package coverage.
- `just lab-02` generated a four-position trace from source commit
  `f7a1690d28cfb48fc825017891b5d3e82eebdd07` using config SHA-256
  `a342b4d1d347587098763e8f2ff6aa75dd86cbb538dc78200963a631b2a0defa`.
- `just verify-lab-02` recomputes the trace and annotated table exactly and passes.
- Selected Stage 2 evidence is in `artifacts/lab-02/trace.json` and
  `artifacts/lab-02/annotated_trace.md`.
- The revised lesson uses one repeatable `Choose next token` control. Its fixed four-word window
  moves left after each sampled word, then supports replay and restart without changing the key or
  window width.
- The lesson-key and comparison-key controls reproduce the exact SHA-256 teaching selector for the
  first sentence context. The browser checker reproduces `G=2, T=4, z=1.1547` with the lesson key
  and `G=0, T=4, z=-1.1547` with the fixed comparison key.
- The exact `file://` lesson passed full generation, replay, restart during motion, rapid-click,
  reduced-motion, and scripts-off fallback checks. The inline script has no imports, network calls,
  or storage. No console errors or horizontal overflow were found.
- `just check` passes locally with 260 tests.
- `just test-cov` passes with 97.83% branch-aware package coverage.
- `just lab-03` generated six 40-token continuations from source commit
  `2f082b7f63853811881c0f23c2d7022e8e5dbc3b` using config SHA-256
  `694a3d09ea341165cef5061360800e43957d2055993f7140b514ebf07ff3117f`.
- `just verify-lab-03` reloads the pinned model from the local cache, regenerates all six records,
  and compares `trace.json` and `annotated_trace.md` byte for byte.
- Same-key counts in the control rows were `8/39`, `10/39`, and `11/39`. The paired score-increase
  rows were `21/39`, `26/39`, and `17/39`. Comparison-key rows ranged from `6/39` to `14/39`.
- All six decoded continuations re-tokenized to the generated token IDs exactly.
- The self-contained `file://` Stage 3 lesson passed desktop light, mobile light, desktop dark,
  reduced-motion, keyboard, and scripts-off fallback checks. Every control and disclosure worked;
  no console errors or horizontal overflow were found.
- `just lab-04` generated six local CPU continuations from source commit
  `20b4860e0d64ca116b173bc42f971d50eb0fef95` using config SHA-256
  `d9367ca271399011703d3e7c150b6646b6612b034fa485026b33d14e49e48ded`.
- `just verify-lab-04` reloads the pinned GPT-2 revision from the local cache, regenerates both
  selected files, and compares them byte for byte.
- The reference order leaves 19 first-step choices and gives token ID 373 an `8.642730%` chance.
  The earlier order calculated on the same GPT-2 values leaves 11 choices and gives it an
  `8.825517%` chance. Only the reference order generated the saved continuation.
- Generation-key counts for the reference-watermarked rows were `17/39`, `21/39`, and `22/39`.
  Their z scores were `2.6811`, `4.1603`, and `4.5301`.
- The pinned repeated-pair option returned `3/5` in both library modes. Explicit value-based
  distinct pairs returned `1/2`, so the selected evidence records the mismatch.
- All six decoded continuations re-tokenized to the generated token IDs exactly. Primary detection
  received no prompt tokens and no padding tokens.
- `just check` passes with 364 tests, and `just test-cov` passes with 97.42% branch-aware package
  coverage.
- The self-contained `file://` Stage 4 lesson passed desktop light, mobile light, desktop dark,
  reduced-motion, keyboard, control, disclosure, and static-fallback checks. No console errors or
  horizontal overflow were found.
- `just verify-lab-05` locally reconstructs selected JSON and Markdown, detector z scores, record
  invariants, and cost projections without a model, GPU, network, or cloud call.
- The Stage 5 disposable worker downloaded the pinned model in 36.739 seconds and loaded it onto
  CUDA in 5.782 seconds. Peak reserved memory was 9.682 GiB of 22.034 GiB, leaving 56.1 percent
  headroom.
- Watermarked generation ran at 18.422, 18.747, and 19.259 generated tokens per second. Separate
  synchronized processor replays took 7.165, 5.373, and 5.898 milliseconds over the complete
  continuations.
- The three watermarked copied continuations scored `11/26` (z `2.0381`), `7/20` (z `1.0328`),
  and `9/22` (z `1.7233`). None crossed the configured strict `z > 3` cutoff.
- At the slowest watermarked rate, 9,600 generated tokens project to 521.1 seconds and `$0.1157`
  of L4 generation time; 19,200 project to 1,042.2 seconds and `$0.2314`. These exclude image,
  download, load, CPU, memory, storage, retry, and non-linear scaling costs.
- The fixed Stage 5 gate passed: exact L4/BF16 path, six complete records, 56.1 percent memory
  headroom, watermarked throughput above 2 tok/s, readable non-empty outputs, and projections below
  the USD 5 ceiling.
- CPU-only tests prove that control and watermarked generation calls differ only by the maintained
  `watermarking_config` argument, Gemma structured responses contribute only assistant content, a
  private key can be read from an injected environment, and public service records omit the key
  value.
- `just verify-lab-05-examples` locally reconstructs the ten-pair JSON and Markdown, paired seeds,
  prompt order, Stage 1 z scores, p-value bounds, and strict `z > 3` decisions without model, GPU,
  network, or cloud access.
- Across the ten paired prompts, no control or watermarked row crossed `z > 3`. Watermarked z was
  higher in seven pairs, lower in two, and equal in one. These twenty outputs demonstrate the
  implementation and do not estimate accuracy or a false-alarm rate.
- In the natural-length ladder, 8 of 12 watermarked rows and 0 of 12 controls crossed `z > 3`.
  Achieved copied lengths ranged from 200 to 800 tokens, and maximum watermarked z was `8.0271`.
  Prompt and length vary together, so this does not isolate a causal length effect.
- `just verify-lab-05-lengths` reconstructs selected length JSON and Markdown, token identities,
  green/red totals, paired seeds, z scores, p-value bounds, and strict decisions locally.
- `just verify-lab-06` reconstructs the 1,024-row manifest, all 1,000 score rows, exact binomial
  tails, strict decisions, quantiles, summaries, and the 400-token spine trace without dataset,
  model, GPU, network, or cloud access.
- `just check` passes with 431 tests, and `just test-cov` passes at 95.23 percent branch-aware
  package coverage.
- The Stage 6 selector scanned 2,479 C4 rows, rejected 1,451 as too short and four as obvious lists,
  selected 1,000 calibration rows, and froze the next 24 passing rows.
- Four all-pair rows crossed strict `z > 3`; median z was `0.0289`, the 99th percentile was `2.4568`,
  and maximum z was `3.7286`. One distinct-pair row crossed.
- The maximum natural-web row changed from `132/399`, z `3.7286`, to `114/358`, z `2.9904`, when
  each repeated value-pair counted once.
- The exact `file://` Stage 6 lesson passed 1440 by 1000 desktop, 390 by 844 mobile, 1200 by 900
  reduced-motion, scripts-off, control, console, and horizontal-overflow checks. Mid-page row,
  cohort, and failure screenshots were inspected.
- `just verify-lab-07` reconstructs every selected Stage 7 row, prefix score, exact binomial tail,
  strict decision, complete-prefix denominator, paired difference, bootstrap interval, and teaching
  selection locally without dataset, model, GPU, network, or cloud access.
- `just check` passes with 443 tests, and `just test-cov` passes at 95.23 percent branch-aware
  package coverage.
- The Stage 7 invocation completed in 743.1 seconds and returned 12,933 generated token IDs. A direct
  projection at the configured L4 rate is `$0.1650` of GPU time, excluding other provider charges.
- Complete matched cohorts were 24 rows at 40 and 80 copied tokens, 21 at 160, 17 at 200, and zero at
  400. The 400 generated-token cap was not an achieved 400 copied-token paired result.
- At 80 copied tokens, mean marked correct-key z exceeded model control by `1.8296` with 95 percent
  paired bootstrap interval `[1.3424, 2.3276]`, natural web by `1.7538` `[1.3100, 2.1977]`, and the
  comparison-key replay by `2.0461` `[1.6131, 2.4792]` across all 24 frozen rows.
- Strict marked cutoff counts were `1/24`, `3/24`, `5/21`, and `4/17` at prefixes 40, 80, 160, and
  200. No paired model control or comparison-key row crossed; one natural-web row crossed at 200.
- The predeclared inconvenient row was rank 1001. Its control and marked paths shared their first 80
  copied token IDs and both scored `26/79`, z `1.6239`, with the generation key.
- The self-contained Stage 7 lesson continues the first frozen Stage 6 test row through paired calls,
  history divergence, copied-text scoring, four controls, prefix growth, the inconvenient equal row,
  and every document-level paired difference before the mean and interval.
- The Stage 7 `file://` lesson passed Chrome 151 desktop 1440 by 1000, mobile 390 by 844, reduced
  motion 1200 by 900, scripts-off structure, all controls, JavaScript syntax, console, horizontal
  overflow, and three mid-page screenshot checks.
- The successful Stage 8 replacement invocation made exactly 28 generation calls, returned 6,965
  generated token IDs, and completed in 599.9 seconds on one Modal NVIDIA L4.
- A first Stage 8 invocation failed after model load because the bias sweep was applied beyond its
  frozen eight-row subset. It returned no result. The boundary was fixed, tested, committed, and a
  replacement invocation received separate approval.
- `just verify-lab-08` rebuilds deterministic edits, every selected token score, metric summaries,
  manual-review joins, JSON, Markdown, and four figure files without model, GPU, network, or cloud.
- At 80 copied tokens, mean paired z change was `0.0000` for normalization, `-0.3248` and `-0.9960`
  for 10/30 percent deletion, `-0.6712` and `-1.3424` for 25/50 percent mixing, and `-1.7105` for
  paraphrase.
- All twelve paraphrases passed automatic preservation screens. The non-independent assistant review
  marked ten pass and two uncertain; all ten passed rewrites reduced z and no paraphrase crossed
  strict `z > 3`.
- Mean 80-token z across the eight bias rows was `0.2923`, `2.1761`, and `2.4684` at delta 1, 2,
  and 3. Mean conditional NLL was `0.5004`, `0.5415`, and `0.5783`; two row-level z paths were not
  monotonic from delta 2 to 3.
- `just verify-stage-09` rebuilds the standalone lesson and checks its Stage 1, 3, 6, 7, and 8
  evidence payloads against the canonical selected artifacts without a model, GPU, network, or cloud.
- The Stage 9 lesson passed Chrome desktop light at 1440 by 1000, mobile light at 390 by 844, desktop
  dark at 1200 by 900, reduced motion, scripts-off fallback, keyboard focus, every control, console,
  JavaScript syntax, and horizontal-overflow checks. Four mid-page screenshots were inspected.
- Three independent lesson reviewers were requested through the workflow runner, but the background
  run did not return a retrievable report. Three separate local review passes were completed and
  recorded; independent reviewer sign-off remains unverified.

## Not implemented

- Authenticated hosted generator, hosted detector, or public playground.
- Production secret creation, key rotation, access control, rate limiting, and abuse policy.
- Publication of the Stage 9 article or lesson.

No generally useful or production-calibrated detector cutoff exists.

## Approval required next

Publication or release of the assembled Stage 9 article and lesson. Any additional dataset,
model/GPU/cloud invocation, persistent cloud resource, GitHub remote change, publishing, or public
deployment requires separate explicit approval.

## Known limitations

- The simulation assumes independent Bernoulli trials; it is not an empirical LLM calibration.
- The `p=0.40` condition is pedagogical and is not derived from an LLM logit bias.
- The selected artifact records local macOS/Python provenance; CI has not run because no GitHub
  remote exists.
- The canonical research material currently lives outside this repository in the user's Obsidian vault.
- The future detector will detect only this project's deliberately embedded watermark profile, not arbitrary AI-generated text.
- The Stage 2 selector is a toy SHA-256 rule. It is not compatible with an upstream KGW
  implementation and is not a production pseudorandom function or key-management design.
- Four generated positions demonstrate mechanics. They do not measure detection rates, text
  quality, or model behavior.
- The Stage 3 `mlx-mix-v1` selector is a portable teaching profile. It is not cryptographic,
  upstream-compatible, or a production key-management design.
- Three passages and 39 eligible tokens per continuation do not measure detection accuracy,
  false-positive rates, language quality, device portability, or a useful cutoff.
- The selected run uses one pinned 4-bit LFM2 checkpoint and local Apple GPU. Results do not
  automatically transfer to another model, tokenizer, checkpoint, device, or MLX version.
- The Stage 4 fixture uses one pinned GPT-2 revision, one local CPU, and three passages. Results do
  not automatically transfer to another Transformers version, device, tokenizer, or watermark
  recipe.
- The Transformers 5.14.1 repeated-pair option did not collapse value-equal pairs in the fixed
  fixture. The explicit distinct-pair result is a compatibility check, not a general claim about
  other library versions.
- Six Gemma smoke generations on one L4 do not measure detector accuracy, a false-alarm rate,
  language quality, a useful cutoff, cross-device portability, or a total cloud bill.
- All three Stage 5 watermarked continuations ended before 30 generated token IDs and remained
  below z `3`. The project did not tune prompts, seeds, keys, or settings after observing them.
- C4 `realnewslike` is natural-web text, not verified human authorship. One thousand selected rows
  cannot validate one-in-100,000 behavior or a production false-alarm rate.
- Stage 6 used one public key, one tokenizer revision, one CUDA pseudorandom profile, one 400-token
  window, and deterministic filters. Results do not transfer automatically to another corpus,
  key, device, tokenizer, length, or repetition policy.
- The first approved Stage 6 remote function completed but its returned JSON was lost because the
  local output directory did not exist. The user approved one exact replacement invocation from the
  same clean source commit and config. Neither invocation loaded model weights or generated text.
- The first control generation includes one-time CUDA warm-up behavior. It is not evidence that
  watermarking speeds generation.
- Stage 7 uses one Gemma revision, tokenizer, CUDA pseudorandom profile, public key pair, sampler,
  and 24 C4 prompts. Its paired intervals summarize this frozen cohort rather than a target
  population or production error rate.
- Generated and copied lengths varied under normal end-token behavior. The complete-prefix cohort
  shrank with length, so comparisons across prefixes do not isolate a causal length effect.
- Stage 7 measured keyed separation but did not measure prose quality, semantic fidelity, editing
  robustness, arbitrary AI origin, human authorship, or Claude's private implementation.
- Synchronized watermark processor timing perturbs execution and is reported as component timing,
  not as an end-to-end speed penalty.
- Stage 8 uses twelve edit rows and eight bias rows under one public key, Gemma revision, tokenizer,
  CUDA profile, sampler, and 80-token scoring prefix. Results do not transfer automatically.
- Deterministic deletion and mixing can damage grammar or meaning. Their detector reductions are not
  called meaning-preserving removals.
- Homoglyph substitution changes Unicode code points and tokenization while trying to look similar.
  It is not a semantic paraphrase attack.
- Embedding cosine and conditional NLL are model-based proxies, not human quality judgments. The
  assistant paraphrase review was non-independent and left two rows uncertain.
- The first failed Stage 8 invocation incurred unmeasured provider work but returned no usable
  artifact. The derived GPU-only amount from the successful invocation excludes that failed run and
  all CPU, memory, image, transfer, rounding, and provider overhead.
