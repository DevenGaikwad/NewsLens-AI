# Model Card — NewsLens Synthetic TF-IDF v1.0.0

## Summary

NewsLens AI packages a Logistic Regression classifier over word/bigram TF-IDF features and transparent, label-independent fact-comparison tokens. All training articles, entities, events, names, places, organizations, and reported facts are synthetic.

- Artifact ID: `newslens-synthetic-tfidf-v1.0.0`
- Positive class: `synthetic_ledger_contradicting`
- Model SHA-256: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`
- Calibration: Platt scaling
- Calibration SHA-256: `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- Editorial-review threshold: 0.50
- Random seed: 42

## Intended use

The model demonstrates a reproducible classification and calibration workflow. It compares the values in two visible structured lines—`Reference note` and `Article account`—within an original fictional article. It may support classroom demonstration, portfolio review, software testing, and research discussion about leakage, calibration, abstention, and explainability.

It is not intended to determine whether ordinary news is true, rate publishers, infer author intent, guide high-stakes decisions, or replace professional fact-checking.

## Training data

Only `newslens-synthetic-articles-v1.0.0` was used. The archive contains 24,000 articles / 12,000 paired events. Event pairs and content hashes never cross partitions.

| Partition | Rows | Purpose |
|---|---:|---|
| Training | 18,000 | Fit candidates |
| Model validation | 2,400 | Select candidate |
| Calibration | 1,200 | Fit Platt mapping |
| Abstention policy | 1,200 | Select threshold |
| Final test | 1,200 | Locked evaluation |

No ISOT content, private ISOT-derived model, private calibration, or external copyrighted training dataset was accessed or used.

## Selection and evaluation

Logistic Regression, Linear SVC, and Multinomial Naive Bayes were evaluated on model validation. Logistic Regression was retained within a declared 0.005 macro-F1 tolerance because it provides a compact CPU artifact, linear explanations, and a stable calibration score.

On the locked final test: accuracy, balanced accuracy, precision, recall, macro F1, ROC AUC, and average precision were all 1.0; the confusion matrix was `[[600, 0], [0, 600]]`. Calibrated Brier score was `1.4968608529442928e-06`; 10-bin ECE was `0.0007422494250466733`; automatic coverage at threshold 0.50 was 100%.

## Shortcut and causal controls

- Surface text with both fact blocks removed: balanced accuracy 0.500.
- Locked model with both fact blocks removed: balanced accuracy 0.498.
- Metadata-only baseline: balanced accuracy 0.521.
- Swapping only the Article account block across each paired event: 100% prediction flips and 100% expected-label accuracy.

These controls support the conclusion that the model uses the authored comparison signal in this benchmark. They do not prove real-world generalisation.

## Calibration and abstention

The Platt calibration file contains the exact model SHA-256. Runtime loading fails closed on a mismatch. Inputs without both supported fact blocks are routed to editorial review even if the raw score is confident.

## Limitations and ethics

The task is intentionally regular and synthetic. Perfect results are expected to be easier than open-world factual reasoning. Confidence is conditional on the benchmark, not a truth probability. Users must independently verify important claims and should not use the output for legal, medical, financial, civic, or reputational decisions.
