# NewsLens AI — Student and Internship Handoff

This handoff uses the verified Phase 5S dataset/model release as its source of truth and incorporates the Phase 5T presentation-only maintenance. Phase 5T repairs PDF table wrapping, clarifies human-readable probability labels and out-of-scope score withholding, and applies narrow public-UI refinements without changing the model, calibration, dataset, thresholds, stable machine-readable score keys, or evaluation results.

## 1. Final project overview

### What problem does NewsLens AI address?

NewsLens AI is an explainable editorial decision-support prototype. It helps a user:

- reduce a long article into a deterministic reading summary;
- compare two visible factual ledgers in a supported fictional article format;
- receive a calibrated synthetic consistency signal;
- understand why the model produced that signal;
- route unsupported or uncertain inputs to human editorial review;
- retain privacy-conscious, session-isolated analysis records.

Its classifier has a deliberately bounded objective. It compares the article’s visible `Reference note` and `Article account` fields and determines whether their authored ledgers are consistent or contradicting.

It is not a universal fake-news detector and does not independently verify real-world facts.

### Purpose of the six application sections

| Section | Purpose |
|---|---|
| News Desk            | Introduces the system, its synthetic-only scope, methodology, evaluation results, limitations, and responsible-use boundary.                                            |
| Analyse Article      | Accepts pasted text, a public URL, TXT, or text-based PDF; generates the summary, supported-scope comparison, explanation, and exports.                                  |
| Model Accountability | Presents the model identity, split strategy, locked evaluation, calibration, shortcut tests, confusion matrix, and limitations.                                         |
| Dataset Analysis     | Explains the 24,000-article synthetic benchmark, label balance, fictional provenance, licensing, and distribution statistics.                                           |
| Editorial Archive    | Stores structured analysis records only within the visitor’s isolated session and provides search, filters, analytics, review fields, drift readiness, and CSV exports. |
| Research & About     | Records the project purpose, synthetic provenance, privacy controls, model identity, responsible-use statements, and explicit limits.                                    |

### Complete user workflow

1. The user submits article text, a public URL, TXT, or text-based PDF.
2. The application validates and cleans the input.
3. A deterministic extractive summarizer returns selected original sentences.
4. The application identifies the supported `Reference note` and `Article account` ledgers.
5. It derives transparent field-level match and mismatch signals.
6. The public TF-IDF and Logistic Regression pipeline evaluates the original cleaned article.
7. Platt scaling converts the native score into calibrated probabilities.
8. Scope and abstention rules decide whether to return a label or require editorial review.
9. Local TF-IDF × coefficient contributions explain the model’s direction.
10. A structured record is added to the visitor’s session-local archive.
11. The user may export analysis results as JSON or PDF and privacy-safe aggregate/archive information as CSV.

The classifier always receives the original cleaned article—not the generated summary. This keeps summarisation and classification technically independent.

### Why the project uses an original synthetic dataset

The dataset was independently created so the public project could provide:

- a reproducible training source;
- clear labels and paired counterfactual events;
- complete schema and provenance documentation;
- a redistributable public model;
- no dependence on private or legally unresolved article datasets.

All articles, entities, places, events, and factual ledgers are fictional. The dataset is licensed as described in its dataset card: CC BY 4.0 to the extent applicable rights subsist.

### How external and non-redistributable source material is avoided

The public release permanently excludes:

- rows or article text from external copyrighted datasets;
- copied phrases or close paraphrases;
- transformations, translations, summaries, or reconstructions of external articles;
- any earlier non-redistributable classifier;
- the earlier private calibration artifact.

The public model uses distinct synthetic-only artifacts whose hashes are recorded in the release manifest and artifact manifest.

### Synthetic performance versus real-world verification

The model achieved perfect performance on its locked synthetic test because that test measures a structured, authored ledger-comparison task under the same benchmark design.

This does not establish that the model can:

- determine whether unrestricted news is true or false;
- verify external events;
- evaluate source reputation;
- detect every form of misinformation;
- generalize with the same accuracy to real journalism.

The correct description is therefore “synthetic ledger-consistency assistance,” not “automatic truth detection.”

---

## 2. End-to-end technical architecture

### Processing flow

| Stage | Verified behavior | Important repository elements |
|---|---|---|
| 1. Input and validation                             | Accepts pasted text, public URLs, TXT, and text-based PDF. Rejects insufficient input and validates supported content.                                                              | `app.py`, `pages/01_Analyse_Article.py`, file-parser and UI tests                                          |
| 2. Preprocessing                                    | Cleans and normalizes the original article while retaining the content required by the summarizer and classifier.                                                                   | `src/text_preprocessor.py`                                                                                 |
| 3. Summarisation                                    | Uses deterministic local TF-IDF-centroid extractive summarisation and returns original sentences. It does not call a generative API or external checkpoint.                         | Analysis-page runtime summarisation service                                                                |
| 4. Signal extraction                                | Parses the visible `Reference note` and `Article account` fields and generates field-level match/mismatch tokens.                                                                   | `src/text_preprocessor.py`, classifier preprocessing                                                       |
| 5. Classification                                   | Applies the packaged TF-IDF, up-to-bigram, Logistic Regression pipeline trained only on the synthetic corpus.                                                                       | `src/fake_news_predictor.py`, `models/newslens_synthetic_pipeline.joblib`                                  |
| 6. Calibration                                      | Applies Platt scaling and verifies that the calibration belongs to the exact model SHA-256.                                                                                         | `src/calibration.py`, `models/newslens_synthetic_calibration.json`, `models/public_artifact_manifest.json` |
| 7. Abstention                                       | Routes missing-format, out-of-scope, or policy-triggered inputs to `Editorial review required`.                                                                                     | Predictor, calibration, and analysis-page decision logic                                                   |
| 8. Explanation                                      | Reports local TF-IDF × coefficient contributions, including derived match/mismatch features.                                                                                        | `src/explainability.py`                                                                                    |
| 9. Analytics and review                             | Stores structured results in a session-isolated SQLite archive and produces aggregate newsroom and drift-readiness views. Full source articles and uploaded files are not retained. | `pages/04_Analysis_History.py`, `src/model_diagnostics.py`, `src/visualizations.py`                        |
| 10. Exports                                         | Generates JSON and PDF analysis exports in memory and privacy-safe analytics/archive CSV files.                                                                                     | Analysis and archive pages                                                                                 |

### Application structure

- `app.py` — Streamlit entry point and six-page navigation.
- `pages/00_News_Desk.py` — project landing page.
- `pages/01_Analyse_Article.py` — principal input and analysis workflow.
- `pages/02_Model_Performance.py` — Model Accountability page.
- `pages/03_Dataset_EDA.py` — Dataset Analysis page.
- `pages/04_Analysis_History.py` — Editorial Archive.
- `pages/05_Research_About.py` — provenance, privacy, research, and limitations.
- `ui/components.py` and `ui/theme.py` — reusable components and responsive visual system.
- `training/train_synthetic_model.py` — deterministic offline training and evaluation entry point. Runtime code does not retrain the model.
- `scripts/audit_public_release.py` — release-safety and artifact-integrity gate.

### Frozen public artifacts

| Artifact | Verified identity |
|---|---|
| Dataset archive           | `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`            |
| Dataset size              | 10,319,934 bytes                                                   |
| Dataset SHA-256           | `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc` |
| Dataset Git blob          | `cb0d5e57407be10fecefb34762e586bacd38dd56`                         |
| Model                     | `models/newslens_synthetic_pipeline.joblib`                        |
| Model SHA-256             | `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6` |
| Calibration               | `models/newslens_synthetic_calibration.json`                       |
| Calibration SHA-256       | `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77` |
| Metadata SHA-256          | `6d868465dfc8e038343a179659e23c5015c10900d8b74fec6b62b80ebf5e1a73` |

Authoritative evidence is retained in `release_manifest.json`, `docs/DATASET_CARD.md`, `docs/MODEL_CARD.md`, `docs/DEPLOYMENT.md`, and `reports/NewsLens_AI_Deployment_and_Audit_Report.md`.

---

## 3. Dataset and model explanation

### Dataset design

The benchmark contains:

- 24,000 entirely synthetic articles;
- 12,000 fictional event pairs;
- 12,000 ledger-consistent articles;
- 12,000 ledger-contradicting articles;
- original fictional entities, locations, events, wording, and ledger values.

Each paired event provides controlled variants. This makes it possible to test whether the classifier reacts to the intended ledger relationship rather than merely memorizing background wording.

### Five-way event-grouped split

| Partition | Articles | Purpose |
|---|---:|---|
| Training                 | 18,000 | Fit the TF-IDF vocabulary and Logistic Regression parameters |
| Model validation         | 2,400  | Compare and select the model configuration                   |
| Calibration              | 1,200  | Fit Platt scaling without using test data                    |
| Abstention policy        | 1,200  | Select the review/abstention policy                          |
| Locked final test        | 1,200  | One-time final evaluation                                    |

The split is performed by event group, not by random article row. Both members of a fictional event pair remain in the same partition.

Verified leakage results:

- cross-partition event overlap: `0`;
- cross-partition content-hash overlap: `0`;
- paired-event and accepted near-duplicate leakage checks: passed.

### Model selection

The selected public pipeline is:

- TF-IDF text representation using features up to bigrams;
- transparent derived field-match/mismatch tokens;
- Logistic Regression;
- Platt-scaled confidence calibration.

Model selection occurred on the model-validation partition. The locked final test was not used for fitting, model selection, calibration, or threshold selection.

### Shortcut controls

| Control | Balanced accuracy | Interpretation |
|---|---:|---|
| Surface/raw-text-only baseline         | 0.500000 | Background prose alone performed at chance                            |
| Fact-block ablation                    | 0.498333 | Removing the intended comparison signal reduced performance to chance |
| Metadata-only baseline                 | 0.520833 | Metadata did not provide a reliable label shortcut                    |
| Full selected pipeline                 | 1.000000 | The intended structured comparison solved the synthetic task          |

These controls support the conclusion that performance depends primarily on the authored ledger relationship rather than superficial style or metadata.

### Counterfactual testing

The account-swap counterfactual flip rate was `100%`.

This means that when the relevant ledger relationship was deliberately changed, the model’s decision changed accordingly. It provides stronger evidence of sensitivity to the intended signal than accuracy alone.

It still does not prove real-world causal reasoning or factual verification.

### Calibration and abstention

Platt scaling was fitted on its own calibration partition. The calibration JSON records the SHA-256 of the exact model it belongs to, and the runtime fails closed if the binding is invalid.

Verified calibrated results:

- Brier score: `0.0000014968608529442928`;
- Expected Calibration Error: `0.0007422494250466733`;
- selected editorial-review threshold: `0.50`;
- automatic coverage on the locked synthetic test: `100%`.

Confidence means agreement with the synthetic benchmark labels. It is not a probability that an external event is factually true.

The application presents the two class scores as:

- **Fields agree - calibrated probability:** the calibrated probability of the synthetic ledger-consistent comparison pattern.
- **Fields conflict - calibrated probability:** the calibrated probability of the synthetic ledger-contradicting comparison pattern.

Reference-comparison confidence is the model's calibrated confidence in its selected synthetic consistency class. It is not factual certainty. When either required structured block is missing, the UI, PDF, and archive CSV show **Outside supported comparison scope** and withhold directional scores. Stable JSON fields remain available for compatibility and are marked as withheld.

Abstention can also occur because the input lacks the supported fact-block structure. Therefore, even a numerical model score cannot override the scope boundary.

### Locked-test results

- Accuracy: `1.000`
- Balanced accuracy: `1.000`
- Macro precision: `1.000`
- Macro recall: `1.000`
- Macro F1: `1.000`
- Confusion matrix: `[[600, 0], [0, 600]]`

The correct interpretation is:

> The pipeline perfectly separated the two authored classes on the locked synthetic benchmark. It has not been validated as a general detector of real-world misinformation.

---

## 4. Five-to-seven-minute demonstration script

Before the demonstration, keep these three repository samples ready:

- `data/sample/reliable_style_article.txt`
- `data/sample/misleading_style_article.txt`
- `data/sample/uncertain_style_article.txt`

### 0:00–0:35 — Open and introduce

**Action:** Open [NewsLens AI](https://newslens-ai-devengaikwad.streamlit.app/).

**Say:**

> “NewsLens AI is an explainable editorial decision-support prototype. It creates a deterministic reading summary and evaluates whether two visible fictional ledgers are consistent or contradicting. It is trained only on an independently authored synthetic benchmark and is not presented as a universal fake-news detector.”

### 0:35–1:05 — Explain the six pages

**Action:** Point to the navigation.

**Say:**

> “The News Desk introduces the scope. Analyse Article performs the complete workflow. Model Accountability presents evaluation and calibration evidence. Dataset Analysis explains synthetic provenance. Editorial Archive provides session-isolated records and analytics. Research & About records the project’s limitations, privacy boundary, and artifact identities.”

### 1:05–2:05 — Ledger-consistent example

**Action:** Open Analyse Article and load the packaged sample or paste `reliable_style_article.txt`. Select a summary length and analyse.

**Say:**

> “The classifier receives the original cleaned article. The summary is a separate deterministic extractive output and is not used as the classifier input.”

After the result appears:

> “This example contains matching Reference note and Article account fields, so the application reports a synthetic ledger-consistent pattern. The Fields agree score is the calibrated probability of that synthetic class; it is not a real-world truth probability.”

### 2:05–2:55 — Ledger-contradicting example

**Action:** Clear the text and paste `misleading_style_article.txt`.

**Say:**

> “This sample changes the authored account values while retaining a similar fictional article structure. The Fields conflict score now dominates because its comparison pattern matches the synthetic contradicting class. It still does not say whether real-world reporting is fake.”

### 2:55–3:35 — Out-of-scope abstention

**Action:** Paste `uncertain_style_article.txt` or ordinary prose without both supported fact blocks.

**Say:**

> “This article does not provide the complete supported ledger structure. NewsLens AI therefore shows Outside supported comparison scope and withholds the directional percentage. The summary remains available, but the model does not present an ordinary external article as factually credible or false.”

### 3:35–4:10 — Confidence and explanations

**Action:** Return to a completed supported analysis and point to confidence, calibration wording, and feature contributions.

**Say:**

> “Fields agree and Fields conflict are the two calibrated synthetic class probabilities for supported structured comparisons. Reference-comparison confidence is the selected class score, not factual certainty. The explanation shows local TF-IDF coefficient contributions and transparent match or mismatch tokens.”

### 4:10–4:40 — Exports

**Action:** Point to the JSON and PDF buttons.

**Say:**

> “The structured result can be exported as JSON for technical inspection or PDF for review. The repaired PDF keeps every wrapped label and value in separate A4 table columns and includes the same score explanation. Exports are generated in memory, and the original uploaded file is not retained.”

### 4:40–5:10 — Model Accountability

**Action:** Open Model Accountability.

**Say:**

> “The model uses five event-grouped partitions so paired events cannot cross between training, validation, calibration, policy selection, and locked testing. Event and content-hash overlap are both zero. The page also reports calibration and shortcut-control results.”

### 5:10–5:35 — Dataset Analysis

**Action:** Open Dataset Analysis.

**Say:**

> “The benchmark contains 24,000 fictional articles from 12,000 event pairs with balanced labels. All article text and entities are independently authored; no external copyrighted article dataset or non-redistributable model artifact is included.”

### 5:35–6:05 — Editorial Archive and privacy

**Action:** Open Editorial Archive.

**Say:**

> “The archive is isolated to the current visitor session. It stores structured analysis fields, summaries, metadata, review information, and supported-scope scores—not uploaded files or complete source articles. Out-of-scope directional values are withheld from its CSV export.”

### 6:05–6:30 — Conclude

**Action:** Open Research & About or return to News Desk.

**Say:**

> “The technical contribution is a reproducible synthetic-data pipeline combining independent extractive summarisation, an explainable linear classifier, hash-bound calibration, abstention, counterfactual evaluation, privacy-conscious analytics, and protected public deployment. Its value is transparent editorial assistance within a documented scope—not automatic truth determination.”

---

## 5. Viva and internship interview preparation

### 1. What is the exact problem statement?

NewsLens AI investigates whether an article-analysis system can combine deterministic summarisation with an explainable and calibrated consistency classifier. Its bounded classifier compares two visible fictional ledgers and supports human review rather than claiming unrestricted truth detection.

### 2. Why should it not be called a universal fake-news detector?

Its training and locked evaluation use a structured synthetic benchmark, not unrestricted real-world journalism. It has not been validated across changing events, languages, publishers, political contexts, satire, or adversarial misinformation.

### 3. Why did you choose synthetic data?

Synthetic data provided clear authorship, provenance, balanced labels, controlled counterfactuals, and reproducible redistribution. It also allowed the project to publish a model without exposing earlier non-redistributable artifacts.

### 4. How was the dataset balanced?

The 24,000 articles represent 12,000 fictional event pairs. Each event pair contributes controlled consistent and contradicting variants, giving 12,000 articles per class.

### 5. Why use event-grouped splitting?

Random row splitting could place two variants of the same fictional event in different partitions, producing leakage. Grouping by event keeps paired material together and produced zero cross-partition event and content-hash overlap.

### 6. Why are there five partitions rather than a simple train-test split?

Each decision requires independent evidence. Training fits the model, validation selects it, calibration fits Platt scaling, the policy set chooses abstention behavior, and the locked final test estimates performance only after all choices are fixed.

### 7. What is TF-IDF?

TF-IDF weights terms according to their importance within one article relative to their frequency across the corpus. NewsLens uses features up to bigrams, allowing the linear model to consider individual terms and short two-term combinations.

### 8. Why was Logistic Regression selected?

It is computationally efficient, supports probabilistic calibration, and provides signed coefficients that can be used for local explanations. It is appropriate for a CPU-friendly student deployment and was selected using the validation partition rather than the locked test.

### 9. How are the ledger fields represented?

The preprocessing stage parses the supported Reference note and Article account fields and derives transparent match or mismatch features. These signals are combined with the TF-IDF representation inside the saved pipeline.

### 10. Why is summarisation separate from classification?

The summary exists to help the user read the article. Classification uses the original cleaned text so compression cannot remove a decisive field or introduce a dependency between the two objectives.

### 11. What is Platt scaling?

Platt scaling learns a logistic mapping from a model’s native decision scores to calibrated probabilities. It was fitted on a separate calibration partition and improves the interpretability of confidence without changing the underlying class boundary.

In the interface, `Fields agree - calibrated probability` and `Fields conflict - calibrated probability` are the two supported-comparison class scores. Reference-comparison confidence is the score of the selected synthetic consistency class, not factual certainty. These values are not displayed for inputs outside the paired-ledger scope.

### 12. What is model-to-calibration binding?

The calibration JSON contains the SHA-256 of the exact model artifact for which it was fitted. At runtime, a mismatch fails closed so calibration from one model cannot silently be applied to another.

### 13. What is abstention?

Abstention means the system declines to make an automatic class claim. Unsupported structure is shown as `Outside supported comparison scope`, with directional probabilities withheld; other review-policy triggers return `Editorial review required`.

### 14. Why report balanced accuracy and macro F1?

Balanced accuracy gives equal importance to class-specific recall, while macro F1 gives equal importance to both classes when combining precision and recall. Although this dataset is balanced, these metrics make the evaluation clearer and remain useful if class distributions change.

### 15. What do Brier score and ECE measure?

Brier score measures the squared difference between predicted probabilities and observed labels; lower is better. ECE compares confidence with empirical accuracy across confidence bins; the reported calibrated ECE is `0.000742` on the synthetic benchmark.

### 16. What does the counterfactual flip test demonstrate?

It deliberately changes the relevant ledger relationship while controlling the surrounding event. The `100%` flip rate shows that decisions respond to the intended consistency signal, although it does not prove general real-world causal reasoning.

### 17. How did you test for shortcut learning?

The project evaluated a surface-text-only baseline, a fact-block ablation, and a metadata-only baseline. Their balanced accuracies were approximately `0.500`, `0.498`, and `0.521`, while the complete pipeline reached `1.000`.

### 18. What privacy controls are present?

Public history is isolated to the visitor session. Uploaded files and complete original articles are not retained, exports are generated in memory, secrets are not required, and the training archive is not exposed through the application.

### 19. How was the system deployed safely?

The app was deployed on Streamlit Community Cloud from `main`, using `app.py`, Python 3.12, empty secrets, and no paid features. Dataset, model, and evidence changes passed protected PRs, exact-head checks, CI, CodeQL, artifact hashing, and the public-release scan.

### 20. What is the most important future validation?

The highest-value next step is an evaluation-only study on an independently licensed, human-reviewed, out-of-distribution dataset. It should be completed before considering retraining or making any broader real-world reliability claim.

---

## 6. Honest limitations and safe claims

### Fully supported claims

- NewsLens AI is a deployed Streamlit editorial decision-support prototype.
- It combines deterministic extractive summarisation with an explainable classifier.
- The public classifier was trained exclusively on an independently authored synthetic benchmark.
- The benchmark contains 24,000 articles and 12,000 fictional event pairs with balanced labels.
- The selected model is a TF-IDF and Logistic Regression pipeline.
- Confidence uses Platt scaling bound to the exact model hash.
- The system can abstain and route unsupported inputs to editorial review.
- Event overlap and content-hash overlap across partitions are zero.
- The locked synthetic test achieved `1.000` accuracy, balanced accuracy, precision, recall, and macro F1.
- Shortcut baselines performed near chance.
- The counterfactual flip rate was `100%`.
- The interface provides local feature explanations.
- Public visitor history is session-isolated.
- JSON, PDF, and privacy-safe CSV export controls are available.
- No external copyrighted article dataset or non-redistributable model/calibration artifact was published.
- The release passed protected CI, CodeQL, and a zero-gate public-release scan.

### Claims that must not be made

- “NewsLens AI detects all fake news.”
- “The model has 100% real-world accuracy.”
- “The confidence score is the probability that an article is factually true.”
- “The system verifies external events or source credibility.”
- “Perfect synthetic performance proves real-world generalization.”
- “The model is unbiased across every topic, publisher, language, or demographic group.”
- “The project is trained on a named real-news dataset” or “uses an improved external-dataset model.”
- “Noncommercial use automatically makes copyrighted datasets legally safe.”
- “The application replaces journalists, fact-checkers, or editorial review.”
- “Editorial review is fully automated.”
- “No privacy or security risk can ever exist.”
- “An extractive summary guarantees that every important fact is preserved.”
- “Calibration eliminates uncertainty.”
- “The application provides legal, political, medical, or financial truth verification.”

The key distinctions are:

- reliability assistance ≠ definitive truth determination;
- synthetic evaluation ≠ unrestricted real-world validation;
- calibrated confidence ≠ factual certainty;
- editorial-review support ≠ replacement of human journalism.

### Safe résumé or LinkedIn description

> Built and deployed NewsLens AI, a Streamlit editorial decision-support prototype using a 24,000-article original synthetic benchmark, TF-IDF and Logistic Regression, Platt calibration, abstention, explainability, counterfactual evaluation, and session-isolated analytics. Achieved 1.000 macro F1 on the locked synthetic ledger-consistency test; the system is explicitly scoped as decision support rather than real-world truth verification.

---

## 7. Prioritized future-enhancement backlog

No enhancement below should be implemented without a separate authorization and protected workflow.

### High-priority improvements

| Enhancement | Expected benefit | Difficulty | Stable-release risk | Data, retraining, and protected PR |
|---|---|---|---|---|
| Licensed out-of-distribution real-world evaluation                                   | Establishes how sharply performance changes outside the synthetic schema and supports more defensible limitations | High        | Low if evaluation-only | Requires affirmatively licensed evaluation data; no initial retraining; protected PR required |
| Stronger scope and out-of-distribution detector                                      | Improves abstention for unusual formats, incomplete ledgers, adversarial text, and unsupported article types      | Medium–High | Medium–High            | Requires new out-of-scope and hard-negative data; likely retraining; protected PR required    |
| Automated live responsive and workflow regression testing                            | Continuously verifies mobile widths, navigation, inference paths, exports, session isolation, and public startup  | Medium      | Low                    | No training data or model retraining; protected PR required                                   |

### Medium-priority improvements

| Enhancement | Expected benefit | Difficulty | Stable-release risk | Data, retraining, and protected PR |
|---|---|---|---|---|
| Harder synthetic counterfactual and near-duplicate cases                             | Tests whether the model handles subtler contradictions and paraphrastic structures             | Medium | Medium     | New synthetic data and reproducibility audit; retraining likely; protected PR required |
| Calibration-under-shift evaluation                                                   | Determines whether confidence remains reliable when writing style and ledger complexity change | Medium | Medium     | New validation/calibration data; recalibration may be required; protected PR required  |
| Accessibility and keyboard regression suite                                          | Improves demonstrability and usability for keyboard and assistive-technology users             | Medium | Low        | No model data or retraining; protected PR required                                     |
| Privacy-preserving operational health monitoring                                     | Detects startup failures and latency regressions without collecting article text               | Medium | Low–Medium | No training data; no retraining; protected PR and privacy review required              |

### Optional research extensions

| Enhancement | Expected benefit | Difficulty | Stable-release risk | Data, retraining, and protected PR |
|---|---|---|---|---|
| Multilingual synthetic benchmark                                                     | Tests whether the architecture can support additional languages                                              | High        | High   | New original multilingual corpus, specialist review, retraining, calibration, and protected PR              |
| Alternative interpretable models                                                     | Compares Logistic Regression with calibrated linear SVM, rule hybrids, or other compact models               | Medium–High | Medium | Existing data may support initial study; retraining and protected PR required                               |
| Compact transformer benchmark                                                        | Studies whether contextual models improve harder cases                                                       | High        | High   | Retraining, larger compute budget, licensing review, new calibration, and protected PR                      |
| Primary-source evidence workflow                                                     | Helps human reviewers organize external evidence without converting the model into an automatic fact checker | High        | High   | New security, URL, privacy, and provenance design; no immediate model retraining, but protected PR required |

---

## 8. Submission-readiness checklist

### Live demonstration

- Open the verified Streamlit URL before entering the room.
- Keep the three consistent, contradicting, and abstention samples in local text files.
- Demonstrate one sample from each decision path.
- Explain that the summary and classifier are independent.
- Point out the Fields agree, Fields conflict, calibrated confidence, review wording, explanation, and repaired PDF export.
- End with limitations rather than only the perfect synthetic metric.
- Avoid retraining, package installation, or configuration changes during the demonstration.

### GitHub repository

- Confirm that the branch shown is `main`.
- Know the roles of PRs #44, #45, and #46 and the separately protected Phase 5T maintenance/evidence record.
- Keep the pre-Phase5T rollback commit available: `f6cae8cedb3364cf03864410b8c5572c4e625504`.
- Keep the pre-Phase5T rollback tree available: `17e5876d56d91eb12fd5861ee6bdd95393e79910`.
- Be ready to show passed CI, CodeQL, and the public-release scan.
- Do not discuss retained Dependabot PRs as part of the project release.

### README and reports

- Use the README for the short project explanation.
- Use the deployment report for exact PR, merge, deployment, and smoke-test evidence.
- Use the dataset card for authorship, license, schema, and split details.
- Use the model card for intended use, metrics, calibration, and limitations.
- Use the release manifest when exact hashes are requested.

### Project presentation

- Include problem, bounded objective, architecture, dataset, grouped split, model, calibration, and abstention.
- Show the five-way split and shortcut baselines.
- Present perfect metrics only with the words “locked synthetic benchmark.”
- Include at least one slide on limitations and responsible use.
- Finish with the live application and protected-release evidence.

### Résumé and LinkedIn

- Use “editorial decision-support prototype” rather than “perfect fake-news detector.”
- Mention synthetic-only training.
- Name TF-IDF, Logistic Regression, Platt calibration, explainability, and Streamlit.
- If using `1.000` macro F1, explicitly qualify it as a locked synthetic ledger-consistency result.
- Link the public repository and Streamlit application.

### Faculty viva

- Memorize the difference between accuracy, balanced accuracy, macro F1, Brier score, and ECE.
- Be able to explain why the test partition was locked.
- Explain event grouping and leakage prevention.
- Explain why calibration requires a separate partition.
- Explain why abstention is technically and ethically necessary.
- State the most important limitation without being prompted.

### Internship interview

- Emphasize reproducibility, protected GitHub workflow, artifact hashing, and deployment discipline.
- Explain why a linear model was appropriate for this bounded CPU-friendly task.
- Discuss shortcut baselines and counterfactual testing—not just accuracy.
- Explain the copyright and provenance decision professionally.
- Propose evaluation-only real-world validation before retraining.
- Be prepared to discuss how you would monitor performance without logging private article text.

### Backup if Streamlit is temporarily unavailable

- Keep the frozen repository available locally at the verified commit.
- Keep the three sample articles ready.
- Save one representative JSON and PDF analysis export before the presentation.
- Keep the deployment report, release manifest, model card, and dataset card available offline.
- Keep links or screenshots of PRs #44–#46 and the passed workflow runs.
- If the Python 3.12 environment is already prepared, use `python -m streamlit run app.py` for an offline demonstration.
- If neither live nor local execution is available, present the recorded evidence honestly and do not claim that a new live check was completed.

## Phase 5T release boundary

The verified pre-maintenance rollback point is:

- Live application: [https://newslens-ai-devengaikwad.streamlit.app/](https://newslens-ai-devengaikwad.streamlit.app/)
- `main`: `f6cae8cedb3364cf03864410b8c5572c4e625504`
- Tree: `17e5876d56d91eb12fd5861ee6bdd95393e79910`

Phase 5T changes are limited to the PDF layout repair, supported-scope probability wording and withholding, the punctuation-free tagline, illustration bounds, concise footer attribution, public banner removal, regression tests, and affected documentation. Model behavior, calibration, dataset, thresholds, stable machine-readable score fields, locked metrics, the historical tag, and Vercel remain unchanged.

The three most valuable candidates for a future separately authorized phase are:

1. Conduct an evaluation-only study on a clearly licensed, independently reviewed out-of-distribution dataset.
2. Develop stronger scope/OOD detection and recalibrate abstention using harder supported and unsupported examples.
3. Add automated live browser regression testing across mobile/desktop layouts, inference paths, exports, and session-isolation behavior.

## Phase 5U scope clarification

The public classifier remains a **Reference comparison** of two visible fictional ledgers. Its human-readable result says the article fields agree or conflict with the supplied reference; calibrated probabilities remain technical details, not truth probabilities. Ordinary articles without the pair receive an out-of-scope editorial-review result. A proposed general-news screening model was not trained or deployed because the reviewed candidate datasets did not establish both suitable full-article labels and the required rights. See the existing [deployment/model license audit](PUBLIC_DEPLOYMENT_MODEL_LICENSE_AUDIT.md) for the specific candidates and the next evidence gate. The synthetic model, calibration, dataset, and machine-readable JSON labels were preserved.
