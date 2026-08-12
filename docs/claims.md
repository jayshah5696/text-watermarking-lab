# Claims ledger

Substantive claims are labelled as `external`, `derived`, `measured`, or `opinion`. Measured
claims remain pending until their committed artifact exists.

| Category | Statement | Source or artifact | Status | Allowed article wording |
|---|---|---|---|---|
| derived | Under the idealized independent null, green hits follow `Binomial(T, gamma)`. | `src/watermark_lab/stats.py` | Pending Stage 1 implementation | State only with the independent-trial qualification. |
| derived | The expected count is `T * gamma`, and the displayed z-score standardizes the excess. | `src/watermark_lab/stats.py` | Pending Stage 1 implementation | Describe as the configured detector statistic. |
| measured | Stage 1 Monte Carlo detection rates. | `artifacts/lab-01/summary.json` | Pending Stage 1 evidence run | Use “simulated” and cite the artifact and source commit. |
| opinion | The biased condition `p=0.40` is pedagogical and not an LLM measurement. | `configs/lab_01.toml` | Approved scope statement | Do not derive it from a future logit bias. |
| opinion | Real token histories can be dependent, repeated, and miscalibrated relative to the ideal binomial model. | Canonical algorithm notes | Approved limitation | Present as a limitation, not a measured Stage 1 result. |
