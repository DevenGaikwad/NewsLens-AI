# Controlled model benchmarking methodology

## Purpose

This study compares three deployment-compatible classical text classifiers for NewsLens AI. It measures patterns associated with the ISOT labels; it does not verify factual truth.

## Dataset integrity and partitions

- Dataset: ISOT Fake News Dataset, downloaded from the documented University of Victoria source for private evaluation only.
- Verified source checksums: `True.csv` `ba0844414a65dc6ae7402b8eee5306da24b6b56488d6767135af466c7dcb2775` and `Fake.csv` `bebf8bcfe95678bf2c732bf413a2ce5f621af0102c82bf08083b2e5d3c693d0c`.
- Clean balanced sample: 24,000 rows, fixed random seed 42.
- Training: 19,200 rows.
- Validation: 2,399 rows, internally divided into 1,199 calibration rows and 1,200 threshold-policy rows.
- Untouched final test: 2,399 rows.
- 2 holdout rows were quarantined because the deterministic near-duplicate screen found a high-similarity counterpart in training.

Exact duplicates and conflicting-label duplicates are removed before sampling. Near-duplicate candidates are generated from eight minimum word-five-gram signatures and verified with Jaccard similarity >= 0.90. Candidate generation is an approximate deterministic screen, not a claim of exhaustive semantic-duplicate detection. Near-duplicate groups are kept inside one validation/test partition. The final leakage audit found 0 cross-partition pairs after controls.

## Candidates and fitting

The candidates are Logistic Regression (`C=2.0`), Linear SVC (`C=1.0`) and Multinomial Naive Bayes (`alpha=0.1`). All use the same word-level TF-IDF configuration and the same training rows. Each vectorizer is fitted only inside its training pipeline. There is no exhaustive search and no threshold tuning on test data.

The packaged Logistic Regression is first verified against its established 4,800-row holdout evidence. Its artifact remains unchanged. Linear SVC and Multinomial Naive Bayes are fitted for this controlled private evaluation only; their model files are not retained in the release.

## Calibration and abstention

Platt scaling fits a one-dimensional Logistic Regression mapping from each candidate's decision score to the misleading-label probability using only the calibration subset. Calibration is evaluated on the untouched test set with Brier score, a ten-bin expected calibration error (ECE), and reliability points.

The validation-policy subset is used for two predeclared policy decisions after the candidate pipelines and Platt mappings are fixed: the 0.01 macro-F1 model-retention check and the production review threshold. The deterministic threshold rule chooses the lowest calibrated-confidence threshold with at least 80% automatic-decision coverage and a 95% Wilson lower bound of at least 99% for accuracy relative to dataset labels. The selected threshold is `0.59`. Inputs below the threshold, with inadequate quality, or outside supported language/domain heuristics return **Editorial review required**. The final test partition is not used for either decision.

## Selection

The selected production family is **Logistic Regression**. Linear SVC's validation-policy macro-F1 advantage is below the predeclared 0.01 tolerance; Logistic Regression therefore remains selected for direct coefficient explanations, compact deployment and an unchanged verified production artefact. The untouched final test is used once for reporting after this decision. The calibrated parameters are a private model artefact and are excluded from public archives.

## Responsible interpretation

Accuracy, F1, discrimination and calibration are dataset-relative measurements. Calibration measures score reliability against the benchmark labels, not factual verification. Explainability reports learned feature influence, not evidence. Human review remains required for consequential decisions.
