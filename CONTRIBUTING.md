# Contributing to NewsLens AI

NewsLens AI is proprietary source-visible software. Reproducible bug, documentation, accessibility, and responsible-security reports are welcome. External code contributions require prior written approval from Deven Sachin Gaikwad.

Approved changes must:

1. use a focused branch from current `main` and preserve protected review;
2. keep `app.py` as the Streamlit entry point and retain native same-tab navigation;
3. never call training code at runtime;
4. use only the public synthetic model and its hash-bound calibration;
5. keep deterministic summarisation independent from classification;
6. preserve the synthetic ledger-consistency wording and abstention boundary;
7. document provenance, license, schema, hashes, splits, and limitations for any model/data change;
8. add relevant tests and run the complete suite and public-release scan;
9. avoid secrets, visitor data, private databases, unsupported datasets, and unrelated generated churn.

Do not submit third-party data, models, imagery, text, or code without documented authority. Public visibility does not grant permission to submit NewsLens AI as another person's academic or professional work.
