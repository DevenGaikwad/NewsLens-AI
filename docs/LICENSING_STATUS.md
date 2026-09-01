# Licensing status

Status checked: 1 September 2026
Publication status: **sanitized proprietary source is public; application deployment blocked**

## Approved position for original material

The author confirmed on 24 August 2026 that he is the sole owner of the
original NewsLens AI components and selected an All Rights Reserved,
proprietary source-visible position for original NewsLens AI material. The
sanitized source repository is publicly visible for academic evaluation,
portfolio review, and demonstration. It is not permission
to copy, modify, redistribute, sublicense, sell, publicly host, or create
derivative works beyond rights necessarily supplied by applicable law and
GitHub's Terms of Service. The controlling text is the root [`LICENSE`](../LICENSE).

No permissive or copyleft open-source licence and no Creative Commons licence
has been applied to original NewsLens AI material.

## Rights boundaries

| Material | Status | Publication treatment |
|---|---|---|
| Original NewsLens AI source, documents, diagrams, and interface assets | © 2026 Deven Sachin Gaikwad; All Rights Reserved | Publicly viewable in the sanitized repository under the root proprietary notice; no broader reuse rights are granted |
| Python/Streamlit/scikit-learn and other dependencies | Third-party software | Retain each package's licence; do not relicense as NewsLens AI material |
| Research papers | Third-party scholarship | Cite; do not redistribute full papers unless separately permitted |
| ISOT and XSum datasets | External datasets under their own terms | Raw records excluded; follow official sources and current terms |
| Pretrained checkpoints | Third-party artifacts | Download separately where applicable; retain upstream terms |
| `fake_news_pipeline.joblib` | Locally trained binary with unresolved public redistribution basis | Private/local package only; excluded from public staging and Git |
| `confidence_calibration.json` | Dataset-derived Platt parameters bound to the private model | Private/local package only; excluded from public staging and Git |

## Open questions

The official ISOT download page and its dataset-description PDF provide the
dataset description and citation guidance but did not state an explicit
redistribution licence in the material reviewed on 24 August 2026. That does
not establish permission to distribute the derived trained model.

The private ISOT-derived model, its private calibration parameters, and the raw
ISOT dataset remain excluded from the public repository. Public source
availability does not authorize redistribution of those private artifacts. The
public deployment-model audit reached a **NO-GO** decision; the authoritative
record is
[`PUBLIC_DEPLOYMENT_MODEL_LICENSE_AUDIT.md`](PUBLIC_DEPLOYMENT_MODEL_LICENSE_AUDIT.md).
Streamlit deployment remains blocked until a suitable model and its complete
rights chain are verified.

This project record is not legal advice and does not guarantee that every
jurisdiction will characterize all rights identically.
