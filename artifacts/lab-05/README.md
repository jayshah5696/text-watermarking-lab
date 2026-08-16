# Stage 5 selected evidence

`trace.json` records the approved three-passage Gemma 4 E2B BF16 smoke test on one Modal NVIDIA
L4. `annotated_trace.md` renders the compact result and bounded projection.

`examples.json` and `examples.md` preserve the ten-pair implementation demonstration. `lengths.json`
and `lengths.md` preserve the twelve-pair natural-length ladder, including every copied Gemma token
piece and its generation-key green/red decision.

Regenerate selected files only from the returned raw Modal JSON:

```console
uv run python scripts/verify_lab_05.py --raw runs/lab-05/modal-result.json
just verify-lab-05
just verify-lab-05-examples
just verify-lab-05-lengths
```

`just verify-lab-05` is local, network-free, model-free, GPU-free, and cloud-free. A new remote run
is not part of verification and requires separate approval.

The six original smoke records measure one pinned runtime path. The ten-pair demonstration expands
prompt coverage. The natural-length ladder records 24 outputs under normal end-token behavior; 8 of
12 watermarked rows and no controls crossed strict `z > 3`.

These artifacts do not measure detector accuracy, prose quality, a false-alarm rate, a causal length
effect, or a total cloud bill. Green token color means only keyed membership for the public
configuration and prior copied token.
