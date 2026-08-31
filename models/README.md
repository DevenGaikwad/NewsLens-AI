# NewsLens AI — Packaged Model

`fake_news_pipeline.joblib` is the verified TF-IDF + Logistic Regression production
pipeline. It is loaded at application start without retraining. The private
`confidence_calibration.json` companion applies Platt scaling and the validation-selected
editorial-review threshold. `model_metadata.json` records the model identity and training
evidence; the controlled benchmark evidence is under `reports/`.

Do not treat the output as a fact-check. High held-out performance on ISOT can be
inflated by publisher, topic and writing-style artefacts even after duplicate and
source-marker mitigation.

## Publication status

The artifact is retained in this local release candidate so the application can
be verified without retraining. Its public redistribution rights and explicit
license have not been confirmed. Do not push `fake_news_pipeline.joblib` to a
public repository or deploy it publicly until the rights holders document that
permission. The dataset-derived calibration parameters are subject to the same gate.
Source-code licensing does not automatically license either artefact.

The official University of Victoria ISOT dataset page was reviewed on
16 August 2026. It provides the dataset download, but no explicit licence for
redistribution of this trained artifact was located on that page. The private
archive retains the exact verified binary; the public-staging archive excludes it.
