# NewsLens Synthetic Article Benchmark v1.0.0

`newslens-synthetic-articles-v1.0.0.zip` is the deterministic public package for
the independently authored NewsLens educational benchmark.

## Release contract

- Dataset ID: `newslens-synthetic-articles-v1.0.0`
- Generator version: `1.0.0`
- Seed: `20260916`
- Fictional event pairs: 12,000
- Articles: 24,000 (12,000 per label)
- ZIP size: 10,319,934 bytes
- ZIP SHA-256: `3b6df1fa17615bfe1b67f6c9136909c668ec846e3fa8d205fa8e4aa2a80526cc`
- Dataset licence: CC BY 4.0 to the extent applicable rights subsist; see the
  package's `LICENSE.txt`

The labels mean synthetic ledger-consistent (`1`) and synthetic
ledger-contradicting (`0`) only inside the benchmark's fictional reference
world. They do not establish whether a real-world claim is true or false.

Each article has a human-readable fictional account plus structured reference
and account fields displayed as stable ten-digit codes. Matching codes agree;
different codes identify the controlled fact changes. Normal model-text
processing maps the digits to a neutral token, while the label-independent
signal extractor compares the visible codes field by field. This prevents a
raw bag-of-words shortcut based on repeated names or status words.

## Split counts

| Split | Articles | Event pairs |
|---|---:|---:|
| Training | 18,000 | 9,000 |
| Model validation | 2,400 | 1,200 |
| Calibration | 1,200 | 600 |
| Abstention-policy selection | 1,200 | 600 |
| Final test | 1,200 | 600 |

Paired articles never cross split boundaries. The final-test split is reserved
for one locked evaluation after model, calibration, and abstention-policy
decisions are complete.

## Reproduce and verify

From the repository root with `requirements-lite.txt` installed:

```bash
python scripts/generate_synthetic_benchmark.py --mode final
python scripts/generate_synthetic_benchmark.py --mode verify
```

The second command regenerates the package in an isolated temporary directory
and requires its SHA-256 to match byte for byte. The external archive metadata
is in `archive_manifest.json`; the exhaustive corpus audit is in
`../../reports/synthetic_dataset_quality_audit.json`.

The final audit records zero exact or normalized duplicates, zero cross-split
event or content-hash overlap, zero fact-code collisions, exact label-symmetric
account-value marginals, metadata-only balanced accuracy `0.509053`, and raw
text balanced accuracy `0.480864` against the fixed `0.75` ceiling.

The benchmark is synthetic, has no live evidence retrieval, is not a
professional fact-checker, and does not demonstrate real-world misinformation
detection performance. The application runtime does not load this ZIP.
