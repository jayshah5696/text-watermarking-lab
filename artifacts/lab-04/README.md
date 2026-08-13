# Stage 4 selected evidence

`trace.json` contains the full-precision record for six continuations from the pinned local
Transformers fixture. `annotated_trace.md` renders the first-step order comparison, six checker
results, the repeated-pair fixture, and prompt-exclusion validation.

The artifact records source commit `20b4860e0d64ca116b173bc42f971d50eb0fef95` and config SHA-256
`d9367ca271399011703d3e7c150b6646b6612b034fa485026b33d14e49e48ded`.

Run `just verify-lab-04` from the repository root to reload the pinned GPT-2 revision from the
local cache, regenerate both selected files, and compare them byte for byte.

This is a measured local CPU fixture for Transformers 5.14.1. Three passages do not measure
detection accuracy, language quality, or a generally useful cutoff. A result above the configured
cutoff means only "consistent with this lab watermark and key." It does not prove AI origin or
authorship.
