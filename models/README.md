# Public model artifacts

The files in this directory are the public synthetic-only inference package.

| File | Purpose |
|---|---|
| `newslens_synthetic_pipeline.joblib` | Authored signal extraction, TF-IDF, and Logistic Regression pipeline |
| `newslens_synthetic_calibration.json` | Platt parameters, abstention threshold, dataset identity, and exact model binding |
| `model_metadata.json` | Human- and machine-readable model provenance |
| `public_artifact_manifest.json` | Sizes and SHA-256 identities for the package |

Accepted identities:

- Model SHA-256: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`
- Calibration SHA-256: `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- Dataset archive SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`

The calibration loader refuses to report calibrated confidence if the active model does not match its bound hash. Historical private ISOT-derived artifact names remain excluded by `.gitignore` and the public-release audit; they are neither needed nor permitted for this runtime.
