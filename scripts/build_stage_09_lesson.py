#!/usr/bin/env python3
# ruff: noqa: E501
"""Build the standalone Stage 9 final lesson from committed evidence."""

from __future__ import annotations

import html as html_lib
import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".agent/diagrams/text-watermarking-stage-9-final-lesson.html"


def load(path: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((ROOT / path).read_text()))


def compact(value: object) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")


def text(value: object) -> str:
    return (
        html_lib.escape(str(value))
        .replace("\u2014", " - ")
        .replace("\u2013", "-")
        .replace("\u2026", "...")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


def main() -> None:
    lab01 = load("artifacts/lab-01/summary.json")
    lab03 = load("artifacts/lab-03/trace.json")
    lab05 = load("artifacts/lab-05/trace.json")
    lab06 = load("artifacts/lab-06/calibration.json")
    lab07 = load("artifacts/lab-07/results.json")
    lab08 = load("artifacts/lab-08/results.json")

    stage03_control = next(
        row
        for row in lab03["records"]
        if row["prompt_id"] == "stage-02-continuity" and row["condition"] == "control"
    )
    stage03_marked = next(
        row
        for row in lab03["records"]
        if row["prompt_id"] == "stage-02-continuity" and row["condition"] == "score_increase"
    )
    step_control = stage03_control["steps"][0]
    step_marked = stage03_marked["steps"][0]
    rows07 = cast(list[dict[str, Any]], lab07["selected_rows"])
    rows08 = cast(list[dict[str, Any]], lab08["selected_rows"])
    spine07 = rows07[0]
    spine08 = rows08[0]
    score80 = spine07["prefix_scores"]["80"]["watermarked_correct"]
    score160 = spine07["prefix_scores"]["160"]
    tokens = spine07["token_evidence"]["watermarked_correct"][:80]

    attack_labels = [
        ("normalization", "Normalize"),
        ("homoglyph_1", "Homoglyph 1%"),
        ("homoglyph_5", "Homoglyph 5%"),
        ("deletion_10", "Delete 10%"),
        ("deletion_30", "Delete 30%"),
        ("mixing_25", "Mix 25%"),
        ("mixing_50", "Mix 50%"),
        ("paraphrase", "Paraphrase"),
    ]
    family_labels = {
        "watermarked_correct": "Marked / generation key",
        "control_correct": "Model control / generation key",
        "natural_correct": "Natural web / generation key",
        "watermarked_comparison": "Marked / comparison key",
    }
    payload_rows = []
    for row in rows07:
        payload_rows.append(
            {
                "rank": row["selection_rank"],
                "prefix": row["prefix_scores"],
            }
        )
    attack_rows = []
    bias_rows = []
    for row in rows08:
        attack_rows.append(
            {
                "rank": row["selection_rank"],
                "baseline": row["baseline_score"]["z_score"],
                "attacks": {
                    label: {
                        "change": row["attacks"][label]["z_change"],
                        "z": row["attacks"][label]["score"].get("z_score"),
                        "ratio": row["attacks"][label]["length_ratio"],
                        "auto": row["attacks"][label].get("automatic_preservation_pass"),
                        "manual": row["attacks"][label].get("manual_review", {}).get("decision"),
                    }
                    for label, _ in attack_labels
                },
            }
        )
        if row["bias_generations"] is not None:
            bias_rows.append(
                {
                    "rank": row["selection_rank"],
                    "values": {
                        delta: {
                            "z": record["score"]["z_score"],
                            "nll": record["conditional_nll"],
                            "repeat": record["repeated_pair_fraction"],
                            "length": record["copied_token_count"],
                        }
                        for delta, record in row["bias_generations"].items()
                    },
                }
            )

    payload = {
        "stage1": [
            {"length": row["length"], "condition": row["condition"], "rate": row["detection_rate"]}
            for row in lab01["rows"]
        ],
        "candidateControl": step_control["candidates"],
        "candidateMarked": step_marked["candidates"],
        "tokens": tokens,
        "rows": payload_rows,
        "prefixSummary": lab07["prefix_summary"],
        "attacks": attack_rows,
        "attackSummary": lab08["attack_summary"],
        "bias": bias_rows,
        "biasSummary": lab08["bias_summary"],
    }
    evidence = {
        "lab01_source_commit": lab01["source_commit"],
        "lab03_source_commit": lab03["source_commit"],
        "lab05_source_commit": lab05["source_commit"],
        "lab06_source_commit": lab06["source_commit"],
        "lab07_source_commit": lab07["source_commit"],
        "lab08_source_commit": lab08["source_commit"],
        "spine_rank": spine07["selection_rank"],
        "spine_80": score80,
        "spine_160": score160,
        "prefix_summary": lab07["prefix_summary"],
        "attack_summary": lab08["attack_summary"],
        "bias_summary": lab08["bias_summary"],
    }
    expected = score80["num_tokens_scored"] * 0.25
    movement = (score80["num_tokens_scored"] * 0.25 * 0.75) ** 0.5
    runtime07 = lab07["runtime_ns"] / 1_000_000_000
    natural_summary = lab06["summary"]
    html = f"""<!doctype html>
<html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Inside a model-level text watermark: the complete open-model lesson</title>
<style>
:root{{color-scheme:dark;--bg:#000;--surface:#111;--raised:#181818;--border:#303238;--text:#f5f7fa;--muted:#a9adb5;--blue:#60a5fa;--cyan:#55d6e8;--green:#4ade80;--yellow:#facc15;--coral:#fb7185;--violet:#a78bfa;--track:#26282d}}
html[data-theme="light"]{{color-scheme:light;--bg:#f7f7f5;--surface:#fff;--raised:#eef0f2;--border:#c9cdd3;--text:#111318;--muted:#5f6570;--track:#dde1e6}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--text);font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}header,main,footer{{width:min(1120px,calc(100% - 40px));margin:auto}}header{{padding:28px 0 42px;border-bottom:1px solid var(--border)}}section{{padding:70px 0;border-bottom:1px solid var(--border)}}h1{{font-size:clamp(2.2rem,6vw,4.9rem);line-height:.98;letter-spacing:-.055em;max-width:1000px;margin:36px 0 24px}}h2{{font-size:clamp(1.65rem,3vw,2.65rem);line-height:1.12;letter-spacing:-.03em;margin:0 0 14px}}h3{{font-size:1.03rem;margin:0 0 8px}}p{{max-width:850px}}a{{color:var(--cyan)}}button{{font:inherit;min-height:44px;padding:.55rem .85rem;background:var(--raised);color:var(--text);border:1px solid var(--border);border-radius:6px;cursor:pointer}}button:hover{{border-color:var(--cyan)}}button.active,button[aria-pressed="true"]{{background:var(--text);color:var(--bg)}}button:disabled{{opacity:.38}}button:focus-visible,a:focus-visible,summary:focus-visible{{outline:3px solid var(--yellow);outline-offset:3px}}.top{{display:flex;justify-content:space-between;gap:16px;align-items:center}}.stage,.eyebrow{{font:700 .76rem/1.2 ui-monospace,monospace;letter-spacing:.11em;text-transform:uppercase;color:var(--cyan)}}.lede{{font-size:clamp(1.08rem,2vw,1.35rem);color:var(--muted);max-width:900px}}.question{{margin-top:24px;padding:15px 18px;border-left:4px solid var(--cyan);background:var(--surface)}}nav,.controls{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}}nav a{{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--border)}}.panel{{background:var(--surface);border:1px solid var(--border);padding:20px;border-radius:8px;min-width:0}}.grid2{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:22px}}.grid3{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px}}.grid4{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:18px}}.metric{{font-size:clamp(2rem,5vw,3.5rem);font-weight:760;line-height:1;letter-spacing:-.04em;margin:10px 0}}.metric small{{display:block;font-size:.34em;line-height:1.3;color:var(--muted);letter-spacing:0;margin-top:8px}}.try{{padding:14px 17px;border-left:3px solid var(--yellow);background:var(--raised);margin:22px 0 12px}}.try strong{{color:var(--yellow)}}.feedback{{padding:12px 14px;min-height:3.2em;border:1px solid var(--border);background:var(--bg);color:var(--muted)}}.state{{border-top:4px solid var(--blue)}}.state.edit{{border-color:var(--coral)}}.state.rewrite{{border-color:var(--violet)}}.source{{max-height:210px;overflow:auto;padding:17px;background:var(--surface);border:1px solid var(--border)}}.loop{{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin:24px 0}}.loop div{{padding:12px 8px;background:var(--surface);border-top:3px solid var(--blue);font-size:.84rem}}.loop div:nth-child(3),.loop div:nth-child(4){{border-color:var(--yellow)}}.candidate{{display:grid;grid-template-columns:1.1fr repeat(4,.8fr);gap:1px;background:var(--border);border:1px solid var(--border);overflow:auto}}.candidate>*{{padding:9px;background:var(--surface);min-width:90px}}.candidate .head{{color:var(--muted);font-size:.78rem}}.candidate .green{{color:var(--green)}}.token-box{{height:245px;overflow:auto;padding:12px;background:var(--bg);border:1px solid var(--border);line-height:2.1}}.token{{display:inline-block;padding:0 4px;margin:2px 2px 2px 0;border:1px solid transparent;border-radius:3px;font:12px ui-monospace,monospace;white-space:pre-wrap}}.token.g{{background:color-mix(in srgb,var(--green) 20%,transparent);border-color:var(--green)}}.token.r{{background:color-mix(in srgb,var(--coral) 15%,transparent);border-color:var(--coral)}}.token.u{{color:var(--muted);border-style:dashed;border-color:var(--muted)}}.token.future{{opacity:.14}}.token.cursor{{outline:3px solid var(--yellow);outline-offset:2px}}.math{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:18px}}.math div{{padding:13px;border-top:3px solid var(--cyan);background:var(--surface)}}.math b{{display:block;font:700 1.1rem ui-monospace,monospace}}.chart{{height:390px;border:1px solid var(--border);background:var(--surface);margin-top:14px}}svg{{width:100%;height:100%;display:block}}.family{{border-top:4px solid var(--green)}}.family.control{{border-color:var(--cyan)}}.family.natural{{border-color:var(--violet)}}.family.compare{{border-color:var(--yellow)}}.family .z{{font:760 1.8rem/1 ui-monospace,monospace;margin:12px 0}}.warning{{border-left:4px solid var(--coral)}}.good{{border-left:4px solid var(--green)}}.table-wrap{{overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:.87rem;min-width:720px}}th,td{{padding:9px;border-bottom:1px solid var(--border);text-align:left}}th{{color:var(--muted)}}code,pre{{font-family:ui-monospace,monospace}}pre{{overflow:auto;padding:16px;background:var(--bg);border:1px solid var(--border)}}details{{margin-top:14px;padding:0 16px;border:1px solid var(--border);background:var(--surface)}}summary{{padding:14px 0;cursor:pointer;font-weight:700}}.claim{{padding:14px 17px;background:var(--raised);border-left:4px solid var(--green);font-size:1.08rem}}.static{{display:none}}footer{{padding:36px 0 70px;color:var(--muted)}}
@media(max-width:820px){{body{{font-size:16px}}header,main,footer{{width:min(100% - 24px,1120px)}}section{{padding:52px 0}}.grid2,.grid3,.grid4{{grid-template-columns:1fr}}.math{{grid-template-columns:1fr 1fr}}.loop{{grid-template-columns:1fr 1fr}}.chart{{height:340px}}}}@media(max-width:460px){{.math,.loop{{grid-template-columns:1fr}}}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}}}
</style><noscript><style>.static{{display:block}}</style></noscript></head><body>
<header><div class="top"><span class="stage">Text watermarking lab / Stage 9</span><button id="theme" type="button">Use light page</button></div><h1>One sampled token at a time. One narrow claim at the end.</h1><p class="lede">This final lesson starts with the exact Stage 8 edit, rewinds to the model's first token choice, and rebuilds the evidence through every control. No new model text was generated for Stage 9.</p><div class="question"><strong>One question.</strong> What did this small open-model watermark experiment establish, and what remains unknown?</div><nav><a href="#opening">Recorded string</a><a href="#sampler">One token</a><a href="#checker">Checker</a><a href="#controls">Controls</a><a href="#cohort">24 rows</a><a href="#editing">Editing</a><a href="#boundary">Answer</a></nav></header>
<main>
<section id="opening"><div class="eyebrow">Continue from Stage 8</div><h2>The same rank 1000 string is still the object.</h2><p>Stage 7 generated it once. Stage 8 edited it. Stage 9 selects no replacement row and runs no model.</p><div class="grid3"><article class="panel state"><h3>Recorded marked copy</h3><p class="metric">28/79 <small>green checks, z 2.1436</small></p><p>Below the fixed strict cutoff of z greater than 3.</p></article><article class="panel state edit"><h3>Delete 10 percent</h3><p class="metric">25/79 <small>green checks, z 1.3641</small></p><p>Length ratio 0.8929. Meaning was not certified.</p></article><article class="panel state rewrite"><h3>Paraphrase</h3><p class="metric">26/79 <small>green checks, z 1.6239</small></p><p>Declared automatic screen and non-independent review passed.</p></article></div><p class="source">{text(spine08["original_text"])}</p><div class="claim">A watermark checker asks whether copied text fits one key and profile unusually well. It does not classify arbitrary prose as AI or human.</div></section>
<section id="sampler"><div class="eyebrow">Rewind to Stage 3</div><h2>Change the chances before one token is drawn.</h2><p>The model supplies candidate scores. The key and previous token select a green group. The marked path adds 2 to green scores, then the sampler filters and draws. Both saved paths start from the same scores and seed.</p><div class="try"><strong>Try this.</strong> Toggle the score increase. Scores, key, context, seed, temperature, top-p, and top-k stay fixed. Watch `Jack` change chance while the saved token stays the same.</div><div class="controls"><button id="biasOff" class="active">Score increase off</button><button id="biasOn">Score increase on</button></div><div id="candidateTable" class="candidate" role="table" aria-label="Saved first-token candidate scores"></div><div class="feedback" id="candidateFeedback" aria-live="polite"></div><p>In the saved control table, `Jack` has an 11.6422 percent chance. With the score increase, it has an 18.5816 percent chance. The saved draw selects `Jack` in both paths.</p><div class="loop" aria-label="Autoregressive generation loop"><div>1. Tokenize</div><div>2. Model scores</div><div>3. Key selects green</div><div>4. Increase green scores</div><div>5. Filter and draw</div><div>6. Append token</div><div>7. Repeat</div></div><p>One matching draw does not make the probability tables equal. The recorded paths diverge later and then keep separate histories.</p><details><summary>The maintained order matters</summary><p>Stage 4 pinned Transformers 5.14.1. It applied temperature, top-k, top-p, then the watermark processor. Stage 3's teaching loop applied its score increase before temperature, top-p, and top-k. The causal pieces correspond, but the recipes are not interchangeable.</p></details></section>
<section id="checker"><div class="eyebrow">Concrete count before notation</div><h2>Replay the generation key on 80 copied tokens.</h2><p>The first token supplies context. Each later token is green or red for its exact previous token ID and the generation key. Green means keyed membership only.</p><div class="controls"><button id="tokenPlay">Play</button><button id="tokenPause">Pause</button><button id="tokenPrev">Previous token</button><button id="tokenNext">Next token</button><button id="tokenReplay">Replay</button></div><div class="token-box" id="tokenBox"></div><div class="feedback" id="tokenFeedback">The first copied token is unscored context.</div><div class="math"><div><span>Ordinary hits</span><b>{expected:.2f}</b><small>79 x 0.25</small></div><div><span>Recorded hits</span><b>28</b><small>among 79 checks</small></div><div><span>Usual movement</span><b>{movement:.4f}</b><small>sqrt(79 x .25 x .75)</small></div><div><span>Standardized distance</span><b>{score80["z_score"]:.4f}</b><small>(28 - 19.75) / {movement:.4f}</small></div></div><p>This standardized distance is the z score. Rank 1000 is 2.1436 usual movements above the configured quarter-green average. The separate decision rule is strict <strong>z greater than 3</strong>, so this 80-token row stays below it.</p></section>
<section id="length"><div class="eyebrow">Clean intuition, then recorded friction</div><h2>More checks can expose a persistent excess.</h2><p>Stage 1 used independent coins so the mechanism was visible without a model. Select a length to compare the teaching-biased condition with the null condition.</p><div class="controls" id="lengthButtons">{"".join(f'<button data-length="{n}"' + (' class="active"' if n == 80 else "") + f">{n} trials</button>" for n in (40, 80, 160, 200, 400))}</div><div class="chart"><svg id="lengthSvg" role="img" aria-labelledby="lengthTitle lengthDesc"><title id="lengthTitle">Stage 1 simulated detection by length</title><desc id="lengthDesc">Null and teaching-biased detection rates at five eligible lengths.</desc></svg></div><div class="feedback" id="lengthFeedback"></div><p>Stage 7 kept normal end-token behavior. Complete paired cohorts were 24 at 40 and 80 copied tokens, 21 at 160, 17 at 200, and zero at 400. The shrinking cohort means this recorded experiment does not isolate a causal length effect.</p></section>
<section id="controls"><div class="eyebrow">One row, four questions</div><h2>A score needs the right comparison.</h2><p>Keep rank 1000, the 160-token prefix, tokenizer, profile, and cutoff fixed. Change only the checked text or key role.</p><div class="controls" id="familyButtons">{"".join(f'<button data-family="{key}"' + (' class="active"' if key == "watermarked_correct" else "") + f">{label}</button>" for key, label in family_labels.items())}</div><div class="grid4">{"".join(f'<article class="panel family {cls}" data-family-card="{key}"><h3>{label}</h3><div class="z">{score160[key]["z_score"]:.4f}</div><p>{score160[key]["num_green_tokens"]}/{score160[key]["num_tokens_scored"]} green checks</p></article>' for (key, label), cls in zip(family_labels.items(), ("", "control", "natural", "compare"), strict=True))}</div><div class="feedback" id="familyFeedback"></div><article class="panel warning" style="margin-top:22px"><h3>The inconvenient row stayed</h3><p>Rank 1001's marked and control paths shared their first 80 copied token IDs. Both scored <strong>26/79, z 1.6239</strong>. A changed sampling distribution did not force a different early path.</p></article></section>
<section id="cohort"><div class="eyebrow">Every row before the mean</div><h2>The average separated. Individual rows overlapped.</h2><p>At 80 copied tokens all 24 pairs were complete. Each dot is one document-level marked z minus its matched control z. Zero means equal scores.</p><div class="controls" id="contrastButtons"><button data-contrast="versus_control" class="active">Versus model control</button><button data-contrast="versus_natural">Versus natural web</button><button data-contrast="versus_comparison_key">Versus comparison key</button></div><div class="chart"><svg id="cohortSvg" role="img" aria-labelledby="cohortTitle cohortDesc"><title id="cohortTitle">Twenty-four document-level paired z differences</title><desc id="cohortDesc">Every row appears before the mean and paired bootstrap interval.</desc></svg></div><div class="feedback" id="cohortFeedback"></div><div class="grid2"><article class="panel good"><h3>Frozen 24-row result</h3><p class="metric">+1.8296 <small>mean z versus model control</small></p><p>95 percent paired bootstrap interval [1.3424, 2.3276].</p></article><article class="panel warning"><h3>Outside text crossed too</h3><p class="metric">4/1000 <small>natural-web all-pair crossings</small></p><p>Median z {natural_summary["all_pair_z_quantiles"]["median"]:.4f}; 99th percentile {natural_summary["all_pair_z_quantiles"]["q99"]:.4f}; maximum {natural_summary["maximum_all_pair_z"]:.4f}.</p></article></div><p>The maximum natural-web row moved from 132/399, z 3.7286, to 114/358, z 2.9904 when each repeated value-pair counted once. One thousand C4 rows do not define a production false-alarm rate.</p></section>
<section id="editing"><div class="eyebrow">Return to the opening string</div><h2>The string changes first. The keyed history rebuilds second.</h2><p>Keep the 12 frozen rows, key, tokenizer, and first-80-ID rule fixed. Select one edit. Each point is edited z minus that row's unedited z. Length and preservation checks remain separate.</p><div class="controls" id="attackButtons">{"".join(f'<button data-attack="{label}"' + (' class="active"' if label == "normalization" else "") + f">{name}</button>" for label, name in attack_labels)}</div><div class="chart"><svg id="attackSvg" role="img" aria-labelledby="attackTitle attackDesc"><title id="attackTitle">Twelve paired score changes after editing</title><desc id="attackDesc">Every frozen row appears for the selected edit.</desc></svg></div><div class="feedback" id="attackFeedback"></div><div class="grid2"><article class="panel warning"><h3>Preservation remains a separate gate</h3><p>Deletion and mixing can damage grammar or claims. Homoglyph substitution diagnoses Unicode and tokenizer sensitivity. A lower score alone is not a meaning-preserving removal.</p></article><article class="panel"><h3>Paraphrase evidence</h3><p>All 12 passed the automatic screen. The non-independent assistant review marked 10 pass and 2 uncertain. Every passed rewrite reduced z; no paraphrase crossed strict z greater than 3.</p></article></div></section>
<section id="tradeoff"><div class="eyebrow">Reset to generation time</div><h2>A stronger bias bought more mean evidence and moved the proxies.</h2><p>Eight prompts kept model, seed, sampler, key, green fraction, context rule, and 400 generated-token safety cap fixed. Delta alone changed. NLL and repetition are model-based proxies, not human quality judgments.</p><div class="controls" id="deltaButtons"><button data-delta="1">Delta 1</button><button data-delta="2" class="active">Delta 2</button><button data-delta="3">Delta 3</button></div><div class="chart"><svg id="biasSvg" role="img" aria-labelledby="biasTitle biasDesc"><title id="biasTitle">Eight row-level z paths across watermark bias</title><desc id="biasDesc">Raw row paths appear with the selected delta highlighted.</desc></svg></div><div class="feedback" id="biasFeedback"></div><div class="table-wrap"><table><thead><tr><th>Delta</th><th>Rows</th><th>Mean z</th><th>Strict crossings</th><th>Mean NLL</th><th>Mean repeated-pair fraction</th><th>Mean copied tokens</th></tr></thead><tbody>{"".join(f"<tr><td>{d}</td><td>8</td><td>{lab08['bias_summary'][str(d)]['mean_z']:.4f}</td><td>{lab08['bias_summary'][str(d)]['cutoff_crossings']}/8</td><td>{lab08['bias_summary'][str(d)]['mean_nll']:.4f}</td><td>{lab08['bias_summary'][str(d)]['mean_repeated_pair_fraction']:.4f}</td><td>{lab08['bias_summary'][str(d)]['mean_copied_tokens']:.1f}</td></tr>" for d in (1, 2, 3))}</tbody></table></div><p>Ranks 1004 and 1006 had lower z at delta 3 than delta 2. The eight-row mean rose, but a larger delta did not force every recorded path upward.</p></section>
<section id="field"><div class="eyebrow">Place the analogue honestly</div><h2>One public family was implemented. The wider field uses other samplers.</h2><div class="grid2"><article class="panel"><h3>KGW-style green list</h3><p>This repository implements a contextual green-list analogue. The key selects a token subset, green scores rise, and the checker counts green excess.</p><p><a href="https://arxiv.org/abs/2301.10226">Primary KGW paper</a></p></article><article class="panel"><h3>SynthID-Text</h3><p>The Nature paper uses keyed tournament sampling and studies non-distortionary and distortionary configurations. It reports a live quality assessment over nearly 20 million Gemini responses. This repository did not implement it.</p><p><a href="https://www.nature.com/articles/s41586-024-08025-4">Primary SynthID-Text paper</a></p></article></div><article class="panel warning" style="margin-top:18px"><h3>What Anthropic has and has not said</h3><p>Anthropic says it is adding machine-readable marks to Claude-generated content. Its support page describes an imperceptible model-level text mark that travels with copied text and may persist through editing. Detection documentation is forthcoming. The page does not disclose an algorithm that this project could reproduce.</p><p><a href="https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content">Anthropic support page, inspected 2026-08-16</a></p></article></section>
<section id="boundary"><div class="eyebrow">Measured answer</div><h2>The configured mark separated on average. The claim stays small.</h2><div class="grid2"><article class="panel good"><h3>Established here</h3><ul><li>A reproducible keyed sampling and copied-text checking path.</li><li>Average correct-key separation from three controls in one frozen 24-row Gemma experiment.</li><li>Measured score changes under named edits and delta settings.</li></ul></article><article class="panel warning"><h3>Still unknown</h3><ul><li>Production calibration, rare false-alarm rates, and adaptive security.</li><li>Human-perceived quality, another model, or another watermark family.</li><li>Generic AI origin, authorship, intent, or Claude's private implementation.</li></ul></article></div><p class="claim">A positive result means only: <strong>consistent with this configured watermark and key.</strong></p><details><summary>Runtime and reproducibility</summary><p>Stage 7 source commit <code>{lab07["source_commit"]}</code>. Its one L4 function made {lab07["generation_call_count"]} generation calls, returned {lab07["generated_token_id_count"]:,} generated token IDs, and ran for {runtime07:.1f} seconds. The configured-rate product is $0.1650 of GPU time, not the provider bill. Stage 9 used existing evidence only.</p><pre>just setup
just check
just verify-lab-07
just verify-lab-08
just verify-stage-09</pre></details><details><summary>Scripts-off evidence summary</summary><p>At 80 copied tokens, mean marked z exceeded model control by 1.8296, natural web by 1.7538, and comparison-key replay by 2.0461 across 24 frozen rows. Stage 8 paraphrase mean z change was -1.7105 across 12 rows. Mean z at delta 1, 2, and 3 was 0.2923, 2.1761, and 2.4684 across eight rows.</p></details><div class="static panel"><h3>Scripts-off fallback</h3><p>The complete narrative, tables, measured answer, and claim boundary remain readable. Interactive token replay and charts require JavaScript.</p></div></section>
</main><footer>Built from committed Stage 1 through Stage 8 artifacts. No external script, font, storage, model, or network request is required to read this page. Article source: <code>blog/article.md</code>.</footer>
<script id="evidence" type="application/json">{compact(evidence)}</script>
<script>const DATA={compact(payload)};const $=id=>document.getElementById(id);const NS='http:'+'//www.w3.org/2000/svg';const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
$('theme').onclick=()=>{{const light=document.documentElement.dataset.theme==='light';document.documentElement.dataset.theme=light?'dark':'light';$('theme').textContent=light?'Use light page':'Use dark page';}};
function candidate(marked){{const rows=marked?DATA.candidateMarked:DATA.candidateControl,root=$('candidateTable');root.replaceChildren();for(const h of ['Token','Raw score','Green','After increase','Final chance']){{const e=document.createElement('div');e.className='head';e.textContent=h;root.append(e)}}for(const r of rows){{for(const [value,cls] of [[r.token_text,''],[r.raw_score.toFixed(4),''],[r.in_green_group?'yes':'no',r.in_green_group?'green':''],[r.score_after_increase.toFixed(4),''],[(r.final_probability*100).toFixed(4)+'%','']]){{const e=document.createElement('div');e.className=cls;e.textContent=value;root.append(e)}}}}const jack=rows.find(r=>r.token_id===30604);$('candidateFeedback').textContent=`Score increase ${{marked?'on':'off'}}: Jack has ${{(jack.final_probability*100).toFixed(4)}}% chance. The saved draw selects Jack in both paths.`;$('biasOff').classList.toggle('active',!marked);$('biasOn').classList.toggle('active',marked)}}$('biasOff').onclick=()=>candidate(false);$('biasOn').onclick=()=>candidate(true);candidate(false);
const box=$('tokenBox');DATA.tokens.forEach(t=>{{const e=document.createElement('span');e.className='token '+(t.eligible?(t.is_green?'g':'r'):'u')+' future';e.textContent=t.piece||' ';e.title=`position ${{t.position}}, ID ${{t.token_id}}, ${{t.eligible?(t.is_green?'green':'red'):'unscored'}}`;box.append(e)}});let ti=0,tt=null;function pauseT(){{if(tt)clearInterval(tt);tt=null}}function renderT(){{[...box.children].forEach((e,i)=>{{e.classList.toggle('future',i>ti);e.classList.toggle('cursor',i===ti)}});const shown=DATA.tokens.slice(0,ti+1),eligible=shown.filter(t=>t.eligible),g=eligible.filter(t=>t.is_green).length;$('tokenFeedback').textContent=ti===0?'The first copied token is unscored context.':`Through position ${{ti}}, ${{g}} of ${{eligible.length}} eligible tokens are green.`;box.children[ti].scrollIntoView({{block:'nearest'}});if(ti>=79)pauseT()}}function playT(){{if(reduced){{$('tokenFeedback').textContent='Reduced motion is active. Use Previous token and Next token.';return}}pauseT();tt=setInterval(()=>{{ti=Math.min(79,ti+1);renderT()}},65)}}$('tokenPlay').onclick=playT;$('tokenPause').onclick=pauseT;$('tokenPrev').onclick=()=>{{pauseT();ti=Math.max(0,ti-1);renderT()}};$('tokenNext').onclick=()=>{{pauseT();ti=Math.min(79,ti+1);renderT()}};$('tokenReplay').onclick=()=>{{pauseT();ti=0;renderT();playT()}};renderT();
function svg(tag,a={{}}){{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(a))e.setAttribute(k,v);return e}}function lengthChart(active){{const root=$('lengthSvg'),lens=[40,80,160,200,400],x=n=>95+lens.indexOf(n)*185,y=v=>325-v*265;root.replaceChildren();root.setAttribute('viewBox','0 0 900 380');for(const cond of ['null','biased']){{const rs=lens.map(n=>DATA.stage1.find(r=>r.length===n&&r.condition===cond));let d='';rs.forEach(r=>d+=(d?'L':'M')+x(r.length)+','+y(r.rate));root.append(svg('path',{{d,fill:'none',stroke:cond==='biased'?'var(--green)':'var(--cyan)','stroke-width':cond==='biased'?'4':'2'}}));rs.forEach(r=>root.append(svg('circle',{{cx:x(r.length),cy:y(r.rate),r:r.length===active?'7':'4',fill:cond==='biased'?'var(--green)':'var(--cyan)'}})))}}lens.forEach(n=>{{const t=svg('text',{{x:x(n),y:355,fill:'var(--muted)','font-size':'13','text-anchor':'middle'}});t.textContent=n;t.setAttribute('aria-hidden','true');root.append(t)}});const a=DATA.stage1.find(r=>r.length===active&&r.condition==='biased'),n=DATA.stage1.find(r=>r.length===active&&r.condition==='null');$('lengthFeedback').textContent=`At ${{active}} independent trials: teaching-biased detection ${{(a.rate*100).toFixed(2)}}%; simulated null detection ${{(n.rate*100).toFixed(2)}}%.`}}document.querySelectorAll('[data-length]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-length]').forEach(x=>x.classList.toggle('active',x===b));lengthChart(Number(b.dataset.length))}});lengthChart(80);
const familyCopy={{watermarked_correct:'Marked text with the generation key: 58/159, z 3.3424. This one row crosses the fixed cutoff.',control_correct:'Paired model control with the generation key: 47/159, z 1.3278. It checks ordinary Gemma variation.',natural_correct:'Frozen natural-web continuation with the generation key: 43/159, z 0.5952. C4 is natural web, not verified human writing.',watermarked_comparison:'The same marked text with another key: 29/159, z -1.9688. It checks whether evidence is tied to the generation key.'}};document.querySelectorAll('[data-family]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-family]').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('[data-family-card]').forEach(x=>x.style.opacity=x.dataset.familyCard===b.dataset.family?'1':'.35');$('familyFeedback').textContent=familyCopy[b.dataset.family]}});$('familyFeedback').textContent=familyCopy.watermarked_correct;
let contrast='versus_control';function cohortChart(){{const root=$('cohortSvg'),s=DATA.prefixSummary['80'].comparisons[contrast],vals=s.row_differences,x=v=>80+(v+4)/11*760;root.replaceChildren();root.setAttribute('viewBox','0 0 900 380');root.append(svg('line',{{x1:x(0),x2:x(0),y1:30,y2:300,stroke:'var(--coral)','stroke-width':'2'}}));vals.forEach((v,i)=>root.append(svg('circle',{{cx:x(v),cy:50+(i%12)*20,r:i<2?'7':'5',fill:i===0?'var(--yellow)':i===1?'var(--coral)':'var(--cyan)'}})));root.append(svg('line',{{x1:x(s.interval_low),x2:x(s.interval_high),y1:315,y2:315,stroke:'var(--green)','stroke-width':'7'}}));root.append(svg('circle',{{cx:x(s.mean_difference),cy:315,r:'8',fill:'var(--green)'}}));[-2,0,2,4,6].forEach(v=>{{const t=svg('text',{{x:x(v),y:355,fill:'var(--muted)','font-size':'13','text-anchor':'middle'}});t.textContent=(v>0?'+':'')+v;root.append(t)}});$('cohortFeedback').textContent=`24 complete pairs. Mean difference ${{s.mean_difference.toFixed(4)}}; paired bootstrap interval [${{s.interval_low.toFixed(4)}}, ${{s.interval_high.toFixed(4)}}]. Every row remains visible.`}}document.querySelectorAll('[data-contrast]').forEach(b=>b.onclick=()=>{{contrast=b.dataset.contrast;document.querySelectorAll('[data-contrast]').forEach(x=>x.classList.toggle('active',x===b));cohortChart()}});cohortChart();
const attackNames={{normalization:'Normalization',homoglyph_1:'Homoglyph 1%',homoglyph_5:'Homoglyph 5%',deletion_10:'Deletion 10%',deletion_30:'Deletion 30%',mixing_25:'Mixing 25%',mixing_50:'Mixing 50%',paraphrase:'Paraphrase'}};function attackChart(label){{const root=$('attackSvg'),vals=DATA.attacks.map(r=>r.attacks[label].change),x=v=>90+(v+5)/7*750;root.replaceChildren();root.setAttribute('viewBox','0 0 900 380');root.append(svg('line',{{x1:x(0),x2:x(0),y1:30,y2:305,stroke:'var(--yellow)','stroke-width':'2'}}));vals.forEach((v,i)=>root.append(svg('circle',{{cx:x(v),cy:50+i*21,r:i<2?'7':'5',fill:i===0?'var(--green)':i===1?'var(--coral)':'var(--violet)'}})));[-4,-2,0,2].forEach(v=>{{const t=svg('text',{{x:x(v),y:350,fill:'var(--muted)','font-size':'13','text-anchor':'middle'}});t.textContent=(v>0?'+':'')+v+' z';root.append(t)}});const s=DATA.attackSummary[label];$('attackFeedback').textContent=`${{attackNames[label]}} across 12 frozen rows: mean z change ${{s.mean_z_change.toFixed(4)}}; mean copied-token length ratio ${{s.mean_length_ratio.toFixed(4)}}.`;if(label==='paraphrase')$('attackFeedback').textContent+=' Automatic screen 12/12; non-independent manual pass 10/12, uncertain 2/12.'}}document.querySelectorAll('[data-attack]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-attack]').forEach(x=>x.classList.toggle('active',x===b));attackChart(b.dataset.attack)}});attackChart('normalization');
function biasChart(active){{const root=$('biasSvg'),x=d=>130+(d-1)*320,y=z=>35+(5-z)/7*285;root.replaceChildren();root.setAttribute('viewBox','0 0 900 380');root.append(svg('line',{{x1:70,x2:840,y1:y(3),y2:y(3),stroke:'var(--yellow)','stroke-dasharray':'7 5'}}));DATA.bias.forEach((r,i)=>{{let path='';['1','2','3'].forEach(d=>path+=(path?'L':'M')+x(Number(d))+','+y(r.values[d].z));root.append(svg('path',{{d:path,fill:'none',stroke:i<2?(i===0?'var(--green)':'var(--coral)'):'var(--muted)','stroke-width':i<2?'3':'1.5',opacity:i<2?'1':'.65'}}));['1','2','3'].forEach(d=>root.append(svg('circle',{{cx:x(Number(d)),cy:y(r.values[d].z),r:d===active?'6':'4',fill:i===0?'var(--green)':i===1?'var(--coral)':'var(--cyan)'}})))}});['1','2','3'].forEach(d=>{{const t=svg('text',{{x:x(Number(d)),y:355,fill:'var(--muted)','font-size':'13','text-anchor':'middle'}});t.textContent='delta '+d;root.append(t)}});const s=DATA.biasSummary[active];$('biasFeedback').textContent=`Delta ${{active}} across eight rows: mean z ${{s.mean_z.toFixed(4)}}, ${{s.cutoff_crossings}} strict crossings, mean NLL ${{s.mean_nll.toFixed(4)}}, mean repeated-pair fraction ${{s.mean_repeated_pair_fraction.toFixed(4)}}.`}}document.querySelectorAll('[data-delta]').forEach(b=>b.onclick=()=>{{document.querySelectorAll('[data-delta]').forEach(x=>x.classList.toggle('active',x===b));biasChart(b.dataset.delta)}});biasChart('2');
</script></body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
