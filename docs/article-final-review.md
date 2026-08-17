# Final interactive article review

## Narrative review

The article now follows one causal question rather than eight stage reports:

1. Why Anthropic's announcement made plain-text marking worth understanding.
2. Why passive AI detection, fingerprinting, watermarking, and C2PA are different problems.
3. How a small statistical bias accumulates.
4. How a key turns token choices into green and red observations.
5. Where that operation sits inside a real model.
6. Why processor order, tokenizer behavior, repetition policy, and key handling belong to the profile.
7. Why short Gemma outputs were weak.
8. Why the checker was calibrated on outside text before the paired run.
9. Why one marked output needs three controls.
10. What all 24 pairs showed and where they overlapped.
11. Why edits rebuild the keyed history.
12. What a stronger bias moved in the measured proxies.
13. How the KGW-style lab differs from SynthID-Text and Anthropic's Claude variant.
14. Why provenance evidence cannot decide authorship or misconduct.

No reader-facing heading uses `Stage`, `Part`, or chapter numbering. Stage names remain only in source notes, artifact names, or interaction captions where they identify evidence provenance.

## Language review

The manuscript passed a manual Humanizer and Unslop review in a plain journalistic register.

Checks applied:

- no em dash, en dash, curly quote, or decorative arrow characters;
- no `not just X, but Y` reversal;
- no `In conclusion`, `In summary`, `Let's break this down`, or `Think of it as` framing;
- no unresolved `TODO` or verification marker;
- no claim that KGW reproduces Claude;
- no use of C4 as verified human writing;
- no use of NLL, repetition, cosine, or assistant review as human quality proof;
- no presentation of a 400-token cap as an achieved paired prefix;
- no positive label broader than the configured watermark and key.

The prose uses first person only where the research sequence or a decision matters. It keeps formulas and exact values concrete and leaves failed or awkward results in place.

## Evidence review

`tests/unit/test_final_article.py` checks:

- exact source commit for every Stage 1 through Stage 8 artifact;
- every Stage 1 row;
- the complete Stage 2 vocabulary and all four trace steps;
- both Stage 3 candidate tables;
- complete Stage 4 order probe and repetition fixture;
- all Stage 5 smoke records;
- all 1,000 Stage 6 z scores and the complete summary;
- the complete Stage 7 prefix summary, including every row difference;
- every Stage 8 attack row and bias row;
- narrative order, claim boundaries, standalone behavior, fallback, and prohibited prose markers.

`just verify-final-article` rebuilds the HTML and runs those checks without a model, dataset, GPU, network request, or cloud call.

## Browser review

Chrome headless QA covered:

- desktop dark, 1440 by 1000;
- desktop light, 1200 by 900;
- mobile dark, 390 by 844;
- 17 figure elements covering the rebuilt opening and later evidence sequence;
- 67 rendered controls in the current article, exercised in desktop dark, desktop light, and mobile
  dark traversals plus isolated state checks for disabled controls;
- 20 source notes;
- every selected control state;
- keyboard focus and reduced motion;
- scripts-off fallback;
- JavaScript syntax;
- console and page errors;
- horizontal overflow.

Measured browser results:

- zero horizontal overflow in every tested view;
- zero console or page errors;
- 17 figure elements and 67 controls rendered in each current scripted view;
- scripts-off mode hid the figures, exposed the fallback, and retained the complete article, tables, source notes, and conclusions.

Seven context-free mid-article screenshots were inspected:

- Stage 1 length curve;
- Stage 2 toy vocabulary;
- Stage 4 processor order;
- Stage 6 natural-web distribution on mobile;
- Stage 7 paired cohort;
- Stage 8 edits on mobile;
- final method-family comparison.

One visual defect appeared in the initial Stage 4 screenshot: the large probability readout clipped. The builder now uses a smaller responsive readout with forced wrapping. The sticky top bar also covered mobile figure captions, so the bar is now non-sticky.

## Remaining boundary

No article or HTML file has been published. The Claude artifact URL supplied during research currently renders `Page not found`, so it is recorded but not cited. Anthropic, Declaude, Theo, and Sean Goedecke claims remain attributed to their sources. Project measurements still come only from committed artifacts.
