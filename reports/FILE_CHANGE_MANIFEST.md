# NewsLens AI file-change manifest

Comparison basis: byte-for-byte relative-file comparison with the authoritative extracted `NewsLens_AI/` package supplied for this release. Generated caches and local dependency/build directories are excluded.

Current delta: **112 added files, 73 modified files, and 6 removed screenshot files**.

No application area, runtime capability, model byte, or training/runtime boundary was removed. The six removed filenames belonged to the ten-capture screenshot naming scheme; the release contains the required 15 current captures under the documented taxonomy.

## Change groups

| Area | Release work |
|---|---|
| Product integrity | Preserved Streamlit, `app.py`, six product areas, packaged model identity, summarization, classification, calibration, explainability, history, analytics, drift readiness, and exports |
| Navigation | Centralised native `st.Page`/`st.navigation` routing and removed internal new-tab mechanisms |
| Privacy and security | Added visitor-scoped temporary SQLite history, URL/redirect/peer controls, upload/PDF limits, export neutralisation, and release scanners |
| Model accountability | Added leakage-controlled private benchmarking, held-out Platt calibration, validation-policy abstention, final-test evidence, and hash-only error analysis |
| Presentation website | Added the lightweight Next.js shell, origin validation, security headers, responsive navigation, and Streamlit iframe route |
| Documentation | Reconciled and privacy-scrubbed four DOCX publications, created the project-report PDF, audited citations, and recorded full visual QA |
| Verification | Expanded the suite to 56 checks while retaining all 29 established checks; added browser, accessibility, privacy, dependency, and public-release evidence |
| Publication controls | Added proprietary ownership records and kept the model/calibration artifacts outside public staging pending documentary redistribution evidence |

## Notable added files

- Public repository governance: `.github/`, `CONTRIBUTING.md`, `SECURITY.md`, `CITATION.cff`, `AUTHORS.md`, `COPYRIGHT.md`, `LICENSE`, and `NOTICE.md`
- Release and deployment records: `PUBLIC_DEPLOYMENT_BLOCKED.md`, `release_manifest.json`, `docs/DEPLOYMENT_CHECKPOINT.md`, `docs/PUBLIC_RELEASE_AUDIT.md`, and this report set
- Model-accountability artifacts: `training/benchmark_models.py`, `models/confidence_calibration.json`, `reports/model_benchmark_*`, `reports/calibration_validation.json`, and `reports/model_reference_profile.json`
- Privacy/review/analytics modules: `src/session_history.py`, `src/editorial_review.py`, `src/newsroom_analytics.py`, and `src/model_diagnostics.py`
- Verification: `tests/test_placement_enhancements.py`, `tests/test_release_policy.py`, `scripts/audit_public_release.py`, `scripts/browser_release_audit.py`, and `scripts/browser_web_audit.py`
- Presentation shell: the complete `web/` application and its lockfile
- Public documentation: architecture, privacy, licensing, redistribution, citation-audit, visual-QA, case-study, and placement-interview records
- Public visuals: six GitHub presentation assets, 15 current interface screenshots, current model/accountability figures, and five-width browser evidence

## Principal modified areas

- `app.py`, `pages/`, `ui/`, and `src/` for native routing, calibrated outcomes, review, analytics, privacy isolation, security, and accessibility
- `requirements-lite.txt` and `requirements.txt` for the tested Python 3.12 dependency profile
- `models/model_metadata.json` and the aggregate benchmark evidence for the final partition/selection/calibration protocol
- all four DOCX publications and the three-sheet research matrix
- `README.md`, deployment guides, model/dataset cards, UI specification, and public-use statements
- test, screenshot, accessibility, dependency, and verification evidence under `reports/results/`

## Removed screenshot filenames

- `reports/screenshots/05_model_performance.png`
- `reports/screenshots/06_dataset_eda.png`
- `reports/screenshots/07_analysis_history.png`
- `reports/screenshots/08_research_about.png`
- `reports/screenshots/09_home_mobile.png`
- `reports/screenshots/10_analysis_mobile.png`

The current capture set is `reports/screenshots/01_home.png` through `15_analysis_mobile.png`, with the exact ordered filenames and SHA-256 values recorded in `reports/results/ui_screenshot_manifest.json`.

## Reproducibility note

The comparison includes both source and generated public evidence. Re-run the project's tests, browser captures, document reconciliation, and verification scripts before comparing an independently regenerated tree because timestamps, rendered images, benchmark latency, and Office package bytes can differ across environments.
