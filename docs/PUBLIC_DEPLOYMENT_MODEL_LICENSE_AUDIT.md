# Public deployment model dataset licence audit

Audit date: 1 September 2026  
Decision: **NO-GO — no public model was trained, committed, released, or deployed**

## Purpose and decision standard

This record evaluates whether NewsLens AI can train and publicly distribute a
separate deployment model without publishing or changing the private
ISOT-derived research model. A candidate must provide documented rights to use,
modify, and redistribute the complete training corpus and a resulting model,
including the rights for every upstream source whose article text is included.
A repository download, an “open” label, or an aggregate-dataset licence is not
treated as proof that third-party article copyrights were cleared.

This is a release-engineering decision, not legal advice.

## Preferred candidate: WELFake

| Field | Audited evidence |
|---|---|
| Record | [WELFake dataset for fake news detection in text data](https://doi.org/10.5281/zenodo.4561253) |
| Record/version | Zenodo record `4561253`; [catalogue version `0.1`](https://live.european-language-grid.eu/catalogue/corpus/21953); published 25 February 2021 and modified 9 April 2021 |
| Creators | Pawan Kumar Verma, Prateek Agrawal, and Radu Prodan |
| Declared licence | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| Required attribution | Credit the creators, link the record and licence, and identify modifications without implying endorsement |
| Corpus | 72,134 English articles: 35,028 real and 37,106 fake, merged from Kaggle, McIntire, Reuters, and BuzzFeed Political |

CC BY 4.0 permits sharing and adaptation, including commercial use, for rights
the licensor actually controls. It does not itself supply permissions for
third-party material outside that rights grant. A trained model could only be
approved for public distribution after the inputs' complete rights chain and
the model's required notices were established.

### Upstream provenance findings

1. The [WELFake paper](https://doi.org/10.1109/TCSS.2021.3068519) says the
   corpus combines Kaggle, McIntire, Reuters, and BuzzFeed article datasets. It
   also states that the Kaggle component lacks source information and that the
   McIntire labels lack authentic confirmation.
2. The cited [Kaggle Fake News competition data](https://www.kaggle.com/c/fake-news/data)
   is marked “Subject to Competition Rules”; no general CC or other public
   redistribution licence for its article text was located.
3. The current [George McIntire dataset repository](https://github.com/GeorgeMcIntire/fake_real_news_dataset)
   contains the CSV and a short reuse request but no licence file or express
   dataset grant. The WELFake paper instead cites a
   [GPL-3.0 downstream analysis repository](https://github.com/lutzhamel/fake-news),
   whose README identifies McIntire as the source. A downstream code licence
   does not establish that repository author's authority to relicense the
   source article corpus.
4. The cited [BuzzFeed Political derivative corpus](https://github.com/BenjaminDHorne/fakenewsdata1)
   contains a permissive notice from its compilers, but its README says full
   article bodies were collected from named third-party publishers. No source-
   by-source article licence or permission chain is supplied.
5. The “Reuters” component is not accompanied by a source-specific licence in
   the WELFake record or paper. The project already records the same unresolved
   full-text/model-redistribution problem for the ISOT/Reuters-derived private
   workflow in [`MODEL_REDISTRIBUTION_DECISION.md`](MODEL_REDISTRIBUTION_DECISION.md).

### WELFake conclusion

**Rejected for public model training and redistribution.** The Zenodo-level CC
BY 4.0 declaration is clear, but the deposit does not establish that the
depositors could grant that licence over all incorporated article text. The
uncertainty affects the proposed public training input and therefore prevents a
positive derivative-model redistribution decision. The WELFake CSV was not
downloaded.

## Alternative candidate screen

| Candidate | Rights/provenance result | Suitability result | Decision |
|---|---|---|---|
| [FA-KES / SVDC](https://doi.org/10.5281/zenodo.2532642) | The deposit is publicly available, but the record describes collected news articles and does not document a source-by-source full-text licence chain. | English article classification, but small and narrowly limited to the Syrian conflict. | Rejected: rights chain incomplete. |
| [FakeNewsAMT](https://arxiv.org/abs/1708.07104) | Available mirrors report an unknown dataset licence; legitimate articles came from mainstream news websites. | English article classification, but only 480 crowdsourced/legitimate items and no adequate distribution grant. | Rejected: licence and upstream rights incomplete. |
| [COVID19FN](https://doi.org/10.17632/b96v5hmfv6.1) | The Mendeley record declares CC BY 4.0, but says articles were scraped from Poynter and other fact-checking sites without documenting their full-text sublicences. | English article classification, but COVID-19-specific. | Rejected: aggregate licence does not resolve upstream text rights. |
| [Multi-Fake-DetectiVE](https://doi.org/10.17632/s3mfjxcg68.1) | The Mendeley record declares CC BY 4.0, but the corpus was downloaded from Twitter and news sources; no complete underlying content-licence chain was located. | English news classification, but conflict- and platform-specific. | Rejected: upstream rights incomplete. |
| [MegaFake](https://github.com/zhe-wang0018/MegaFake) | The repository declares CC BY 4.0 but derives its texts from FakeNewsNet/GossipCop/PolitiFact and requires a request form and email for dataset access. | English generated-news classification, but the inherited full-text chain is unresolved and third-party permission requests are outside this task. | Rejected: rights chain and access gate unresolved. |
| [FEVER](https://fever.ai/dataset/fever.html) | The official licence explicitly traces annotations to Wikipedia and applies the relevant Wikipedia/CC BY-SA terms. | Claims with Supported/Refuted/NotEnoughInfo labels, not English news articles; substituting it would materially change the product task and label meaning. | Rights traceable, but rejected as technically unsuitable. |
| [Japanese FakeNews Dataset](https://github.com/tanreinama/Japanese-Fakenews-Dataset) | The repository traces human text to Japanese Wikinews Creative Commons terms and identifies GPT-2-generated derivatives. | Japanese, not English; machine-generated-text detection is not the existing article-credibility task. | Rights comparatively clear, but rejected as technically unsuitable. |

No candidate passed both the rights and product-suitability gates. No dataset was
downloaded and no custom or synthetic substitute was created to force a result.

## Consequences for NewsLens AI

- The private `isot-tfidf-lr-v1.0.0` artifact and its hash-bound calibration
  remain unchanged and private.
- The public repository continues to exclude
  `models/fake_news_pipeline.joblib`,
  `models/confidence_calibration.json`, raw ISOT files, and all candidate raw
  datasets.
- No public-model architecture, artifact, calibration, metrics, or comparison
  is claimed because training was prohibited by the licence gate.
- The existing 52 public model-independent tests and four private-artifact-gated
  tests remain the applicable baseline; no test was weakened.
- Streamlit functional deployment remains blocked. Vercel remains downstream of
  a verified Streamlit URL and was not started.

## Exact evidence required to resume

Resume the public deployment-model stage only when one of these is available:

1. a source-by-source permission/licence record covering the complete WELFake
   article corpus, public model training, redistribution of the trained artifact,
   and public hosting; or
2. a different English article-level credibility dataset whose official record
   documents the complete upstream provenance and grants reuse, modification,
   public redistribution, and model-training/hosting rights.

After that evidence is recorded, create a new model branch, train the separately
named public deployment model, apply the prescribed same-evaluation-set quality
gate, and open a protected pull request. Do not move or reuse
`public-release-2026-09-01`.

## Primary sources reviewed

- [WELFake Zenodo record](https://doi.org/10.5281/zenodo.4561253)
- [WELFake paper](https://doi.org/10.1109/TCSS.2021.3068519)
- [Creative Commons Attribution 4.0 deed and legal-code link](https://creativecommons.org/licenses/by/4.0/)
- [Kaggle Fake News competition data](https://www.kaggle.com/c/fake-news/data)
- [George McIntire dataset repository](https://github.com/GeorgeMcIntire/fake_real_news_dataset)
- [Lutz Hamel downstream McIntire analysis](https://github.com/lutzhamel/fake-news)
- [Horne and Adalı article corpus](https://github.com/BenjaminDHorne/fakenewsdata1)
- [FA-KES / SVDC Zenodo record](https://doi.org/10.5281/zenodo.2532642)
- [FakeNewsAMT paper](https://arxiv.org/abs/1708.07104)
- [COVID19FN Mendeley record](https://doi.org/10.17632/b96v5hmfv6.1)
- [Multi-Fake-DetectiVE Mendeley record](https://doi.org/10.17632/s3mfjxcg68.1)
- [MegaFake official repository](https://github.com/zhe-wang0018/MegaFake)
- [FEVER dataset and licence](https://fever.ai/dataset/fever.html)
- [Japanese FakeNews Dataset repository](https://github.com/tanreinama/Japanese-Fakenews-Dataset)
