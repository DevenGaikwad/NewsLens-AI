# Synthetic Model Benchmark Methodology

NewsLens AI model version `newslens-synthetic-tfidf-v1.0.0` is trained only from the independently
authored `newslens-synthetic-articles-v1.0.0` benchmark. No ISOT content, private ISOT-derived model, or
external copyrighted training dataset is used.

## Locked protocol

- Group key: `event_id`; paired articles never cross partitions.
- Training: 18,000 rows; model validation: 2,400 rows.
- Calibration: 1,200 rows; abstention-policy selection: 1,200 rows.
- Locked final test: 1,200 rows, evaluated once after selection and calibration.
- Candidate selection: validation macro-F1 with a 0.005 interpretable-model retention tolerance.
- Calibration: Platt scaling bound to model SHA-256 `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`.
- Editorial-review threshold: `0.50`.

## Controls

The evaluation includes content-hash and paired-event leakage checks, a visible
fact-block counterfactual swap, surface-text-only and metadata-only baselines, and
fact-block ablation. Metrics and per-partition evidence are recorded in
`reports/model_benchmark_summary.json`; artifact identities are recorded in
`models/public_artifact_manifest.json`.
