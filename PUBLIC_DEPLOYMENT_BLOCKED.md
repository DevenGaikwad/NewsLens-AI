# Historical Deployment Gate — Resolved by Synthetic Replacement

This retained file preserves the identity and history of the earlier deployment-gate record.

Public deployment was previously blocked because the private ISOT-derived classifier and calibration could not be redistributed. Phase 5S resolves that issue by excluding those artifacts and replacing them with a new public classifier trained exclusively from an original synthetic dataset.

The synthetic model and exact bound calibration are public, tested, and covered by `models/public_artifact_manifest.json`. Deployment is therefore no longer blocked by model redistribution. The only remaining pre-deployment boundary is completion and protected merge of PR B; afterward the app is deployed to Streamlit Community Cloud and smoke-tested.

No Vercel deployment is required.
