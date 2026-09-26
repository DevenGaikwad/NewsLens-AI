# Phase 5S Deployment Checkpoint

Updated: 26 September 2026

State: **complete — protected dataset and model releases merged; public Streamlit deployment smoke-tested**

## Dataset release

- Archive path: `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`
- Size / SHA-256 / Git blob: `10,319,934` / `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc` / `cb0d5e57407be10fecefb34762e586bacd38dd56`
- PR A: #44; validated head `326499bb6f58f0420a0cf36a00828a901836323d`
- Squash merge / tree: `d3e77e6610c4a9c83d9137ca672a9aad4278285f` / `520bad55ea12f1a8e48ad2e533af26312c62933d`

## Synthetic model release

- Model / calibration SHA-256: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6` / `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- PR B: #45; validated head `56f6e3e7137bd03fe45a0cd3e88978588968cdd1`
- Squash merge / tree: `214b22745736b25f4c1121822a1811c76687bb00` / `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- PR and exact-new-main CI, public-release scan, presentation build, dependency review, and both CodeQL analyses passed as applicable.

## Deployment

- Workspace / branch / entry point / Python: `devengaikwad` / `main` / `app.py` / 3.12
- Public URL: <https://newslens-ai-devengaikwad.streamlit.app/>
- Initial deployed runtime commit: `214b22745736b25f4c1121822a1811c76687bb00`
- Startup, public access, six routes, summary, both labels, abstention, invalid input, explanations, JSON/PDF/CSV controls, and session isolation passed.
- No raw training archive is exposed through the application.
- Application-origin console errors: 0.

## Boundaries preserved

No ISOT content or private ISOT-derived artifact was published. The six retained Dependabot PRs, historical release tag, and every Vercel deployment remain untouched.
