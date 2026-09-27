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

## Phase 5T addendum — 27 September 2026

The earlier Phase 5S hold is preserved above as a historical checkpoint. The later owner instruction authorized a protected presentation correction and zero-open-PR cleanup. [PR #47](https://github.com/DevenGaikwad/NewsLens-AI/pull/47) merged as `d9291605ac9813982837dcb5fade645035795a34` (tree `c9db63a911d6c34cbecd0935336866a6280bde88`); exact-new-main CI and CodeQL passed. Live public UI checks included all six routes, both supported comparison outcomes, unsupported score withholding, input validation, exports, isolated archive, and visually inspected newly downloaded PDF pages.

[PR #42](https://github.com/DevenGaikwad/NewsLens-AI/pull/42) merged the patched pypdf 6.19.0 pin as `0e58189b8cbfd92126e5f4268bff320bdeb25bd1` (tree `b59b7ccb51a3177ec5044280a66cf7201ee8cfaf`); 165 Python tests with 6.19.0 and exact-new-main CI/CodeQL passed. Seven other old dependency PRs closed with individual explanations, leaving zero open PRs. The dataset, model, and calibration hashes stayed unchanged. Repository alert counts and the exact current Streamlit deployment commit await authorized dashboard verification. The historical release tag and Vercel remain untouched.
