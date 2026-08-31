# Third-party software, data, and research notices

This file distinguishes external material from original NewsLens AI work. It is
an attribution and release-audit record, not a substitute for the licence text
distributed by each dependency or source.

## Runtime and development dependencies

The following direct-package identifiers were read from the installed Python
3.12 distribution metadata and `web/package-lock.json` on 16 August 2026. The
licence files shipped by each package remain controlling; this summary neither
relicenses the packages nor replaces their notices.

| Direct dependency | Staged version | Licence identifier/metadata |
|---|---:|---|
| Streamlit | 1.59.2 | Apache-2.0 |
| pandas | 2.2.3 | BSD licence metadata |
| NumPy | 2.3.5 | BSD licence metadata |
| scikit-learn | 1.8.0 | BSD-3-Clause |
| Joblib | 1.5.3 | BSD-3-Clause |
| Plotly | 6.9.0 | MIT |
| Matplotlib | 3.10.8 | Matplotlib/PSF-style licence metadata |
| Seaborn | 0.13.2 | BSD licence classifier |
| Requests | 2.34.2 | Apache-2.0 |
| Beautiful Soup | 4.15.0 | MIT |
| Trafilatura | 2.1.0 | Apache-2.0 |
| pypdf | 6.15.0 | BSD-3-Clause |
| ReportLab | 4.4.9 | BSD licence metadata |
| pytest | 9.0.3 | MIT |
| Playwright (audit-only) | 1.55.0 | Apache-2.0 |
| Next.js | 16.3.1 | MIT |
| React / React DOM | 19.2.4 | MIT |
| TypeScript | 5.9.3 | Apache-2.0 |
| Node/React type packages | lockfile versions | MIT |

The optional full profile also declares version ranges for Transformers,
PyTorch, and SentencePiece. Their exact resolved releases and shipped licence
files must be recorded from the environment used for an approved public build;
they were not installed merely to manufacture a licence inventory.

The dependency set is declared in `requirements-lite.txt`, `requirements.txt`,
and `web/package-lock.json`. The project does not claim ownership of any direct
or transitive dependency.

Before a public release, GitHub dependency review, Dependabot, CodeQL, and a
dependency-inventory review should be run against the exact lockfiles. If a
dependency's current terms conflict with the intended distribution, resolve or
replace it only through an explicit technical review.

## Datasets and checkpoints

| Material | Project use | Redistribution treatment |
|---|---|---|
| ISOT Fake News Dataset, University of Victoria ISOT Research Group | Offline classifier training/evaluation | Raw CSV files excluded. Official source terms govern. The reviewed source page did not state an explicit redistribution licence. |
| XSum, EdinburghNLP | Fixed-sample summarisation evaluation | Raw records excluded. Obtain from the official/current host under its terms. |
| `sshleifer/distilbart-cnn-6-6` | Optional abstractive summarisation | Not bundled; downloaded on demand and governed by its upstream model and dependency terms. |
| `fake_news_pipeline.joblib` | Packaged runtime classifier in the private package | Separate derived-artifact rights assessment; not covered by the NewsLens AI proprietary grant and excluded from public staging. |

Official ISOT source reviewed 16 August 2026:
<https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/>

## Research literature

Bibliographic references and project relevance notes appear in
`docs/NewsLens_AI_Research_Paper_Matrix.xlsx` and `docs/research_papers.json`.
The papers remain the property of their respective authors/publishers. The
repository does not bundle paper PDFs.

## Original visual assets

The NewsLens AI logo, editorial masthead, diagrams, social preview, and README
collage were created specifically for the project. Their ownership and
permission status follow the root proprietary notice. System font fallbacks are
used; no font files are bundled.
