# Contributing to NewsLens AI

NewsLens AI is proprietary, source-visible software. Issues that report
reproducible bugs, documentation errors, accessibility concerns, or responsible
security findings are welcome. **Unsolicited external code contributions are
not currently accepted unless Deven Sachin Gaikwad gives prior written
approval.** Opening a pull request does not grant a licence to NewsLens AI or
automatically transfer rights in the submitted material.

An approved external contributor must complete the contribution/rights terms
specified by the owner before merge. Do not submit third-party code, data,
models, imagery, or text unless you have authority to do so and document its
provenance and licence.

## Before opening a pull request

1. Obtain prior approval from the owner and agree the contribution/rights terms.
2. Create a focused branch from `main`.
3. Keep `app.py` as the runtime entrypoint and use native `st.Page`, `st.navigation` or `st.page_link` for internal routes.
4. Do not call training code from Streamlit. Runtime code may only load the packaged model.
5. Keep summarisation and classification independent: the classifier receives the original cleaned article, not the generated summary.
6. Preserve cautious wording. Outputs estimate linguistic credibility risk; they do not establish truth.
7. Add or update tests and public documentation for changed behaviour.
8. Run `python -m pytest -q` and confirm the current packaged check count recorded in `docs/TESTING.md` passes without failures or unexpected skips.
9. For UI changes, run the browser audits at 360, 390, 768, 1366 and 1920 pixels and inspect screenshots manually.

## Public data and privacy

Never commit secrets, `.env`, `.streamlit/secrets.toml`, visitor uploads, logs containing article text, personal history databases or raw datasets without redistribution permission. Public history must remain visitor-isolated; persistent SQLite is for explicit trusted-local use only.

## Model or dataset changes

Document provenance, license, schema, hashes, label policy and known limitations. Deduplicate before splitting, keep TF-IDF inside the training pipeline and use grouped or temporal evaluation where possible. Do not replace the packaged artifact until the model card, dataset card, metrics, figures and tests agree.

## Review expectations

Pull requests should explain scope, user-visible behavior, tests, privacy implications and documentation changes. Avoid unrelated formatting or generated-artifact churn.

By submitting an approved contribution, the contributor represents that the
submission is their original work or is lawfully reusable under disclosed
terms. Final acceptance remains at the owner's discretion. The repository's
root `LICENSE` applies to original NewsLens AI material after merge unless a
separate signed agreement states otherwise.
