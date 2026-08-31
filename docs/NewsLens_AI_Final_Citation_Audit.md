# NewsLens AI final citation audit

Audit date: 25 August 2026  
Scope: public project report, research matrix, model/dataset documentation, and supporting guides  
Result: **passed with two explicit evidence-boundary notes**

## Method

The ten scholarly records in `docs/research_papers.json` and the three-sheet
research matrix were checked against DOI-registry metadata. The four ACL records
were also checked against their official ACL Anthology pages. Dataset and
software references were checked against the official ISOT Research Lab page,
the Edinburgh NLP XSum repository, scikit-learn documentation, and Streamlit
documentation. Titles, author order, publication year, venue, page range, DOI,
and public source route were compared where the source supplied those fields.

## Scholarly reference results

| No. | Short title | DOI / primary record | Audit result |
|---:|---|---|---|
| 1 | Text Summarization using Transformer Model | [10.1109/SNAMS58071.2022.10062698](https://doi.org/10.1109/SNAMS58071.2022.10062698) | Title, two authors, 2022 venue, and pp. 1–5 match the DOI record. |
| 2 | Text Summarization using NLP Technique | [10.1109/DISCOVER55800.2022.9974823](https://doi.org/10.1109/DISCOVER55800.2022.9974823) | Title, six authors, 2022 venue, and pp. 30–35 match the DOI record. |
| 3 | Explainable Detection of Fake News on Social Media Using Pyramidal Co-Attention Network | [10.1109/TCSS.2022.3207993](https://doi.org/10.1109/TCSS.2022.3207993) | Title, six authors, journal volume 11(4), 2024, and pp. 4574–4583 match the DOI record. |
| 4 | Explainable Fact-Checking Through Question Answering | [10.1109/ICASSP43922.2022.9747214](https://doi.org/10.1109/ICASSP43922.2022.9747214) | Title, four authors, ICASSP 2022, and pp. 8952–8956 match the DOI record; the [author preprint](https://arxiv.org/abs/2110.05369) links the same IEEE DOI. |
| 5 | Advancing Fake News Detection: Hybrid Deep Learning With FastText and Explainable AI | [10.1109/ACCESS.2024.3381038](https://doi.org/10.1109/ACCESS.2024.3381038) | Title, five authors, IEEE Access volume 12, 2024, and pp. 44462–44480 match the DOI record. |
| 6 | Understanding the Use and Abuse of Social Media | [10.1109/TCSS.2022.3221811](https://doi.org/10.1109/TCSS.2022.3221811) | Title, four authors, journal volume 11(4), 2024, and pp. 4878–4887 match the DOI record. |
| 7 | BART | [ACL Anthology record](https://aclanthology.org/2020.acl-main.703/) | Title, eight authors, ACL 2020, pp. 7871–7880, and DOI match the official record. |
| 8 | Automatic Fake News Detection: Are Models Learning to Reason? | [ACL Anthology record](https://aclanthology.org/2021.acl-short.12/) | Title, three authors, ACL-IJCNLP 2021, pp. 80–86, and DOI match the official record. |
| 9 | Don’t Give Me the Details, Just the Summary! | [ACL Anthology record](https://aclanthology.org/D18-1206/) | Title, three authors, EMNLP 2018, pp. 1797–1807, and DOI match the official record. |
| 10 | “Liar, Liar Pants on Fire” | [ACL Anthology record](https://aclanthology.org/P17-2067/) | Title punctuation normalised; author, ACL 2017 short-paper venue, pp. 422–426, and DOI match the official record. |

## Dataset and software references

- The [official ISOT Research Lab dataset page](https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/)
  describes the dataset and links its download. It does not display an explicit
  redistribution licence for the dataset or trained derivative model. That
  absence is treated as a publication gate, not as permission.
- The [official Edinburgh NLP XSum repository](https://github.com/EdinburghNLP/XSum)
  identifies the EMNLP 2018 paper and provides the dataset preparation route.
  NewsLens AI publishes download/evaluation instructions, not the raw corpus.
- The [scikit-learn documentation](https://scikit-learn.org/stable/) and
  [Streamlit documentation](https://docs.streamlit.io/) are the canonical
  implementation references used by the project.

## Evidence-boundary notes

1. The two YouTube items supplied with the original project brief remain labelled
   **conceptual references**. They are not used as scholarly evidence for model,
   dataset, performance, security, or deployment claims.
2. DOI and access-route verification establishes citation identity and public
   routing. It does not grant redistribution rights. The packaged ISOT-derived
   model and private calibration artefact therefore remain excluded from the
   public package until documentary permission or an applicable explicit licence
   is verified.

No citation in the audited public documentation is used to claim that NewsLens
AI proves factual truth. The cited research supports methods, datasets,
limitations, and evaluation context only.
