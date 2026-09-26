# NewsLens AI Interface Design Specification

## Visual system

The existing interface uses warm paper surfaces, serif-led editorial hierarchy, compact top navigation, measured evidence panels, and restrained brown, green, amber, and red status colors. Phase 5S preserves that original design; changes are limited to technically necessary labels, metrics, and synthetic-scope content.

## Page responsibilities

- **News Desk:** purpose, measured synthetic evidence, workflow, and scope warning.
- **Analyse Article:** paste/URL/TXT/PDF input, deterministic summary, synthetic consistency result, calibration, explanations, diagnostics, and exports.
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
- No external pretrained summarizer, paid API, raw training-data surface, or Vercel dependency is present.
