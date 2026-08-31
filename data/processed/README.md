# NewsLens AI — Processed Dataset Directory

This directory is reserved for reproducible intermediate datasets created by
the preparation and training scripts. Processed benchmark rows are not bundled
because the original datasets have separate usage terms and are straightforward
to regenerate from `data/raw/`.

The ready-to-run application does not require this directory to contain data;
it loads the packaged pipeline from `models/fake_news_pipeline.joblib`.
