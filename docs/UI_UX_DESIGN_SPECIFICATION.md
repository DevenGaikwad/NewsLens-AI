# NewsLens AI Interface Design Specification

## 1. Design system

NewsLens AI uses
warm paper surfaces, serif-led editorial hierarchy, compact top navigation,
publication-style evidence panels, measured charts, and restrained semantic
status colours. The application is intentionally presented as a local academic
news-intelligence and credibility-risk research product.

The summarizer, saved classifier, probability logic, explainability, SQLite
history, URL/file validation, charts, and exports retain stable backend
contracts. All screenshots and documentation describe this interface.

## 2. Implementation approach

- Use warm ivory, beige, taupe, muted brown, charcoal, and restrained semantic
  colours throughout the application and associated report visuals.
- Pair Georgia serif display headings with system sans-serif body text.
- Use one reusable desktop/mobile top navigation bar with a clear active state.
- Establish an editorial hierarchy: masthead, overline, headline, deck,
  section rule, evidence card, caption, and footnote.
- Centralise tokens and components in `ui/theme.py`, `ui/navigation.py`, and
  `ui/components.py`; retain `src/ui.py` as a compatibility re-export.
- Use original local SVG assets so the interface has no runtime dependency on
  third-party image URLs.
- Apply the same warm visual language to Plotly figures, PDF exports, report
  diagrams, and documentation screenshots.
- Preserve keyboard-visible focus, colour-independent labels, readable contrast,
  reduced-motion support, flexible grids, and narrow-screen stacking.

## 3. Page responsibilities

### News Desk

Introduces a publication-style masthead, clear project boundary, measured
headline values, a black two-layer information strip, workflow steps, capability
cards, and an always-visible verification warning.

### Analyse Article

Groups input method, article details, summary settings, and action controls into
a calm reading workflow. Results are organised as a textual credibility verdict,
probability/confidence strip, summary reading panel, article metadata, local
linear evidence, timing/model facts, disclaimer, and exports.

### Model Accountability

Reframes performance as an accountability report. Saved metrics, candidate-model
comparison, diagnostics, class-wise results, timing, ROUGE, evaluation protocol,
and limitations are presented as evidence rather than promotional scores.

### Dataset Analysis

Uses numbered research-appendix sections with short interpretation text beside
each saved figure. Data quality, class balance, article/title/sentence
distributions, duplicates, n-grams, correlations, and leakage controls remain
available without reproducing the raw dataset.

### Editorial Archive

Presents local history as a searchable archive with verdict/date filters,
sorting, compact article records, inspect/export actions, explicit deletion
confirmation, and a local-privacy note.

### Research & About

Explains purpose, architecture, methods, technology, responsible-use limits,
privacy, literature, and academic context in a readable long-form structure.

## 4. Implementation files

- `ui/__init__.py`
- `ui/theme.py`
- `ui/navigation.py`
- `ui/components.py`
- `assets/logo.svg`
- `assets/editorial_masthead.svg`
- `assets/ATTRIBUTIONS.md`
- `.streamlit/config.toml`
- `app.py`
- `pages/01_Analyse_Article.py`
- `pages/02_Model_Performance.py`
- `pages/03_Dataset_EDA.py`
- `pages/04_Analysis_History.py`
- `pages/05_Research_About.py`
- `src/ui.py`
- `src/visualizations.py`
- `src/report_exporter.py`
- documentation, diagram, screenshot, and test-generation scripts

## 5. Functional and visual acceptance checklist

- [x] Original cleaned article still feeds the summarizer and classifier
  independently.
- [x] Saved classifier loads without retraining in the UI.
- [x] Direct text, public URL, TXT, and text-PDF input paths remain available.
- [x] Summary length/method controls remain available.
- [x] Confidence, probabilities, local contributions, disclaimer, SQLite history,
  JSON, and PDF export remain available.
- [x] All six pages use the shared editorial shell and top navigation.
- [x] Warm palette and typography tokens are centralised.
- [x] The approved warm editorial palette is consistently applied.
- [x] Result meaning is expressed in text, not colour alone.
- [x] Keyboard focus and reduced-motion styles are defined.
- [x] Desktop and mobile screenshot scenarios are included.
- [x] Diagrams and report-layout figures were regenerated and visually checked
  for clipping, overflow, and cut arrows.
- [x] Fifteen genuine local Streamlit captures using the exact production CSS passed
  horizontal-bounds, heading-overflow, and asset-loading checks.
- [x] The capture manifest records filename, dimensions, byte size, and SHA-256
  hash for each interface image.
- [x] Python compilation and dependency-light backend integration
  passed for summarization, saved prediction, XAI, SQLite, JSON, and PDF.
- [x] Verification evidence clearly separates the 23-test historical baseline,
  six focused interface contracts, and the final 56-check packaged suite,
  including the 29 established checks.

The complete packaged suite was executed in the tested Python 3.12 environment:
`56 passed, 0 failed, 0 skipped`. Run `python -m pytest -q` after installing
`requirements.txt` to repeat the release check.
