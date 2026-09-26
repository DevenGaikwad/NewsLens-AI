# Streamlit Community Cloud Deployment

## Live configuration

- Workspace: `devengaikwad`
- Repository: `DevenGaikwad/NewsLens-AI`
- Branch: `main`
- Entry point: `app.py`
- Python: 3.12
- Secrets: empty
- Plan: free / Community Cloud
- Public URL: <https://newslens-ai-devengaikwad.streamlit.app/>

The repository includes the public synthetic model and bound calibration. Startup does not download a checkpoint or retrain, and no paid feature is enabled.

## Protected release record

- PR B: [#45](https://github.com/DevenGaikwad/NewsLens-AI/pull/45)
- Validated head: `56f6e3e7137bd03fe45a0cd3e88978588968cdd1`
- Squash merge: `214b22745736b25f4c1121822a1811c76687bb00`
- Resulting tree: `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- Merge time: `2026-09-26T03:18:37Z`
- GitHub signature: verified
- Exact-new-main CI run: `36214408496`, passed
- Exact-new-main CodeQL run: `36214408382`, passed

## Public smoke-test record

| Check | Result |
|---|---|
| Startup and public URL | Passed |
| Six-page navigation | Passed |
| Deterministic extractive summary | Passed |
| Ledger-consistent and ledger-contradicting samples | Passed |
| Unsupported-format abstention | Passed |
| Short-input error handling | Passed |
| Explanations and confidence wording | Passed |
| JSON, PDF, analytics CSV, and filtered-archive CSV controls | Passed |
| Fresh-session archive isolation | Passed; zero records before the session analysis |
| Raw training data exposure | None observed; archive ZIP is not offered through the app |
| Application-origin console errors | 0 |
| Desktop overflow at 1363 CSS pixels | None |
| Responsive/mobile evidence | The unchanged responsive system retains its 360/390/768/1366/1920 viewport audit; live desktop behavior was rechecked after deployment |

The deployment browser could not create a separate 390-pixel harness because its URL policy permits only HTTP(S) navigation. No unsupported workaround was used; the retained five-width audit and repository breakpoints at 900 and 560 pixels remain the mobile evidence.

## Failure behavior

Missing model files raise an actionable startup error. A calibration/model hash mismatch fails closed and forces review rather than reporting unverified confidence. Inputs outside the paired-ledger format abstain.

Vercel is not required and was not created or modified. Six retained Dependabot pull requests and the historical release tag remain outside this deployment.
