# NewsLens AI deployment checkpoint

Checkpoint updated: 25 August 2026, 04:13 IST  
Authoritative source root: `NewsLens-AI/`  
Owner: Deven Sachin Gaikwad  
State: **Streamlit release candidate verified locally; public publication and deployment gated**

## Confirmed release decisions

- NewsLens AI is the sole product name.
- Streamlit remains the functional application, with `app.py` as its runtime entry point.
- The Next.js application under `web/` is a presentation shell only.
- The public repository target is `DevenGaikwad/NewsLens-AI` on branch `main`.
- The owner confirmed sole ownership of the original NewsLens AI components. Original material uses the repository's proprietary All Rights Reserved notice; third-party rights are not relabelled.
- Runtime inference loads `isot-tfidf-lr-v1.0.0` and never invokes training code.

## Current verification

| Check | Current result |
|---|---|
| Packaged pytest suite | 56 passed in 5.90 seconds; 0 failed, 0 errors, 0 skipped |
| Established checks | All 29 remain included; 27 hardening checks added |
| Python source verification | 65 files compiled; backend, model evidence, branding, release language, documents, and screenshots passed |
| Packaged sample evaluation | Required lower-risk, higher-risk, and editorial-review outcomes all produced |
| Streamlit Chromium audit | Six areas, same-tab routes, direct routes, refresh, back/forward, keyboard use, analysis, confidence, explanation, review, downloads, analytics, drift, and visitor isolation passed |
| Responsive Streamlit widths | 360, 390, 768, 1366, and 1920 pixels; no horizontal overflow |
| Unexpected browser failures | 0 console errors and 0 failed responses after separating 32 known Streamlit nested-route probes |
| Python dependency integrity | `pip check`: no broken requirements |
| Public source-tree scan | 249 files; 0 forbidden files, secrets, personal-data findings, local paths, broken local Markdown links, or internal new-tab findings |
| Documentation | 4 DOCX files, 170 rendered pages, 0 high/medium/low accessibility findings |
| Project-report PDF | 77 pages; reopened successfully; tagged, unencrypted, no JavaScript |
| Research workbook | 3 rendered sheets, 17 valid formulas, 0 formula errors |
| Current interface screenshots | 15 captures, all visually reviewed and SHA-256 indexed |

The model SHA-256 remains:

`e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb`

## Presentation-shell checkpoint

The source under `web/` contains the required landing page, methodology and responsible-use content, public-document links, GitHub link, responsive mobile menu, exact editorial tokens, and `/app` iframe contract using `NEXT_PUBLIC_STREAMLIT_APP_URL` plus `?embed=true`.

A dated 16 August 2026 build/browser record is retained. Current-source npm installation, TypeScript, production build, unsafe-origin rejection, and browser checks were not rerun because this workspace cannot access the package registry and has no complete local dependency cache. These gates must run in a package-network-enabled environment before Vercel deployment.

## Hosting identifiers

| Identifier | Value |
|---|---|
| GitHub account | `DevenGaikwad` |
| Intended repository | `https://github.com/DevenGaikwad/NewsLens-AI` — absent at this checkpoint |
| Branch | `main` |
| Streamlit entry point | `app.py` |
| Streamlit production URL | Not deployed or verified |
| Vercel project root | `web/` |
| Public Vercel variable | `NEXT_PUBLIC_STREAMLIT_APP_URL` |
| Vercel production URL | Not deployed or verified |
| Canonical commit SHA | Unavailable because the repository does not exist |

## Blocking gates

1. The GitHub connector can inspect and modify existing repositories but cannot create a repository. `DevenGaikwad/NewsLens-AI` must be created as an empty public repository before the source package can be pushed.
2. Documentary permission or explicit applicable licence terms for redistribution and public hosting of the ISOT-derived model and matching calibration parameters have not been supplied.
3. The canonical Git history cannot be scanned until the repository exists.
4. Functional Streamlit hosting cannot preserve the specified classifier from the model-excluded public tree.
5. Vercel requires both the current-source presentation checks and a final verified Streamlit URL.

## Exact next safe actions

1. Create an empty public repository named `NewsLens-AI` under `DevenGaikwad`, without initializing a README, licence, or `.gitignore`.
2. Provide documentary model-redistribution evidence before committing the model or performing functional public deployment.
3. Push only the model-excluded public package, inspect the resulting Git history, and run GitHub security checks.
4. After the model gate clears, deploy Streamlit from `main`/`app.py`, verify cross-visitor isolation and logs, run the current Next.js gates, then deploy Vercel and update only real live links.

Do not request credentials in chat, publish the private model, retrain or replace the ML pipeline, or claim deployment success before these gates are resolved.
