#!/usr/bin/env python3
# ruff: noqa: E501
"""Build the standalone Stage 6 lesson from selected evidence."""

from __future__ import annotations

import html as html_lib
import json
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/lab-06/calibration.json"
OUTPUT = ROOT / ".agent/diagrams/text-watermarking-stage-6-lesson.html"


def compact_json(value: object) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")


def main() -> None:
    artifact: dict[str, Any] = json.loads(ARTIFACT.read_text())
    summary = cast(dict[str, Any], artifact["summary"])
    scores = cast(list[dict[str, Any]], artifact["scores"])
    spine = cast(dict[str, Any], artifact["spine"])
    manifests = cast(list[dict[str, Any]], artifact["selection"]["manifest"])
    maximum_index = cast(int, summary["maximum_all_pair_selection_rank"])
    maximum = scores[maximum_index]
    maximum_manifest = manifests[maximum_index]
    first = scores[0]
    all_z = [row["all_pairs"]["z_score"] for row in scores]
    distinct_z = [row["distinct_pairs"]["z_score"] for row in scores]
    payload = {
        "allZ": all_z,
        "distinctZ": distinct_z,
        "tokens": spine["token_evidence"],
        "first": first,
        "maximum": maximum,
        "maximumManifest": maximum_manifest,
        "summary": summary,
    }

    def page_text(value: object) -> str:
        return html_lib.escape(str(value)).replace("—", ", ").replace("…", "...")

    expected_hits = first["all_pairs"]["num_tokens_scored"] * 0.25
    ordinary_movement = (first["all_pairs"]["num_tokens_scored"] * 0.25 * (1 - 0.25)) ** 0.5
    excess = first["all_pairs"]["num_green_tokens"] - expected_hits
    html = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Stage 6: check the checker on natural-web text</title>
<style>
:root{{color-scheme:dark;--bg:#000;--surface:#111;--raised:#181818;--border:#303238;--text:#f5f7fa;--muted:#a9adb5;--blue:#60a5fa;--cyan:#55d6e8;--green:#4ade80;--yellow:#facc15;--coral:#fb7185;--violet:#a78bfa;--track:#24262b;--focus:#fff}}
html[data-theme="light"]{{color-scheme:light;--bg:#f7f7f5;--surface:#fff;--raised:#f0f1f2;--border:#cdd0d5;--text:#111318;--muted:#5f6570;--track:#dfe2e6;--focus:#111}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--text);font:17px/1.58 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}button,a,summary{{font:inherit}}button{{min-height:44px;padding:.55rem .85rem;border:1px solid var(--border);background:var(--raised);color:var(--text);cursor:pointer;border-radius:6px}}button:hover{{border-color:var(--cyan)}}button[aria-pressed="true"],button.active{{background:var(--text);color:var(--bg)}}button:focus-visible,a:focus-visible,summary:focus-visible{{outline:3px solid var(--focus);outline-offset:3px}}a{{color:var(--cyan)}}code,.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}header,main,footer{{width:min(1120px,calc(100% - 40px));margin-inline:auto}}header{{padding:28px 0 24px;border-bottom:1px solid var(--border)}}.topline{{display:flex;align-items:center;justify-content:space-between;gap:18px}}.stage{{font:700 .78rem/1.2 ui-monospace,monospace;letter-spacing:.12em;color:var(--cyan);text-transform:uppercase}}h1{{font-size:clamp(2rem,5vw,4.2rem);line-height:1.02;letter-spacing:-.045em;max-width:900px;margin:38px 0 22px}}.lede{{font-size:clamp(1.08rem,2vw,1.38rem);line-height:1.48;max-width:830px;color:var(--muted)}}.question{{border-left:4px solid var(--cyan);padding:16px 20px;margin-top:28px;background:var(--surface);font-size:1.1rem}}nav{{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}}nav a{{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--border)}}main{{padding-bottom:100px}}section{{padding:76px 0;border-bottom:1px solid var(--border)}}section>h2{{font-size:clamp(1.65rem,3vw,2.55rem);line-height:1.12;letter-spacing:-.025em;margin:0 0 16px}}h3{{font-size:1.08rem;margin:0 0 8px}}p{{max-width:800px}}.eyebrow{{font:700 .75rem/1.2 ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);margin-bottom:12px}}.note{{color:var(--muted)}}.grid2{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:28px}}.panel{{min-width:0;background:var(--surface);border:1px solid var(--border);padding:22px;border-radius:8px}}.panel.coral{{border-left:4px solid var(--coral)}}.panel.green{{border-left:4px solid var(--green)}}.metric{{font-size:clamp(2rem,5vw,3.6rem);font-weight:760;line-height:1;letter-spacing:-.04em;margin:10px 0}}.metric small{{font-size:.42em;color:var(--muted);letter-spacing:0}}.continuity{{display:grid;grid-template-columns:1fr auto 1fr;gap:18px;align-items:stretch;margin-top:30px}}.continuity .bridge{{align-self:center;color:var(--yellow);font:800 1.3rem ui-monospace,monospace}}.object-row{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}}.object{{border:1px solid var(--border);padding:5px 9px;border-radius:999px;font:700 .84rem ui-monospace,monospace}}.object.g{{color:var(--green)}}.object.c{{color:var(--cyan)}}.object.y{{color:var(--yellow)}}.try{{margin:24px 0 14px;padding:16px 18px;background:var(--raised);border-left:3px solid var(--yellow)}}.try strong{{color:var(--yellow)}}.controls{{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:14px 0}}.feedback{{min-height:3.2em;padding:12px 14px;border:1px solid var(--border);background:var(--bg);color:var(--muted)}}.source-line{{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:9px 0;border-bottom:1px solid var(--border)}}.source-line b{{font-size:.82rem;color:var(--muted);font-family:ui-monospace,monospace}}.filter-list{{list-style:none;padding:0;margin:18px 0}}.filter-list li{{display:flex;gap:10px;padding:10px;border-bottom:1px solid var(--border);color:var(--muted)}}.filter-list li.current{{color:var(--text);background:var(--raised)}}.filter-list li.done::before{{content:"PASS";font:700 .7rem ui-monospace,monospace;color:var(--green)}}.filter-list li:not(.done)::before{{content:"WAIT";font:700 .7rem ui-monospace,monospace;color:var(--muted)}}.token-ruler{{display:grid;grid-template-columns:1fr 8fr 2.75fr;height:54px;margin:24px 0 10px;border:1px solid var(--border)}}.token-ruler>div{{display:grid;place-items:center;text-align:center;font:700 .78rem ui-monospace,monospace;border-right:1px solid var(--bg)}}.prompt-band{{background:color-mix(in srgb,var(--blue) 35%,var(--surface))}}.continuation-band{{background:color-mix(in srgb,var(--yellow) 30%,var(--surface))}}.unused-band{{background:var(--track);color:var(--muted)}}.ruler-labels{{display:grid;grid-template-columns:1fr 8fr 2.75fr;color:var(--muted);font:.75rem ui-monospace,monospace}}.ruler-labels span:nth-child(2){{text-align:right}}.ruler-labels span:nth-child(3){{text-align:right}}.token-box{{height:265px;overflow:auto;padding:14px;background:var(--bg);border:1px solid var(--border);line-height:2.15;scrollbar-color:var(--border) var(--bg)}}.token{{display:inline-block;margin:2px 2px 2px 0;padding:0 4px;border:1px solid transparent;border-radius:3px;font-family:ui-monospace,monospace;font-size:.82rem;white-space:pre-wrap}}.token.green-token{{background:color-mix(in srgb,var(--green) 20%,transparent);border-color:var(--green)}}.token.red-token{{background:color-mix(in srgb,var(--coral) 15%,transparent);border-color:color-mix(in srgb,var(--coral) 60%,var(--border))}}.token.unscored{{color:var(--muted);border-style:dashed;border-color:var(--muted)}}.token.future{{opacity:.2}}.token.cursor{{outline:3px solid var(--yellow);outline-offset:2px}}.legend{{display:flex;flex-wrap:wrap;gap:15px;color:var(--muted);font-size:.82rem;margin:10px 0}}.legend span::before{{content:"";display:inline-block;width:10px;height:10px;margin-right:6px;border:1px solid currentColor}}.legend .lg::before{{background:var(--green)}}.legend .lr::before{{background:var(--coral)}}.legend .lu::before{{background:transparent;border-style:dashed}}.countline{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}}.countline div{{padding:12px;background:var(--raised);border:1px solid var(--border)}}.countline b{{display:block;font:750 1.2rem ui-monospace,monospace}}.math-flow{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:26px}}.math-step{{padding:16px;border-top:3px solid var(--cyan);background:var(--surface)}}.math-step b{{display:block;font:700 1.25rem ui-monospace,monospace;margin:8px 0}}.chart-wrap{{position:relative;height:390px;border:1px solid var(--border);background:var(--surface);margin-top:16px;overflow:hidden}}#scoreSvg{{width:100%;height:100%;display:block}}.chart-note{{font-size:.82rem;color:var(--muted)}}.reveal-buttons button{{min-width:85px}}.failure-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px}}.score-rule{{display:grid;grid-template-columns:1fr auto;align-items:center;gap:12px;padding:14px;border:1px solid var(--border);background:var(--raised)}}.score-rule .bar{{grid-column:1/-1;height:8px;background:var(--track);position:relative}}.score-rule .fill{{height:100%;background:var(--coral)}}.score-rule .cut{{position:absolute;left:75%;top:-5px;width:2px;height:18px;background:var(--yellow)}}.funnel{{margin-top:26px}}.funnel-row{{display:grid;grid-template-columns:180px 1fr 80px;gap:12px;align-items:center;margin:9px 0}}.funnel-track{{height:18px;background:var(--track)}}.funnel-fill{{height:100%;background:var(--blue)}}.sample-grid{{display:grid;grid-template-columns:repeat(50,1fr);gap:2px;margin:18px 0}}.sample-grid span{{aspect-ratio:1;background:var(--track)}}.sample-grid span.hit{{background:var(--coral)}}details{{margin-top:16px;border:1px solid var(--border);padding:0 16px;background:var(--surface)}}summary{{padding:14px 0;cursor:pointer;font-weight:700}}table{{width:100%;border-collapse:collapse;font-size:.88rem;table-layout:fixed}}th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--border);overflow-wrap:anywhere}}th{{color:var(--muted);width:32%}}footer{{padding:35px 0 70px;color:var(--muted)}}.static{{display:none}}noscript .static{{display:block}}@media(max-width:800px){{body{{font-size:16px}}header,main,footer{{width:min(100% - 24px,1120px)}}section{{padding:54px 0}}.grid2,.continuity,.failure-grid{{grid-template-columns:1fr}}.continuity .bridge{{transform:rotate(90deg);justify-self:start}}.math-flow{{grid-template-columns:1fr 1fr}}.countline{{grid-template-columns:1fr 1fr}}.source-line{{grid-template-columns:1fr}}.funnel-row{{grid-template-columns:115px 1fr 52px;font-size:.78rem}}.chart-wrap{{height:330px}}.sample-grid{{grid-template-columns:repeat(25,1fr)}}}}@media(max-width:480px){{.math-flow{{grid-template-columns:1fr}}.token-ruler,.ruler-labels{{grid-template-columns:1fr 8fr 1.4fr}}}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}}}@media print{{:root{{--bg:#fff;--surface:#fff;--raised:#f3f3f3;--border:#aaa;--text:#111;--muted:#444}}button,nav{{display:none}}section{{break-inside:avoid}}}}
</style>
<noscript><style>.static{{display:block}}</style></noscript>
</head>
<body>
<header>
  <div class="topline"><div class="stage">Text watermarking lab / Stage 6</div><button id="theme" type="button" aria-pressed="false">Use light page</button></div>
  <h1>Before trusting the checker, check its background noise.</h1>
  <p class="lede">Stage 5 showed that Gemma can plant a keyed token pattern. That is only half the job. The same checker must also face text where we did not plant the pattern.</p>
  <div class="question"><strong>One question.</strong> What scores does the Stage 5 checker assign to text that was not generated with its key?</div>
  <nav aria-label="Lesson sections"><a href="#handoff">Handoff</a><a href="#row">One row</a><a href="#checker">Same checker</a><a href="#cohort">1,000 rows</a><a href="#failure">Failure case</a><a href="#limits">Limits</a></nav>
</header>
<main>
<section id="handoff">
  <div class="eyebrow">Continue the same story</div><h2>The objects stay. The source changes.</h2>
  <p>Stage 5 used 12 fixed prompts to prove that generation and checking worked. No control row crossed the strict cutoff. Twelve rows cannot tell us how often outside text wanders into the same score range.</p>
  <div class="continuity">
    <article class="panel"><div class="eyebrow">Stage 5 handoff</div><div class="metric">0 <small>of 12 controls</small></div><p>Above strict <span class="mono">z &gt; 3</span> in the natural-length ladder.</p><div class="object-row"><span class="object g">G hits</span><span class="object c">T checks</span><span class="object y">z score</span></div></article>
    <div class="bridge" aria-hidden="true">THEN</div>
    <article class="panel"><div class="eyebrow">Stage 6 change</div><div class="metric">1,000 <small>natural-web rows</small></div><p>Same Gemma tokenizer, public key, green fraction, CUDA rule, score, and cutoff.</p><div class="object-row"><span class="object g">G hits</span><span class="object c">T checks</span><span class="object y">z score</span></div></article>
  </div>
  <p class="note">A negative reference means text selected without using the checker result. C4 calls this split <span class="mono">realnewslike</span>. We call it natural-web text. We do not know that every row was written only by a human.</p>
</section>
<section id="row">
  <div class="eyebrow">Spine example / selected before scoring</div><h2>Follow the first accepted row.</h2>
  <p>The selection rule starts at dataset row 0 and walks forward. The first accepted row remains the worked example even though its score is not dramatic.</p>
  <div class="grid2">
    <article class="panel"><h3>Source identity</h3><div class="source-line"><b>dataset row</b><span>0</span></div><div class="source-line"><b>timestamp</b><span>{page_text(spine["timestamp"])}</span></div><div class="source-line"><b>URL</b><a href="{page_text(spine["url"])}">{page_text(spine["url"])}</a></div><div class="source-line"><b>text SHA-256</b><span class="mono">{page_text(spine["text_sha256"][:16])}...</span></div><div class="source-line"><b>Gemma tokens</b><span>{spine["full_token_count"]}</span></div></article>
    <article class="panel"><h3>Recorded excerpt</h3><p class="note">Prompt end</p><p>{page_text(spine["prompt_excerpt"])}</p><p class="note">Continuation start</p><p>{page_text(spine["continuation_excerpt"])}</p></article>
  </div>
  <div class="try"><strong>Try this.</strong> Step through the fixed filter. The row, tokenizer, and text never change. Watch which information is available before any score exists.</div>
  <div class="controls"><button id="filterPrev" type="button">Previous check</button><button id="filterNext" type="button">Next check</button><button id="filterReset" type="button">Start again</button></div>
  <ol class="filter-list" id="filterList"><li>At least 500 Gemma tokens</li><li>Exact text hash not seen earlier</li><li>Not an obvious list</li><li>Not a code dump</li><li>At least 65 percent Unicode letters among non-space characters</li></ol>
  <div class="feedback" id="filterFeedback" aria-live="polite">No detector score is available yet. Selection begins with length.</div>
  <div class="token-ruler" role="img" aria-label="The first 50 tokens form a future prompt. The next 400 form the natural-web continuation scored in Stage 6. Remaining tokens are unused."><div class="prompt-band">50<br>future prompt</div><div class="continuation-band">400<br>scored now</div><div class="unused-band">538<br>unused</div></div>
  <div class="ruler-labels" aria-hidden="true"><span>0</span><span>450</span><span>988</span></div>
  <p><strong>Why split it?</strong> Stage 6 scores the recorded 400-token continuation. It freezes the first 50 tokens for a future paired-generation experiment. No model runs here.</p>
</section>
<section id="checker">
  <div class="eyebrow">One recorded continuation / same Stage 5 profile</div><h2>Replay 400 copied token pieces through the checker.</h2>
  <p>The first continuation token supplies context. Each later token is green or red for the public key and the exact previous token. Green is keyed membership. It says nothing about meaning or quality.</p>
  <div class="try"><strong>Try this.</strong> Press Play. The token sequence, key, and cutoff stay fixed. Only the number of revealed checks changes. Watch the running green count.</div>
  <div class="controls"><button id="tokenPlay" type="button">Play</button><button id="tokenPause" type="button">Pause</button><button id="tokenPrev" type="button">Previous token</button><button id="tokenNext" type="button">Next token</button><button id="tokenReplay" type="button">Replay</button></div>
  <div class="token-box" id="tokenBox" aria-label="All 400 recorded continuation token pieces"></div>
  <div class="legend"><span class="lg">green for this key</span><span class="lr">outside this green set</span><span class="lu">unscored context</span></div>
  <div class="countline"><div><span>Revealed positions</span><b id="revealed">1 / 400</b></div><div><span>Eligible checks</span><b id="runningT">0</b></div><div><span>Green hits</span><b id="runningG">0</b></div><div><span>Running z</span><b id="runningZ">n/a</b></div></div>
  <div class="feedback" id="tokenFeedback" aria-live="polite">The first piece supplies context, so it is not scored.</div>
  <div class="math-flow">
    <div class="math-step"><span>Ordinary average</span><b>{expected_hits:.2f}</b><small>399 x 0.25</small></div>
    <div class="math-step"><span>Recorded hits</span><b>{first["all_pairs"]["num_green_tokens"]}</b><small>out of 399 checks</small></div>
    <div class="math-step"><span>Difference</span><b>{excess:.2f}</b><small>81 minus 99.75</small></div>
    <div class="math-step"><span>Usual movement</span><b>{ordinary_movement:.4f}</b><small>square root of 399 x .25 x .75</small></div>
  </div>
  <p>The row is {abs(excess):.2f} hits below the configured average. Divide by {ordinary_movement:.4f}. Its standardized distance, called a z-score, is <strong>{first["all_pairs"]["z_score"]:.4f}</strong>. The score and the cutoff are separate objects.</p>
</section>
<section id="cohort">
  <div class="eyebrow">Recorded cohort / no resampling</div><h2>One row is a story. One thousand rows show the background.</h2>
  <p>Each dot below is one frozen 400-token natural-web continuation. Its vertical position is z. The horizontal order is the manifest order. Coral dots crossed the unchanged strict cutoff.</p>
  <div class="try"><strong>Try this.</strong> Reveal 12 rows, then 100, then all 1,000. The rows and cutoff stay fixed. Watch the visible maximum and crossing count.</div>
  <div class="controls reveal-buttons" role="group" aria-label="Number of recorded rows to reveal"><button type="button" data-count="12">Show 12</button><button type="button" data-count="100">Show 100</button><button type="button" data-count="1000" class="active">Show 1,000</button></div>
  <div class="chart-wrap"><svg id="scoreSvg" role="img" aria-labelledby="scoreTitle scoreDesc"><title id="scoreTitle">Natural-web z scores</title><desc id="scoreDesc">One thousand recorded scores in manifest order with a strict cutoff at z greater than three.</desc></svg></div>
  <div class="feedback" id="cohortFeedback" aria-live="polite">All 1,000 recorded rows are visible. Four crossed strict z greater than 3.</div>
  <div class="countline"><div><span>Median z</span><b>{summary["all_pair_z_quantiles"]["median"]:.4f}</b></div><div><span>95th percentile</span><b>{summary["all_pair_z_quantiles"]["q95"]:.4f}</b></div><div><span>99th percentile</span><b>{summary["all_pair_z_quantiles"]["q99"]:.4f}</b></div><div><span>Maximum z</span><b>{summary["maximum_all_pair_z"]:.4f}</b></div></div>
  <p class="chart-note">Percentiles summarize this cohort. They are recorded order statistics, not promises about another corpus.</p>
</section>
<section id="failure">
  <div class="eyebrow">The inconvenient row stays</div><h2>A natural-web row crossed the frozen cutoff.</h2>
  <p>Selection 558 was present before scoring. The checker saw 132 green hits in 399 adjacent-pair checks. That is z <strong>{maximum["all_pairs"]["z_score"]:.4f}</strong>, above the strict cutoff. For this declared negative cohort, that is an empirical false alarm.</p>
  <div class="grid2">
    <article class="panel coral"><h3>Count every adjacent pair</h3><div class="metric">{maximum["all_pairs"]["num_green_tokens"]} / {maximum["all_pairs"]["num_tokens_scored"]}</div><p>z = {maximum["all_pairs"]["z_score"]:.4f}. Decision: above the strict cutoff.</p><div class="score-rule"><span>score</span><b>{maximum["all_pairs"]["z_score"]:.4f}</b><div class="bar"><div class="fill" style="width:{min(100, maximum["all_pairs"]["z_score"] / 4 * 100):.1f}%"></div><span class="cut" title="z = 3"></span></div></div></article>
    <article class="panel green"><h3>Count each value-pair once</h3><div class="metric">{maximum["distinct_pairs"]["num_green_tokens"]} / {maximum["distinct_pairs"]["num_tokens_scored"]}</div><p>z = {maximum["distinct_pairs"]["z_score"]:.4f}. Decision: below the strict cutoff.</p><div class="score-rule"><span>score</span><b>{maximum["distinct_pairs"]["z_score"]:.4f}</b><div class="bar"><div class="fill" style="width:{min(100, maximum["distinct_pairs"]["z_score"] / 4 * 100):.1f}%;background:var(--green)"></div><span class="cut" title="z = 3"></span></div></div></article>
  </div>
  <div class="try"><strong>Try this.</strong> Switch the counting rule. The text, token IDs, key, and green decisions stay fixed. Only repeated identical previous-token and current-token pairs stop adding new observations.</div>
  <div class="controls"><button id="allRule" class="active" type="button">Count every pair</button><button id="distinctRule" type="button">Count distinct value-pairs</button></div>
  <div class="feedback" id="ruleFeedback" aria-live="polite">Every pair counts: 132/399, z 3.7286. This row crosses the frozen cutoff.</div>
  <p><strong>What changed?</strong> Forty-one repeated observations disappeared, including 18 green hits. The result moved from 3.7286 to 2.9904. This diagnostic does not prove that one policy is universally correct. It shows that repetition policy is part of the detector profile, not a formatting detail.</p>
  <p class="note">The row came from dataset index {maximum["dataset_row_index"]}, timestamp {maximum_manifest["timestamp"]}. A cutoff crossing establishes only "consistent with this configured watermark and key." It does not prove AI origin, authorship, or model source.</p>
</section>
<section id="limits">
  <div class="eyebrow">Read the count before the rate</div><h2>We observed 4 out of 1,000. Do not stretch it into a guarantee.</h2>
  <div class="sample-grid" id="sampleGrid" role="img" aria-label="One thousand cells. Four coral cells represent natural-web rows above the all-pair cutoff."></div>
  <div class="grid2"><article class="panel"><div class="metric">4 / 1,000</div><p>Observed all-pair cutoff crossings in this frozen sample. The empirical fraction is 0.004.</p></article><article class="panel"><div class="metric">1 / 1,000</div><p>Observed distinct-pair cutoff crossings. The empirical fraction is 0.001.</p></article></div>
  <p>One thousand rows move in count steps of one. The smallest non-zero observed fraction is 0.001. A one-in-100,000 claim would need evidence at a much larger scale and on a declared target population. Zero crossings would not have solved that problem either.</p>
  <h3>How the frozen cohort was made</h3>
  <div class="funnel">
    <div class="funnel-row"><span>Rows scanned</span><div class="funnel-track"><div class="funnel-fill" style="width:100%"></div></div><b>2,479</b></div>
    <div class="funnel-row"><span>Too short</span><div class="funnel-track"><div class="funnel-fill" style="width:{1451 / 2479 * 100:.2f}%;background:var(--coral)"></div></div><b>1,451</b></div>
    <div class="funnel-row"><span>Obvious list</span><div class="funnel-track"><div class="funnel-fill" style="width:{max(0.5, 4 / 2479 * 100):.2f}%;background:var(--coral)"></div></div><b>4</b></div>
    <div class="funnel-row"><span>Calibration</span><div class="funnel-track"><div class="funnel-fill" style="width:{1000 / 2479 * 100:.2f}%;background:var(--cyan)"></div></div><b>1,000</b></div>
    <div class="funnel-row"><span>Frozen for Stage 7</span><div class="funnel-track"><div class="funnel-fill" style="width:{max(1, 24 / 2479 * 100):.2f}%;background:var(--violet)"></div></div><b>24</b></div>
  </div>
  <p>The first 1,000 passing rows filled calibration. The next 24 passing rows were frozen for paired generation. Score did not influence either split.</p>
  <div class="panel" style="margin-top:28px"><h3>What Stage 6 establishes</h3><p>The recorded score distribution belongs to one pinned C4 sample, one Gemma tokenizer revision, one public key, one CUDA pseudorandom rule, and one selection contract.</p><h3 style="margin-top:22px">What remains open</h3><p>Stage 6 does not establish verified human authorship, a production false-alarm rate, a universal cutoff, text quality, edit robustness, or separation from paired model outputs. Stage 7 generation has not started.</p></div>
  <details><summary>Reproducibility record</summary><table><tbody><tr><th scope="row">Source commit</th><td class="mono">{artifact["source_commit"]}</td></tr><tr><th scope="row">Config SHA-256</th><td class="mono">{artifact["config_sha256"]}</td></tr><tr><th scope="row">Dataset revision</th><td class="mono">{artifact["config"]["dataset_revision"]}</td></tr><tr><th scope="row">Dataset file SHA-256</th><td class="mono">{artifact["dataset_file_sha256"]}</td></tr><tr><th scope="row">Tokenizer revision</th><td class="mono">{artifact["config"]["tokenizer_revision"]}</td></tr><tr><th scope="row">GPU</th><td>{artifact["gpu_name"]}</td></tr></tbody></table></details>
  <details><summary>Formal score and exact tail</summary><p><span class="mono">z = (G - 0.25T) / sqrt(T x 0.25 x 0.75)</span>. The selected artifact also records the exact binomial upper tail for every row. Both calculations assume the configured no-watermark model. The observed cohort tests how those idealized values behave on one real text source.</p></details>
  <details><summary>Operational record</summary><p>The first approved Modal function completed but its JSON was lost after the local write directory was missing. The user approved one exact replacement invocation. The replacement used the same clean source commit and config, loaded no model weights, made zero generation calls, and produced the selected evidence.</p></details>
  <div class="static panel"><h3>Scripts-off summary</h3><p>The first selected row scored 81/399, z -2.1678. Across 1,000 recorded natural-web continuations, 4 crossed strict z greater than 3 under all-pair counting. The maximum was 132/399, z 3.7286. Counting each repeated value-pair once changed that row to 114/358, z 2.9904.</p></div>
</section>
<section>
  <div class="eyebrow">Next Lego block</div><h2>The negative reference is frozen before paired generation.</h2>
  <p>Stage 7 can now give the same 50-token prompts to control and watermarked Gemma generation. The prompts cannot be replaced after seeing the baseline. That is the point of freezing the manifest first.</p>
</section>
</main>
<footer>Measured claims come from <span class="mono">artifacts/lab-06/calibration.json</span>. The page has no external scripts, fonts, model calls, storage, or network dependency.</footer>
<script>
const DATA={compact_json(payload)};
const $=id=>document.getElementById(id);
const theme=$('theme');theme.addEventListener('click',()=>{{const light=document.documentElement.dataset.theme==='light';document.documentElement.dataset.theme=light?'dark':'light';theme.textContent=light?'Use light page':'Use dark page';theme.setAttribute('aria-pressed',String(!light));}});
const filterCopy=[
  'Length passes: this row has 988 Gemma tokens, above the fixed minimum of 500.',
  'Hash passes: this exact UTF-8 text hash had not appeared earlier.',
  'List check passes: the row does not meet the fixed obvious-list rule.',
  'Code check passes: the row does not meet the fixed code-dump rule.',
  'Letter check passes. The row is accepted before any keyed score is computed.'
];
let filterStep=0;function renderFilter(){{[...$('filterList').children].forEach((li,i)=>{{li.classList.toggle('done',i<filterStep);li.classList.toggle('current',i===filterStep&&filterStep<5);}});$('filterFeedback').textContent=filterStep?filterCopy[filterStep-1]:'No detector score is available yet. Selection begins with length.';$('filterPrev').disabled=filterStep===0;$('filterNext').disabled=filterStep===5;}}
$('filterNext').onclick=()=>{{filterStep=Math.min(5,filterStep+1);renderFilter();}};$('filterPrev').onclick=()=>{{filterStep=Math.max(0,filterStep-1);renderFilter();}};$('filterReset').onclick=()=>{{filterStep=0;renderFilter();}};renderFilter();
const tokenBox=$('tokenBox');DATA.tokens.forEach((t,i)=>{{const span=document.createElement('span');span.className='token '+(t.eligible?(t.is_green?'green-token':'red-token'):'unscored')+' future';span.textContent=t.piece||' ';span.title=`position ${{i}}, ID ${{t.token_id}}, ${{t.eligible?(t.is_green?'green':'red'):'unscored'}}`;span.dataset.i=i;tokenBox.append(span);}});
let tokenIndex=0,timer=null;const motion=matchMedia('(prefers-reduced-motion: reduce)').matches;function tokenStats(index){{const shown=DATA.tokens.slice(0,index+1),eligible=shown.filter(t=>t.eligible),g=eligible.filter(t=>t.is_green).length;return {{t:eligible.length,g,z:eligible.length?(g-.25*eligible.length)/Math.sqrt(eligible.length*.25*.75):null}};}}
function renderTokens(){{const spans=[...tokenBox.children];spans.forEach((s,i)=>{{s.classList.toggle('future',i>tokenIndex);s.classList.toggle('cursor',i===tokenIndex);}});const n=tokenStats(tokenIndex);$('revealed').textContent=`${{tokenIndex+1}} / 400`;$('runningT').textContent=n.t;$('runningG').textContent=n.g;$('runningZ').textContent=n.z===null?'n/a':n.z.toFixed(4);$('tokenFeedback').textContent=tokenIndex===0?'The first piece supplies context, so it is not scored.':`At position ${{tokenIndex}}, ${{n.g}} of ${{n.t}} eligible tokens are green. The running z is ${{n.z.toFixed(4)}}.`;spans[tokenIndex].scrollIntoView({{block:'nearest',inline:'nearest'}});if(tokenIndex>=399)pauseTokens();}}
function pauseTokens(){{if(timer)clearInterval(timer);timer=null;}}
function playTokens(){{if(motion){{$('tokenFeedback').textContent='Reduced motion is active. Use Previous token and Next token for manual inspection.';return;}}pauseTokens();timer=setInterval(()=>{{tokenIndex=Math.min(399,tokenIndex+1);renderTokens();}},55);}}
$('tokenPlay').onclick=playTokens;$('tokenPause').onclick=pauseTokens;$('tokenNext').onclick=()=>{{pauseTokens();tokenIndex=Math.min(399,tokenIndex+1);renderTokens();}};$('tokenPrev').onclick=()=>{{pauseTokens();tokenIndex=Math.max(0,tokenIndex-1);renderTokens();}};$('tokenReplay').onclick=()=>{{pauseTokens();tokenIndex=0;renderTokens();playTokens();}};renderTokens();
const NS='http:'+'//www.w3.org/2000/svg';function svg(tag,attrs={{}}){{const el=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));return el;}}
function renderChart(count){{const root=$('scoreSvg');root.replaceChildren();const W=1000,H=380,pad={{l:48,r:22,t:22,b:42}},min=-4,max=4.5;root.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);const x=i=>pad.l+i/(Math.max(count-1,1))*(W-pad.l-pad.r),y=z=>pad.t+(max-z)/(max-min)*(H-pad.t-pad.b);[-3,0,3].forEach(v=>{{root.append(svg('line',{{x1:pad.l,x2:W-pad.r,y1:y(v),y2:y(v),stroke:v===3?'var(--yellow)':'var(--border)','stroke-width':v===3?2:1,'stroke-dasharray':v===3?'7 5':'none'}}));const text=svg('text',{{x:8,y:y(v)+4,fill:'var(--muted)','font-size':13}});text.textContent=`z ${{v}}`;root.append(text);}});for(let i=0;i<count;i++){{const z=DATA.allZ[i],cross=z>3;const c=svg('circle',{{cx:x(i),cy:y(z),r:cross?4.2:count<20?5:2.2,fill:cross?'var(--coral)':'var(--cyan)',opacity:cross?1:.66}});const title=svg('title');title.textContent=`manifest ${{i}}, z ${{z.toFixed(4)}}`;c.append(title);root.append(c);}}const axis=svg('text',{{x:W/2,y:H-8,fill:'var(--muted)','font-size':13,'text-anchor':'middle'}});axis.textContent=`first ${{count}} manifest rows`;root.append(axis);const values=DATA.allZ.slice(0,count),crossings=values.filter(v=>v>3).length,peak=Math.max(...values);$('cohortFeedback').textContent=`${{count}} recorded rows are visible. ${{crossings}} crossed strict z greater than 3. The visible maximum is ${{peak.toFixed(4)}}.`;document.querySelectorAll('[data-count]').forEach(b=>b.classList.toggle('active',Number(b.dataset.count)===count));}}
document.querySelectorAll('[data-count]').forEach(b=>b.onclick=()=>renderChart(Number(b.dataset.count)));renderChart(1000);
$('allRule').onclick=()=>{{$('allRule').classList.add('active');$('distinctRule').classList.remove('active');$('ruleFeedback').textContent='Every pair counts: 132/399, z 3.7286. This row crosses the frozen cutoff.';}};$('distinctRule').onclick=()=>{{$('distinctRule').classList.add('active');$('allRule').classList.remove('active');$('ruleFeedback').textContent='Each value-pair counts once: 114/358, z 2.9904. The same row now stays below the frozen cutoff.';}};
const sampleGrid=$('sampleGrid');for(let i=0;i<1000;i++){{const cell=document.createElement('span');if(DATA.allZ[i]>3)cell.className='hit';cell.title=`row ${{i}}, z ${{DATA.allZ[i].toFixed(4)}}`;sampleGrid.append(cell);}}
</script>
</body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
