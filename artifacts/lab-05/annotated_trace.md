# Stage 5 annotated Gemma Modal smoke trace

This measured smoke used one pinned Gemma 4 E2B BF16 model on one Modal NVIDIA L4.
It ran three fixed passages with watermarking off and on, then scored copied
continuation text.

- Source commit: `09831ba8f960d7070b67b9b5350cdffbae9b4c4d`
- Config SHA-256: `761d1eb699b403f8dad6375b2ef57f1695d54014788c850493a69b0617dae7e1`
- Model revision: `3e22461f65e89153144f8adb70e3b8c2cc9845a7`
- GPU: `NVIDIA L4` with 22.034 GiB
- Cold model download: 36.739 s
- Model load to CUDA: 5.782 s

## Six saved continuations

| Passage | Watermark | Generated | Seconds | tok/s | Peak reserved GiB | Processor ms | G/T | z |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stage-02-continuity` | off | 13 | 3.850 | 3.376 | 9.650 | 0.000 | 3/11 | 0.1741 |
| `stage-02-continuity` | on | 28 | 1.520 | 18.422 | 9.666 | 7.165 | 11/26 | 2.0381 |
| `notebook` | off | 18 | 0.954 | 18.869 | 9.666 | 0.000 | 4/16 | 0.0000 |
| `notebook` | on | 22 | 1.173 | 18.747 | 9.666 | 5.373 | 7/20 | 1.0328 |
| `library` | off | 30 | 1.873 | 16.018 | 9.666 | 0.000 | 8/28 | 0.4364 |
| `library` | on | 24 | 1.246 | 19.259 | 9.666 | 5.898 | 9/22 | 1.7233 |

## Continuity passage

### Control

saw the entire valley bathed in a soft, ethereal glow.

### Watermarked

saw the entire valley bathed in the soft, ethereal glow of the rising sun, a breathtaking spectacle that made him pause in his ascent.

## Bounded projection

- 9,600 generated tokens / 18.422 tok/s = 521.1 s, or USD 0.1157 of L4 generation time.
- 19,200 generated tokens / 18.422 tok/s = 1042.2 s, or USD 0.2314 of L4 generation time.

These are GPU-only linear projections. They exclude image build, model download,
model load,
CPU, memory, storage, retries, and non-linear scaling.

## Review gate

- Peak-memory headroom: 56.1% (pass)
- Slowest watermarked throughput: 18.422 tok/s (pass)
- Runtime smoke: pass
- Projection below USD 5.00: pass

The three watermarked rows remained below the configured z > 3 cutoff. This does not
invalidate the runtime path, and it does not estimate detection accuracy. The smoke stops
for human review.

A positive score would mean only consistent with this configured watermark and key. Six
generations do not measure quality, accuracy, a false-alarm rate, or a total cloud bill.
