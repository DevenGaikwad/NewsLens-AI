# NewsLens AI placement interview guide

## 30-second introduction

NewsLens AI is a Streamlit-based editorial decision-support project that ingests article text, public URLs, TXT, or PDF; produces an independent summary; and estimates linguistic misleading-content risk with a saved TF-IDF and Logistic Regression pipeline. I added held-out Platt calibration, a validation-selected abstention threshold, local coefficient explanations, a session-isolated human review workflow, privacy-safe newsroom analytics, and lightweight drift checks. The system never retrains at runtime and never claims to prove whether an article is true.

## Two-minute technical explanation

The application has two independent NLP branches. After safe extraction and conservative cleaning, the original article goes to an extractive TF-IDF-centroid summariser or optional DistilBART summariser. Separately, the original cleaned article goes to a word unigram/bigram TF-IDF vectoriser and Logistic Regression classifier. Keeping the classifier independent from the generated summary avoids losing or rewriting signals before classification.

For evaluation, I reconstructed a fixed seed-42 24,000-row balanced ISOT sample. Exact duplicates were removed before sampling. A deterministic approximate word-five-gram screen found 17 near-duplicate pairs and two train/holdout contaminations; I quarantined only the contaminated holdout rows and kept remaining near-duplicate groups within one partition. The final split has 19,200 training, 2,399 validation, and 2,399 untouched test rows. The validation set is divided into 1,199 calibration and 1,200 threshold-policy rows.

I compared Logistic Regression, Linear SVC, and Multinomial Naive Bayes using identical partitions and training-only vectoriser fitting. Linear SVC had the highest final-test macro F1 at 0.994581; Logistic Regression achieved 0.992080, only 0.002501 lower. It remains selected under the predefined 0.01 tolerance because the verified artefact stays unchanged, the model is compact, and its signed coefficients support direct local explanations.

The native Logistic Regression score is not presented as a reliable probability. Platt scaling is fitted only on calibration rows. On the final test, Brier score improves from 0.010464 to 0.006292 and ten-bin ECE from 0.044799 to 0.005295. A separate validation-policy subset selects a 0.59 calibrated-confidence threshold. Below it, or for inadequate/out-of-scope inputs, the system returns `Editorial review required`.

The archive uses a random per-session SQLite path in public-safe mode so one visitor cannot list another visitor's history. Review notes and sources remain in that boundary. Aggregated analytics and drift diagnostics exclude article text and never trigger retraining.

## Five-minute demonstration sequence

1. **News Desk:** identify the six areas, the final-test macro F1, the no-runtime-retraining rule, and the responsible-use boundary.
2. **Analyse Article:** load the packaged uncertain sample. Show independent summarisation and the `Editorial review required` outcome around 50% calibrated confidence.
3. **Calibration and explanation:** point to the 0.59 validation-selected threshold, calibrated probability gauge, vocabulary/OOV checks, signed local feature contributions, and exact disclaimer.
4. **Model Accountability:** compare the three classical candidates, show the 2,399-row confusion matrix, Brier/ECE evidence, reliability curve, and selection rationale.
5. **Editorial Archive:** open the selected record, save an `Inconclusive` review with a public source URL and a final assessment, then show that the model output and human status remain distinct.
6. **Newsroom Analytics:** show outcome/confidence/review distributions, latency, activity, and the privacy-safe analytics CSV.
7. **Drift Readiness:** before 20 records, point out the explicit insufficient-observations message; explain that warnings indicate distributional change and do not trigger retraining.
8. **Research & About:** close with limitations, visitor isolation, the Marathi roadmap, ownership, and the deployment/licensing gate.

## Architecture explanation

```text
Streamlit pages (app.py + six native routes)
        |
        +-- ingestion: text / public URL / TXT / PDF
        +-- preprocessing: clean, segment, metadata, language hint
        +-- summarisation: extractive or optional DistilBART
        +-- classification: saved TF-IDF + Logistic Regression
        +-- confidence: private Platt calibration + 0.59 review policy
        +-- explainability: observed TF-IDF x coefficient contributions
        +-- session services: SQLite review/archive + analytics + drift
        +-- exports: JSON / PDF / CSV

Next.js under web/ is a presentation shell only; /app embeds Streamlit with ?embed=true.
Training and benchmarking remain offline and are never imported by runtime modules.
```

## Dataset, preprocessing, and leakage controls

- Official dataset: ISOT Fake News Dataset from the University of Victoria ISOT Research Lab.
- Raw rows: 44,898; eligible clean corpus: 37,883; balanced working sample: 24,000.
- Labels: `True.csv` to reliable label 0; `Fake.csv` to misleading label 1.
- Features: cleaned title plus body; source filename, subject, and date excluded.
- Source-marker mitigation: explicit Reuters leads and reporting/byline markers are neutralised.
- Exact duplicates: removed before sampling and splitting.
- Near duplicates: approximate five-gram candidate screen followed by Jaccard >=0.90 verification.
- Partition isolation: two contaminated holdout rows quarantined; zero verified near-duplicate pairs cross final train/validation/test partitions.
- Vectoriser isolation: TF-IDF fits only on training rows inside each scikit-learn Pipeline.
- Final test: untouched by candidate fitting, Platt calibration, and review-threshold selection.

## Compared models and verified final-test metrics

| Model | Accuracy | Macro F1 | ROC-AUC | Calibrated Brier | Calibrated ECE |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.992080 | 0.992080 | 0.999481 | 0.006292 | 0.005295 |
| Linear SVC | 0.994581 | 0.994581 | 0.999851 | 0.004059 | 0.004451 |
| Multinomial Naive Bayes | 0.960817 | 0.960815 | 0.991564 | 0.029562 | 0.009859 |

Macro F1 gives the reliable and misleading-labelled classes equal weight. ROC-AUC measures ranking, not calibration. Brier score measures squared probability error. ECE summarises the gap between predicted probability and observed label frequency across bins.

## Calibration and abstention

Platt scaling fits a one-feature Logistic Regression from the production model's decision score to the misleading-label probability. It uses 1,199 validation-calibration rows. A separate 1,200-row validation-policy subset selects the review threshold. The rule chooses the lowest threshold with at least 80% automatic-decision coverage and a 95% Wilson lower accuracy bound of at least 99% relative to validation labels; 0.59 is selected.

The final test is used only once for reporting. It shows 99.833% confidence-only automatic coverage and 99.290% selective accuracy; the 95% Wilson lower bound is 98.866%. That lower test bound is reported honestly even though it is below the validation policy target. Language, input-quality, and domain-support checks can create additional real-session reviews.

## False-positive and false-negative consequences

- **False positive:** a reliable-labelled article receives a higher-risk direction. It can waste editorial time, unfairly stigmatise writing, or delay publication. The final-test Logistic Regression confusion matrix contains four such cases.
- **False negative:** a misleading-labelled article receives a lower-risk direction. It can create false reassurance and reduce scrutiny. The final-test matrix contains 15 such cases.
- **Mitigation:** cautious labels, calibrated confidence, abstention, local explanations, visible limitations, human review, and no automatic moderation or publication action.

## Security, privacy, and database design

- URL ingestion rejects non-HTTP(S), credentials, private/loopback/link-local targets, unsafe redirects, oversized responses, and excessive redirect hops.
- Uploads enforce safe filenames, supported formats, 10 MB limits, PDF page limits, and bounded extraction.
- CSV exports neutralise spreadsheet-formula prefixes; PDF text is escaped before ReportLab rendering.
- Runtime errors avoid stack traces and local paths in the public interface.
- Public-safe history uses an opaque random session token hashed into a temporary SQLite filename.
- SQLite stores summaries and structured fields, not complete original articles or upload bytes.
- Review fields include status, notes, source URLs, final assessment, and update timestamp.
- The isolation design is not authentication or durable enterprise storage. A managed database and identity layer are future production work.

## Analytics and drift

Newsroom analytics aggregate analysed count, risk outcomes, confidence bands, review and inconclusive rates, latency, model comparison, and activity. The privacy-safe analytics export contains metrics only.

Drift readiness monitors article length, vocabulary coverage, OOV rate, predicted-class distribution, calibrated-confidence distribution, invalid-input rate, language mismatch, and a length/coverage domain heuristic. Fewer than 20 observations returns an insufficient-data message. No indicator retrains the model or proves failure.

## Deployment architecture and gate

The approved zero-cost academic architecture is a public GitHub repository, Streamlit Community Cloud for `app.py`, and Vercel Hobby for the lightweight Next.js shell under `web/`. The shell reads only `NEXT_PUBLIC_STREAMLIT_APP_URL` and embeds `?embed=true`.

Public functional deployment is pending because redistribution permission for the packaged model and dataset-derived calibration parameters is unresolved. Public packages exclude both artefacts. No live repository, Streamlit URL, or Vercel URL is claimed before verification.

## Limitations and Marathi roadmap

ISOT is English-heavy, political, time-bound, and affected by outlet/topic/style shortcuts. Random-split performance may not transfer to new publishers, events, regions, satire, opinion, adversarial paraphrases, or future language. Explainability shows influence, not evidence. Human review reduces risk but does not guarantee correctness.

Marathi and multilingual news processing are future research. A defensible extension requires a licensed regional corpus, newsroom-reviewed labels, language-specific preprocessing, publisher/event/time-separated evaluation, calibration per language/domain, and human evaluation. Translation alone is not a validated Marathi model.

## Likely interview questions and accurate answers

### 1. What problem does NewsLens AI solve?

It reduces reading load with summarisation and supplies a cautious, explainable linguistic risk signal to help prioritise human editorial review. It does not verify facts.

### 2. Why keep summarisation and classification independent?

A generated summary can omit or rewrite phrases used by the classifier. Both branches therefore receive the original cleaned article and are joined only in the UI.

### 3. Why use TF-IDF instead of a transformer classifier?

TF-IDF is CPU-efficient, interpretable, reproducible, and suitable for a zero-cost student deployment. The goal is a well-evaluated classical baseline, not maximum model complexity.

### 4. Why select Logistic Regression when Linear SVC scored higher?

The SVC macro-F1 advantage is 0.002501, below the predefined 0.01 tolerance. Logistic Regression preserves the verified compact artefact and direct signed-coefficient explanations. Both require calibration for probability UX; the selected model has a validated Platt mapping.

### 5. What is macro F1?

It is the unweighted mean of the F1 score for each class, so both reliable and misleading-labelled classes contribute equally.

### 6. What is data leakage here?

Leakage occurs if test information influences training, feature fitting, calibration, or threshold selection. Controls include pre-split duplicate removal, training-only TF-IDF fitting, near-duplicate quarantine/grouping, and separate validation/final-test use.

### 7. Is the near-duplicate method exhaustive?

No. It is a deterministic approximate candidate screen using minimum word-five-gram signatures, followed by exact Jaccard verification. The limitation is documented rather than represented as semantic deduplication.

### 8. Why not tune the threshold on the test set?

That would optimise policy against the evaluation labels and make the final metric optimistic. Calibration and threshold selection use separate validation subsets; test labels are reserved for reporting.

### 9. What does Platt scaling do?

It fits a logistic mapping from a model decision score to a probability using held-out labels. It improves probability reliability but does not verify factual truth.

### 10. What is Brier score?

It is the mean squared difference between predicted probability and the binary dataset label. Lower is better.

### 11. What is expected calibration error?

ECE bins predictions and computes a weighted average of the absolute gap between mean confidence and observed positive-label rate. It is useful but depends on the binning scheme.

### 12. How was the 0.59 review threshold selected?

On the validation-policy subset, the lowest threshold satisfying at least 80% coverage and a 95% Wilson lower accuracy bound of at least 99% was selected. The test set did not choose it.

### 13. When does the system abstain?

It returns `Editorial review required` for confidence below 0.59, inadequate input, non-English/mixed-script input, or length/vocabulary conditions outside the configured reference checks.

### 14. What does local explainability mean here?

For each observed feature, the UI shows TF-IDF value multiplied by the Logistic Regression coefficient. The sign and magnitude explain model influence, not evidence for a claim.

### 15. How is visitor history isolated?

Public-safe mode creates a cryptographically random session identifier, hashes it into a temporary SQLite filename, and passes that path to every CRUD call. Separate sessions receive different files.

### 16. Is the archive durable in cloud hosting?

No. It is an academic session/local prototype. Streamlit restarts may remove temporary files. Durable multi-user persistence would require deliberate identity and managed storage.

### 17. How do analytics protect privacy?

They operate only on the visitor's scoped archive. The analytics export contains aggregate metrics and excludes titles, summaries, URLs, notes, and analysis identifiers.

### 18. What is drift in this project?

Drift is a measurable change in input or output distributions relative to a reference profile. A warning suggests review; it does not prove model failure.

### 19. Why is there no automatic retraining?

Retraining needs licensed data, label review, evaluation, approval, and a new verified artefact. Automatic cloud retraining would violate the project's safety, reproducibility, and cost boundaries.

### 20. What are the largest model risks?

Outlet/topic/style leakage, cross-domain degradation, English-only support, false reassurance, unfair higher-risk labelling, and interpreting confidence or explanations as truth evidence.

### 21. How do you secure URL extraction?

The extractor validates every redirect, rejects private and local addresses, resolves globally routable DNS, disables environment proxies, checks peer addresses where observable, applies timeouts and hop limits, and caps streamed response bytes.

### 22. Why use SQLite?

It is lightweight, dependency-free, easy to test, and appropriate for a local/session academic prototype. It is not represented as an enterprise multi-user database.

### 23. What would you improve for production?

Add authenticated roles, encrypted managed storage, retention controls, audit logs, editor-agreement studies, publisher/event/time-split evaluation, licensed multilingual data, monitoring ownership, and an evidence-retrieval workflow evaluated separately.

### 24. What part was AI-assisted?

AI tools assisted with code drafting, test ideas, documentation structure, and QA automation. I retained ownership of requirements, reviewed changes, ran the measured benchmark and tests, checked security/privacy boundaries, reconciled evidence, and can explain the implemented design. I do not claim unreviewed AI output as independent research evidence.

## Resume description

NewsLens AI is an explainable editorial NLP system built with Streamlit, scikit-learn, TF-IDF, Logistic Regression, SQLite, Plotly, and a lightweight Next.js presentation shell. It combines independent summarisation and linguistic risk classification with held-out confidence calibration, validation-based abstention, human editorial review, privacy-safe analytics, drift readiness, security-hardened ingestion, and reproducible release auditing.

## Three resume bullet points

- Built an end-to-end Streamlit editorial NLP application supporting text, public URL, TXT, and PDF ingestion; independent summarisation; calibrated TF-IDF/Logistic Regression risk signals; local explanations; and JSON/PDF/CSV exports.
- Designed a leakage-controlled three-model benchmark on 24,000 balanced ISOT rows, preserving an untouched 2,399-row final test; achieved 0.992080 macro F1 with the selected model and improved Brier score from 0.010464 to 0.006292 using held-out Platt calibration.
- Implemented validation-based abstention, visitor-isolated SQLite editorial review, privacy-safe newsroom analytics, drift diagnostics, SSRF-resistant URL extraction, secure exports, responsive same-tab navigation, automated tests, and model-excluded public-release controls.

## Honest AI-assisted development statement

I used AI as a development assistant for drafting and review, not as an authority for results. I verified the dataset and model checksums, reproduced the baseline, executed the controlled benchmark, inspected generated evidence, tested failure cases, reviewed the code and documentation, and preserved a clear audit trail. I can explain each architectural and methodological choice and will state when a detail requires consultation with primary documentation.

> This result is a machine-learning risk signal. It is not independent confirmation that an article is factually true or false.
