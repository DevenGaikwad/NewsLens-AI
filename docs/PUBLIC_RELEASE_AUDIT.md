# Public-release and deployment audit

Audit date: 25 August 2026 (IST)  
Status: **protected publication staging; public push and functional hosting gated**

## Verified in the current source tree

- The authoritative package remains a Streamlit application with `app.py` as the runtime entry point.
- All six product areas render through native same-tab Streamlit navigation.
- The 56 packaged checks, including all 29 established checks, passed in Python 3.12.13 with zero failures, errors, or skips.
- Project verification compiled 65 Python files and passed backend, model-evidence, branding, document-media, release-language, and screenshot-integrity checks.
- The current Chromium audit passed direct routes, refresh, back/forward, keyboard activation, same-tab navigation, article analysis, summarization, classification, calibrated confidence, explainability, human review, downloads, analytics, drift readiness, and cross-visitor archive isolation.
- Streamlit showed no horizontal page overflow at 360, 390, 768, 1366, or 1920 pixels.
- All 15 current beige/brown interface screenshots were recaptured, visually inspected, and SHA-256 indexed.
- Public history defaults to temporary per-session SQLite. A second browser context could not view the first context's record.
- Runtime entry points do not import `training/`; the application loads the packaged model and never retrains it.
- The model remains byte-for-byte unchanged at SHA-256 `e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb`.
- The controlled private benchmark uses separate calibration, validation-policy, and untouched final-test partitions. The final-test error record now contains the 19 current misclassifications as hashes and aggregate fields only.
- `pip check` reports no broken requirements. The dated 24 August dependency audit records zero known vulnerabilities for the pinned Python environment and Next.js lockfile; the matching requirement and lockfile hashes are preserved in its evidence file.
- Four privacy-scrubbed DOCX publications rendered to 170 pages in total and returned zero high, medium, or low accessibility findings. The 77-page project-report PDF reopened successfully and matches the final DOCX render.
- The three-sheet research workbook has 17 valid formulas, zero formula errors, and no observed clipping in its rendered sheets.
- The current source-tree scanner examined 249 files and found zero forbidden files, secrets, personal-data patterns, absolute local paths, broken local Markdown links, or internal new-tab mechanisms.

## Browser-console interpretation

The Streamlit audit recorded 32 route-relative 404 responses for nested `/_stcore/health` and `/_stcore/host-config` probes. They are retained as known Streamlit development-server route probes. The audit recorded zero unexpected console errors and zero unexpected failed responses, and every route and workflow assertion passed. Production-origin console output and platform logs must still be checked after deployment.

## Presentation-shell verification limit

The repository retains a 16 August 2026 Next.js browser/build record showing the required five widths, 44-pixel targets, mobile menu, same-tab `/app` navigation, accessible iframe title, `?embed=true`, restricted iframe sandbox, security headers, exact design tokens, and zero console errors. The current `web/` source has since received content and styling changes.

This workspace could not download the lockfile-pinned npm packages because package-registry access is restricted. Therefore, the current source has not been revalidated with `npm ci`, TypeScript, a production build, the unsafe-origin rejection build, or the current browser audit. Those checks remain mandatory in a package-network-enabled environment; the dated evidence is not represented as a current-source build result.

## Evidence

- `reports/results/pytest_results.xml`
- `reports/results/project_verification.json`
- `reports/release_audit/streamlit/streamlit_browser_audit.json`
- `reports/results/ui_screenshot_manifest.json`
- `reports/results/public_release_scan.json`
- `reports/results/dependency_security_audit.json`
- `docs/NewsLens_AI_Project_Report_Visual_QA.md`
- `docs/NewsLens_AI_Final_Citation_Audit.md`

## Publication gates

1. **Canonical target not created.** The connected account is `DevenGaikwad`, and `DevenGaikwad/NewsLens-AI` does not exist. The available GitHub connector does not expose repository creation.
2. **Model redistribution rights unconfirmed.** The reviewed official ISOT page and dataset-description PDF provide description, download, and citation guidance but no explicit trained-artifact redistribution licence. The model and its dataset-derived calibration parameters remain private, Git-ignored, and excluded from public archives.
3. **Canonical Git history unavailable.** No public repository exists, so a history-wide secrets and runtime-data scan cannot yet be performed.
4. **Live URLs unavailable.** Streamlit and Vercel have not been deployed, so README links, production console output, and platform logs cannot be verified.
5. **Current presentation build pending.** The current `web/` source needs the package-network-enabled checks listed above.

Functional public deployment must stop until the repository and model-rights gates are cleared. Afterward, scan the genuine Git history, run the current Next.js gates, deploy Streamlit first, set only the public Streamlit origin in `NEXT_PUBLIC_STREAMLIT_APP_URL`, deploy Vercel, repeat the deployed browser/privacy/log checks, and update README links with real URLs.
