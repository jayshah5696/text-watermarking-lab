# Stage 5 publication brief

## Article role

Stage 5 explains how to put the maintained Transformers watermark into a real generation path and
how to place that keyed path behind a host. Gemma 4 E2B is the worked model. Modal supplies the L4
used for the saved smoke; it is not part of the watermark algorithm.

The section answers:

> How do we add a generation-time watermark to a compatible Transformers model and keep its key
> inside a hosted service?

The answer must show actual code boundaries. A vague architecture diagram is insufficient.

## Implementation spine

The reusable path has four pieces:

1. A model adapter loads the model, renders or encodes prompts, exposes the text model config, and
   extracts assistant continuation text.
2. A watermark profile owns the green fraction, bias, key, seeding scheme, and context width.
3. The generation function passes the profile's `WatermarkingConfig` to `model.generate()` only for
   the watermarked condition.
4. The detector tokenizes only copied continuation text and builds `WatermarkDetector` from the
   matching text config, device, profile, and key.

Use the continuity passage for every code and data boundary. The article should show the Gemma
structured-response bug because it demonstrates why the adapter exists.

## Compatible-model claim

Use "compatible Transformers generation model," not "any Hugging Face model." Compatibility
requires:

- next-token text generation through a `generate()` implementation that accepts the maintained
  watermark configuration;
- a text vocabulary available from model configuration;
- a tokenizer or processor that can encode prompts and copied text;
- a continuation boundary that removes prompt and control tokens;
- a way to decode or parse assistant content;
- the selected device being supported by the model and watermark processor.

A plain decoder-only model may use `AutoModelForCausalLM` and `AutoTokenizer`. Gemma 4 uses
`AutoModelForMultimodalLM`, `AutoProcessor`, `model.config.get_text_config()`, a chat template, BF16
CUDA weights, and structured-response parsing. Other architectures may require another adapter or
may be incompatible.

## Key boundary

The public Stage 5 fixture key stays in versioned config so readers can reproduce the evidence. It
is unsuitable for a real trust boundary because anyone can know it.

A hosted service should:

- receive the private key from the host's secret store as an environment variable or equivalent;
- parse it once during process startup;
- construct generation and detector profiles inside the process;
- never put it in prompts, logs, traces, exceptions, responses, or client-side JavaScript;
- return a non-secret key version label when rotation requires one;
- restrict detector access if exposing detection would help an attacker tune around the signal.

This stage provides the code boundary and deployment blueprint. It does not create a secret or
endpoint.

## Provider-neutral hosting blueprint

The long-lived process loads one model and one key. The transport layer is thin:

```text
POST /generate
  prompt + approved sampling fields
        -> process-local adapter and keyed generation
        <- continuation + model/profile/key-version labels

POST /detect (optional and access controlled)
  copied text
        -> process-local tokenizer and matching detector
        <- G, T, z, cutoff decision, profile/key-version labels
```

Modal can wrap this process in a class or web endpoint. A VM, container platform, or another GPU
service can host the same core. GPU selection, autoscaling, authentication, rate limits, request
validation, timeouts, audit policy, and key rotation belong to the deployment layer.

## Recorded proof

The selected Stage 5 smoke proves that the implementation path completed for the pinned Gemma 4 E2B
revision in BF16 on one L4. It generated three control/watermarked pairs, extracted copied assistant
content, and ran matching detectors.

The continuity watermarked row generated 28 IDs. Its copied continuation produced 26 eligible
checks, 11 green hits, and z `2.0381`. The other watermarked rows also stayed below `z > 3`. Preserve
that result. The smoke validates the path, not a production detector threshold or accuracy claim.

## Figures

### Figure 1: one core, two model adapters

Show the shared generation and detector functions in the center. Put a plain causal-LM adapter and
Gemma adapter beside them. Label the exact methods each adapter supplies.

Caption:

> The watermark core depends on text IDs, a text vocabulary, generation, and continuation parsing.
> A model adapter supplies those details without putting model IDs into the shared algorithm.

### Figure 2: the key enters during generation

Show the control and watermarked `generate()` calls side by side. Highlight the sole extra argument.
Open one next-token step to show the keyed processor changing scores before sampling.

Caption:

> The watermarked call passes `WatermarkingConfig` into `generate()`. Transformers applies the
> keyed score change during each next-token decision. The key is absent from prompt text and public
> output.

### Figure 3: hosted trust boundary

Draw client, authenticated transport, long-lived model process, host secret store, and replaceable
compute provider. Mark every field that may cross the boundary.

Caption:

> The host injects the private key into the model process. Clients send prompts and receive text plus
> non-secret profile labels. Modal is one possible compute provider beneath this boundary.

### Figure 4: parsing failure and repair

Show Gemma's parsed object, the invalid `str(parsed)` path, and the corrected `parsed["content"]`
path into copied-text tokenization.

Caption:

> The first smoke scored a serialized response object. The corrected adapter extracts assistant
> content before re-tokenization. Generation can succeed while evidence handling fails.

## Claims

Allowed:

- The shared code supports compatible Transformers generation models through an explicit adapter.
- The saved Gemma example completed on the pinned revision and L4 runtime.
- The public demo key supports reproduction and provides no secrecy.
- A private hosted key must stay inside the service boundary.
- Modal is a replaceable host for the measured example.

Prohibited:

- Every Hugging Face model works without an adapter.
- This is production key management, a deployed service, or a secure public detector.
- The saved smoke measures accuracy, quality, robustness, or a calibrated threshold.
- A positive result proves AI origin or reproduces Anthropic's private implementation.

## Handoff artifacts

Update:

- `src/watermark_lab/transformers_runtime.py`
- `src/watermark_lab/gemma_adapter.py`
- `src/watermark_lab/key_policy.py`
- `docs/stages/05-hosting-blueprint.md`
- Stage 5 tests
- `.agent/diagrams/text-watermarking-stage-5-lesson.html`
- Stage 5 blog note, claims ledger, README, and status language

Reuse the selected Stage 5 trace. No new model or cloud run is needed for this reframing.
