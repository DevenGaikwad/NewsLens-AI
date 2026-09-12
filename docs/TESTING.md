# Testing summary

## Automated checks

The current public Python 3.12 suite reports:

```text
144 passed, 4 deselected
```

The model-independent tests cover preprocessing, short/long summarisation, prediction contracts using test fixtures, abstention, explanation shape, redirect-safe SSRF validation, DNS/peer and response-size controls, mocked URL extraction, upload-name/TXT/PDF parsing, SQLite CRUD and duplicate handling, session-path isolation, human review, analytics, drift readiness, formula-safe CSV and escaped PDF exports, attribution/release policy, all Streamlit scripts and editorial UI contracts. Four tests marked `private_model` require the excluded classifier/calibration artifacts: packaged-model loading, calibration quality, model-bound diagnostics, and the validation-selected review threshold. They are intentionally deselected, not claimed as passing public checks.

Run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-lite.txt
python -m pytest -q --strict-markers -m "not private_model"
```

## Streamlit browser audit

`scripts/browser_release_audit.py` verifies:

- all six sections render;
- native internal links keep one browser tab;
- direct routes, refresh and browser back/forward;
- keyboard focus and Enter activation;
- text analysis, summary, classification, confidence and explanation;
- JSON, PDF and archive CSV downloads;
- a second browser context cannot view the first context's archive;
- no horizontal overflow at 360, 390, 768, 1366 and 1920 pixels.

The retained private-release Streamlit 1.59.2 Chromium run passed all functional assertions at 360, 390, 768, 1366 and 1920 pixels. It recorded 32 route-relative 404 responses for Streamlit's nested `/_stcore/health` and `/_stcore/host-config` probes and zero unexpected console or network failures. This is historical browser evidence, not a fresh current-main private-runtime test. Production-origin console and platform-log verification remains required after deployment.

## Presentation website audit

`scripts/browser_web_audit.py` verifies the five required widths, mobile menu, no horizontal overflow, same-tab `/app` navigation, iframe title, loading/fallback structure, `?embed=true`, console output, response security headers, iframe sandbox and all required design tokens. Current-source `npm ci`, `npm run lint` (TypeScript checking), and `npm run build` pass in GitHub Actions and the Phase 4Z disposable validation environment. The production build generates `/`, `/app`, and the not-found route. The repository's browser record remains dated 16 August 2026; build success does not replace a production-origin browser and iframe-integration check using the approved Streamlit URL before deployment.

## Evidence boundaries

The public-release scan currently covers 248 tracked files with zero forbidden-file, secret, personal-data, local-path, broken-local-link or navigation findings. It reports two intentional publication gates for the private model and calibration. CodeQL analyzes Python and JavaScript/TypeScript; dependency review runs on pull requests with `fail-on-severity: high` and intentionally skips push events. Successful workflow runs do not by themselves prove that repository-wide alert collections are empty or that every dependency-graph manifest is current.

Dated release audits and packaged DOCX/PDF documents retain their original environment and benchmark evidence. They are historical records; use the current manifests and lockfile for installation. The public repository cannot freshly rerun private-model tests, benchmark evaluation, or private-runtime browser checks without the owner's excluded artifacts and the applicable redistribution approval.

## Manual acceptance

Inspect current screenshots for cropped text, controls, charts or arrows. Test Paste text, Public URL and TXT/PDF upload paths; the deterministic suite mocks remote HTML rather than depending on a mutable news website. Confirm that confidence is described as model certainty and that no page claims to prove truth.
