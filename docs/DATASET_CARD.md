# Dataset Card — NewsLens Synthetic Articles v1.0.0

## Identity

- Repository path: `data/synthetic/newslens-synthetic-articles-v1.0.0.zip`
- Size: 10,319,934 bytes
- SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`
- Git blob: `cb0d5e57407be10fecefb34762e586bacd38dd56`
- Generator version: 1.0.0
- Generator seed: 20260916
- License: CC BY 4.0 to the extent applicable rights subsist; project code and application retain their separate notices.

## Provenance

The corpus was independently generated for NewsLens AI from project-authored fictional vocabularies, templates, entities, and event records. Functional compatibility is limited to label, schema, interface, objective, and application behavior.

The archive contains no ISOT row, copied phrase, close paraphrase, transformation, translation, summary, reconstruction, or private artifact. No external copyrighted article dataset was used as generation material.

## Structure

The 24,000 rows represent 12,000 event pairs. Each pair contains one `synthetic_ledger_consistent` and one `synthetic_ledger_contradicting` article. Both expose a `Reference note` and an `Article account` with eleven comparable fields.

The CSV includes article and event IDs, title, text, label, topic, template family, mutation family, authored split, generator version, seed, and content SHA-256. The archive also includes event records, generation metadata, a manifest, and documentation.

## Quality and leakage controls

- Exact row duplicates: 0.
- Cross-partition event overlap: 0.
- Cross-partition content-hash overlap: 0.
- Balanced labels: 12,000 each.
- Authored partition counts: 18,000 / 2,400 / 1,200 / 1,200 / 1,200.
- Completed generator reproducibility, schema, label-balance, paired-event, phrase-screening, and human-review evidence remains under `reports/`.

## Appropriate and inappropriate use

Appropriate uses include deterministic ML demonstrations, leakage teaching, calibration exercises, regression tests, and portfolio review. Inappropriate uses include representing the corpus as real reporting, attributing its entities to real people, or claiming it measures unrestricted real-world fake-news detection.
