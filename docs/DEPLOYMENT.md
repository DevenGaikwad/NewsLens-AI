# Deployment guide

## Publication prerequisites

Before any public push, use the confirmed GitHub owner `DevenGaikwad`, clear the packaged-model
redistribution gate, preserve the approved proprietary repository notice, run
the release audit, and replace all deployment sentinels. The public-staging
archive excludes the model and private calibration parameters and is not deployable. Never request or paste a
password, recovery code, private key, or personal access token into chat or
documentation.

## Streamlit Community Cloud

1. Create the public GitHub repository `NewsLens-AI` and push the reviewed release to `main`.
2. Confirm `app.py` and `requirements.txt` are at the repository root.
3. In Community Cloud, create an app from the repository, branch `main`, entrypoint `app.py` and Python 3.12.
4. Do not set `NEWSLENS_HISTORY_MODE=persistent` for the public multi-user app.
5. Add only necessary secrets through Community Cloud settings; this application needs no secret for its core workflow.
6. Verify all six routes, direct navigation, refresh, back/forward, text/URL/document input, summary, classification, confidence, explanation, exports and two-browser-context history isolation.
7. Verify the editorial review, aggregate analytics, insufficient-observation drift state, and calibration artefact/model hash binding.
8. Inspect deployment logs and the browser console. The local audit records non-fatal framework health-probe 404s on nested development routes; re-check this behavior on the deployed Community Cloud origin.

Community Cloud local SQLite files are temporary. Do not advertise permanent cloud history.

Do not retrain during build/startup and do not silently substitute a classifier.
If documentary model rights remain unclear, stop before this section.

## Vercel

Use only a personal, non-commercial Vercel Hobby account whose dashboard shows a zero base price, no paid trial, and no required payment method for the selected workflow. Stop if a payment, upgrade, billable integration, or commercial plan is required.

1. Import the same GitHub repository into Vercel.
2. Set the project root directory to `web/` and keep the detected Next.js build settings.
3. Create one public environment variable:

   ```text
   NEXT_PUBLIC_STREAMLIT_APP_URL=https://YOUR-APP.streamlit.app
   ```

4. Do not append `?embed=true`; the `/app` route adds it safely.
5. Use a bare HTTPS `*.streamlit.app` origin with no credentials, port, path,
   query, or fragment. The production build rejects unsafe values.
6. Never place secrets in `NEXT_PUBLIC_` variables.
7. Verify CSP/`frame-src`, `frame-ancestors`, Referrer-Policy,
   Permissions-Policy, `X-Content-Type-Options`, HSTS, and the iframe sandbox in
   the deployed response without breaking Streamlit downloads or interaction.
8. Verify the landing page and `/app` at 360, 390, 768, 1366 and 1920 pixels. Check the mobile menu, 44-pixel controls, visible focus, reduced motion, loading state, iframe title and same-tab fallback.

## Final link pass

After both deployments succeed, replace the pending URLs recorded in
`docs/DEPLOYMENT_VALUES_TO_FILL.md`, update README/website/CITATION metadata, run
both builds/audits again, inspect browser console and provider logs, and confirm
every documentation link resolves from the public repository.

## Rollback

Use GitHub releases and deployment history as the source of truth. Roll back to a tested tagged commit; do not retrain or replace the model during a runtime rollback. Do not enable paid overage or create another account to bypass a free-tier limit.
