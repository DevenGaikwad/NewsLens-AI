# NewsLens AI Interface Design Specification

## Visual system

The existing interface uses warm paper surfaces, serif-led editorial hierarchy, compact top navigation, measured evidence panels, and restrained brown, green, amber, and red status colors. Phase 5S preserves that original design; changes are limited to technically necessary labels, metrics, and synthetic-scope content.

## Page responsibilities

- **News Desk:** purpose, measured synthetic evidence, workflow, and scope warning.
- **Analyse Article:** paste/URL/TXT/PDF input, deterministic summary, synthetic consistency result, calibrated `Fields agree` and `Fields conflict` probabilities for supported comparisons, reference-comparison confidence, explanations, diagnostics, and exports.
- **Model Accountability:** partition discipline, candidates, locked metrics, calibration, shortcut baselines, and counterfactual evidence.
- **Dataset Analysis:** synthetic provenance, archive identity, balance, diversity, leakage, and limitations.
- **Editorial Archive:** session-local search, review, privacy-safe analytics, drift indicators, and deletion.
- **Research & About:** architecture, public artifacts, privacy, literature, ownership, and explicit limits.

## Accessibility and responsive behavior

Meaning is expressed in text rather than color alone. Focus styles, readable contrast, reduced motion, flexible grids, same-tab navigation, and narrow-screen stacking are retained. Final desktop and mobile validation is performed against the live Streamlit deployment after PR B merges.

## Acceptance state

- The classifier loads the public synthetic artifact without runtime training.
- Calibration is bound to the exact model hash.
- Summarisation and classification remain independent.
- Both supported ledger outcomes and missing-block abstention are explicit.
- Calibrated class scores use plain-language labels, define confidence as selected-class confidence, and state that neither score determines real-world truth.
- Missing-ledger inputs show `Outside supported comparison scope`; their directional scores are withheld from the UI, PDF, and archive CSV while stable JSON fields remain compatibility-marked.
- PDF table labels and values wrap within calculated A4 column widths with no overlap or clipping.
- The News Desk headline is deliberately set as `News intelligence` / `With scope intact`, without punctuation, at responsive widths.
- The editorial illustration keeps all title text and navigation labels inside its source bounds, and the shared footer uses one concise author attribution plus a minimal copyright line.
- The Research & About page contains no distracting publication-status banner.
- No external pretrained summarizer, paid API, raw training-data surface, or Vercel dependency is present.
