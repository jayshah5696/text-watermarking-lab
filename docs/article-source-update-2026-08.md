# Source update for the final text-watermarking article

> Research snapshot: 2026-08-17. This note records sources that appeared after the project premise was frozen. It separates provider statements, papers, commentary, and unavailable material.

## The premise changed during the project

The Obsidian project began on 2026-08-11. Anthropic's support page then described a planned model-level text watermark but did not name its method. The project therefore chose a public KGW-style green-list analogue and treated SynthID-Text as a separate production comparison.

On 2026-08-14, Anthropic published [How Claude's text watermark works](https://www.anthropic.com/news/claude-text-watermark). The page now says Claude's watermark is "a version of the SynthID-Text approach". It still describes future Claude models, a forthcoming detection API, and a provider-specific key. It does not publish Anthropic's exact tournament configuration, key construction, masking rules, scorer, threshold, model coverage, or production evaluation data.

Safe narrative:

> We started with an unnamed Claude marking plan, built a transparent KGW-style analogue to understand the mechanism, and then learned that Anthropic had chosen a version of SynthID-Text. The lab explains the common generation-time idea and measures one public analogue. It does not reproduce Claude's implementation.

## Anthropic announcement

- URL: <https://www.anthropic.com/news/claude-text-watermark>
- Published: 2026-08-14, as shown on the page.
- Evidence type: current provider statement.
- Primary claims used:
  - future Claude models will generate watermarked text;
  - the watermark changes the randomness used to pick among acceptable next words;
  - Anthropic calls its method a version of SynthID-Text;
  - it attributes no practical quality impact to internal testing;
  - short and low-choice passages carry less evidence;
  - proofreading may leave too few Claude-chosen words to detect;
  - exact code often gives the watermark less room to act;
  - full rewriting can remove the mark;
  - a planned API will check for Claude's watermark;
  - the mark contains no user, organization, or chat identity.
- Required boundary: attribute quality, latency, coverage, and removal statements to Anthropic. "A version of SynthID-Text" does not expose the exact production profile.

The earlier support page remains useful for the rollout and C2PA distinction:
<https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content>

## EU policy sources

- Article 50 text: <https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50>
- Commission Code of Practice page: <https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content>

Use as policy motivation only. The lab is not a compliance test and offers no legal interpretation. Distinguish provider-side machine-readable marking from deployer disclosure duties and from the standard-editing or no-substantial-alteration qualification.

## Theo video

- Title: `Claude watermarks your code now`
- Channel: Theo - t3.gg
- URL: <https://www.youtube.com/watch?v=Be-NqsW-wuk>
- Published: 2026-08-14, from YouTube metadata.
- Duration: 31:58.
- Transcript: extracted with `summarize.sh` from YouTube caption tracks, 6,358 words.

Useful narrative beats:

- `00:00-01:12`: uncertainty about AI involvement and the EU/Anthropic announcement;
- `05:33-14:51`: media-watermark intuition, pixel redundancy, and compression;
- `14:51-20:12`: why plain text has much less room for hidden changes;
- `21:48-23:11`: token probabilities and a simplified SynthID explanation;
- `24:47-25:12`: claim that paraphrasing can remove a token watermark;
- `28:55-31:58`: skeptical policy conclusion.

Use Theo as a motivating skeptical voice. Verify technical and legal claims independently. The video sometimes treats different media marks, C2PA, Unicode tricks, and generative text watermarks too broadly. Its statement that all text watermarks are trivially removable is stronger than the evidence supports across watermark families and attacker models.

## Declaude explainer

- URL: <https://declaude.org/watermarking/>
- Title: `How AI text watermarking works`
- Author attribution on page: James Padolsey at NOPE.
- Evidence type: interactive commentary plus self-reported known-key experiments.

The page gives a strong visual explanation of low-stakes token choices, keyed coloring, accumulated evidence, and surviving wording windows under editing. It reports its own open-model MarkLLM KGW/EXP rewrite results. Those measurements are not peer-reviewed project evidence and do not test Claude's production watermark. Attribute them to Declaude and keep them separate from this repository's Stage 8 results.

## Sean Goedecke article and passive detectors

- Article: <https://www.seangoedecke.com/ai-detection/>
- Published: 2025-12-05, as shown on the page.
- Core contribution: passive AI-text detectors return uncertain evidence and can cause social harm when people treat a score as proof.

Primary papers linked from the article:

1. [Ghostbuster](https://arxiv.org/abs/2305.15047), submitted 2023-05-24, NAACL 2024. It derives features by passing text through weaker language models, searches feature combinations, and trains a classifier. It does not require token probabilities from the target generator.
2. [DNA-GPT](https://arxiv.org/abs/2305.17359), submitted 2023-05-27. It truncates candidate text, regenerates continuations, and compares original and regenerated suffixes through n-grams or probability divergence.
3. [EditLens](https://arxiv.org/abs/2510.03154), submitted 2025-10-03. It trains a regression model to estimate the amount of AI editing and reports binary and ternary classification results on its own data.

These methods belong in the taxonomy. The repository did not implement or compare them.

## SynthID-Text

- Paper: <https://www.nature.com/articles/s41586-024-08025-4>
- Citation: Dathathri et al., Nature 634, 818-823, 2024.
- Core facts used:
  - generative watermarking changes next-token sampling;
  - the scheme has a seed generator, sampling algorithm, and scoring function;
  - SynthID-Text uses Tournament sampling;
  - the paper studies non-distortionary and distortionary configurations;
  - repeated-context masking and context-dependent seeds matter;
  - longer and higher-entropy text carries more evidence;
  - the paper reports a live quality assessment over nearly 20 million Gemini responses;
  - detection does not require access to the underlying LLM.

Do not transfer its quality or detection curves to Claude or to the repository's KGW-style experiment.

## Unavailable supplied source

The supplied Claude artifact URL
<https://claude.ai/code/artifact/803916fd-3bc1-465f-8738-d4ece6fc5071>
currently renders `Page not found`; supporting requests return HTTP 403. It cannot be cited or included unless an exported HTML, Markdown, PDF, or screenshot is supplied.

## Project evidence remains unchanged

The new sources change the framing, not the recorded experiment. All repository measurements still come from the committed Stage 1 through Stage 8 artifacts. No new source authorizes a model rerun, seed search, result replacement, or claim that the lab reproduced Claude.
