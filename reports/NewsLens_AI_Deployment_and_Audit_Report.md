# NewsLens AI deployment and audit report

Audit date: 25 August 2026 (IST)  
Owner and author: Deven Sachin Gaikwad  
Release state: **verified Streamlit release candidate; public functional deployment blocked at documented gates**

## Outcome

The uploaded `NewsLens_AI/` package remains the authoritative implementation. The Streamlit/Python/ML application is intact, `app.py` remains the runtime entry point, all six product areas are preserved, and runtime code never imports or invokes training modules. The separate `web/` directory contains only the optional Next.js/Vercel presentation shell.

The owner confirmed sole ownership of the original NewsLens AI components. The source-visible release uses the repository's proprietary All Rights Reserved notice and preserves third-party attributions without inventing a licence for external datasets, publications, packages, or trained artifacts.

No GitHub repository, Streamlit Community Cloud application, or Vercel project was created or deployed. The intended repository is `DevenGaikwad/NewsLens-AI`, but it does not exist and the connected GitHub application exposes no repository-creation action.

## Current verification results

| Check | Result |
|---|---|
| Packaged pytest suite | 56 passed in 5.90 seconds; 0 failed, 0 errors, 0 skipped in Python 3.12.13 |
| Expected-check continuity | All 29 established checks remain; 27 hardening checks added |
| Python source compilation | 65 files passed |
| Backend integration | Saved-model inference, summarization, calibrated confidence, explanation, SQLite lifecycle, duplicate detection, human review, analytics, drift readiness, JSON, and PDF passed |
| Runtime retraining guard | Passed; runtime entry points do not import `training/` |
| Packaged examples | Lower-risk, higher-risk, and editorial-review outcomes all reproduced |
| Streamlit browser audit | All six routes and acceptance workflows passed at the five required widths |
| Same-tab/navigation checks | Same tab, direct route, refresh, back/forward, focus, and Enter activation passed |
| Visitor privacy | A second browser context could not view the first visitor's archive |
| Unexpected browser failures | 0 console errors and 0 failed responses after preserving 32 known Streamlit nested-route probes separately |
| Python dependency integrity | `pip check` found no broken requirements |
| Public source-tree scan | 249 files; 0 forbidden files, secrets, personal-data patterns, local paths, broken local Markdown links, or internal new-tab mechanisms |

## Model evidence

The packaged model remains unchanged:

- Artifact ID: `isot-tfidf-lr-v1.0.0`
- File size: 819,447 bytes
- SHA-256: `e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb`
- Runtime retraining: disabled

The controlled private evaluation reconstructs a balanced 24,000-row ISOT sample. It uses 19,200 training rows, quarantines two cross-boundary near-duplicate rows, divides 2,399 validation rows into 1,199 calibration and 1,200 validation-policy rows, and reports once on an untouched 2,399-row final test.

| Metric | Logistic Regression result |
|---|---:|
| Accuracy | 0.992080 |
| Macro F1 | 0.992080 |
| ROC-AUC | 0.999481 |
| PR-AUC | 0.999423 |
| Calibrated Brier score | 0.006292 |
| Ten-bin calibrated ECE | 0.005295 |
| Confusion matrix | `[[1196, 4], [15, 1184]]` |

The final-test error analysis contains 19 misclassified rows and publishes only content hashes, labels, probabilities, word counts, and the evidence scope. The final test is not used for fitting, Platt calibration, model retention, or the 0.59 editorial-review threshold.

These values measure agreement with dataset labels, not factual truth. NewsLens AI estimates linguistic credibility risk and does not replace professional fact-checking.

## Browser and responsive evidence

The current Streamlit Chromium run verifies:

- all six product areas;
- direct routes, refresh, browser history, keyboard activation, and same-tab navigation;
- text analysis, summary, risk outcome, calibrated confidence, explanation, and policy text;
- JSON, PDF, archive CSV, and privacy-safe analytics CSV downloads;
- human editorial review, newsroom analytics, and drift readiness;
- visitor-isolated archive history; and
- no horizontal overflow at 360, 390, 768, 1366, or 1920 pixels.

Thirty-two 404 responses are retained for route-relative Streamlit `/_stcore/health` and `/_stcore/host-config` probes. All are classified as known development-server probes; there are zero unexpected console/network findings. Deployment-origin console and platform logs still require verification.

## Presentation-shell status

The `web/` source implements the approved beige/brown editorial identity, responsive navigation, responsible-use language, documentation and GitHub links, and the `/app` iframe using `NEXT_PUBLIC_STREAMLIT_APP_URL` plus `?embed=true`. Static Python tests cover its URL policy, CSP headers, iframe sandbox, design tokens, and non-duplication of the ML application.

The retained 16 August 2026 web-browser record shows all five widths, 44-pixel targets, mobile menu, same-tab fallback, security headers, and zero console errors. Content and styling changed after that record. This workspace could not download the lockfile-pinned npm dependencies, so the current source has not been rerun through `npm ci`, TypeScript, production build, unsafe-origin rejection, or the browser audit. Those checks are mandatory before Vercel deployment.

## Security and privacy controls

- URL extraction accepts only public HTTP(S), revalidates redirects and connected peers, disables environment proxies, rejects private/reserved targets, and caps redirects and response size.
- TXT/PDF uploads reject traversal-style names, unsupported or encrypted files, over-limit payloads, excess pages, and excess extracted text.
- CSV exports neutralise spreadsheet formulas; PDF values are escaped.
- Public history uses a visitor-scoped temporary SQLite file and makes no durable cloud-history promise.
- `.env`, Streamlit secrets, caches, logs, uploads, activity databases, raw datasets, build output, model bytes, and calibration parameters are excluded from public Git as applicable.

## Documentation, citations, and visual QA

| Publication | Rendered scope | Result |
|---|---:|---|
| Final project report | 77 pages | Full visual review passed; accessibility 0 high/medium/low |
| Setup and run guide | 14 pages | Full visual review passed; accessibility 0 high/medium/low |
| Code explanation and developer guide | 18 pages | Full visual review passed; accessibility 0 high/medium/low |
| Concepts, methodologies, and terminology guide | 61 pages | Full visual review passed; accessibility 0 high/medium/low |
| Research paper matrix | 3 sheets | 17 formulas, 0 formula errors, no observed clipping |
| Streamlit screenshots | 15 images | Current interface, visually reviewed and SHA-256 indexed |

The 77-page project-report PDF is tagged, unencrypted, contains no JavaScript, and reopened successfully with Poppler and pypdf. The citation audit cross-checked all ten DOI records and the official project sources. The official XSum repository is used as the primary dataset citation.

## Model and dataset publication decision

The reviewed University of Victoria ISOT page and linked description PDF provide a dataset description, download, and citation guidance. No explicit trained-artifact redistribution licence was located. That absence does not establish permission to redistribute or publicly host the model; this is a release-engineering risk decision, not legal advice.

The public package therefore excludes:

- `models/fake_news_pipeline.joblib`; and
- `models/confidence_calibration.json`.

The complete private/local package retains both for the owner's local review. Functional public deployment remains blocked because the user prohibited replacing, mocking, simplifying, or retraining the established pipeline.

Official references:

- [University of Victoria ISOT dataset page](https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/)
- [Official ISOT dataset-description PDF](https://onlineacademiccommunity.uvic.ca/isot/wp-content/uploads/sites/7295/2023/02/ISOT_Fake_News_Dataset_ReadMe.pdf)

## Deployment state and remaining gates

| Destination | State |
|---|---|
| Public GitHub repository | Intended `DevenGaikwad/NewsLens-AI`; repository absent; no connector creation action |
| Canonical Git history | Unavailable; history-wide scan not possible |
| Streamlit Community Cloud | Not deployed; model redistribution gate unresolved |
| Vercel | Not deployed; current web build and final Streamlit URL pending |

Required next actions:

1. Create an empty public `DevenGaikwad/NewsLens-AI` repository without initializing a README, licence, or `.gitignore`.
2. Provide documentary redistribution permission or explicit applicable licence terms before the model or calibration artifact is committed or hosted.
3. Push only the model-excluded public package, inspect the resulting Git history, and complete GitHub security checks.
4. Run the current Next.js install/type/build/unsafe-origin/browser gates in a package-network-enabled environment.
5. After the model gate clears, deploy Streamlit first, verify logs and cross-visitor isolation, deploy Vercel, and update README links with real production URLs.

No production success is claimed at this checkpoint.
