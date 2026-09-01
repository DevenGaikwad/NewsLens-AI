# Security policy

## Supported branch

Security fixes target the public `main` branch.

The public and active repository is
[`DevenGaikwad/NewsLens-AI`](https://github.com/DevenGaikwad/NewsLens-AI).

## Reporting a vulnerability

Report vulnerabilities through GitHub private vulnerability reporting. Do not
post sensitive vulnerability information, secrets, exploit details, personal
article history or private URLs in a public issue.

Include the affected component, reproduction steps, impact and a minimal safe proof of concept. Maintainers should acknowledge a report before public disclosure and publish remediation details through GitHub advisories and releases.

## Security boundaries

- Public URL ingestion rejects credentials, localhost and private, loopback, link-local or reserved addresses to reduce SSRF risk.
- Uploads are limited to TXT and text-based PDF, capped at 10 MB and processed in memory.
- Public Streamlit history defaults to a temporary, per-session SQLite file. Persistent SQLite is not a safe shared-cloud user database.
- The application stores structured results and a duplicate hash, not uploaded files or full source articles.
- Secrets must use hosting-provider secret storage and must never use `NEXT_PUBLIC_` variables.
- Machine-learning output is not factual verification. Treat confident errors and domain shift as safety risks.

No response-time guarantee is asserted until repository maintainers publish one.

NewsLens AI is not currently publicly deployed through Streamlit or Vercel.
The public repository does not imply that a hosted application is available.
Never send passwords, personal access tokens, recovery codes, private keys, or
production secrets with a report.

## Coordinated disclosure workflow

1. Open a private vulnerability report from the repository **Security** tab.
2. Describe the affected component, impact, safe reproduction, and proposed
   embargo needs without including unrelated personal data.
3. Allow the owner to validate and remediate the issue before public disclosure.
4. Publish an advisory or release note only after remediation and coordination.

Public GitHub issues are appropriate for non-sensitive bugs only. Use private
vulnerability reporting for security-sensitive information.
