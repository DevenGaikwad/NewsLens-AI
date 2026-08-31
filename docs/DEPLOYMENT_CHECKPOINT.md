# NewsLens AI deployment checkpoint

Checkpoint updated: 1 September 2026, 00:52 IST  
Authoritative public repository: `https://github.com/DevenGaikwad/NewsLens-AI`  
Owner: Deven Sachin Gaikwad  
State: **public GitHub publication verified; functional deployment gated**

## Confirmed release decisions

- NewsLens AI is the sole product name.
- Streamlit remains the functional application, with `app.py` as its runtime entry point.
- The Next.js application under `web/` is a presentation shell only.
- The canonical public repository is `DevenGaikwad/NewsLens-AI` on branch `main`.
- The owner confirmed sole ownership of the original NewsLens AI components. Original material uses the repository's proprietary All Rights Reserved notice; third-party rights are not relabelled.
- Runtime inference loads `isot-tfidf-lr-v1.0.0` privately and never invokes training code.
- The public repository intentionally excludes the classifier and private calibration parameters.

## GitHub publication checkpoint

| Item | Verified result |
|---|---|
| Repository | `https://github.com/DevenGaikwad/NewsLens-AI` |
| Owner / visibility | `DevenGaikwad` / public |
| Default branch | `main` |
| Publication baseline | `30470c6767352c02db9aa0484f97f5473304f845` |
| Verified CI correction | `8694b0ec86331a1be7d56a84f94ef270383bbfa6` |
| Public tracked files | 247 |
| README local images | 6 of 6 resolve and return PNG content |
| README local documentation links | 31 of 31 resolve |
| Private artifacts | Model and calibration absent |
| Raw ISOT data | Absent; packaged demonstration articles remain intentionally public |
| History review through the verified CI commit | No historical-only prohibited paths or secret-bearing blobs |

The publication baseline contains the verified model-excluded release. The focused CI commit changes only the workflow, scanner semantics, marker declarations, affected test markers, and checksum manifest. A later documentation-only checkpoint commit may advance `main` without changing that verified source behavior.

## Current verification

| Check | Current result |
|---|---|
| Private packaged pytest suite | 56 passed in the preserved private validation environment; 0 failed, 0 errors, 0 skipped |
| Public GitHub Python suite | 52 model-independent tests passed; 4 private-artifact tests explicitly deselected |
| Python source compilation | Passed in GitHub Actions |
| Public committed-tree scan | 247 files; 0 forbidden files, secrets, personal-data findings, local paths, broken local Markdown links, or internal new-tab findings |
| Prohibited-fixture validation | A committed `.env` and private calibration artifact each produced hard failure exit code `3` |
| CodeQL | Python and JavaScript/TypeScript analyses passed |
| Next.js dependency installation | `npm ci` passed in GitHub Actions |
| Next.js lint | Passed in GitHub Actions |
| Next.js production build | Passed in GitHub Actions |
| Dependabot proposals | 13 open and unmerged; 12 presentation builds pass, while PR 12 has a genuine React/ReactDOM peer conflict |
| Commit email privacy | Owner-created commits expose a personal Gmail address; no history rewrite was performed |
| Streamlit Chromium audit | Six areas, same-tab routes, direct routes, refresh, back/forward, keyboard use, analysis, confidence, explanation, review, downloads, analytics, drift, and visitor isolation passed in the retained private release audit |
| Responsive Streamlit widths | 360, 390, 768, 1366, and 1920 pixels; no horizontal overflow in the retained audit |
| Documentation | 4 DOCX files, 170 rendered pages, and 0 high/medium/low accessibility findings in the retained release evidence |
| Current interface screenshots | 15 captures, all visually reviewed and SHA-256 indexed |

The private model SHA-256 remains:

`e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb`

This hash is recorded for private integrity verification only. The corresponding artifact is not present in public Git history.

## CI semantics

The public workflow fails closed if either private artifact is committed. It compiles the Python source, runs all model-independent tests, and explicitly reports that four classifier/calibration tests require the owner's private local artifacts. The committed-tree scanner uses `git ls-files`, so GitHub runner metadata under `.git/` is not misclassified as published content. Archive-mode scanning remains strict, and actual safety violations use a hard-failure exit code distinct from a documented publication gate.

## Presentation-shell checkpoint

The source under `web/` contains the required landing page, methodology and responsible-use content, public-document links, GitHub link, responsive mobile menu, exact editorial tokens, and `/app` iframe contract using `NEXT_PUBLIC_STREAMLIT_APP_URL` plus `?embed=true`.

Current-source dependency installation, lint, and production build now pass in GitHub Actions. The retained browser evidence remains dated 16 August 2026; production-origin browser, console, and platform-log verification must occur only after an approved Streamlit URL exists and Vercel deployment is separately authorised.

## Hosting identifiers

| Identifier | Value |
|---|---|
| GitHub account | `DevenGaikwad` |
| Public repository | `https://github.com/DevenGaikwad/NewsLens-AI` — published and verified |
| Branch | `main` |
| Streamlit entry point | `app.py` |
| Streamlit production URL | Not deployed or verified |
| Vercel project root | `web/` |
| Public Vercel variable | `NEXT_PUBLIC_STREAMLIT_APP_URL` |
| Vercel production URL | Not deployed or verified |

## Remaining gates

1. Documentary permission or explicit applicable licence terms for redistribution and public hosting of the ISOT-derived model and matching calibration parameters have not been supplied.
2. Functional Streamlit hosting cannot preserve the specified classifier from the model-excluded public tree.
3. Vercel requires a final verified Streamlit URL and separate deployment authorisation.
4. Production-origin browser, privacy, console, and platform-log checks remain unavailable until deployment is authorised and completed.

## Exact next safe action

Obtain documentary model-redistribution permission or an applicable licence before committing or hosting the model or calibration artifacts. Do not deploy Streamlit or Vercel, substitute another classifier, retrain during startup, or claim a live ML deployment before that evidence is recorded.
