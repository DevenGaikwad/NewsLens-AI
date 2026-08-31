# NewsLens AI — Analysis History

The public-safe default creates a separate temporary SQLite file for each
Streamlit session outside this directory. This prevents one visitor from listing
another visitor's archive and does not promise durable cloud history.

Only a trusted, single-user local runtime may set
`NEWSLENS_HISTORY_MODE=persistent`; that mode creates `analysis_history.db` here.
Only compact analysis results, calibrated confidence, aggregate input diagnostics,
human-review fields and a SHA-256 article hash are stored. Uploaded files and the
complete original article are not retained. Review notes and supporting-source URLs
remain inside the same visitor-scoped file. Delete or clear history from the UI and
never commit generated database files.
