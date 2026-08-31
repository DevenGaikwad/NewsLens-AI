# NewsLens AI — Dataset Card

*ISOT classification and XSum summarization evaluation*

## 1. ISOT Fake News Dataset

**Source:** University of Victoria ISOT Research Lab, official dataset page:
<https://onlineacademiccommunity.uvic.ca/isot/2022/11/27/fake-news-detection-datasets/>

**Source reviewed:** 16 August 2026. The reviewed page describes and provides a
download for the dataset, but no explicit redistribution licence was located on
that page. Download availability is not treated as permission to redistribute
the raw data or the derived trained model.

**Purpose in this project:** supervised binary credibility-risk classification.

**Raw schema:** `title`, `text`, `subject`, `date`; class comes from the source
file (`True.csv` → reliable 0; `Fake.csv` → misleading 1). The model receives only
cleaned title + article body. Subject, source filename, and date are excluded.

| Stage | Rows |
|---|---:|
| Raw True + Fake CSVs | 44,898 |
| Exact duplicate rows removed | 5,713 |
| Short/empty rows removed | 1,302 |
| Eligible cleaned corpus | 37,883 |
| Balanced reproducible working sample | 24,000 |
| Reliable / misleading | 12,000 / 12,000 |
| Established train / original holdout | 19,200 / 4,800 |
| Quarantined holdout rows after near-duplicate screen | 2 |
| Validation / untouched final test | 2,399 / 2,399 |
| Validation calibration / threshold-policy subsets | 1,199 / 1,200 |

### Preprocessing and leakage controls

1. Missing values become empty strings and unusable rows are removed.
2. Title and body are combined, HTML entities/control characters/URLs normalised.
3. Exact duplicate model texts are removed before splitting.
4. Explicit Reuters leads, reporting/editing bylines, and wire markers are
   neutralised in training and inference.
5. Source/subject metadata is not a feature.
6. A fixed seed-42 stratified 80/20 split reconstructs the verified production-model evidence.
7. A deterministic approximate five-gram screen identifies high-similarity candidates, verifies them at Jaccard similarity at least 0.90, quarantines two contaminated holdout members, and keeps remaining near-duplicate groups inside one final partition.
8. The clean holdout is split into validation and untouched final-test partitions. Validation is internally divided for Platt calibration and threshold-policy selection.
9. TF-IDF is fitted only inside the training Pipeline. Calibration and the editorial-review threshold do not use final-test labels.

Dataset SHA-256 checksums for the measured run are stored in
`models/model_metadata.json`. The training script intentionally uses a balanced
sample to control runtime on a student laptop; it does not invent labels.

### Known limitations

True-labelled stories are largely Reuters reports while fake-labelled stories
come from other outlets; subject values also differ. Outlet, topic, period, and
writing-style artefacts can yield unrealistically high random-split results even
after marker mitigation. Publisher/event groups are not available consistently
enough for a reliable group split. The dataset is English-heavy and political,
with limited time and regional diversity. Licence/redistribution terms must be
established from authoritative evidence before republishing raw files or the
trained artefact; therefore the large CSVs are downloaded separately and
excluded from every release archive. The trained model and dataset-derived
calibration parameters remain private and
deployment-gated as recorded in `docs/MODEL_REDISTRIBUTION_DECISION.md`.

## 2. XSum

**Primary source:** Edinburgh NLP XSum project repository:
<https://github.com/EdinburghNLP/XSum>

**Evaluation distribution route:**
<https://huggingface.co/datasets/EdinburghNLP/xsum>

**Purpose in this project:** evaluation of the implemented extractive summarizer
against human-written one-sentence reference summaries.

**Schema:** `document` (BBC article), `summary` (one-sentence reference), `id`.
The reported evaluation samples 150 test examples with seed 42. Only derived
per-example ROUGE values and aggregate metrics are packaged, not article text.

| Actual metric | Value |
|---|---:|
| ROUGE-1 precision / recall / F1 | 0.098031 / 0.439227 / 0.153559 |
| ROUGE-2 precision / recall / F1 | 0.017256 / 0.089341 / 0.027824 |
| ROUGE-L precision / recall / F1 | 0.065309 / 0.297377 / 0.102530 |
| Mean compression ratio | 70.6572% |
| Mean latency | 3.368 ms/article |

XSum is deliberately “extreme” and highly abstractive. Low extractive overlap is
therefore expected. ROUGE does not measure factual consistency, completeness,
fairness, or readability by itself. The dataset's usage/licence status should be
checked at the current host before redistribution; raw parquet is excluded.

## 3. Packaged sample data

`data/sample/` contains three original synthetic teaching articles and a tiny CSV.
Scenario labels are for UI demonstration only. These samples were **not** used for
training or reported evaluation and do not imply real-world truth labels.

## Download and placement

From the project root:

```bash
python training/download_data.py --dataset all
```

Or manually place `True.csv`, `Fake.csv`, and `xsum-test.parquet` under
`data/raw/`. No Kaggle account is required for the selected official sources.
