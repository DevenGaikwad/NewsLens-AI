# Streamlit Community Cloud Deployment

## Required configuration

- Workspace: `devengaikwad`
- Repository: `DevenGaikwad/NewsLens-AI`
- Branch: `main`
- Entry point: `app.py`
- Python: 3.12
- Secrets: empty
- Plan: free / Community Cloud

The repository includes the public synthetic model and bound calibration, so deployment does not download a checkpoint or retrain. `requirements.txt` delegates to the lightweight pinned runtime requirements and contains no external transformer stack.

## Procedure

1. Confirm PR B is merged and exact-new-main checks pass.
2. In Streamlit Community Cloud, create or update the app with the values above.
3. Wait for dependency installation and startup to finish; inspect logs for model or calibration errors.
4. Record the exact deployed main commit and final `https://…streamlit.app` URL.
5. Test News Desk navigation, consistent, contradicting, and abstention samples, extractive summary, explanations, JSON/PDF/CSV exports, invalid input, session isolation, desktop/mobile layout, and public access.
6. Confirm the UI does not expose the dataset ZIP or raw training rows.

Vercel is not required and must not be created or modified for this deployment.

## Failure behavior

Missing model files raise an actionable startup error. A calibration/model hash mismatch fails closed and forces review rather than reporting unverified confidence. Inputs outside the paired-ledger format abstain.
