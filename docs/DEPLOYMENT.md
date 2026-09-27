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

Vercel is not required and was not created or modified. At the Phase 5S checkpoint, the retained Dependabot pull requests and historical release tag remained outside that deployment.

## Phase 5T maintenance boundary

The post-release maintenance changes only human-readable result presentation and documentation. PDF table cells use wrapping-aware paragraphs, calculated A4 widths, expanding row heights, top alignment, and padding. Supported comparisons use **Fields agree - calibrated probability**, **Fields conflict - calibrated probability**, and **Reference-comparison confidence**. Missing-ledger inputs are presented as **Outside supported comparison scope** and do not display directional probabilities in the UI, PDF, or archive CSV.

The same pass removes the public publication-status banner, uses the punctuation-free two-line News Desk tagline, repairs the editorial illustration title bounds, and reduces the shared footer to one concise author attribution plus a minimal copyright line. None of these changes alters inference or deployment configuration.

The maintenance release retained the existing `reliable_probability` and `misleading_probability` machine-readable fields and did not change the model, calibration, dataset, threshold, class semantics, locked metrics, summariser, privacy boundary, or export availability.

## Phase 5T verified code and live smoke

- Protected maintenance [PR #47](https://github.com/DevenGaikwad/NewsLens-AI/pull/47): head `6d2ac240491a7ac6cf0b7d838f065865242254c6`; squash merge `d9291605ac9813982837dcb5fade645035795a34`; tree `c9db63a911d6c34cbecd0935336866a6280bde88`.
- Exact-new-main [CI 36293926319](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36293926319) and [CodeQL 36293926442](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36293926442): passed.
- Public startup, six pages, supported agreement and contradiction, unsupported scope abstention without a directional percentage, short-input validation, private-session archive isolation, and JSON/PDF/CSV controls: passed on 27 September 2026. Two newly downloaded A4 PDFs were rasterized and visually inspected with PyMuPDF; their two probability rows were separated and correctly paired with the values. Application-origin console errors: zero. Desktop width 1363 CSS pixels: no horizontal overflow. The retained five-width audit supplies mobile evidence.
- Security-relevant [PR #42](https://github.com/DevenGaikwad/NewsLens-AI/pull/42) advanced `pypdf` from 6.16.1 to the patched 6.19.0. It changed only `requirements-lite.txt`; 165 Python tests passed with the new version, followed by exact-new-main [CI 36296310448](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36296310448) and [CodeQL 36296310449](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36296310449). Its merge is `0e58189b8cbfd92126e5f4268bff320bdeb25bd1`, tree `b59b7ccb51a3177ec5044280a66cf7201ee8cfaf`.
- Seven optional or unsuitable older dependency PRs were closed with individual explanations. The public open-PR list returned zero. Repository-specific security and Dependabot alert counts could not be read (HTTP 401); no zero-alert claim is made.

The public interface demonstrates the Phase 5T code changes, but its public page does not expose the exact deployed Git commit. The deployment dashboard requires sign-in in this browser. The exact current deployment revision remains a separate verification item; the prior Phase 5S deployed revision above is historical.
