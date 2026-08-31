# NewsLens AI editorial AI case study

## Scenario

Consider a generic high-volume regional newsroom receiving a continuous mix of staff copy, agency reports, community submissions, public statements, and rapidly developing updates. Editors must decide what to read first, which claims need additional evidence, and where limited review time carries the greatest value. NewsLens AI is designed as an academic decision-support prototype for that prioritisation problem. It is not a newsroom endorsement, partnership, or production deployment.

The system combines article ingestion, summarisation, a calibrated linguistic credibility-risk signal, local feature influence, a human review record, session-local analytics, and lightweight drift diagnostics. The model detects patterns associated with its training labels. It does not retrieve independent evidence or establish factual truth.

## Proposed editorial workflow

1. **Ingest safely.** An editor pastes text, submits a public HTTP(S) URL, or uploads a TXT or text-based PDF. The application validates size and type, blocks private-network URL targets, extracts readable text, and rejects inputs shorter than the supported minimum.
2. **Create a reading view.** The extractive summariser ranks original sentences around a TF-IDF centroid. Optional DistilBART summarisation remains separate from classification, so generated wording never becomes classifier input.
3. **Estimate linguistic risk.** The saved TF-IDF and Logistic Regression pipeline processes the original cleaned article. Runtime never retrains the model.
4. **Calibrate confidence.** Private Platt-scaling parameters map the classifier decision score to a dataset-relative probability. The validation-selected editorial-review threshold is 0.59.
5. **Apply responsible abstention.** The system reports one of three outcomes: `Lower misleading-content risk indicated`, `Higher misleading-content risk indicated`, or `Editorial review required`. It abstains when calibrated confidence is below the threshold or when input quality, language, length, or vocabulary-coverage checks fall outside supported conditions.
6. **Inspect model influence.** Signed TF-IDF-by-coefficient contributions show which observed terms moved the linear score. These terms are learned correlations, not journalistic evidence.
7. **Complete human review.** The editor records one supported review status, notes, public supporting-source URLs, and a final assessment. The model result remains visible but does not overwrite the human conclusion.
8. **Monitor aggregates.** Session-local analytics summarise volume, outcome distribution, confidence bands, review rate, inconclusive rate, latency, activity, model comparison, and drift indicators without exporting full articles, notes, URLs, or identifiers.

## Preliminary article-risk screening

The system can help order an incoming queue for attention. A higher-risk signal or required-review outcome can move an item into a closer-reading queue; a lower-risk signal can still require verification when the subject is consequential. The label should never be used as an automatic publish, reject, takedown, or author-trust decision.

The calibrated threshold is deliberately a review policy, not a truth boundary. It was selected using a 1,200-row validation-policy subset. The rule chooses the lowest confidence threshold with at least 80% automatic-decision coverage and a 95% Wilson lower accuracy bound of at least 99% relative to validation dataset labels. On the untouched 2,399-row final test, the confidence-only review rate was 0.167%; scope and quality checks can require additional reviews in real use.

## Explainable review assistance

For a linear text model, local influence can be stated directly: a term's TF-IDF value is multiplied by its learned Logistic Regression coefficient. Positive values move the score toward the misleading-labelled class and negative values toward the reliable-labelled class. An editor can use the display to ask whether the model is responding to meaningful article structure or to a fragile outlet, topic, date, or vocabulary shortcut.

Explainability does not show whether a claim is supported by evidence. It explains model influence only. A term such as a place, institution, or reporting phrase may correlate with the training labels for reasons that do not generalise to a regional newsroom.

## Human oversight and accountability

Each stored analysis includes an identifier, timestamp, model outcome, calibrated confidence, model identifier, review requirement, review status, reviewer notes, supporting-source URLs, and final editorial assessment. Supported statuses are:

- Pending review
- Evidence supports the claim
- Evidence contradicts the claim
- Inconclusive
- Out of supported scope

This separation makes disagreement visible. A reviewer can conclude that evidence contradicts a claim even when the model indicates lower linguistic risk, or mark an item out of scope even when confidence is high. Human review reduces some risks but does not guarantee correctness.

## Newsroom analytics and quality monitoring

The analytics view uses only the current visitor's session-scoped SQLite records. It reports analysed-article count, predicted-risk distribution, confidence bands, editorial-review rate, inconclusive rate, average inference latency, controlled model comparison, and dated activity where observations exist.

Lightweight drift readiness checks article length, unigram vocabulary coverage, out-of-vocabulary rate, predicted-class distribution, calibrated-confidence distribution, invalid-input rate, language mismatch, and a domain-support heuristic. Before 20 observations exist, the application displays: `Insufficient observations for a reliable drift assessment.` A later warning indicates distributional change, not automatic model failure, and never triggers retraining.

## Privacy and persistence boundary

Public-safe mode creates an opaque, randomly scoped temporary SQLite file for each Streamlit session. One visitor cannot list another visitor's archive through the application. Uploaded bytes and complete original article text are not stored. Review notes and source URLs share the same visitor boundary.

This is an academic prototype, not an authenticated newsroom records system. Cloud restarts may delete session files, SQLite is not encrypted by the application, and durable multi-user history is not claimed. A production newsroom would require deliberate identity, authorisation, retention, encryption, audit-log, and managed-database design.

## Evidence and limitations

The controlled benchmark compares Logistic Regression, Linear SVC, and Multinomial Naive Bayes on identical partitions. Logistic Regression remains selected: its final-test macro F1 is 0.992080, within 0.002501 of Linear SVC and inside the predefined 0.01 tolerance, while preserving the verified model artefact and direct coefficient explanations. Platt scaling improves Brier score from 0.010464 to 0.006292 and ten-bin expected calibration error from 0.044799 to 0.005295 on the final test.

These high same-dataset scores may reflect ISOT outlet, topic, period, and writing-style artefacts. The dataset is English-heavy and political. Random-split performance does not establish cross-publisher, cross-event, regional, or future reliability. Calibration measures agreement with benchmark labels, not factual verification.

## Regional and multilingual roadmap

Marathi and multilingual processing remain future research. A responsible extension would require a licensed, documented regional-news dataset; label-policy review with newsroom experts; language-specific tokenisation and quality checks; event-, publisher-, and time-separated evaluation; calibrated confidence for each supported language; and human evaluation of explanations. Translating the current English input or reusing its threshold would not establish Marathi capability.

## Deployment status

The source is prepared for a zero-cost academic architecture: a public GitHub repository, Streamlit Community Cloud for the Python application, and Vercel Hobby for the presentation shell. Public functional deployment remains blocked because redistribution permission for the packaged model and dataset-derived calibration parameters is unresolved. No repository or hosting deployment is claimed by this case study.

> This result is a machine-learning risk signal. It is not independent confirmation that an article is factually true or false.
