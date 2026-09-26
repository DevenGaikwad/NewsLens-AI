# Privacy and Data Handling

The public Streamlit workflow is designed to minimize retained data.

- Pasted text and uploaded TXT/PDF content are processed for the active request.
- Uploaded files are not saved by application code.
- Full article text is not written to SQLite.
- The structured analysis archive uses a visitor-scoped temporary database in public hosting.
- Source URLs and reviewer notes remain within that visitor session.
- Privacy-safe analytics export only aggregates and excludes titles, summaries, URLs, notes, identifiers, and article text.
- URL fetching occurs only after the user supplies a public HTTP(S) URL; private and loopback targets are blocked.
- No paid AI API, authentication token, telemetry key, or Streamlit secret is required.
- Raw training rows and the dataset ZIP are not exposed through the interface.

Cloud infrastructure and GitHub/Streamlit remain subject to their own privacy terms. Users should avoid submitting confidential or personal material.
