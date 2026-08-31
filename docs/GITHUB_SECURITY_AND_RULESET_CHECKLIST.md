# GitHub account, security, and ruleset checklist

Complete these settings manually only after the owner creates the canonical
repository. Do not paste credentials, recovery codes, private keys, or personal
access tokens into issues, documentation, or ChatGPT.

## Owner account

- [ ] Enable two-factor authentication with a TOTP authenticator.
- [ ] Add a passkey such as Windows Hello where available.
- [ ] Store recovery codes offline in a secure location.
- [ ] Review and remove unnecessary authorised GitHub Apps.
- [ ] Review and remove unnecessary OAuth applications.
- [ ] Review SSH keys; remove unknown, expired, or unused keys.
- [ ] Keep collaborator access minimal and role-appropriate.
- [ ] Never share a password or personal access token.
- [ ] Configure a verified Git commit email without publishing a private address.
- [ ] Prefer signed commits and signed/verified release tags where practical.

## Repository security features

- [ ] Make the reviewed `NewsLens-AI` repository public only after all release gates clear.
- [ ] Enable secret scanning and push protection.
- [ ] Enable Dependabot alerts and security updates.
- [ ] Enable dependency graph and dependency review.
- [ ] Enable CodeQL default/setup workflow or the staged workflow, avoiding duplicates.
- [ ] Enable private vulnerability reporting.
- [ ] Limit Actions permissions to read-only by default; grant only job-specific permissions.
- [ ] Review every installed GitHub App's repository scope.

## `main` branch ruleset

- [ ] Require pull requests before merging.
- [ ] Require the Python, public-release-scan, presentation-build, and dependency-review status checks once they have run successfully in the real repository.
- [ ] Require code-owner review.
- [ ] Require conversation resolution.
- [ ] Require signed commits where practical.
- [ ] Block force pushes.
- [ ] Block branch deletion.
- [ ] Restrict direct updates/bypass to the minimum owner role needed for recovery.
- [ ] Protect tags used for official releases from deletion or movement.
- [ ] Do not claim that CODEOWNERS or a ruleset creates copyright ownership.

## Deployment accounts

- [ ] Connect Vercel through the correct GitHub owner account with minimum repository scope.
- [ ] Connect Streamlit Community Cloud through the correct GitHub owner account.
- [ ] Enter environment values through provider dashboards, never repository files.
- [ ] Expose only the public Streamlit origin through `NEXT_PUBLIC_STREAMLIT_APP_URL`.
- [ ] Review deployment members and remove unnecessary access.

## Authorship provenance and release

- [ ] Set the accurate Git author name to `Deven Sachin Gaikwad` for future commits.
- [ ] Preserve the existing genuine Git history; do not fabricate or rewrite dates.
- [ ] Scan the complete canonical Git history for secrets and private data before public push.
- [ ] Make the first official release only after approval, with its actual date.
- [ ] Attach the reviewed archive checksum and clear release notes identifying the original author.
- [ ] Add a test-status badge only after the first real GitHub Actions run succeeds.
