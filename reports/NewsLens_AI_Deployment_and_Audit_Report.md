# NewsLens AI Phase 5S Deployment and Audit Report

Updated: 26 September 2026

## Dataset release (PR A)

- PR: #44
- URL: `https://github.com/DevenGaikwad/NewsLens-AI/pull/44`
- Owner upload commit: `e6031fa6ec193131be5fed4704722125104b066f`
- Follow-up head: `326499bb6f58f0420a0cf36a00828a901836323d`
- Squash merge: `d3e77e6610c4a9c83d9137ca672a9aad4278285f`
- Resulting tree: `520bad55ea12f1a8e48ad2e533af26312c62933d`
- Signature: GitHub verified
- Merge time: 2026-09-25T12:14:59Z
- Required PR and exact-new-main checks: passed

## Dataset identity

- Path: `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`
- Size: 10,319,934 bytes
- SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`
- Git blob: `cb0d5e57407be10fecefb34762e586bacd38dd56`
- License: CC BY 4.0 to the extent applicable rights subsist
- Provenance: independently generated original fictional articles and entities

## Model evidence

- Model: `models/newslens_synthetic_pipeline.joblib`
- Model SHA-256: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`
- Calibration: `models/newslens_synthetic_calibration.json`
- Calibration SHA-256: `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- Binding: exact model hash recorded in calibration and public manifest
- Training / validation / calibration / policy / test rows: 18,000 / 2,400 / 1,200 / 1,200 / 1,200
- Cross-partition event/content overlap: 0 / 0
- Locked accuracy, balanced accuracy, macro F1: 1.0 / 1.0 / 1.0
- Brier / ECE: 0.000001497 / 0.000742
- Coverage at threshold 0.50: 100%
- Counterfactual flip rate: 100%
- Surface-only / ablation / metadata balanced accuracy: 0.500 / 0.498 / 0.521

## Publication boundary

No ISOT content, private ISOT-derived artifact, or external copyrighted article dataset is in the model, repository archive, or intended release. Noncommercial status was not used as a substitute for rights.

## PR B and deployment

PR B number, validated head, squash merge, resulting tree, exact-new-main workflow evidence, Streamlit URL, deployed commit, and public smoke-test evidence are pending execution. These fields will be updated after the protected merge and live deployment; they are not claimed in advance.

Vercel and six retained Dependabot PRs remain outside scope.
