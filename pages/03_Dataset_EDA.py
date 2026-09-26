"""Synthetic benchmark provenance, composition, and release evidence."""

from __future__ import annotations

import json

import streamlit as st

from src.config import FIGURES_DIR, RESULTS_DIR
from ui import callout, configure_page, footer, metric_strip, page_header, section_heading


configure_page("NewsLens AI | Dataset Analysis", active="eda")
page_header(
    "Dataset Analysis · Synthetic Benchmark",
    "Original fiction,\nreproducible evidence.",
    "The benchmark contains only independently authored fictional articles and entities. It contains no ISOT rows, transformations, summaries, translations, or reconstructions.",
)
profile = json.loads((RESULTS_DIR / "dataset_profile.json").read_text(encoding="utf-8"))

metric_strip(
    (
        ("Articles", f"{profile['articles']:,}", "All synthetic"),
        ("Paired events", f"{profile['event_pairs']:,}", "One consistent + one contradicting"),
        ("Consistent", f"{profile['synthetic_ledger_consistent']:,}", "Balanced label"),
        ("Contradicting", f"{profile['synthetic_ledger_contradicting']:,}", "Balanced label"),
        ("Exact duplicates", str(profile['exact_duplicate_rows']), "Integrity gate"),
    )
)

section_heading("01 · Provenance", "Deterministic original generation", "The generator creates fictional civic initiatives, organizations, people, places, timelines, and visible fact ledgers from project-authored vocabularies and templates.")
st.code(f"Dataset: {profile['dataset_id']}\nArchive SHA-256: {profile['archive_sha256']}\nArchive bytes: {profile['archive_size_bytes']:,}\nLicense: {profile['license']}")
callout("Copyright boundary", "Functional compatibility is limited to labels, schemas, objectives, and application behavior. No external copyrighted article dataset was used.", kind="success")

section_heading("02 · Composition", "Balanced paired-event design", "Each fictional event has a ledger-consistent and ledger-contradicting rendering. Pair groups remain intact across all partitions.")
left, right = st.columns(2, gap="large")
with left:
    st.image(FIGURES_DIR / "class_distribution.png", use_container_width=True)
with right:
    st.image(FIGURES_DIR / "word_count_distribution.png", use_container_width=True)

section_heading("03 · Diversity", "Controlled variation without hidden labels", "Topics and templates vary across both labels. Mutations alter one or more Article account fields while preserving a visible Reference note.")
metric_strip((("Topics", profile["topics"], "Fictional domains"), ("Template families", profile["template_families"], "Authored structures"), ("Mutation families", profile["mutation_families"], "Contradiction patterns")))

section_heading("04 · Leakage and Shortcut Controls", "What was measured", "Event IDs and content hashes are checked before modelling. Baselines probe whether label-independent metadata or ordinary prose can predict the class.")
st.markdown(
    f"""
1. Cross-partition event overlap: **{profile['cross_partition_event_overlap']}**.
2. Cross-partition content-hash overlap: **{profile['cross_partition_content_hash_overlap']}**.
3. Surface-text-only balanced accuracy: **{profile['surface_text_only_balanced_accuracy']:.3f}**.
4. Metadata-only balanced accuracy: **{profile['metadata_only_balanced_accuracy']:.3f}**.
5. Final-test labels remained locked until model, calibration, and abstention choices were fixed.
"""
)
callout("Scope limit", "The benchmark evaluates a transparent synthetic ledger-consistency task. It does not represent the distribution of real journalism, languages, publishers, or political events.", kind="warning")
footer("NewsLens AI · Dataset Analysis", "Original synthetic corpus · measured provenance")
