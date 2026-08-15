# Stage 5 lesson storyboard

## One question

How do we add the maintained Transformers watermark at generation time and host the keyed path for
Gemma or another compatible generation model?

Stage 4 established the library behavior. Stage 5 must show the implementation. Modal appears only
where the process needs a machine with an L4.

## One recorded story

Carry the continuity prompt through the actual boundary:

`Early one morning Jack went up the hill. At the top he`

The learner starts with a generic `TextGenerationAdapter`. They choose the Gemma profile, render one
user message with Gemma's chat template, encode it on CUDA, and call one shared generation function.
The only condition change is whether that function passes a `WatermarkingConfig` into
`model.generate()`. The generated IDs exclude the prompt. Gemma's response parser returns a
structured object, so the adapter extracts `content`, re-tokenizes that copied text, and gives only
those IDs to a detector built from the same text config, device, profile, and key.

The measured continuation closes the story. Infrastructure and cost prove that this implementation
ran on one L4; they do not define the lesson.

## Visual language

- Use one horizontal code path: request, adapter, encoded prompt, generation, parsed continuation,
  detector, response.
- Keep the key as a labeled server-side object. Draw a boundary when it enters
  `WatermarkingConfig`. Never draw it inside prompt text or the public response.
- Use blue for model adapters and data movement, green for keyed watermark operations, orange for
  generated continuation text, yellow for code under examination, and coral for trust boundaries
  or bugs.
- Keep code excerpts short, exact, and linked to repository modules in the appendix.
- Modal receives one small side label: replaceable GPU host.

## Beat order

1. State the implementation question and show the Stage 4 handoff: Transformers already owns the
   maintained processor order.
2. Define compatible model in concrete terms. The model must expose text IDs, text vocabulary,
   `generate()`, and continuation decoding. Some models also need chat rendering and structured
   response parsing.
3. Present the four reusable objects: `ModelAdapter`, `WatermarkProfile`, generation function, and
   detector function.
4. Switch between a GPT-style plain causal model and Gemma. Keep the common interface fixed. Change
   loader class, prompt renderer, text config lookup, precision/device, and parser.
5. Follow the continuity prompt into the Gemma adapter. Show the exact user message and rendered chat
   input boundary.
6. Build a watermark profile from green fraction, bias, seeding scheme, context width, and one key.
   Explain that the public fixture key is reproducible, not secret.
7. Put the profile into the real call:
   `model.generate(..., watermarking_config=profile.to_transformers())`.
8. Toggle the argument off for control and on for watermarked generation. Keep model, prompt IDs,
   seed, sampler, and token cap fixed.
9. Open the next-token loop conceptually. Transformers computes logits, applies sampling warpers and
   the keyed watermark processor, samples one token, appends it, and repeats. Do not reimplement the
   loop in Stage 5.
10. Slice generated IDs after `prompt_length`. Prompt IDs never become copied-text evidence.
11. Show the real Gemma parsing failure. `str(parsed)` serializes role and content labels into the
   checked string. Replace it with a strict `content` extractor and a documented decode fallback.
12. Re-tokenize only the displayed continuation. Build `WatermarkDetector` from the matching text
   config, device, profile, and key.
13. Return `G`, `T`, z, and a narrow decision. Do not return the private key.
14. Wrap the same runtime in a provider-neutral service boundary. Process startup loads model and
   server key once. A request supplies prompt and safe generation parameters. A response returns
   text and approved metadata.
15. Compare key modes. The public demo key may live in config and artifacts. The private service key
   comes from a secret environment variable, is parsed once, never logged, never serialized, and
   receives a non-secret version label for rotation.
16. Place Modal, a VM, and another GPU platform under the same host interface. State that Modal is
   the measured example, not part of the algorithm.
17. Reveal the saved Gemma result: six calls completed, continuity watermark result `11/26`, z
   `2.0381`, and no row crossed the cutoff. Explain that implementation success and detector power
   are different questions.
18. Put download, memory, speed, and cost in a compact feasibility appendix. They show that the
   example fits the chosen host.
19. End with the unsupported edges: arbitrary remote code, encoder-only models, APIs that hide
   logits, unknown multimodal processors, key rotation, abuse controls, and calibrated production
   thresholds.

## Interaction sequence

### Adapter switch

- Instruction: choose plain causal LM or Gemma.
- Fixed: the `ModelAdapter` contract and watermark generation/detection functions.
- Changed: model-specific loading, prompt formatting, text config, and response parsing.
- Watch: the shared core never checks a model ID.
- Result: portability comes from an explicit adapter contract, not from claiming every model works.

### Generation-time toggle

- Instruction: turn watermarking off, then on.
- Fixed: model, prompt IDs, random seed, sampling settings, and output limit.
- Changed: one `watermarking_config` argument.
- Watch: the key enters the logits processor during token generation.
- Result: no post-processing can reproduce this intervention after text has already been sampled.

### Parser repair

- Instruction: compare the first stringified parser output with the corrected content extraction.
- Fixed: generated model output.
- Changed: the copied-text boundary.
- Watch: role labels and dictionary punctuation disappear before tokenization.
- Result: a working model call can still produce invalid detector evidence if parsing is wrong.

### Hosting boundary

- Instruction: choose reproducible demo or private service mode.
- Fixed: model runtime and public request/response schema.
- Changed: key source and disclosure policy.
- Watch: the private key remains inside the server process.
- Result: the compute provider is replaceable; the key boundary is not.

### Saved proof

- Instruction: replay the recorded continuity result through the implementation diagram.
- Fixed: selected Stage 5 trace.
- Changed: visible layer, from request to generation to detection.
- Watch: each saved field belongs to one code boundary.
- Result: the smoke proves this path ran on pinned Gemma; it does not establish production accuracy.

## Main path and appendix

Keep on the main path:

- compatibility contract;
- concrete adapter differences;
- actual generation call;
- key insertion and trust boundary;
- continuation slicing and strict response parsing;
- matching detector call;
- provider-neutral hosting process;
- measured Gemma proof and claim boundary.

Move to disclosures:

- full package versions, commit and config hashes;
- full Modal resource declaration;
- raw token arrays and nanoseconds;
- memory and cost projection;
- alternative detector policies;
- deployment work that remains unimplemented.

## Screenshot tests

1. Implementation screenshot: a programmer can name the four shared objects and the methods supplied
   by a model adapter.
2. Generation screenshot: a programmer can point to the exact line where the key affects generation
   and explain what stays fixed in the control call.
3. Hosting screenshot: a programmer can identify key source, process boundary, public request fields,
   public response fields, and the replaceable compute provider.
