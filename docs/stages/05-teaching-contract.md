# Stage 5 teaching contract

## Learner

- Intended learner: a Python programmer who can call a Transformers model but has never added a
  generation-time watermark or hosted a keyed model service.
- Safe prior knowledge: tokenization, `model.generate()`, and the Stage 4 idea that a logits
  processor changes next-token scores before sampling.
- Knowledge taught here: the reusable model contract, where the watermark key enters generation,
  how copied text reaches the matching detector, which pieces vary by model, and where a host must
  keep a private key.

## One learning question

- Question: how do we add the maintained Transformers watermark at generation time and host the
  keyed path for a compatible model?
- Project role: Stage 4 verified the maintained library behavior. Stage 5 turns that behavior into
  an implementation boundary that can run on Gemma or another compatible Transformers generation
  model.
- Plain answer: load a compatible model and tokenizer or processor, derive its text configuration,
  construct `WatermarkingConfig` from a server-held key, pass it only to the watermarked
  `generate()` call, parse only the assistant continuation, and run `WatermarkDetector` with the
  same profile and key.

## Learning outcome

After the page, the learner should be able to explain:

1. the exact generation and detection calls that carry the watermark key;
2. which adapter details change for GPT-2, Gemma, or another compatible Transformers model;
3. how to place model loading, keyed generation, copied-text detection, and public responses behind
   a host without returning the private key.

## Spine example

- Smallest example containing the full mechanism: the Stage 5 continuity prompt goes through the
  pinned Gemma 4 processor, BF16 model, generation-time watermark processor, structured-response
  parser, copied-text tokenizer, and matching detector.
- Starting state: one compatible Transformers model, one text vocabulary, one device, one public
  demo key for reproducibility, and one watermark profile.
- Observable result: the saved watermarked continuation and its copied-text result `G=11`, `T=26`,
  `z=2.0381`.
- Hand-worked reasoning: identify the key at configuration construction, follow the config into
  `generate()`, remove prompt and chat control tokens from the returned continuation, then build the
  detector from the same model text config, device, profile, and key.
- Failure case: the first implementation stringified Gemma's parsed response object. It scored the
  dictionary representation instead of the assistant's `content`. The corrected implementation
  extracts content before re-tokenization.

## Controlled exploration

### First comparison: model profile

- Held fixed: watermark profile, key contract, generation API, continuation boundary, and detector
  contract.
- Changed: model loader, tokenizer or processor, chat rendering, response parser, text config,
  precision, and device.
- Watch: a portable implementation carries settings and interfaces, never token IDs or green sets.
- Sentence afterward: a compatible model adapter supplies text IDs and a text vocabulary to the same
  generation-time watermark contract.

### Second comparison: control and watermarked generation

- Held fixed: loaded model, encoded prompt, seed, sampling settings, device, and output limit.
- Changed: `watermarking_config` is absent or present in `model.generate()`.
- Watch: the key stays inside the constructed configuration; it is not written into the prompt or
  returned with the generated text.
- Sentence afterward: the maintained logits processor applies the keyed score change during each
  next-token decision.

### Third comparison: public demo and hosted service

- Held fixed: the same Python generation and detection functions.
- Changed: the demo reads a documented public key while the service reads a private key from the
  host's secret store at process start.
- Watch: requests contain prompts and generation settings; responses contain generated text and
  approved metadata; neither contains the private key.
- Sentence afterward: Modal, a VM, or another GPU host provides compute. The watermark boundary is
  the same process-local Transformers code.

## Evidence ledger

| Page claim or value | Type | Source | Verification |
| --- | --- | --- | --- |
| `WatermarkingConfig` enters through `generate()` | external and checked | Transformers 5.14.1 API; `src/watermark_lab/transformers_runtime.py` | unit fakes and Stage 4/5 evidence |
| Detector uses matching model text config, device, profile, and key | external and checked | Transformers 5.14.1 API; runtime core | unit fakes and saved detector evidence |
| Gemma uses a processor, chat template, text config, BF16 CUDA model, and parsed assistant content | measured implementation | `src/watermark_lab/gemma_adapter.py`; selected Stage 5 trace | unit tests and `just verify-lab-05` |
| Public demo key and server-held private key have different trust properties | opinion and limitation | `src/watermark_lab/key_policy.py`; hosting blueprint | contract and tests |
| Modal is one replaceable host | implementation fact | `src/watermark_lab/modal_app.py`; hosting blueprint | import-free architecture tests |
| Continuity watermarked result is `11/26`, z `2.0381` | measured | `artifacts/lab-05/trace.json` | `just verify-lab-05` |
| Ten paired control/watermarked outputs and generation-key z, p-value, and decision | measured | `artifacts/lab-05/examples.json` | `just verify-lab-05-examples` |
| Cost and memory show that the pinned example fits one L4 | measured and derived | selected Stage 5 trace | local verifier |

## Boundaries

- This stage establishes a reusable, tested implementation boundary for compatible Transformers
  generation models and demonstrates it with the already measured Gemma 4 smoke.
- Compatibility means the runtime can encode a text prompt, call a `generate()` path that accepts a
  logits processor through `watermarking_config`, expose a text vocabulary through model config,
  and decode or parse continuation text. It does not mean every Hub repository works unchanged.
- A public demo key makes the educational fixture reproducible but offers no secrecy. Anyone who
  knows it can try to spoof or remove the signal.
- A production service must inject a private key server-side, restrict detector access, avoid logs
  that reveal the key, and define rotation and versioning outside the model response.
- The separately approved ten-pair extension permits exactly one additional bounded L4 invocation
  and twenty generation calls. It does not deploy an endpoint, create a secret, access a dataset,
  or start Stage 6.
- Ten pairs show the implementation on more fixtures but do not calibrate a detection probability,
  false-alarm rate, accuracy estimate, or production threshold.
- A positive result means only "consistent with this configured watermark and key."

## Interaction contract

1. Follow one prompt through the actual Python modules.
2. Switch between a plain causal-LM profile and the Gemma profile. Show exactly which adapter methods
   change.
3. Toggle the `watermarking_config` argument in the real `generate()` call while every other input
   remains fixed.
4. Place the same runtime inside a provider-neutral process boundary. Choose public demo key or
   server-held key and inspect what may cross the HTTP boundary.
5. Repair the structured-response parsing bug by selecting `content` instead of `str(parsed)`.
6. Replay the saved continuation through the matching detector.
7. Compare ten fixed paired prompts from the separately approved implementation demonstration.
   Show control and watermarked text, generation-key `G/T`, z, p-value, and strict decision. Define
   the p-value as evidence under the configured no-watermark baseline, never as a watermark
   probability.
8. End with the measured Gemma smoke as proof that the implementation ran, with cost in a compact
   feasibility appendix.

## Output and QA

- Destination: `.agent/diagrams/text-watermarking-stage-5-lesson.html`.
- Main screenshots: implementation pipeline, generation-time key insertion, and hosted key boundary.
- Test 1440 by 1000 desktop, 390 by 844 mobile, 1200 by 900 dark, reduced motion, keyboard focus,
  scripts-off fallback, every control, console output, and horizontal overflow.
- No required network, font, script, model, or cloud dependency in the HTML.
