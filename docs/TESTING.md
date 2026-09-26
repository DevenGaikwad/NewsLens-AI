# Testing and Validation

## Commands

```bash
python -m compileall -q app.py pages src ui tests scripts training synthetic_benchmark
python -m pytest -q --strict-markers --junitxml=reports/results/pytest_results.xml
python scripts/evaluate_packaged_samples.py
python scripts/audit_public_release.py --allow-publication-gates
python -m pip check
```

The web reference source is checked with `npm ci`, `npm run lint`, and `npm run build` from `web/`.

## Coverage

Tests cover synthetic archive identity, authored split counts, event/content isolation, signal derivation, model loading, model-to-calibration binding, consistent and contradicting samples, abstention, preprocessing, summarisation, URL/file safety, exports, database/session behavior, UI contracts, analytics, drift readiness, legal records, secret scanning, and release fail-closed behavior.

The CI workflow runs the complete test suite with the public model. No private-artifact test is deselected.

## Evaluation discipline

The final test is not used for candidate selection, calibration fitting, or threshold choice. Candidate selection uses model validation; Platt fitting uses calibration; policy selection uses abstention policy. Event pairs never cross partitions. Exact metrics and controls are in `reports/model_benchmark_summary.json`.

## Interpretation

Passing tests establishes implementation and in-distribution benchmark behavior. It does not establish factual accuracy on real articles. Deployment smoke tests must separately validate public startup, all three packaged paths, exports, error handling, session isolation, responsive layout, and absence of raw training-data exposure.
