# Historical Deployment Gate — Resolved by Synthetic Replacement

This retained file preserves the identity and version history of the earlier deployment-gate record.

Public deployment was previously blocked because the private ISOT-derived classifier and calibration could not be redistributed. Phase 5S resolved that issue by permanently excluding those artifacts and publishing a new classifier trained exclusively from an original synthetic dataset.

The synthetic model and its exact hash-bound calibration are covered by `models/public_artifact_manifest.json`. PR B was protected-merged as [#45](https://github.com/DevenGaikwad/NewsLens-AI/pull/45), and the resulting `main` commit was deployed and smoke-tested at <https://newslens-ai-devengaikwad.streamlit.app/>.

No deployment gate remains. No Vercel deployment was required or created.
