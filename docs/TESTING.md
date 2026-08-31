# Testing summary

## Automated checks

The tested Python 3.12 environment reports:

```text
56 passed in 5.90s
```

The 56 checks include all 29 established checks plus 27 hardening checks. Coverage includes preprocessing, short/long summarisation, packaged model loading without fitting, calibrated prediction semantics, abstention, explanation shape, redirect-safe SSRF validation, DNS/peer and response-size controls, mocked URL extraction, upload-name/TXT/PDF parsing, SQLite CRUD and duplicate handling, session-path isolation, human review, analytics, drift readiness, formula-safe CSV and escaped PDF exports, attribution/release policy, all Streamlit scripts and editorial UI contracts.

Run:

```bash
python -m pytest -q
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

The current Streamlit 1.59.2 Chromium run passed all functional assertions at 360, 390, 768, 1366 and 1920 pixels. It recorded 32 route-relative 404 responses for Streamlit's nested `/_stcore/health` and `/_stcore/host-config` probes and zero unexpected console or network failures. Functional navigation and rendering passed; production-origin console and platform-log verification remains required after deployment.

## Presentation website audit

`scripts/browser_web_audit.py` verifies the five required widths, mobile menu, no horizontal overflow, same-tab `/app` navigation, iframe title, loading/fallback structure, `?embed=true`, console output, response security headers, iframe sandbox and all required design tokens. The repository retains a dated 16 August 2026 browser/build record for the presentation shell. Because this workspace could not download the lockfile-pinned packages, the current source must still pass `npm ci`, `npm run lint`, `npm run build`, the unsafe-origin rejection check, and `scripts/browser_web_audit.py` in a package-network-enabled environment before deployment.

## Manual acceptance

Inspect current screenshots for cropped text, controls, charts or arrows. Test Paste text, Public URL and TXT/PDF upload paths; the deterministic suite mocks remote HTML rather than depending on a mutable news website. Confirm that confidence is described as model certainty and that no page claims to prove truth.
