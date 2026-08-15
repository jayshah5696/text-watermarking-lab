# Stage 5 selected evidence

`trace.json` records the approved three-passage Gemma 4 E2B BF16 smoke test on one Modal NVIDIA
L4. `annotated_trace.md` renders the compact result and bounded projection.

Regenerate selected files only from the returned raw Modal JSON:

```console
uv run python scripts/verify_lab_05.py --raw runs/lab-05/modal-result.json
just verify-lab-05
```

`just verify-lab-05` is local, network-free, model-free, GPU-free, and cloud-free. A new remote run
is not part of verification and requires separate approval.

The six records measure one pinned runtime path. They do not measure detector accuracy, prose
quality, a false-alarm rate, or a total cloud bill. The three watermarked rows remain below the
configured strict `z > 3` cutoff.
