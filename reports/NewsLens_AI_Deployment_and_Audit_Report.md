# NewsLens AI Phase 5S Deployment and Audit Report

Updated: 26 September 2026

Release state: **complete and publicly deployed**

## Dataset release (PR A)

- PR: [#44](https://github.com/DevenGaikwad/NewsLens-AI/pull/44)
- Owner upload commit: `e6031fa6ec193131be5fed4704722125104b066f`
- Follow-up head: `326499bb6f58f0420a0cf36a00828a901836323d`
- Squash merge: `d3e77e6610c4a9c83d9137ca672a9aad4278285f`
- Resulting tree: `520bad55ea12f1a8e48ad2e533af26312c62933d`
- Signature: GitHub verified
- Merge time: `2026-09-25T12:14:59Z`
- Required PR and exact-new-main checks: passed

## Dataset identity and provenance

- Path: `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`
- Size: 10,319,934 bytes
- SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`
- Git blob: `cb0d5e57407be10fecefb34762e586bacd38dd56`
- License: CC BY 4.0 to the extent applicable rights subsist
- Generator and corpus: deterministic, independently authored, fictional articles and entities
- Article / paired-event count: 24,000 / 12,000

## Model and calibration evidence

- Model: `models/newslens_synthetic_pipeline.joblib`
- Model size / SHA-256: 161,709 bytes / `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`
- Calibration: `models/newslens_synthetic_calibration.json`
- Calibration size / SHA-256: 728 bytes / `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- Metadata SHA-256: `6d868465dfc8e038343a179659e23c5015c10900d8b74fec6b62b80ebf5e1a73`
- Binding: the calibration and public manifest record the exact model SHA-256
- Training / validation / calibration / policy / test rows: 18,000 / 2,400 / 1,200 / 1,200 / 1,200
- Cross-partition event/content overlap: 0 / 0
- Locked accuracy / balanced accuracy / precision / recall / macro F1: 1.0 / 1.0 / 1.0 / 1.0 / 1.0
- Confusion matrix: `[[600, 0], [0, 600]]`
- Brier / ECE: 0.0000014968608529442928 / 0.0007422494250466733
- Coverage at threshold 0.50: 100%
- Counterfactual flip rate: 100%
- Surface-only / fact-block ablation / metadata balanced accuracy: 0.500 / 0.498333 / 0.520833

## Model release (PR B)

- PR: [#45](https://github.com/DevenGaikwad/NewsLens-AI/pull/45)
- Validated head: `56f6e3e7137bd03fe45a0cd3e88978588968cdd1`
- Squash merge: `214b22745736b25f4c1121822a1811c76687bb00`
- Resulting tree: `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- Signature: GitHub verified
- Sole parent: `d3e77e6610c4a9c83d9137ca672a9aad4278285f`
- Merge time: `2026-09-26T03:18:37Z`
- Changed files: 192
- PR checks: complete Python suite, public-release scan, presentation build, dependency review, and both CodeQL analyses passed.
- Exact-new-main CI run `36214408496`: passed.
- Exact-new-main CodeQL run `36214408382`: passed.

## Validation summary

- Complete Python suite: 154 passed; 0 failures, errors, or skips.
- Focused integration suite: 33 passed.
- Python compile, dependency consistency, pip audit, npm install/lint/build, npm audit, reproducibility, and artifact identity gates: passed.
- Four DOCX guides: 28 pages total; project PDF: 9 pages; render and visual inspection passed.
- Final public-release scan: safe tree and artifact integrity passed; secrets, personal data, forbidden files, broken local links, internal navigation findings, and publication gates all 0.

## Streamlit deployment

- Workspace: `devengaikwad`
- Repository / branch / entry point: `DevenGaikwad/NewsLens-AI` / `main` / `app.py`
- Python: 3.12; secrets: empty; plan: free Community Cloud
- Initial deployed runtime commit / tree: `214b22745736b25f4c1121822a1811c76687bb00` / `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- Public URL: <https://newslens-ai-devengaikwad.streamlit.app/>

### Public smoke evidence

- Startup, public access, and all six application pages passed.
- Packaged ledger-consistent input produced a 24-word deterministic summary, the expected consistency label, calibrated confidence, explanation, and session record.
- A ledger-contradicting input and an unsupported-format input produced the expected contradictory and abstention paths; short input produced the expected validation error.
- JSON and PDF analysis controls, analytics CSV, filtered-archive CSV, selected-record JSON/PDF, and archive workflows were visible and enabled when applicable.
- A fresh browser session opened an empty archive; the active session showed only its own new record.
- Dataset Analysis and Research & About state synthetic provenance and do not expose the training archive or raw rows.
- Application-origin console errors: 0. Browser-extension metadata warnings were excluded because they did not originate from the application.
- Desktop layout at 1363 CSS pixels had no horizontal overflow. The unchanged responsive system retains its five-width 360/390/768/1366/1920 release audit. The cloud browser's HTTP(S)-only URL policy prevented creation of a new 390-pixel harness; no unsupported workaround was attempted.

## Publication boundary

All training articles and entities are synthetic. No ISOT row, copied phrase, close paraphrase, transformation, translation, summary, reconstruction, private ISOT-derived classifier/calibration artifact, or external copyrighted article dataset is present in the model, repository, archive, deployment, or release. Noncommercial status was not treated as permission.

Vercel was not deployed. The six retained Dependabot PRs and historical release tag were not modified.
