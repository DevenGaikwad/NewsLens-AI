# Architecture

## Runtime

1. Streamlit accepts pasted text, a public URL, or a TXT/text-based PDF.
2. Input controls validate type, size, network destination, and minimum length.
3. A deterministic extractive summarizer ranks original sentences locally.
4. The public model parses visible fact blocks, appends auditable match/mismatch tokens, applies TF-IDF, and scores Logistic Regression.
5. The bound Platt calibration converts the score; missing blocks or diagnostic concerns trigger review.
6. For supported comparisons, the interface exposes the summary, bounded outcome, calibrated `Fields agree` and `Fields conflict` class probabilities, reference-comparison confidence, local contributions, disclaimer, and exports. For missing blocks it presents an outside-scope abstention and withholds directional scores and explanations.
7. SQLite stores only a session-isolated structured result; full article text is not persisted.

Summarisation and classification are independent: the classifier never consumes the generated summary. Runtime never imports training modules or retrains the model.

The display layer preserves the existing `reliable_probability` and `misleading_probability` JSON/database fields. For supported inputs it presents them as **Fields agree - calibrated probability** and **Fields conflict - calibrated probability** so users can understand the comparison without mistaking either score for factual truth. Reference-comparison confidence remains the selected-class confidence. When the required pair is absent, the UI/PDF/CSV withhold those directional values; JSON retains them only for compatibility and adds `supported_scope: false` plus `score_reporting_status: withheld_outside_supported_scope`.

## Offline evidence pipeline

`training/train_synthetic_model.py` verifies the authoritative ZIP, consumes its authored event-grouped splits, compares three bounded candidates, fits calibration, selects the abstention policy, evaluates the locked test once, performs shortcut and counterfactual controls, and writes hash-bound artifacts and reports.

## Security boundaries

- URL extraction blocks private/local network targets and bounds redirects and response sizes.
- Uploads are size- and type-restricted.
- Calibration fails closed on model-hash mismatch.
- Public release scanning rejects secrets, local paths, private artifact filenames, broken links, and artifact identity drift.
- Streamlit secrets are not required.
