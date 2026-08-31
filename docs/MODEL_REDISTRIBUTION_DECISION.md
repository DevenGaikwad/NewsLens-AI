# Packaged-model redistribution decision

Decision status: **permission unclear — public distribution and deployment blocked**  
Artifact: `models/fake_news_pipeline.joblib`  
Artifact ID: `isot-tfidf-lr-v1.0.0`
Companion artefact: `models/confidence_calibration.json`

## Evidence reviewed

Official source: University of Victoria ISOT Research Group, “Fake News
Detection Datasets”:
<https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/>  
Accessed: 24 August 2026

The reviewed page describes the ISOT dataset and provides a download. Its
linked two-page dataset-description PDF describes the CSV contents and gives
citation instructions. No explicit licence or express permission to
redistribute a trained derivative model was located in either official source.
Download availability alone is not treated as permission. No written
permission was supplied with this release package.

The binary and dataset-derived calibration parameters were produced offline from the ISOT-derived workflow. The
NewsLens AI proprietary notice applies to original project material only and
does not automatically relicense the dataset or this derived artifact.

## Decision table

| Evidence state | Required treatment | Public application consequence |
|---|---|---|
| Written redistribution permission obtained from an authorised rights contact | Preserve the complete permission record; verify scope covers the trained artifact and public GitHub/cloud hosting; then document any conditions before inclusion | May be reconsidered for public inclusion/deployment after legal/technical review |
| Explicit applicable licence located | Preserve the licence text/source/version; assess derivative-model, attribution, commercial-hosting, and notice requirements | Include only if the licence clearly permits the intended distribution and all conditions are met |
| Permission denied | Keep the artifact private; do not push or deploy it | Public deployment remains blocked unless the owner explicitly approves a separately licensed technical replacement |
| Permission remains unclear | Keep the artifact private, Git-ignored, and outside public staging | Public classifier is unavailable; deployment remains blocked |

## Current package treatment

- The private/local complete archive may include the artifact solely for the
  owner's local review and operation.
- The public-staging archive excludes both artefacts and carries an explicit
  deployment-blocked marker.
- Runtime code still expects the exact packaged model and matching calibration hash and never retrains it.
- Replacing or retraining the model is outside this hardening scope and requires
  explicit owner approval.

This is a release-engineering decision record, not legal advice.
