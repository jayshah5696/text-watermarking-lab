# Project status

## Current stage

Stages 0 through 5 complete locally on `main`; Stage 5 smoke passed its runtime gate and awaits
human review before Stage 6.

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
- Stage 5 uses one disposable cloud invocation with no dataset, no Hugging Face Secret, no
  persistent Volume, and no deployed endpoint.

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

## Not implemented

- Dataset access or manifests.
- Hosted detector or public playground.
- Stage 6 natural-web calibration or any 24-row generation run.

No dataset-backed calibration or generally useful detector cutoff exists.

## Approval required next

Stage 6 planning or implementation. Any dataset, additional model/GPU/cloud invocation, persistent
cloud resource, GitHub remote, publishing, or public deployment requires separate explicit approval.

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
- The first control generation includes one-time CUDA warm-up behavior. It is not evidence that
  watermarking speeds generation.
- Synchronized watermark processor timing perturbs execution and is reported as component timing,
  not as an end-to-end speed penalty.
