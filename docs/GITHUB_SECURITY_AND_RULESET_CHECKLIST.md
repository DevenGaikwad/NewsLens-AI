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
- Six retained Dependabot PRs are handled separately.
- Streamlit Community Cloud is the deployment target; Vercel is not required.
