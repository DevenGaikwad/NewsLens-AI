# Architecture

## Runtime

1. Streamlit accepts pasted text, a public URL, or a TXT/text-based PDF.
2. Input controls validate type, size, network destination, and minimum length.
3. A deterministic extractive summarizer ranks original sentences locally.
4. The public model parses visible fact blocks, appends auditable match/mismatch tokens, applies TF-IDF, and scores Logistic Regression.
5. The bound Platt calibration converts the score; missing blocks or diagnostic concerns trigger review.
6. The interface exposes the summary, bounded outcome, confidence, local contributions, disclaimer, and exports.
7. SQLite stores only a session-isolated structured result; full article text is not persisted.

Summarisation and classification are independent: the classifier never consumes the generated summary. Runtime never imports training modules or retrains the model.

## Offline evidence pipeline

`training/train_synthetic_model.py` verifies the authoritative ZIP, consumes its authored event-grouped splits, compares three bounded candidates, fits calibration, selects the abstention policy, evaluates the locked test once, performs shortcut and counterfactual controls, and writes hash-bound artifacts and reports.

## Security boundaries

- URL extraction blocks private/local network targets and bounds redirects and response sizes.
- Uploads are size- and type-restricted.
- Calibration fails closed on model-hash mismatch.
- Public release scanning rejects secrets, local paths, private artifact filenames, broken links, and artifact identity drift.
- Streamlit secrets are not required.
