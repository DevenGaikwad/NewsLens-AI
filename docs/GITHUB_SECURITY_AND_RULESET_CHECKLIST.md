# GitHub Security and Ruleset Checklist

## Account and repository

- Maintain two-factor authentication, recovery codes, passkeys, and minimum app/OAuth/SSH access.
- Never place passwords, tokens, private keys, recovery codes, secrets, or private datasets in GitHub or reports.
- Keep secret scanning, push protection, Dependabot alerts, dependency review, CodeQL, and private vulnerability reporting enabled.
- Retain read-only default Actions permissions and job-specific exceptions only.

## Protected `main`

- Require pull requests, conversations resolved, code-owner review, and exact required checks.
- Block force pushes and branch deletion; minimize bypass access.
- Verify the exact PR head before squash merge and exact new main afterward.
- Preserve genuine history and the historical `public-release-2026-09-01` tag.

## Phase 5S boundaries

- Public model/calibration must match `models/public_artifact_manifest.json`.
- Historical private artifact filenames remain prohibited.
- The Phase 5S retained Dependabot PRs were handled separately in Phase 5T under the owner's later zero-open-PR instruction. Security-relevant pypdf PR #42 was merged; seven other optional or unsuitable updates were closed with explanations. The public open-PR list returned zero after cleanup.
- Repository-specific security and Dependabot alert endpoints returned HTTP 401 without alert-read permission. Do not report zero alerts until an authorized view confirms the counts.
- Streamlit Community Cloud is the deployment target; Vercel is not required.

## Phase 5U parser security correction — pre-merge evidence

- The authenticated security view confirmed one open High CodeQL alert (#6,
  `py/polynomial-redos`) on `synthetic_benchmark/signals.py:66` at the
  `f691ec7310fe64c146321c36910349805056b43b` baseline. Dependabot had
  zero open vulnerability alerts. A successful CodeQL workflow alone does not
  close this finding.
- The flagged `_BLOCK.findall` call processed article text in the prediction
  path. The correction replaces block and field extraction with line-scoped,
  semicolon-delimited parsing and first-colon partitioning. A later occurrence
  of the same field or block continues to replace its earlier value. Empty
  malformed headings no longer consume the following line.
- Old/new comparison covered all 24,000 accepted articles and six packaged
  samples: zero mismatches in parsed fields, derived tokens, augmented input,
  class scores, predictions, or calibrated probabilities.
- Local tests: 25 focused and 171 complete, all passed. Bounded 100k–400k
  crafted-input measurements were approximately linear for long heading
  whitespace, missing colons, and repeated fields; 400k–1.6m long-value
  measurements scaled by about 2× per input doubling. Crafted inputs were
  never sent to the public application.
- The 191-file tracked-tree public-release scan passed with zero findings and
  publication gates. The dataset, model, and calibration hashes were unchanged.
  Exact-head CodeQL and authenticated alert closure remain merge gates.
