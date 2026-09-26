# Public Release Audit

The release gate is implemented by `scripts/audit_public_release.py` and fails closed.

It checks:

1. dataset archive path, 10,319,934-byte size, SHA-256, and Git blob;
2. public model and calibration existence, size, SHA-256, and exact binding;
3. synthetic-only manifest declaration and absence of historical private artifact paths;
4. secret, key, personal-data, and absolute local-path patterns;
5. forbidden runtime/cache/database files;
6. local Markdown links and internal navigation controls;
7. legal and attribution files;
8. the remaining live Streamlit URL publication gate.

Before deployment the scan may run with `--allow-publication-gates`, which permits only the explicitly reported unresolved URL while preserving every safety and artifact-integrity gate. After deployment it must pass without that flag.

The sanitized machine-readable result is `reports/results/public_release_scan.json`. Finding contents are never printed to shared CI logs.
