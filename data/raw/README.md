# NewsLens AI — Raw Dataset Directory

Large benchmark files are intentionally excluded from the submission archive.
From the project root, run:

```bash
python training/download_data.py --dataset all
```

The downloader places `True.csv`, `Fake.csv`, and `xsum-test.parquet` here.
Source, licence, checksum, and leakage notes are documented in
`docs/DATASET_CARD.md`.
