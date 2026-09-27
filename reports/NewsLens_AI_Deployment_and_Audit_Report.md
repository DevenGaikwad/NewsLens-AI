# NewsLens AI Phase 5S Deployment and Audit Report

Updated: 27 September 2026

Release state: **complete and publicly deployed**

## Dataset release (PR A)

- PR: [#44](https://github.com/DevenGaikwad/NewsLens-AI/pull/44)
- Owner upload commit: `e6031fa6ec193131be5fed4704722125104b066f`
- Follow-up head: `326499bb6f58f0420a0cf36a00828a901836323d`
- Squash merge: `d3e77e6610c4a9c83d9137ca672a9aad4278285f`
- Resulting tree: `520bad55ea12f1a8e48ad2e533af26312c62933d`
- Signature: GitHub verified
- Merge time: `2026-09-25T12:14:59Z`
- Required PR and exact-new-main checks: passed

## Dataset identity and provenance

- Path: `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`
- Size: 10,319,934 bytes
- SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`
- Git blob: `cb0d5e57407be10fecefb34762e586bacd38dd56`
- License: CC BY 4.0 to the extent applicable rights subsist
- Generator and corpus: deterministic, independently authored, fictional articles and entities
- Article / paired-event count: 24,000 / 12,000

## Model and calibration evidence

- Model: `models/newslens_synthetic_pipeline.joblib`
- Model size / SHA-256: 161,709 bytes / `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`
- Calibration: `models/newslens_synthetic_calibration.json`
- Calibration size / SHA-256: 728 bytes / `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`
- Metadata SHA-256: `6d868465dfc8e038343a179659e23c5015c10900d8b74fec6b62b80ebf5e1a73`
- Binding: the calibration and public manifest record the exact model SHA-256
- Training / validation / calibration / policy / test rows: 18,000 / 2,400 / 1,200 / 1,200 / 1,200
- Cross-partition event/content overlap: 0 / 0
- Locked accuracy / balanced accuracy / precision / recall / macro F1: 1.0 / 1.0 / 1.0 / 1.0 / 1.0
- Confusion matrix: `[[600, 0], [0, 600]]`
- Brier / ECE: 0.0000014968608529442928 / 0.0007422494250466733
- Coverage at threshold 0.50: 100%
- Counterfactual flip rate: 100%
- Surface-only / fact-block ablation / metadata balanced accuracy: 0.500 / 0.498333 / 0.520833

## Model release (PR B)

- PR: [#45](https://github.com/DevenGaikwad/NewsLens-AI/pull/45)
- Validated head: `56f6e3e7137bd03fe45a0cd3e88978588968cdd1`
- Squash merge: `214b22745736b25f4c1121822a1811c76687bb00`
- Resulting tree: `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- Signature: GitHub verified
- Sole parent: `d3e77e6610c4a9c83d9137ca672a9aad4278285f`
- Merge time: `2026-09-26T03:18:37Z`
- Changed files: 192
- PR checks: complete Python suite, public-release scan, presentation build, dependency review, and both CodeQL analyses passed.
- Exact-new-main CI run `36214408496`: passed.
- Exact-new-main CodeQL run `36214408382`: passed.

## Validation summary

- Complete Python suite: 154 passed; 0 failures, errors, or skips.
- Focused integration suite: 33 passed.
- Python compile, dependency consistency, pip audit, npm install/lint/build, npm audit, reproducibility, and artifact identity gates: passed.
- Four DOCX guides: 28 pages total; project PDF: 9 pages; render and visual inspection passed.
- Final public-release scan: safe tree and artifact integrity passed; secrets, personal data, forbidden files, broken local links, internal navigation findings, and publication gates all 0.

## Streamlit deployment

- Workspace: `devengaikwad`
- Repository / branch / entry point: `DevenGaikwad/NewsLens-AI` / `main` / `app.py`
- Python: 3.12; secrets: empty; plan: free Community Cloud
- Initial deployed runtime commit / tree: `214b22745736b25f4c1121822a1811c76687bb00` / `093cdbacf815be22791ae73bf5a581a9e84edd3d`
- Public URL: <https://newslens-ai-devengaikwad.streamlit.app/>

### Public smoke evidence

- Startup, public access, and all six application pages passed.
- Packaged ledger-consistent input produced a 24-word deterministic summary, the expected consistency label, calibrated confidence, explanation, and session record.
- A ledger-contradicting input and an unsupported-format input produced the expected contradictory and abstention paths; short input produced the expected validation error.
- JSON and PDF analysis controls, analytics CSV, filtered-archive CSV, selected-record JSON/PDF, and archive workflows were visible and enabled when applicable.
- A fresh browser session opened an empty archive; the active session showed only its own new record.
- Dataset Analysis and Research & About state synthetic provenance and do not expose the training archive or raw rows.
- Application-origin console errors: 0. Browser-extension metadata warnings were excluded because they did not originate from the application.
- Desktop layout at 1363 CSS pixels had no horizontal overflow. The unchanged responsive system retains its five-width 360/390/768/1366/1920 release audit. The cloud browser's HTTP(S)-only URL policy prevented creation of a new 390-pixel harness; no unsupported workaround was attempted.

## Phase 5T protected maintenance release

Phase 5T is a presentation and interpretation correction based on `f6cae8cedb3364cf03864410b8c5572c4e625504`. It repairs the ReportLab probability table, withholds directional values outside the supported two-block comparison format, clarifies the human-readable probability labels, removes the obsolete public publication banner, uses the punctuation-free responsive tagline `News intelligence / With scope intact`, repairs the editorial masthead bounds, and reduces repetitive footer attribution.

The repeated approximately 84–90% internal outputs for unrelated unsupported prose were reproduced and diagnosed. Controlled cases and same-session/fresh-session checks ruled out hard-coded scores, stale state, cache reuse, positive-class reversal, and calibration misapplication. Those inputs all lacked the required structured pair and shared the dominant `signal_fact_blocks_unavailable` feature. The structured evidence is retained in `reports/results/phase5t_prediction_diagnostic.json`.

Local candidate validation completed before protected publication:

- complete Python suite: 165 passed; 0 failures, errors, or skips;
- affected regression suite: 38 passed;
- Python compilation and packaged-sample evaluation: passed;
- `pip check`: passed;
- deterministic `npm ci`, TypeScript lint, and Next.js production build: passed;
- production `npm audit --omit=dev`: 80 dependencies audited; 0 vulnerabilities;
- dataset, model, calibration, and model-to-calibration binding: exact and unchanged;
- four tracked DOCX reports: 28 pages inspected;
- tracked project report PDF: 9 pages independently rasterized and inspected;
- representative application-export matrix: 7 pages inspected across supported, boundary, unsupported, and long-content cases;
- model retraining: not performed.

The retained branch was recovered with no stalled dependency-audit process. The bounded production `npm audit --omit=dev` completed in 8.2 seconds: 80 dependencies, zero reported vulnerabilities. The repaired source, UI, tests, four existing Word reports, and existing project PDF were committed as local `a33de69136ad05b6e3514a99b372770e691d27cd` (tree `c9db63a911d6c34cbecd0935336866a6280bde88`). GitHub's protected workflow used the same exact tree on remote head `6d2ac240491a7ac6cf0b7d838f065865242254c6` in [PR #47](https://github.com/DevenGaikwad/NewsLens-AI/pull/47). Its CI and both CodeQL languages passed on that head. The squash merge was `d9291605ac9813982837dcb5fade645035795a34`, with the same resulting tree. Exact-new-main [CI run 36293926319](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36293926319) and [CodeQL run 36293926442](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36293926442) passed. PR #47 is merged and closed.

### Public Phase 5T verification

On 27 September 2026 the public Streamlit application started and all six pages loaded. The News Desk displayed the two-line punctuation-free tagline and repaired masthead; the publication banner was absent and the footer attribution was concise. In the live Analyse Article page, the authored paired-ledger agreement sample yielded 100.0% **Fields agree** and 0.0% **Fields conflict**; the contradiction sample yielded 0.0% and 100.0%, respectively. These are synthetic comparison probabilities, not factual truth probabilities. Ordinary fictional prose without both ledgers displayed **Outside supported comparison scope**, **Reference-comparison confidence: Not reported**, no directional feature explanation, and a human editorial-review path. A short input produced the 40-word validation message. A fresh browser session had zero archive records; its later analysis appeared only in that session. JSON, PDF, and privacy-safe analytics CSV controls were present. Application-origin console errors were zero; extension metadata errors were excluded.

New PDFs were downloaded from the live application. The agreement and contradiction PDFs were each one A4 page, with separately aligned probability labels and their corresponding 100.0%/0.0% or 0.0%/100.0% values. Their pages were independently rasterized and visually inspected with PyMuPDF; text extraction and page size were checked separately. The seven-page local PDF matrix retained the unsupported-score-withholding and long-content evidence. The live desktop viewport at 1363 CSS pixels had no horizontal overflow; the retained 360/390/768/1366/1920 responsive audit remains the mobile evidence. The browser did not expose an exact Streamlit deployment commit in its public interface.

### Security-relevant dependency follow-up and PR disposition

The `pypdf==6.16.1` pin was within published affected ranges for resource-consumption advisories, including GHSA-jw7q-gvrg-4vj3 and GHSA-php9-fj8v-98fj. [PR #42](https://github.com/DevenGaikwad/NewsLens-AI/pull/42) changed only `requirements-lite.txt` to `pypdf==6.19.0`, the patched version. Its exact head `7d40f439fcd3c8f9f3d3130018dcfbbfddcee522` had successful CI and CodeQL. The complete 165-test suite passed locally with 6.19.0. It was squash merged as `0e58189b8cbfd92126e5f4268bff320bdeb25bd1` (tree `b59b7ccb51a3177ec5044280a66cf7201ee8cfaf`). Exact-new-main [CI run 36296310448](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36296310448) and [CodeQL run 36296310449](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36296310449) passed. The dataset, model, calibration and binding hashes remained exact. The dependency-only change did not retrain or alter the model.

| PR | Update | Disposition and reason |
|---|---|---|
| [#32](https://github.com/DevenGaikwad/NewsLens-AI/pull/32) | ReportLab 5.0.1 | Closed with explanation; major renderer migration needs its own compatibility and visual review. |
| [#33](https://github.com/DevenGaikwad/NewsLens-AI/pull/33) | react-dom and types 19.3.0 | Closed with explanation; exact-head CI failed and the web package is not deployed. |
| [#34](https://github.com/DevenGaikwad/NewsLens-AI/pull/34) | joblib 1.6.0 | Closed with explanation; optional model-serialization dependency change needs a separate compatibility gate. |
| [#36](https://github.com/DevenGaikwad/NewsLens-AI/pull/36) | react and types 19.3.0 | Closed with explanation; optional nondeployed web update should be validated with react-dom. |
| [#37](https://github.com/DevenGaikwad/NewsLens-AI/pull/37) | pytest 9.1.1 | Closed with explanation; optional development update, existing 165 tests pass. |
| [#40](https://github.com/DevenGaikwad/NewsLens-AI/pull/40) | @types/node 26.6.1 | Closed with explanation; major types update for nondeployed web package needs separate review. |
| [#42](https://github.com/DevenGaikwad/NewsLens-AI/pull/42) | pypdf 6.19.0 | Merged; patched the published affected ranges. |
| [#43](https://github.com/DevenGaikwad/NewsLens-AI/pull/43) | Next.js 16.3.5 | Closed with explanation; nondeployed web package and production npm audit reported zero vulnerabilities. |

The public GitHub open-PR listing returned zero after these actions. `pip-audit` could not complete a new advisory-service lookup within the bounded 55-second command; its historical Phase 5S result is not treated as a current scan. Repository-specific security and Dependabot alert endpoints returned HTTP 401 without an authorized alert-reading permission, so their current open counts remain unverified. The protected CI, CodeQL, dependency review, current npm audit, and the cited upstream pypdf advisories are the available evidence. No zero-alert claim is inferred from a denied endpoint.

## Publication boundary

All training articles and entities are synthetic. No ISOT row, copied phrase, close paraphrase, transformation, translation, summary, reconstruction, private ISOT-derived classifier/calibration artifact, or external copyrighted article dataset is present in the model, repository, archive, deployment, or release. Noncommercial status was not treated as permission.

Vercel was not deployed or modified. The historical release tag was not modified. The earlier six-PR Phase 5S hold was superseded by the owner's Phase 5T instruction to resolve every open PR; the full eight-PR disposition is recorded above.

## Phase 5U continuation — security and presentation

The Phase 5U security correction replaced the CodeQL-alerted `_BLOCK.findall` path with line-scoped linear fact parsing. It preserved all 24,000 accepted article and six packaged-sample fields, tokens, augmented input, raw scores, predictions, and calibrated probabilities with zero mismatches. The retained 25 focused tests, 171 full tests, crafted-input scaling measurements, frozen-artifact hashes, and 191-file public-release scan passed. [PR #49](https://github.com/DevenGaikwad/NewsLens-AI/pull/49) exact head `4747c378586daec198bc94bbe028356ba5d34119` passed CI, dependency review, and Python/JavaScript CodeQL. Protected squash merge `6a4c769f41aee14a77f6b0f6e9d4d3f06eb0d013` retained tree `afdb5411493fcfc329cc4b320d4e027415bf5f20`. Exact-new-main [CI](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36327104638) and [CodeQL](https://github.com/DevenGaikwad/NewsLens-AI/actions/runs/36327104624) passed; authenticated alert #6 reads **Fixed via commit 6a4c769**, not dismissed.

The separate presentation follow-up shortens the public analysis-PDF footer to one developer attribution and a name-free copyright line, matching the established app footer. A responsive width subtraction gives the native `Open Archive` link a right-side gutter before the illustration divider; stacked narrow links remain full width. The existing classifier's primary UI and PDF outcomes are now plain-language `Reference comparison` statements, while the stable JSON label/score fields and frozen model/probabilities are retained. The existing PDF probability wrapping, tagline, masthead, banner removal, and out-of-scope score withholding were verified as already implemented.

The general-news dataset gate is **not met**. The candidate-by-candidate rights, provenance, label, date, privacy, and task-fit decision is in [the existing deployment/model license audit](../docs/PUBLIC_DEPLOYMENT_MODEL_LICENSE_AUDIT.md). No general-news classifier was trained or deployed, and no general-news performance, calibration, or real/fake claims are reported. Ordinary article prose continues to receive `Outside supported comparison scope` and human review. The public Streamlit URL remains unchanged; its public interface does not establish the exact deployed commit SHA without an authenticated dashboard view.
