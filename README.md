# NewsLens AI

NewsLens AI is a noncommercial student and placement-portfolio demonstration built by **Deven Sachin Gaikwad**. It combines deterministic extractive summarisation with an explainable classifier trained exclusively on an independently created synthetic benchmark.

The classifier has a deliberately narrow purpose: compare the visible `Reference note` and `Article account` fields in the supported fictional format and indicate whether their ledgers are consistent or contradicting. It is **not** a general fake-news detector and does not establish real-world truth.

## What is public

- 24,000 original synthetic articles representing 12,000 fictional paired events.
- Deterministic generator, manifest, audit evidence, and reproducibility tests.
- TF-IDF bigram + Logistic Regression public model.
- Platt calibration cryptographically bound to the exact model SHA-256.
- Group-safe training, validation, calibration, abstention-policy, and locked-test partitions.
- Streamlit interface with summarisation, classification, abstention, explanations, exports, session-local review, and aggregate monitoring.

No ISOT row, copied phrase, close paraphrase, transformation, translation, summary, reconstruction, private ISOT model, private calibration artifact, or external copyrighted training dataset is included.

## Measured evidence

| Measure | Result |
|---|---:|
| Locked final-test rows | 1,200 |
| Accuracy / balanced accuracy / macro F1 | 1.000 / 1.000 / 1.000 |
| Confusion matrix | `[[600, 0], [0, 600]]` |
| Platt Brier score | 0.000001497 |
| Expected calibration error | 0.000742 |
| Counterfactual account-swap flip rate | 100% |
| Surface-text-only balanced accuracy | 0.500 |
| Fact-block ablation balanced accuracy | 0.498 |
| Metadata-only balanced accuracy | 0.521 |

Perfect in-distribution performance reflects a structured synthetic comparison task; it must not be interpreted as unrestricted news-veracity performance.

## Run locally

Python 3.12 is the deployment target.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lite.txt
python -m streamlit run app.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

No API key or secret is required. The packaged model and calibration are loaded from `models/` without runtime training.

## Reproduce the model package

The authoritative dataset archive is already versioned. The following command verifies its identity, trains on the authored training split, selects only on model validation, fits calibration, selects the abstention policy, and evaluates the locked final test once:

```bash
python training/train_synthetic_model.py
```

The accepted public artifacts are described in `models/public_artifact_manifest.json`. Re-running training in a materially different dependency environment can change serialized bytes; publication uses the recorded artifacts and hashes.

## Validate

```bash
python -m compileall -q app.py pages src ui tests scripts training synthetic_benchmark
python -m pytest -q --strict-markers
python scripts/audit_public_release.py --allow-publication-gates
```

The release scan verifies the dataset ZIP, public model, calibration binding, legal package, secrets, private artifact exclusions, navigation, and local links.

## Responsible use

- Inputs lacking both supported fact blocks are routed to **Editorial review required**.
- Confidence measures agreement with synthetic benchmark labels, not factual truth.
- The app does not expose raw training rows.
- Public history is isolated to a visitor session; full article text is not persisted.
- Human verification against independent primary sources remains necessary.

See `docs/DATASET_CARD.md`, `docs/MODEL_CARD.md`, `docs/TESTING.md`, and `docs/DEPLOYMENT.md` for the full evidence trail.

© 2026 Deven Sachin Gaikwad. All Rights Reserved. The synthetic dataset has the separate license described in its dataset card.
