# Privacy and data handling

NewsLens AI processes article content to produce a summary and linguistic credibility-risk estimate. Uploaded files are parsed in memory and are not retained. The archive stores structured metadata, summary, calibrated probabilities, input diagnostics, human-review fields and a duplicate-detection hash, not the full source article or upload bytes.

Public Streamlit sessions default to separate temporary SQLite files derived from random, hashed session identifiers. Browser testing with two isolated contexts confirms that a second visitor cannot list the first visitor's record.

Limitations:

- SQLite is not encrypted by the application.
- Session files are temporary and may disappear during restart or redeployment.
- The safe isolation boundary is not an authentication system or durable account store.
- Review notes, supporting-source URLs and final assessments share the same temporary session boundary.
- Newsroom analytics and drift checks use aggregates from the current visitor's archive; their privacy-safe export omits titles, summaries, URLs, notes and analysis identifiers.
- Trusted, single-user local installations can explicitly enable persistent mode; public multi-user hosting must not.

Do not publish generated databases, personal analysis history, uploads or logs containing private article content.

## Security controls at the data boundary

- Article URLs are fetched without environment proxies, with independent
  validation of every redirect, globally routable DNS answers, peer-address
  checking where observable, loop/hop limits, timeout, and a streamed 5 MB cap.
- Upload filenames reject traversal; bytes are processed in memory; encrypted
  PDFs, PDFs over 200 pages, and excessive extracted text are rejected.
- CSV user fields beginning with spreadsheet formula/control prefixes are
  neutralised, and PDF Paragraph values are escaped before ReportLab parsing.
- Unexpected public-interface errors do not display paths, stack traces, or
  implementation details.
