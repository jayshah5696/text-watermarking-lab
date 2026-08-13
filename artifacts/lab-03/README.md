# Stage 3 selected evidence

`trace.json` contains the full-precision record for six continuations from the pinned local MLX
fixture. `annotated_trace.md` renders the first token step and the six checker results.

The artifact records source commit `2f082b7f63853811881c0f23c2d7022e8e5dbc3b` and config
SHA-256 `694a3d09ea341165cef5061360800e43957d2055993f7140b514ebf07ff3117f`.

Run `just verify-lab-03` from the repository root to reload the pinned model from the local cache,
regenerate all six continuations, and compare both selected files byte for byte.

This is a measured local fixture for the lab's `mlx-mix-v1` profile. Three passages do not measure
detection accuracy, language quality, or a useful cutoff. A score is not an AI-origin decision.
