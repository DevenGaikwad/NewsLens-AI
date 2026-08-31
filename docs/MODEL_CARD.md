# Model Card — NewsLens AI Credibility-Risk Classifier

## Model details

- **Artifact ID:** `isot-tfidf-lr-v1.0.0`
- **Type:** scikit-learn Pipeline; TF-IDF word 1–2 grams + Logistic Regression
- **Positive class:** potentially misleading (`1`)
- **Language/domain:** English political/news-style articles
- **Training dataset:** ISOT Fake News Dataset
- **Working sample:** 24,000 balanced articles; 19,200 train, 2,399 validation and 2,399 final test after quarantining two contaminated holdout rows
- **Random seed:** 42
- **File:** `models/fake_news_pipeline.joblib`
- **Confidence method:** private Platt-scaling parameters fitted on 1,199 validation-calibration rows
- **Editorial-review threshold:** 0.59, selected on a separate 1,200-row validation-policy subset
- **Core service dependency:** local inference; no paid API is required. Hosting, network, compute and third-party terms may still carry costs.

## Intended use

The model estimates whether an article's wording resembles reliable- or
misleading-labelled ISOT examples. It is suitable for teaching classical NLP,
demonstrating reproducible pipeline design, comparing baselines, displaying calibrated
dataset-relative probabilities, applying responsible abstention, and studying feature-level explanations.

It is **not** suitable for autonomous moderation, legal/medical/electoral
decisions, author-intent attribution, or definitive fact-checking. It does not
retrieve evidence or validate individual claims.

## Training and selection

Exact duplicate texts were removed before splitting. Empty/short rows were removed;
titles and bodies were combined; source/subject fields were excluded; Reuters and
byline markers were neutralised. The established stratified 80/20 split was reconstructed
with seed 42. A deterministic approximate five-gram screen found two high-similarity
train/holdout pairs; the contaminated holdout members were quarantined before the
validation/final-test split. Verified near-duplicate groups do not cross final partitions.
Every comparison candidate uses the same training rows and training-only TF-IDF fit.

| Model | Test macro-F1 | Selection note |
|---|---:|---|
| Linear SVC | 0.994581 | Best score; 0.002501 above selected model and within the 0.01 tolerance |
| Logistic Regression | 0.992080 | **Selected:** verified artefact, calibrated confidence and direct XAI |
| Multinomial Naive Bayes | 0.960815 | Classical probabilistic baseline |

## Actual champion evaluation

| Metric | Value |
|---|---:|
| Accuracy | 0.992080 |
| Precision (misleading) | 0.996633 |
| Recall (misleading) | 0.987490 |
| F1 (misleading) | 0.992040 |
| Macro F1 | 0.992080 |
| ROC-AUC | 0.999481 |
| PR-AUC | 0.999423 |
| Calibrated Brier score | 0.006292 |
| Calibrated expected calibration error | 0.005295 |
| Mean calibrated inference | 0.502761 ms/article |
| Final test rows | 2,399 |

Metrics come from the saved evaluation artifacts and are not estimates. Accuracy
alone was not used because it can hide minority-class failure under imbalance.

## Explainability and confidence

For terms present in a single article, the application displays signed
`TF-IDF value × Logistic Regression coefficient` contributions. Positive values
support the misleading class and negative values support the reliable class.
These are correlations learned from ISOT—not causal evidence or proof.

The native Logistic Regression output is not presented as a reliable probability.
Platt scaling maps the decision score using held-out validation-calibration rows.
On the final test partition, Brier score improved from 0.010464 to 0.006292 and
ten-bin ECE improved from 0.044799 to 0.005295. A separate validation-policy subset
selected the 0.59 review threshold with a predeclared coverage/Wilson-bound rule.
Below that confidence, or when input quality/language/domain heuristics fall outside
support, the UI displays `Editorial review required`.

Calibration measures probability reliability against ISOT labels. It does not verify
the factual truth of an article or claim.

## Limitations and bias

ISOT's reliable items are largely Reuters while fake-labelled items come from
other outlets and subjects. Removing explicit markers reduces, but does not
eliminate, outlet/topic/style leakage. The collection is English-heavy, political,
and time-bound. Real performance may degrade on regional news, breaking events,
satire, parody, opinion, clickbait, multilingual text, adversarial paraphrases,
or future writing conventions. False positives and negatives can cause social or
reputational harm.

## Recommended monitoring and improvement

- Evaluate by unseen publisher, topic, time, and event—not only random rows.
- Evaluate separate evidence-retrieval and claim-level verification research paths.
- Measure subgroup/domain errors and human explanation usefulness.
- Retrain only with documented licences, label audits, and duplicate/event controls.
- Preserve the verification disclaimer and allow abstention.

## Reproducibility

Download the official ISOT CSV files for private evaluation, then run
`python training/benchmark_models.py --raw-dir <private-isot-directory>`. The script
verifies source/model checksums and writes aggregate benchmark/calibration evidence
without copying raw records into the project. Environment pins are in the two requirements files.

## License and distribution status

The artifact is present in the local release candidate for runtime verification.
Public redistribution rights and an explicit artifact license have not been
confirmed. Do not publish or deploy `fake_news_pipeline.joblib` or
`confidence_calibration.json` until the rights holders document permission. A license
selected for original project source code does not automatically apply to trained or
dataset-derived artefacts or their source datasets.

Official ISOT source reviewed 16 August 2026:
<https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/>.
No explicit trained-artifact redistribution licence was located on the reviewed
page. See `docs/MODEL_REDISTRIBUTION_DECISION.md` before any public push or deployment.

NewsLens AI was designed and developed by Deven Sachin Gaikwad.  
© 2026 Deven Sachin Gaikwad. All Rights Reserved.
