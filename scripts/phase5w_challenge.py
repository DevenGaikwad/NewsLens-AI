"""Evaluate a sealed, project-authored challenge set without fitting anything.

The cases are new fictional exercises, separate from every benchmark partition.
Their expected outcomes and input text are fixed in this source before the first
model run. This script reads the published model and its bound calibration only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from src.fake_news_predictor import load_model, predict_credibility
from src.model_diagnostics import assess_input
from src.text_preprocessor import clean_article_text
from synthetic_benchmark.signals import FACT_FIELDS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "results" / "phase5w_challenge.json"

# title, lead, site, date, time, quantity (words, digits), result,
# attribution, rationale, status, sequence, certainty, narrative
EVENTS = (
    ("Amber Kite Register", "Aster Vale circle", "Briar Hall", "June fourth", "nine twenty", "thirty seven", "37", "amber tags counted", "Lina Voss", "practice inventory", "proposed", "catalogue before rehearsal", "tentative", "The Aster Vale circle arranged an invented registry exercise in Briar Hall. Volunteers would count coloured tags before rehearsing a small catalogue demonstration. No public office or real event is described."),
    ("Marble Finch Exercise", "Orin Grove team", "Cobalt Annex", "July eleventh", "ten fifteen", "forty two", "42", "finch cards sorted", "Dara Merin", "training exercise", "scheduled", "briefing before review", "provisional", "The Orin Grove team described a fictional card-sorting rehearsal in Cobalt Annex. Its schedule gives learners a quiet briefing and a separate review session. Every participant and location is invented."),
    ("Copper Rain Notebook", "Lumen Ford group", "Willow Studio", "August third", "eight forty", "twenty six", "26", "copper slips archived", "Neri Solan", "catalogue practice", "drafted", "survey before filing", "preliminary", "The Lumen Ford group prepared an imaginary notebook trial for Willow Studio. The group would survey the room, file coloured slips, and discuss the completeness of the fictional record."),
    ("Ivory Moth Workshop", "Mossbridge circle", "Hollow Atrium", "September ninth", "eleven thirty", "fifty one", "51", "moth tokens labelled", "Tavi Noren", "orientation practice", "approved", "label before inspection", "confirmed", "A made-up workshop at Hollow Atrium invited the Mossbridge circle to label tokens. The exercise deliberately separates a preparatory orientation from later inspection, with fictional names throughout."),
    ("Silver Reed Catalogue", "Pinecrest makers", "Juniper Room", "October sixth", "fourteen ten", "sixty four", "64", "reed samples indexed", "Elda Quen", "indexing rehearsal", "planned", "count before display", "tentative", "The Pinecrest makers imagined a catalogue for Juniper Room. Volunteers would count reed-shaped samples and then arrange a display. These details are authored solely as a classroom example."),
    ("Velvet Comet Trial", "Eastmere stewards", "Topaz Gallery", "November second", "twelve twenty", "thirty nine", "39", "comet cards grouped", "Riva Tal", "sorting demonstration", "pending", "sorting before audit", "uncertain", "Eastmere stewards invented a demonstration in Topaz Gallery using comet-shaped cards. The trial describes a small group activity followed by a separate audit of the sample cards."),
    ("Blue Heron Ledger", "Dawnwick cohort", "Elm Pavilion", "December fifth", "thirteen thirty", "seventy two", "72", "heron labels checked", "Korin Bel", "ledger practice", "scheduled", "review before dispatch", "provisional", "The Dawnwick cohort proposed an imaginary ledger session at Elm Pavilion. Learners would review heron labels before dispatching sample folders within the fictional exercise."),
    ("Quartz Meadow Notes", "Fernhaven club", "Opal Studio", "January eighth", "fifteen forty", "twenty four", "24", "quartz notes filed", "Mira Fen", "filing rehearsal", "proposed", "filing before summary", "tentative", "Fernhaven club drafted a fictional notes activity in Opal Studio. The plan sets out filing and summarisation stages and uses entirely invented people, quantities, and locations."),
)


def facts(event: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(FACT_FIELDS, (event[1], event[2], event[3], event[4], event[5], event[7], event[8], event[9], event[10], event[11], event[12]), strict=True))


def fact_line(heading: str, values: dict[str, str], *, reverse: bool = False, extra: str = "") -> str:
    keys = tuple(reversed(FACT_FIELDS)) if reverse else FACT_FIELDS
    pairs = "; ".join(f"{key}: {values[key]}" for key in keys if key in values)
    return f"{heading} - {pairs}{extra}."


def article(event: tuple[str, ...], reference: dict[str, str], account: dict[str, str], *,
            reverse: bool = False, extra: str = "", prefix: str = "", duplicate: str = "",
            reference_heading: str = "Reference note") -> str:
    intro = (f"{event[0]} is an independently invented NewsLens AI challenge. "
             f"{event[13]} The reference and account below belong only to this fictional exercise. "
             "Their comparison is not an external source check or a claim about any real news article.")
    return "\n\n".join((intro + " " + prefix + " " + extra,
                        fact_line(reference_heading, reference),
                        fact_line("Article account", account, reverse=reverse, extra=duplicate)))


def build_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []

    def add(event_index: int, category: str, expected: str, text: str) -> None:
        cases.append({"id": f"P5W-{len(cases)+1:03d}", "event": f"fiction-{event_index+1:02d}",
                      "category": category, "expected": expected, "text": text})

    changes = (("quantity", "ninety nine"), ("site", "Saffron Hall"),
               ("date", "March nineteenth"), ("lead", "Another fictional circle"),
               ("status", "not approved"), ("result", "no cards filed"),
               ("sequence", "dispatch before review"), ("certainty", "confirmed"))
    for i, event in enumerate(EVENTS):
        reference = facts(event)
        add(i, "exact agreement", "agree", article(event, reference, reference))

        changed = {**reference, changes[i][0]: changes[i][1]}
        add(i, "single factual contradiction", "conflict", article(event, reference, changed))

        # Same quantity represented in ordinary words and digits; this is a
        # semantic agreement challenge, not an exact-string match.
        equivalent = {**reference, "quantity": event[6]}
        add(i, "paraphrased agreement", "agree", article(event, reference, equivalent))

        reversed_claim = {**reference, "status": f"not {reference['status']}"}
        add(i, "paraphrased contradiction and negation", "conflict",
            article(event, reference, reversed_claim,
                    prefix="The account retains the event setting but explicitly negates its stated status."))

        if i < 4:
            reordered = reference if i % 2 == 0 else changed
            add(i, "reordered fields", "agree" if i % 2 == 0 else "conflict",
                article(event, reference, reordered, reverse=True))

        long_prose = (f"The fictional {event[0]} notes also discuss room lighting, paper texture, "
                      "volunteer arrival, and unrelated sample-card colours. These surface details "
                      "do not change the values in either structured field block. ") * 4
        longer = reference if i % 2 == 0 else changed
        add(i, "long distracting prose", "agree" if i % 2 == 0 else "conflict",
            article(event, reference, longer, extra=long_prose))

        if i < 4:
            missing = {key: value for key, value in reference.items() if key != "quantity"}
            add(i, "missing comparison field", "review", article(event, reference, missing))
            duplicate = f"; site: {('Different Gallery' if i % 2 else reference['site'])}"
            add(i, "duplicate comparison field", "review",
                article(event, reference, {**reference, "site": "Different Gallery"}, duplicate=duplicate))
            add(i, "malformed reference heading", "review",
                article(event, reference, reference, reference_heading="Reference memo"))
            add(i, "ordinary outside-scope prose", "review",
                f"{event[0]} is a wholly fictional reading exercise. {event[13]} "
                "Readers discuss which sentences express the plan most clearly, whether the "
                "description distinguishes an orientation from a later review, and how a concise "
                "summary can preserve useful context. There is no paired reference record or "
                "structured article account to compare. The text is intended for summarisation "
                "and human editorial interpretation only; a real-or-fake verdict would be "
                "unjustified. All persons, places, and activities are invented for this exercise.")
    assert len(cases) == 60
    return cases


def expected_calibration_error(labels: np.ndarray, probabilities: np.ndarray) -> float:
    result = 0.0
    for low in np.arange(0.0, 1.0, 0.1):
        high = min(1.0, low + 0.1)
        mask = (probabilities >= low) & ((probabilities < high) if high < 1 else (probabilities <= high))
        if mask.any():
            result += mask.mean() * abs(labels[mask].mean() - probabilities[mask].mean())
    return float(result)


def evaluate() -> dict[str, object]:
    cases = build_cases()
    canonical = json.dumps(cases, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    model = load_model()
    rows = []
    for case in cases:
        cleaned = clean_article_text(case["text"], remove_source_markers=False)
        diagnostics = assess_input(cleaned, model)
        result = predict_credibility(cleaned, model, diagnostics=diagnostics)
        supported = not diagnostics.domain_mismatch and not result.score_withheld
        rows.append({"id": case["id"], "event": case["event"],
                     "category": case["category"], "expected": case["expected"],
                     "displayed_outcome": result.display_label if supported else "Outside supported comparison scope",
                     "predicted_class": result.predicted_class if supported else None,
                     "diagnostic_model_class": result.predicted_class,
                     "fields_agree_probability": result.reliable_probability if supported else None,
                     "fields_conflict_probability": result.misleading_probability if supported else None,
                     "confidence": result.confidence if supported else None,
                     "review_required": result.review_required,
                     "supported_scope": supported, "input_quality_inadequate": diagnostics.input_quality_inadequate,
                     "vocabulary_coverage": diagnostics.vocabulary_coverage,
                     "review_reason": result.review_reason,
                     "leading_conflict_feature": result.explanation["supports_misleading"][:1],
                     "leading_agreement_feature": result.explanation["supports_reliable"][:1],
                     "inference_ms": round(result.processing_time_seconds * 1000, 3)})

    supported_rows = [row for row in rows if row["expected"] != "review"]
    labels = np.asarray([int(row["expected"] == "conflict") for row in supported_rows])
    predicted = np.asarray([int(row["diagnostic_model_class"] == "misleading") for row in supported_rows])
    reported_rows = [row for row in supported_rows if row["supported_scope"]]
    reported_labels = np.asarray([int(row["expected"] == "conflict") for row in reported_rows])
    probabilities = np.asarray([float(row["fields_conflict_probability"]) for row in reported_rows])
    calibration_estimable = len(set(reported_labels.tolist())) == 2
    precision, recall, f1, support = precision_recall_fscore_support(labels, predicted, labels=[0, 1], zero_division=0)
    matrix = confusion_matrix(labels, predicted, labels=[0, 1]).tolist()
    review_rows = [row for row in rows if row["expected"] == "review"]
    automatic = [row for row in supported_rows if not row["review_required"]]
    result = {
        "purpose": "Independent synthetic challenge; exploratory, correlated by fictional event; no training or tuning",
        "case_count": len(cases), "event_count": len(EVENTS),
        "case_set_sha256": hashlib.sha256(canonical).hexdigest(),
        "class_order": ["agree", "conflict"], "confusion_matrix": matrix,
        "precision": precision.tolist(), "recall": recall.tolist(), "f1": f1.tolist(), "support": support.tolist(),
        "balanced_accuracy": balanced_accuracy_score(labels, predicted),
        "macro_f1": f1_score(labels, predicted, average="macro"),
        "false_positive_rate": matrix[0][1] / sum(matrix[0]),
        "false_negative_rate": matrix[1][0] / sum(matrix[1]),
        "reported_probability_count": len(reported_rows),
        "brier_score_reported_only": float(np.mean((probabilities - reported_labels) ** 2)) if calibration_estimable else None,
        "ece_10_equal_width_reported_only": expected_calibration_error(reported_labels, probabilities) if calibration_estimable else None,
        "reported_calibration_note": "Not estimated: automatic decisions contain only one class" if not calibration_estimable else "Exploratory small challenge subset",
        "automatic_coverage_supported": len(automatic) / len(supported_rows),
        "automatic_accuracy_supported": sum((row["predicted_class"] == ("misleading" if row["expected"] == "conflict" else "reliable")) for row in automatic) / max(1, len(automatic)),
        "review_cases_routed_to_review": sum(row["review_required"] for row in review_rows),
        "review_cases_total": len(review_rows),
        "outside_scope_probabilities_withheld": all(row["fields_conflict_probability"] is None and row["confidence"] is None for row in rows if not row["supported_scope"]),
        "counterfactual_pairs": len(EVENTS),
        "counterfactual_exact_pair_flip_rate": sum(
            next(row for row in rows if row["event"] == f"fiction-{i+1:02d}" and row["category"] == "exact agreement")["diagnostic_model_class"]
            != next(row for row in rows if row["event"] == f"fiction-{i+1:02d}" and row["category"] == "single factual contradiction")["diagnostic_model_class"]
            for i in range(len(EVENTS))
        ) / len(EVENTS),
        "median_inference_ms": median(row["inference_ms"] for row in rows),
        "model_size_bytes": (ROOT / "models" / "newslens_synthetic_pipeline.joblib").stat().st_size,
        "calibration_size_bytes": (ROOT / "models" / "newslens_synthetic_calibration.json").stat().st_size,
        "categories": {category: {"count": sum(row["category"] == category for row in rows),
                                  "correct_or_reviewed": sum((row["review_required"] if row["expected"] == "review" else row["review_required"] or row["predicted_class"] == ("misleading" if row["expected"] == "conflict" else "reliable")) for row in rows if row["category"] == category)}
                       for category in dict.fromkeys(row["category"] for row in rows)},
        "cases": rows,
    }
    return result


if __name__ == "__main__":
    report = evaluate()
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"cases"}}, indent=2))
