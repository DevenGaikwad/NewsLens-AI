# Public deployment blocked

This publication-staging source intentionally excludes
`models/fake_news_pipeline.joblib` and `models/confidence_calibration.json`
because documentary public redistribution rights have not been established.
Without those exact private artefacts, the packaged classifier cannot provide
the preserved calibrated NewsLens AI runtime functionality.

Do not deploy this staging package, retrain during build/startup, or silently
substitute a different model. Resolve the decision in
`docs/MODEL_REDISTRIBUTION_DECISION.md` and obtain explicit owner approval before
any technical replacement. Public deployment remains blocked.
