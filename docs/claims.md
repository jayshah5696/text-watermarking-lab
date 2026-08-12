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
| derived | The locked Stage 2 toy rule selects exactly 5 of 20 token IDs for each context. | `configs/lab_02.toml`; `src/watermark_lab/toy_greenlist.py`; frozen vector tests | Verified | Call this a property of the toy rule, not a property of an upstream KGW implementation. |
| derived | Adding `delta=2.0` to a green logit multiplies its odds relative to an unchanged red logit by `exp(2)`, about 7.389, before softmax normalization. | `src/watermark_lab/toy_greenlist.py`; `tests/unit/test_toy_greenlist.py` | Verified | State that final token probabilities still depend on every original logit and normalization. |
| derived | In the locked four-position trace, the choices after the boost are token IDs `[0, 1, 1, 2]`; checker replay counts 2 green hits in 4 eligible positions. | `artifacts/lab-02/trace.json`, source `f7a1690d28cfb48fc825017891b5d3e82eebdd07` | Verified by `just verify-lab-02` | Describe only this deterministic teaching trace. Do not report it as a detection rate. |
| opinion | Limitation: the public development key and SHA-256 selector are teaching devices, not a secure or upstream-compatible design. | `docs/stages/02-toy-vocabulary.md` | Approved scope statement | Keep this warning next to the toy trace and any interactive lesson. |
