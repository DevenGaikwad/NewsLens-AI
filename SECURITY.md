# Security Policy

Security fixes target the public `main` branch of `DevenGaikwad/NewsLens-AI`.

Report sensitive vulnerabilities through GitHub private vulnerability reporting. Do not disclose secrets, exploit details, personal article history, private URLs, or private artifacts in a public issue.

## Boundaries

- Public URL ingestion rejects credentials and private, loopback, link-local, or reserved destinations and bounds redirects and response size.
- Uploads are restricted to TXT and text-based PDF, capped at 10 MB, and processed in memory.
- Public history defaults to a temporary session-isolated SQLite file and does not store full article text.
- Model calibration fails closed when the active model hash differs from the recorded binding.
- Release scanning verifies the accepted dataset, model, calibration, private-artifact exclusion, secrets, local paths, links, and legal records.
- No API key or Streamlit secret is required.
- Machine-learning output is a synthetic consistency signal, not factual verification.

Include the affected component, safe reproduction steps, impact, and a minimal proof of concept. No response-time guarantee is asserted until maintainers publish one.
