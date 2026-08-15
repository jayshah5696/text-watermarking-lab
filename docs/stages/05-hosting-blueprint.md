# Stage 5 hosting blueprint

This blueprint wraps the reusable Transformers watermark core in a host. It does not deploy a
service or create a secret.

## Process boundary

A long-lived model process owns:

- one loaded compatible Transformers model and its adapter;
- one device;
- one `KeyMaterial` value read during startup;
- the watermark and sampling profiles;
- generation and optional detection functions.

The HTTP, RPC, queue, or batch transport stays thin. It validates a request, calls the process-local
core, and serializes an allowlisted response.

## Startup

The educational path uses the public key from `configs/lab_05.toml`:

```python
key = public_demo_key(value=config.generation_key, version="demo-v1")
```

A private service reads an injected secret once:

```python
key = private_key_from_environment(
    variable="WATERMARK_HASHING_KEY",
    version_variable="WATERMARK_KEY_VERSION",
)
```

The host's secret store must inject those variables. Do not put the key in the container image,
source repository, command line, request body, response body, browser JavaScript, exception text,
or telemetry.

## Generation path

```python
adapter = load_compatible_adapter(model_revision, device="cuda")
encoded = adapter.encode_prompt(request.prompt)
profile = WatermarkProfile(
    green_fraction=0.25,
    bias=2.0,
    hashing_key=key.value,
    seeding_scheme="lefthash",
    context_width=1,
)
result = generate_continuation(
    adapter=adapter,
    encoded=encoded,
    sampling=sampling,
    condition="watermarked",
    watermark=profile,
)
response = public_generation_response(
    text=result.copied_text,
    model_revision=model_revision,
    watermark_profile="kgw-reference-v1",
    key=key,
)
```

The response contains `key_version`; it never contains `key.value`.

## Optional detector path

Detection uses the same model text config, tokenizer, device, watermark profile, and key:

```python
detector = build_detector(adapter=adapter, watermark=profile)
record = detect_copied_text(
    adapter=adapter,
    detector=detector,
    copied_text=request.text,
    z_threshold=3.0,
)
```

A public detector may help an attacker test edits until a signal disappears. Decide whether to keep
it internal, rate-limit it, or expose only a coarse result. That policy is outside the Stage 5 smoke.

## Transport schema

`POST /generate` may accept:

- prompt;
- `max_new_tokens` in a server-defined range;
- temperature, top-k, and top-p in server-defined ranges.

It may return:

- continuation text;
- exact model revision;
- non-secret watermark profile name;
- non-secret key version;
- whether the key is a public demo key.

It must not accept an arbitrary model repository ID, remote-code flag, device, key, secret name, or
unbounded generation length from an untrusted client.

## Replaceable host

Modal can supply an L4 and keep the model process warm. The same core can run in a container on a VM,
a Kubernetes deployment, or another GPU provider. The host layer owns:

- model artifact access and license compliance;
- GPU and memory selection;
- authentication and authorization;
- request limits, timeouts, concurrency, and rate limits;
- secret injection and rotation;
- logging policy and abuse monitoring;
- health checks and rollout strategy.

The watermark core does not import a cloud SDK. `src/watermark_lab/modal_app.py` is one adapter
around it.

## Compatible model checklist

Before adding another Transformers model, verify:

1. Its `generate()` path accepts the maintained `watermarking_config` argument.
2. The adapter can expose the text model config and vocabulary size.
3. Prompt encoding returns text `input_ids` and an attention mask.
4. Generated IDs can be sliced after the prompt boundary.
5. The adapter can isolate assistant content without role labels or control tokens.
6. Copied text can be re-tokenized with the same tokenizer.
7. The model, tokenizer or processor, precision, revision, and device are pinned.
8. A fixed fake or recorded vector test covers the adapter before a GPU run.

Models that hide logits behind a remote API, encoder-only models, and repositories requiring
unreviewed remote code do not satisfy this blueprint without another design and approval.
