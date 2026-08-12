# Claims ledger

Substantive claims are labelled as `external`, `derived`, `measured`, or `opinion`. Measured
claims remain pending until their committed artifact exists.

| Category | Statement | Source or artifact | Status | Allowed article wording |
|---|---|---|---|---|
| derived | Under the idealized independent null, green hits follow `Binomial(T, gamma)`. | `src/watermark_lab/stats.py`; fixed tests in `tests/unit/test_stats.py` | Verified | State only with the independent-trial qualification. |
| derived | The expected count is `T * gamma`, and the displayed z-score standardizes the excess. | `src/watermark_lab/stats.py`; fixed tests in `tests/unit/test_stats.py` | Verified | Describe as the configured detector statistic. |
| measured | With the locked Stage 1 seed and configuration, simulated biased detection rises from 0.2133 at `T=40` to 1.0 at `T=400`; simulated null detection ranges from 0.0013 to 0.0021. | `artifacts/lab-01/summary.json`, source `e99e9e5f9b8bc426d1cc4e13f874854f8c303475` | Verified by `just verify-lab-01` | Use “simulated,” include the configured probabilities and threshold, and cite the artifact. |
| opinion | Limitation: the biased condition `p=0.40` is pedagogical and not an LLM measurement. | `configs/lab_01.toml` | Approved scope statement | Do not derive it from a future logit bias. |
| opinion | Limitation: real token histories can be dependent, repeated, and miscalibrated relative to the ideal binomial model. | Canonical algorithm notes | Approved limitation | Present as a limitation, not a measured Stage 1 result. |
