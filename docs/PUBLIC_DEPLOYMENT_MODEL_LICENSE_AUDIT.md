# Public Deployment Model and License Audit

## Decision

Public deployment is now technically and legally scoped to the independently created synthetic package. The earlier private ISOT-derived classifier and calibration remain excluded and are not used by training, runtime, tests, repository artifacts, or deployment.

## Evidence

- Dataset: `newslens-synthetic-articles-v1.0.0`, original fictional content.
- Dataset license: CC BY 4.0 to the extent applicable rights subsist.
- Public model hash: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`.
- Public calibration hash: `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`.
- Binding: calibration `model_sha256` equals the public model SHA-256.
- External copyrighted training data: none.
- Private ISOT content or derived artifact: none.

## Limit

This audit does not convert a synthetic benchmark result into a claim about unrestricted real-world truth detection. The deployed app must retain its synthetic scope and abstention wording.
