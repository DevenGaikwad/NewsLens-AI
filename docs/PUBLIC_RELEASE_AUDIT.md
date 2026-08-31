# Public-release and deployment audit

Audit updated: 1 September 2026 (IST)  
Status: **public GitHub publication verified; functional hosting gated**

## Verified GitHub publication

- Canonical repository: `https://github.com/DevenGaikwad/NewsLens-AI`.
- Owner: `DevenGaikwad`; visibility: public; default branch: `main`.
- Model-excluded publication baseline: `30470c6767352c02db9aa0484f97f5473304f845`.
- Verified CI-semantics commit: `8694b0ec86331a1be7d56a84f94ef270383bbfa6`.
- The public tree contains 247 tracked files.
- `models/` contains only `README.md` and `model_metadata.json`.
- The private classifier, private calibration, raw ISOT data, release ZIPs, runtime databases, credentials, caches, and user history are absent.
- The complete Git history through the verified CI commit contains no historical-only prohibited path or secret-bearing blob.
- All six README-local PNG images load, and all 31 local README documentation links resolve.
- `CITATION.cff`, All Rights Reserved ownership language, author records, notices, and third-party attribution files remain present.

## Current GitHub checks

| Check | Result |
|---|---|
| Python source compilation | Passed |
| Model-independent pytest selection | 52 passed |
| Private-artifact pytest selection | 4 explicitly deselected and reported as requiring owner-private artifacts |
| Public committed-tree scan | Passed; 247 files and zero safety findings |
| Deliberate prohibited fixtures | Committed `.env` and private calibration fixtures each returned hard failure exit code `3` |
| Next.js dependency installation | `npm ci` passed |
| Next.js lint | Passed |
| Next.js production build | Passed |
| CodeQL Python | Passed |
| CodeQL JavaScript/TypeScript | Passed |
| Dependency review | Correctly skipped on the direct `main` push; configured for pull requests |
| Dependabot pull requests | 13 open; 0 merged or closed by this audit |

The public workflow does not use `continue-on-error`. It fails if a private model or calibration artifact is committed, and it preserves the existing secret, personal-data, forbidden-file, navigation, legal-file, and link checks. The scanner's tracked-file mode excludes GitHub runner metadata under `.git/` because that metadata is not repository content; archive-mode scanning remains strict.

## Dependabot review

The 13 proposals remain open and unmerged. Six are major-version proposals (`transformers`, TypeScript, `@types/node`, `actions/checkout`, `actions/setup-node`, and `actions/dependency-review-action`); three are minor or lower-bound changes (`trafilatura`, `matplotlib`, and `torch`); and four are patch or mixed compatible-line proposals (`sentencepiece`, React, Next.js, and the combined ReactDOM/types update).

All proposal commits passed CodeQL. Twelve passed the presentation build. Pull request 12 fails `npm ci` because it proposes ReactDOM 19.2.8 while leaving React at 19.2.4, which does not satisfy ReactDOM's peer requirement. The common Python and public-scan failures were produced by the original pre-correction workflow and therefore do not demonstrate dependency incompatibility. Dependency review is unavailable because GitHub's dependency graph is not enabled for this repository. No proposal was merged, closed, rebased, or modified during this audit.

## Commit-metadata privacy note

The four owner-created `main` commits expose a personal Gmail author/committer address in public Git metadata. Dependabot commits use GitHub noreply addresses. History was not rewritten or force-pushed. For future commits, the owner should enable GitHub's private noreply email and configure Git/GitHub Desktop to use it.

## Preserved private-release evidence

- The authoritative package remains a Streamlit application with `app.py` as its runtime entry point.
- All six product areas use native same-tab Streamlit navigation.
- The preserved private suite has 56 passing checks, including classifier loading, calibrated inference, and model-bound diagnostics.
- The retained Chromium audit covers the five required widths, analysis, summarisation, classification, calibrated confidence, explainability, review, exports, analytics, drift readiness, and cross-visitor isolation.
- Fifteen current interface screenshots are visually reviewed and SHA-256 indexed.
- Four privacy-scrubbed DOCX publications render to 170 pages in total with zero accessibility findings.
- The private model integrity hash remains `e9dd8368a4eec1ea5111da6c002889a146af98acba06742d2795486977d93dcb`.

These private-runtime results are not falsely represented as executable public CI results because the public repository intentionally excludes the classifier and calibration.

## Presentation-shell status

The exact committed `web/` source now passes dependency installation, lint, and production build in GitHub Actions. The retained browser evidence remains dated 16 August 2026. Production-origin browser behavior, iframe integration, console output, and platform logs require an approved Streamlit URL and a separately authorised Vercel deployment.

## Remaining publication and deployment gates

1. **Model redistribution rights remain unconfirmed.** The official ISOT materials reviewed for this release do not state an explicit trained-artifact redistribution licence. The model and its dataset-derived calibration remain private and Git-ignored.
2. **Functional Streamlit hosting remains blocked.** The approved classifier cannot run from the model-excluded public tree.
3. **Vercel integration remains blocked.** It requires the final verified Streamlit URL and separate deployment authorisation.
4. **Production verification remains pending.** Deployed browser, privacy, console, and platform-log checks cannot run before deployment.

No Streamlit or Vercel deployment is claimed. The exact next safe action is to obtain documentary model-redistribution permission or an applicable licence before committing or hosting either private artifact.
