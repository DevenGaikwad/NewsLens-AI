"""Sealed, independently authored confirmation cases for one Phase 5X decision.

This module neither loads nor fits a model. Its fictional events and expected
outcomes were fixed before the Phase 5X candidate was evaluated. The cases are
separate from the original benchmark and the exploratory Phase 5W challenge.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from synthetic_benchmark.signals import FACT_FIELDS

SEAL_PATH = ROOT / "reports/results/phase5x_confirmation_seal.json"

# Name, lead, site, date, time, quantity in words, quantity in digits,
# result, attribution, rationale, status, sequence, certainty, fresh context.
EVENTS = (
    ("Ochre Compass Practice", "Bellmere learners", "Harbor Loft", "February twelfth", "nine ten", "thirty one", "31", "compass tabs indexed", "Sela Orrin", "map-reading rehearsal", "draft", "sorting before display", "tentative", "A classroom group sketches routes on invented maps and files coloured compass tabs after a morning practice."),
    ("Paper Tern Exchange", "Rillhaven tutors", "Fable Courtyard", "March twenty first", "ten forty", "fifty eight", "58", "tern cards exchanged", "Ivo Nerin", "peer-learning exercise", "planned", "orientation before exchange", "provisional", "An imaginary exchange pairs paper birds with handwritten prompts in a courtyard created for this exercise."),
    ("Cedar Prism Inventory", "Westhaven students", "Citrine Chamber", "April seventh", "eleven five", "sixty three", "63", "prism tiles catalogued", "Esen Vale", "inventory lesson", "approved", "counting before storage", "confirmed", "The cohort uses wooden tokens to rehearse a small inventory before placing them into fictional storage boxes."),
    ("Moss Lantern Exercise", "Ternwick makers", "Garnet Alcove", "May eighteenth", "twelve thirty", "twenty nine", "29", "lantern patterns reviewed", "Uma Farren", "drawing practice", "scheduled", "sketching before review", "tentative", "Participants in a made-up studio compare sketches of lanterns while discussing how to label the drawings."),
    ("Indigo Pebble Register", "Narrowbrook circle", "Pine Atrium", "June twenty third", "thirteen fifteen", "forty six", "46", "pebble slips filed", "Joren Pell", "recordkeeping lesson", "pending", "filing before audit", "uncertain", "An invented circle prepares a small set of paper slips for a recordkeeping game in a fictional atrium."),
    ("Chalk Heron Briefing", "Larkford guides", "Amber Workshop", "July fourteenth", "fourteen twenty", "seventy four", "74", "heron charts assembled", "Risa Mellen", "charting tutorial", "proposed", "briefing before assembly", "preliminary", "The tutorial describes a fictional briefing followed by the assembly of hand-drawn bird charts."),
    ("Walnut Orbit Survey", "Farpoint class", "Mallow Studio", "August twenty sixth", "fifteen five", "thirty four", "34", "orbit markers surveyed", "Toma Venn", "survey rehearsal", "accepted", "survey before archiving", "confirmed", "A group of imaginary learners marks circles on paper and stores its notes after a short classroom survey."),
    ("Lilac Harbor Ledger", "Sablefield club", "Quartz Annex", "September seventeenth", "eight fifty", "fifty two", "52", "harbor notes sorted", "Nila Fenwick", "filing lesson", "draft", "sorting before summary", "tentative", "The club invents a harbor-themed filing lesson using cards that represent no actual port or shipment."),
    ("Copper Orchard Trial", "Aldercrest mentors", "Bluebell Room", "October twenty eighth", "nine thirty", "sixty seven", "67", "orchard labels checked", "Oren Kir", "label-check practice", "planned", "inspection before display", "provisional", "Mentors describe an imaginary orchard made of paper labels to practice recording the order of checks."),
    ("Sandglass Willow Notes", "Brookmoor team", "Ivory Gallery", "November thirteenth", "ten twenty", "twenty five", "25", "willow sheets annotated", "Veda Rell", "annotation workshop", "scheduled", "reading before annotation", "confirmed", "The team annotates sheets about fictional trees during a brief educational workshop."),
    ("Coral Atlas Session", "Merewick cohort", "Slate Pavilion", "December nineteenth", "eleven forty", "eighty one", "81", "atlas inserts arranged", "Kira Thorne", "layout rehearsal", "proposed", "layout before discussion", "preliminary", "Students arrange invented atlas inserts in a pavilion and discuss how their layout affects readability."),
    ("Pearl Ridge Catalogue", "Fenmoor scholars", "Copper Room", "January twenty ninth", "twelve ten", "forty three", "43", "ridge samples listed", "Milo Saren", "catalogue lesson", "pending", "listing before review", "uncertain", "Scholars draft a catalogue of fictional ridge samples and schedule a later classroom review."),
)


def _facts(event: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(FACT_FIELDS, (event[1], event[2], event[3], event[4], event[5], event[7], event[8], event[9], event[10], event[11], event[12]), strict=True))


def _line(heading: str, values: dict[str, str], *, reverse: bool = False, duplicate: str = "") -> str:
    fields = tuple(reversed(FACT_FIELDS)) if reverse else FACT_FIELDS
    return f"{heading} - " + "; ".join(f"{field}: {values[field]}" for field in fields if field in values) + duplicate + "."


def _article(event: tuple[str, ...], reference: dict[str, str], account: dict[str, str], *, reverse: bool = False, duplicate: str = "", heading: str = "Reference note") -> str:
    opening = (
        f"{event[0]} is a wholly invented classroom account. {event[13]} "
        "The following two records are authored for comparison, not obtained from an outside authority. "
        "A reader should use the visible records to examine the limited exercise rather than infer any real-world fact."
    )
    return "\n\n".join((opening, _line(heading, reference), _line("Article account", account, reverse=reverse, duplicate=duplicate)))


def build_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    changes = (
        ("quantity", "thirty two"), ("site", "River Gallery"), ("date", "March twenty second"),
        ("lead", "a second fictional cohort"), ("status", "not pending"), ("result", "no labels were checked"),
        ("sequence", "archiving before survey"), ("certainty", "unconfirmed"), ("time", "sixteen fifty"),
        ("attribution", "another invented tutor"), ("rationale", "a different rehearsal"), ("quantity", "forty four"),
    )
    for index, event in enumerate(EVENTS):
        reference = _facts(event)
        changed = {**reference, changes[index][0]: changes[index][1]}
        double = {**changed, "result": "no sample sheets were prepared"}
        equivalent = {**reference, "quantity": event[6]}
        rows = (
            ("exact agreement", "agree", _article(event, reference, reference)),
            ("numeric paraphrase agreement", "agree", _article(event, reference, equivalent, reverse=True)),
            ("single-field counterfactual", "conflict", _article(event, reference, changed, reverse=index % 2 == 0)),
            ("two-field counterfactual", "conflict", _article(event, reference, double, reverse=index % 2 == 1)),
        )
        if index % 3 == 0:
            incomplete = {key: val for key, val in reference.items() if key != "site"}
            review = ("missing field", "review", _article(event, reference, incomplete))
        elif index % 3 == 1:
            review = ("duplicate field", "review", _article(event, reference, changed, duplicate="; site: a third room"))
        else:
            review = ("ordinary prose", "review", (
                f"{event[0]} is invented. {event[13]} "
                "Readers discuss the order of a rehearsal, the clarity of the written account, "
                "and the difference between a summary and external verification. No paired "
                "reference and account fields are provided for an automatic comparison. "
                "Every activity and person in this example is fictional."
            ))
        for category, expected, text in (*rows, review):
            cases.append({"id": f"P5X-{len(cases)+1:03d}", "event": f"confirmation-{index+1:02d}", "category": category, "expected": expected, "text": text})
    assert len(cases) == 60
    return cases


def case_hash(cases: list[dict[str, str]]) -> str:
    serialized = json.dumps(cases, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    cases = build_cases()
    payload = {
        "purpose": "Independent one-time confirmation for Phase 5X, never used in candidate fitting or threshold selection",
        "case_count": len(cases), "event_count": len(EVENTS),
        "expected_counts": {name: sum(case["expected"] == name for case in cases) for name in ("agree", "conflict", "review")},
        "case_set_sha256": case_hash(cases),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    if SEAL_PATH.exists():
        assert json.loads(SEAL_PATH.read_text()) == payload, "Confirmation seal changed; stop."
    else:
        SEAL_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
