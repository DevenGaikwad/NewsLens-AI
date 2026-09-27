# Public Deployment Model and License Audit

## Decision

Public deployment is now technically and legally scoped to the independently created synthetic package. The earlier private ISOT-derived classifier and calibration remain excluded and are not used by training, runtime, tests, repository artifacts, or deployment.

## Evidence

- Dataset: `newslens-synthetic-articles-v1.0.0`, original fictional content.
- Dataset license: CC BY 4.0 to the extent applicable rights subsist.
- Public model hash: `c1ad8c044cd95bc7bf25a94716010ddbe21fbae2ec92a0c1cefb01f5c3c979c6`.
- Public calibration hash: `adcf03a860ef8fb41058b3a4dcc80351dbd02e05f81e0fc1e7f971624af6ab77`.
- Binding: calibration `model_sha256` equals the public model SHA-256.
- External copyrighted training data: none.
- Private ISOT content or derived artifact: none.

## Limit

This audit does not convert a synthetic benchmark result into a claim about unrestricted real-world truth detection. The deployed app must retain its synthetic scope and abstention wording.

## Phase 5U general-news screening feasibility decision

**Gate: not met.** The candidates checked below do not provide an affirmatively licensed, provenance-clear corpus of full news articles with suitable real/fake labels for redistribution, derivative public model release, and both noncommercial and commercial deployment. This is a decision about these candidates and this proposed task, not a claim that no suitable dataset could ever exist. No candidate data were downloaded, trained on, or published.

| Candidate and authoritative record | Provenance, labels, and time | Rights, article text, and task fit |
|---|---|---|
| [FakeNewsNet maintainer README](https://github.com/KaiDMML/FakeNewsNet#overview) | PolitiFact and GossipCop real/fake article identifiers; article publish dates may be collected by its downloader. Social data include Twitter user activity. | Maintainers explicitly say the complete dataset cannot be distributed because of publisher copyright and platform privacy policy. The distributed minimal CSVs contain IDs, URLs, titles, and tweet IDs, not a licensed full-article corpus. Re-scraping publisher articles would not establish redistribution rights. **Reject.** |
| [LIAR original paper](https://aclanthology.org/P17-2067/) | Approximately 12,800 manually labeled PolitiFact statements over a decade, reported in 2017. | These are short claims in context, not full news articles. A paper's public availability or license is not evidence of a transferable license to all underlying PolitiFact material or a released article corpus. **Reject for this task.** |
| [FEVER dataset and license](https://fever.ai/dataset/fever.html) | 185,445 altered Wikipedia-derived claims, labeled Supports, Refutes, or NotEnoughInfo; accompanying Wikipedia evidence from a June 2017 dump. | The dataset's license follows applicable Wikipedia terms, with CC BY-SA 3.0 as fallback. It is a claim/evidence verification benchmark, not an ordinary real/fake full-news-article dataset. **Reject for this task.** |
| [AVeriTeC dataset and license](https://fever.ai/dataset/averitec.html) | 4,568 real-world claims from 50 fact-checking organizations, four verdict labels, dates and source metadata, with linked web evidence. | The linked license is [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The task and included text are claims with evidence, not licensed complete news articles. Noncommercial terms do not establish the requested commercial compatibility, and linked publisher pages retain separate rights. **Reject for this task.** |

The candidates do not justify mapping a source's reputation or a fact-check of one claim to the truth of an entire pasted article. They do not establish a matched, labeled article collection with reliable event/source/topic and temporal partitions. A credible next phase would first obtain explicit rights for each full-text source and model redistribution, document the labeling process and collection dates, and then build grouped exact/near-duplicate-safe evaluation with source/style/topic baselines, calibration, and abstention. Until that evidence exists, **no general-news model, metrics, or beginner-facing real/fake outcome is released**. The existing public `Reference comparison` task and frozen artifacts remain in place.
