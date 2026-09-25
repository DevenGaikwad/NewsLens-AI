"""Deterministically author the NewsLens Synthetic Article Benchmark.

The generator uses only project-authored fictional lexicons, event ledgers,
sentence components, article structures, and mutation rules.  It does not call
an external service or read any third-party news dataset.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from .signals import fact_value_code


DATASET_ID = "newslens-synthetic-articles-v1.0.0"
DATASET_NAME = "NewsLens Synthetic Article Benchmark v1.0.0"
GENERATOR_VERSION = "1.0.0"
RANDOM_SEED = 20260916
FINAL_EVENT_COUNT = 12_000
PILOT_EVENT_COUNT = 500
ARTICLE_COLUMNS = (
    "article_id",
    "event_id",
    "title",
    "text",
    "label",
    "label_name",
    "topic",
    "template_family",
    "mutation_family",
    "split",
    "generator_version",
    "seed",
    "content_sha256",
)
SPLIT_COUNTS_PER_TOPIC = {
    "training": 750,
    "model_validation": 100,
    "calibration": 50,
    "abstention_policy": 50,
    "final_test": 50,
}
MUTATION_FAMILIES = (
    "entity_substitution",
    "location_contradiction",
    "date_time_displacement",
    "quantity_change",
    "result_reversal",
    "attribution_change",
    "causal_fabrication",
    "policy_status_inversion",
    "sequence_reversal",
    "unsupported_certainty",
)
TEMPLATE_FAMILIES = (
    "briefing_first",
    "scene_first",
    "record_first",
    "impact_first",
    "timeline_first",
    "operations_first",
    "community_first",
    "context_first",
)


@dataclass(frozen=True)
class TopicSpec:
    slug: str
    display_name: str
    institution_types: tuple[str, ...]
    initiative_names: tuple[str, ...]
    actions: tuple[str, ...]
    units: tuple[str, ...]
    objectives: tuple[str, ...]
    results: tuple[str, ...]
    reverse_results: tuple[str, ...]
    roles: tuple[str, ...]
    participants: tuple[str, ...]


TOPICS = (
    TopicSpec(
        "civic_administration",
        "Civic administration",
        ("Civic Registry", "Resident Services Office", "Municipal Access Bureau"),
        ("Service Window Plan", "Permit Access Programme", "Neighbourhood Desk Project"),
        ("open a rotating service desk", "extend permit appointments", "publish a revised service roster"),
        ("appointments", "service slots", "permit consultations"),
        ("shorten routine waiting times", "bring services closer to outer wards", "coordinate requests through one timetable"),
        ("the opening timetable remained in place", "the service target was reached", "the first operating cycle concluded"),
        ("the opening timetable was withdrawn", "the service target was missed", "the first operating cycle was suspended"),
        ("registry coordinator", "resident-services director", "civic operations lead"),
        ("ward clerks", "resident panels", "permit advisers"),
    ),
    TopicSpec(
        "education",
        "Education",
        ("Learning Council", "Community Academy Office", "Scholarship Board"),
        ("Study Access Scheme", "Learning Studio Initiative", "Mentor Hours Programme"),
        ("open evening study rooms", "add mentor sessions", "allocate community scholarship places"),
        ("study places", "mentor sessions", "scholarship places"),
        ("expand access to supervised study", "support project-based learning", "coordinate academic mentoring"),
        ("the planned learning cycle began", "the allocated places were filled", "the mentor schedule was completed"),
        ("the planned learning cycle was cancelled", "the allocated places remained vacant", "the mentor schedule was abandoned"),
        ("learning programme coordinator", "academy planning lead", "scholarship secretary"),
        ("student councils", "family representatives", "learning mentors"),
    ),
    TopicSpec(
        "transport",
        "Transport",
        ("Transit Coordination Office", "Route Planning Cooperative", "Mobility Services Board"),
        ("Connector Route Pilot", "Neighbourhood Shuttle Plan", "Interchange Access Project"),
        ("begin a connector route", "add off-peak shuttle journeys", "reorganise interchange bays"),
        ("daily journeys", "shuttle departures", "interchange bays"),
        ("reduce transfer delays", "link outer neighbourhoods", "make off-peak travel more predictable"),
        ("the service entered its published timetable", "the transfer target was met", "the first route cycle finished"),
        ("the service was removed from the timetable", "the transfer target was missed", "the first route cycle ended early"),
        ("route operations coordinator", "mobility planning director", "interchange manager"),
        ("driver representatives", "passenger panels", "route stewards"),
    ),
    TopicSpec(
        "environment",
        "Environment",
        ("Watershed Stewardship Office", "Habitat Renewal Council", "Urban Canopy Cooperative"),
        ("Brook Renewal Plan", "Shade Corridor Initiative", "Wetland Edge Project"),
        ("restore a stream corridor", "plant a shaded walking belt", "stabilise a wetland boundary"),
        ("native plantings", "survey plots", "restoration sections"),
        ("improve habitat continuity", "reduce exposed soil", "create a repeatable seasonal survey"),
        ("the first restoration section was accepted", "the planting target was reached", "the survey cycle was completed"),
        ("the first restoration section was rejected", "the planting target was missed", "the survey cycle was halted"),
        ("habitat programme coordinator", "watershed planning lead", "canopy project director"),
        ("volunteer stewards", "neighbourhood observers", "field survey teams"),
    ),
    TopicSpec(
        "science",
        "Science",
        ("Applied Observation Institute", "Field Research Council", "Civic Science Laboratory"),
        ("Sky Sensor Study", "Water Pattern Survey", "Materials Observation Project"),
        ("deploy a network of observation sensors", "begin a seasonal field survey", "open a shared measurement station"),
        ("sensor stations", "observation rounds", "measurement kits"),
        ("compare repeated observations", "publish a transparent measurement schedule", "support classroom research exercises"),
        ("the observation cycle produced a complete record", "the station met its sampling target", "the scheduled survey concluded"),
        ("the observation cycle produced no usable record", "the station missed its sampling target", "the scheduled survey was discontinued"),
        ("field study coordinator", "observation programme lead", "laboratory operations director"),
        ("student observers", "field technicians", "community science groups"),
    ),
    TopicSpec(
        "technology",
        "Technology",
        ("Digital Services Laboratory", "Community Systems Office", "Local Technology Cooperative"),
        ("Shared Sensor Network", "Civic Kiosk Pilot", "Open Device Lab"),
        ("install shared information kiosks", "begin a low-power sensor pilot", "open a device repair laboratory"),
        ("public devices", "sensor nodes", "repair appointments"),
        ("improve access to routine information", "measure local infrastructure conditions", "extend the usable life of small devices"),
        ("the system completed its first operating period", "the device target was reached", "the service remained available as scheduled"),
        ("the system failed its first operating period", "the device target was missed", "the service was taken offline"),
        ("systems programme coordinator", "digital service director", "device laboratory lead"),
        ("accessibility advisers", "maintenance technicians", "resident user panels"),
    ),
    TopicSpec(
        "agriculture",
        "Agriculture",
        ("Field Practice Cooperative", "Grower Support Council", "Regional Crop Office"),
        ("Water Use Demonstration", "Seed Exchange Plan", "Soil Observation Programme"),
        ("open demonstration plots", "coordinate a seed exchange", "begin a soil observation cycle"),
        ("demonstration plots", "seed lots", "field observations"),
        ("compare low-waste field practices", "share locally adapted planting material", "record seasonal soil conditions"),
        ("the field cycle reached its planned close", "the exchange target was met", "the observation record was completed"),
        ("the field cycle was abandoned", "the exchange target was missed", "the observation record was left incomplete"),
        ("field programme coordinator", "grower council secretary", "crop services director"),
        ("grower groups", "field advisers", "cooperative members"),
    ),
    TopicSpec(
        "public_health_administration",
        "Public health administration",
        ("Community Health Administration Office", "Appointment Services Board", "Public Wellness Registry"),
        ("Appointment Access Plan", "Records Desk Initiative", "Community Information Schedule"),
        ("extend administrative appointment hours", "open a records assistance desk", "publish a community information schedule"),
        ("administrative appointments", "records consultations", "information sessions"),
        ("reduce paperwork delays", "clarify non-clinical service routes", "coordinate administrative access points"),
        ("the administrative schedule was completed", "the appointment target was reached", "the records desk opened as planned"),
        ("the administrative schedule was cancelled", "the appointment target was missed", "the records desk did not open"),
        ("administration coordinator", "appointment services director", "records programme lead"),
        ("service clerks", "community liaison groups", "records advisers"),
    ),
    TopicSpec(
        "local_business",
        "Local business",
        ("Market Development Cooperative", "Small Enterprise Council", "Neighbourhood Trade Office"),
        ("Shared Stall Programme", "Workshop Access Plan", "Local Supplier Forum"),
        ("open shared market stalls", "schedule small-workshop access", "convene a local supplier forum"),
        ("vendor places", "workshop sessions", "supplier meetings"),
        ("lower entry barriers for small traders", "share practical equipment", "coordinate local purchasing information"),
        ("the first market cycle met its target", "the workshop schedule was completed", "the supplier forum concluded"),
        ("the first market cycle missed its target", "the workshop schedule was cancelled", "the supplier forum was dissolved"),
        ("market programme coordinator", "enterprise council director", "trade office lead"),
        ("vendor groups", "workshop stewards", "small supplier panels"),
    ),
    TopicSpec(
        "culture",
        "Culture",
        ("Community Arts Archive", "Local Heritage Council", "Cultural Programme Office"),
        ("Neighbourhood Exhibition", "Oral History Schedule", "Shared Performance Series"),
        ("open a neighbourhood exhibition", "begin an oral history schedule", "stage a shared performance series"),
        ("exhibited works", "recorded sessions", "scheduled performances"),
        ("make local collections easier to explore", "preserve community accounts", "share rehearsal and performance space"),
        ("the programme completed its opening cycle", "the collection target was reached", "the scheduled series concluded"),
        ("the programme ended before opening", "the collection target was missed", "the scheduled series was cancelled"),
        ("arts programme coordinator", "heritage council secretary", "cultural operations director"),
        ("artist groups", "archive volunteers", "community performers"),
    ),
    TopicSpec(
        "sports_administration",
        "Sports administration",
        ("Community Athletics Council", "League Services Office", "Recreation Scheduling Board"),
        ("Shared Ground Schedule", "Youth League Calendar", "Equipment Access Plan"),
        ("publish a shared ground schedule", "begin a youth league calendar", "open an equipment access desk"),
        ("scheduled fixtures", "participating clubs", "equipment bookings"),
        ("reduce venue clashes", "coordinate club calendars", "make shared equipment easier to reserve"),
        ("the schedule completed its first round", "the club target was reached", "the booking service opened"),
        ("the schedule was withdrawn before the first round", "the club target was missed", "the booking service remained closed"),
        ("league operations coordinator", "recreation planning lead", "athletics council director"),
        ("club delegates", "ground stewards", "youth organisers"),
    ),
    TopicSpec(
        "community_infrastructure",
        "Community infrastructure",
        ("Neighbourhood Works Agency", "Shared Facilities Council", "Community Infrastructure Office"),
        ("Footbridge Renewal", "Library Room Upgrade", "Water Point Improvement"),
        ("renew a pedestrian connection", "upgrade shared library rooms", "improve a community water point"),
        ("work sections", "shared rooms", "service fixtures"),
        ("improve everyday access", "extend the useful life of shared facilities", "make routine maintenance easier to schedule"),
        ("the first work stage passed inspection", "the upgrade target was reached", "the facility reopened on schedule"),
        ("the first work stage failed inspection", "the upgrade target was missed", "the facility remained closed"),
        ("works programme coordinator", "facilities council director", "infrastructure planning lead"),
        ("maintenance crews", "resident observers", "facility stewards"),
    ),
)


ORG_STEMS = (
    "Avelor", "Brenwick", "Cindara", "Dorell", "Esmere", "Farlon", "Galenor",
    "Hespera", "Ilynd", "Joravel", "Kelmora", "Luneth", "Merovan", "Nirel",
    "Orlissa", "Pavren", "Quenara", "Ravelle", "Sorevin", "Talmere", "Ulden",
    "Virela", "Wendara", "Xandrel", "Yorven", "Zelora",
)
PLACE_STEMS = (
    "Avenmere", "Brelon", "Cindra", "Dovarin", "Elmsora", "Fendrel", "Gavora",
    "Helwick", "Iverna", "Jaspen", "Korell", "Lydora", "Marnel", "Novara",
    "Orellin", "Pryden", "Quillan", "Rostara", "Selven", "Tavora", "Ulmere",
    "Valden", "Wistera", "Xelmont", "Yarrowen", "Zorrel",
)
PLACE_SUFFIXES = ("Ward", "Quay", "Vale", "Reach", "Terrace", "Crossing", "Hollow", "Harbour")
GIVEN_NAMES = (
    "Arel", "Brena", "Cevra", "Dalen", "Eris", "Faren", "Galen", "Hira", "Iven",
    "Jessa", "Kalen", "Liora", "Maren", "Neris", "Orin", "Pela", "Quira", "Rovan",
    "Sela", "Tarin", "Ula", "Varen", "Wira", "Xela", "Yoren", "Zera",
)
FAMILY_NAMES = (
    "Aldren", "Bexel", "Corven", "Demer", "Eldin", "Farrel", "Gavren", "Helor",
    "Iskan", "Jorrel", "Kelm", "Lorven", "Merin", "Navor", "Ordel", "Pellin",
    "Quenor", "Ravel", "Sorren", "Tavel", "Ulden", "Veyor", "Wester", "Xandor",
    "Yelven", "Zorin",
)
PUBLICATION_TYPES = ("Community Bulletin", "District Circular", "Neighbourhood Journal", "Local Record")
RATIONALES = (
    "a scheduled review of access patterns",
    "a seasonal change in local demand",
    "a joint request from participating groups",
    "a routine renewal of shared facilities",
    "a documented gap in the previous timetable",
    "a planned comparison of operating methods",
    "a community request recorded during open meetings",
    "a maintenance cycle set out in the annual schedule",
)
STATUSES = (
    "approved", "withdrawn", "scheduled", "cancelled",
    "under review", "fully authorised", "completed", "not started",
)
INVERTED_STATUS = {
    "approved": "withdrawn",
    "withdrawn": "approved",
    "scheduled": "cancelled",
    "cancelled": "scheduled",
    "under review": "fully authorised",
    "fully authorised": "under review",
    "completed": "not started",
    "not started": "completed",
}
CERTAINTIES = ("conditional", "guaranteed", "provisional", "definitive", "subject to review", "unqualified")
INVERTED_CERTAINTY = {
    "conditional": "guaranteed",
    "guaranteed": "conditional",
    "provisional": "definitive",
    "definitive": "provisional",
    "subject to review": "unqualified",
    "unqualified": "subject to review",
}
TIMES = ("08:15", "09:30", "10:45", "12:10", "14:20", "15:35", "17:00", "18:15")
PENDING_RESULT = "the recorded outcome remained pending"
REVIEW_RESULT = "the recorded outcome remained under review"
MILESTONES = (
    "site review", "public briefing", "equipment check", "staff orientation",
    "opening session", "progress review", "community walk-through", "close-out meeting",
)
ACTION_NOUN_PHRASES = {
    "open a rotating service desk": "a rotating service desk",
    "extend permit appointments": "expanded permit appointments",
    "publish a revised service roster": "a revised service roster",
    "open evening study rooms": "evening study rooms",
    "add mentor sessions": "additional mentor sessions",
    "allocate community scholarship places": "community scholarship places",
    "begin a connector route": "a connector route",
    "add off-peak shuttle journeys": "additional off-peak shuttle journeys",
    "reorganise interchange bays": "reorganised interchange bays",
    "restore a stream corridor": "a restored stream corridor",
    "plant a shaded walking belt": "a shaded walking belt",
    "stabilise a wetland boundary": "a stabilised wetland boundary",
    "deploy a network of observation sensors": "an observation-sensor network",
    "begin a seasonal field survey": "a seasonal field survey",
    "open a shared measurement station": "a shared measurement station",
    "install shared information kiosks": "shared information kiosks",
    "begin a low-power sensor pilot": "a low-power sensor pilot",
    "open a device repair laboratory": "a device repair laboratory",
    "open demonstration plots": "demonstration plots",
    "coordinate a seed exchange": "a coordinated seed exchange",
    "begin a soil observation cycle": "a soil observation cycle",
    "extend administrative appointment hours": "extended administrative appointment hours",
    "open a records assistance desk": "a records assistance desk",
    "publish a community information schedule": "a community information schedule",
    "open shared market stalls": "shared market stalls",
    "schedule small-workshop access": "scheduled small-workshop access",
    "convene a local supplier forum": "a local supplier forum",
    "open a neighbourhood exhibition": "a neighbourhood exhibition",
    "begin an oral history schedule": "an oral history schedule",
    "stage a shared performance series": "a shared performance series",
    "publish a shared ground schedule": "a shared ground schedule",
    "begin a youth league calendar": "a youth league calendar",
    "open an equipment access desk": "an equipment access desk",
    "renew a pedestrian connection": "a renewed pedestrian connection",
    "upgrade shared library rooms": "upgraded shared library rooms",
    "improve a community water point": "an improved community water point",
}

HEADLINE_PATTERNS = (
    "{project} sets out next stage in {site}",
    "{lead} outlines {action_short} for {site}",
    "New timetable published for {project}",
    "{site} prepares for {project}",
    "{project} moves into its next operating phase",
    "Local groups review plans for {project}",
    "{lead} schedules {project} update",
    "Details released for {project} in {site}",
)

LEAD_SENTENCES = (
    "{lead} has outlined the {project}, a plan to {action} in {site} beginning on {date_human}.",
    "A new phase of the {project} is due to begin in {site} on {date_human}, according to {lead}.",
    "Residents in {site} received an updated timetable for the {project}, which is intended to {objective}.",
    "The {project} will bring {action_short} to {site}, with the opening activity listed for {date_human}.",
)
SCENE_SENTENCES = (
    "Notice boards near {site} carried the new timetable while {participants} reviewed the practical arrangements.",
    "At a small planning session in {site}, {participants} compared the published sequence with the available facilities.",
    "The announcement drew a steady group of {participants}, who focused on access, timing, and day-to-day operation.",
    "Preparatory signs appeared around {site} as organisers set out the first operating steps.",
)
RECORD_SENTENCES = (
    "The reference summary and the account below use the same eleven fields so that readers can compare the stated details directly.",
    "A compact source summary was published alongside the narrative account to make dates, quantities, and attribution easier to inspect.",
    "The notice separates the filed reference details from the article account, giving readers a field-by-field record.",
    "The publication retained both the source note and the reported account rather than merging them into one description.",
)
OPERATIONS_SENTENCES = (
    "The operating plan allocates {quantity} and places the first activity at {time}, with staff expected to record attendance after each session.",
    "Organisers said the initial period would use {quantity}, followed by a short review of scheduling and access.",
    "The first operating block is planned for {time}; coordinators will then compare participation with the published allocation of {quantity}.",
    "Day-to-day arrangements cover signs, queues, staff handovers, and the use of {quantity} across the opening period.",
)
QUOTE_SENTENCES = (
    "\"The purpose is to {objective}, and the published sequence gives every participating group the same starting point,\" {attribution}, the {role}, said.",
    "{attribution}, the {role}, said the team would document each stage and publish a short operational update after the opening period.",
    "\"People should be able to see who is responsible, when the work begins, and how the allocation is used,\" said {attribution}, the {role}.",
    "The {role}, {attribution}, said the schedule was designed around ordinary access needs rather than a one-day launch.",
)
CONTEXT_SENTENCES = (
    "The proposal followed {rationale} and several planning sessions with {participants}.",
    "Earlier discussions concentrated on staffing, safe access, and how updates would be recorded for later review.",
    "The initiative forms part of a broader sequence of small local projects rather than a permanent expansion of authority.",
    "Planning papers describe a limited opening period, after which the organisers will decide whether the timetable needs adjustment.",
)
IMPACT_SENTENCES = (
    "For participating groups, the immediate change is a clearer route to {objective} without relying on an informal timetable.",
    "The practical effect will depend on attendance, staff availability, and whether the published allocation matches day-to-day demand.",
    "Organisers expect the first cycle to show where access remains uneven and which steps can be simplified.",
    "Community observers said the value of the plan would be judged by routine operation rather than the opening announcement.",
)
CLOSING_SENTENCES = (
    "{publication} will publish the next scheduled update after the {milestone_second}.",
    "The next notice is expected after the {milestone_second}, when the first operating figures are available.",
    "A follow-up summary will record attendance, timetable changes, and the outcome of the {milestone_second}.",
    "The organising office said any revision would be added to the same public record after the {milestone_second}.",
)
EXTRA_SENTENCES = (
    "Access points will display the same timetable so that participants do not have to rely on separate informal notices.",
    "A short orientation will cover responsibilities, contact routes, and the method used to record routine observations.",
    "The opening period is deliberately limited, allowing organisers to adjust capacity without changing the wider programme.",
    "Feedback will be grouped by operational theme, and individual comments will not be presented as broad community agreement.",
    "The plan does not create a new enforcement role; it coordinates facilities, times, and administrative responsibility.",
    "Routine maintenance has been assigned before the opening date, with a separate check planned after the busiest session.",
    "Participants may submit written observations through the local office during the first operating cycle.",
    "The published allocation is a planning ceiling, not a forecast that every place will be used.",
    "Organisers will compare attendance across several sessions instead of drawing conclusions from the first day alone.",
    "The source record will remain available after the opening period so later changes can be compared with the original schedule.",
    "No personal case information is included in the operational note or the public attendance summary.",
    "The coordinating group will use a standard checklist for access, staffing, maintenance, and schedule changes.",
    "A reserve arrangement covers ordinary delays, but any major change requires a new dated notice.",
    "The first review will focus on whether the sequence can be followed with the staff and space already assigned.",
    "Community representatives asked that the next update distinguish observed use from estimates made before opening.",
    "The schedule includes time for setup and close-out so the public operating window is not reduced by routine preparation.",
)

STRUCTURE_ORDERS = {
    "briefing_first": ("lead", "record", "account", "operations", "quote", "context", "impact", "close"),
    "scene_first": ("scene", "lead", "account", "record", "quote", "operations", "impact", "close"),
    "record_first": ("record", "lead", "account", "context", "operations", "quote", "impact", "close"),
    "impact_first": ("impact", "lead", "record", "account", "operations", "quote", "context", "close"),
    "timeline_first": ("operations", "lead", "record", "account", "context", "quote", "impact", "close"),
    "operations_first": ("operations", "scene", "lead", "account", "record", "quote", "impact", "close"),
    "community_first": ("scene", "impact", "lead", "record", "account", "quote", "context", "close"),
    "context_first": ("context", "lead", "record", "account", "scene", "operations", "quote", "close"),
}


def _stable_int(value: str, bits: int = 64) -> int:
    size = max(1, bits // 8)
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:size], "big")


MUTATION_PLAN_COUNT = len(MUTATION_FAMILIES) * 3

# Every prefix used by a per-topic mutation-plan population (32 or 34 events)
# contains complete adjacent status pairs.  Status inversion therefore
# preserves the joint event-type/status distribution, including the
# topic-specific result vocabulary derived from it.
EVENT_STATUS_SCHEDULE = (
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
)


def _topic_plan_count(topic_index: int, plan_position: int) -> int:
    # Twenty plans receive 34 events and ten receive 32 in each 1,000-event
    # topic.  Rotating by five positions gives every plan eight 34-event topics
    # and four 32-event topics: exactly 400 events per plan across the corpus.
    return 34 if (plan_position - 5 * topic_index) % MUTATION_PLAN_COUNT < 20 else 32


def _topic_plan_assignments(topic_index: int) -> tuple[tuple[int, int], ...]:
    slots: list[tuple[int, int]] = []
    for plan_position in range(MUTATION_PLAN_COUNT):
        slots.extend(
            (plan_position, occurrence)
            for occurrence in range(_topic_plan_count(topic_index, plan_position))
        )
    if len(slots) != 1_000:
        raise RuntimeError("Per-topic mutation-plan allocation must contain 1,000 events.")
    return tuple(
        slots[(local_index * 337 + topic_index * 97) % 1_000]
        for local_index in range(1_000)
    )


TOPIC_PLAN_ASSIGNMENTS = tuple(
    _topic_plan_assignments(topic_index) for topic_index in range(len(TOPICS))
)


def _plan_assignment(global_index: int) -> tuple[int, int, int, int]:
    topic_index, local_index = divmod(global_index, 1_000)
    plan_position, occurrence = TOPIC_PLAN_ASSIGNMENTS[topic_index][local_index]
    return (
        topic_index,
        plan_position,
        occurrence,
        _topic_plan_count(topic_index, plan_position),
    )


def _paired_index(index: int) -> int:
    """Return the other member of an adjacent, frequency-matched pair."""

    return index ^ 1


def _event_type_rank(cycle_index: int, event_type_index: int) -> int:
    full_cycles, offset = divmod(cycle_index, len(EVENT_STATUS_SCHEDULE))
    return full_cycles * 8 + sum(
        scheduled_type == event_type_index
        for scheduled_type, _ in EVENT_STATUS_SCHEDULE[:offset]
    )


def _event_type_population(plan_population: int, event_type_index: int) -> int:
    return sum(
        EVENT_STATUS_SCHEDULE[index % len(EVENT_STATUS_SCHEDULE)][0] == event_type_index
        for index in range(plan_population)
    )


def _person_from_pool(index: int) -> str:
    pool_size = len(GIVEN_NAMES) * len(FAMILY_NAMES)
    value = index % pool_size
    return f"{GIVEN_NAMES[value // len(FAMILY_NAMES)]} {FAMILY_NAMES[value % len(FAMILY_NAMES)]}"


def _location_from_pool(index: int) -> str:
    pool_size = len(PLACE_STEMS) * len(PLACE_SUFFIXES)
    value = index % pool_size
    return f"{PLACE_STEMS[value // len(PLACE_SUFFIXES)]} {PLACE_SUFFIXES[value % len(PLACE_SUFFIXES)]}"


def _event_date(topic_index: int, plan_position: int, occurrence: int) -> date:
    value = (topic_index * 911 + plan_position * 41 + occurrence * 17) % 1_420
    return date(2032, 1, 1) + timedelta(days=value)


def _words(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value))


def _content_hash(title: str, text: str) -> str:
    return hashlib.sha256(f"{title}\n{text}".encode("utf-8")).hexdigest()


def _split_map(topic: TopicSpec, seed: int) -> dict[int, str]:
    indices = list(range(1_000))
    random.Random(_stable_int(f"{seed}:split:{topic.slug}")).shuffle(indices)
    mapping: dict[int, str] = {}
    start = 0
    for name, count in SPLIT_COUNTS_PER_TOPIC.items():
        for index in indices[start : start + count]:
            mapping[index] = name
        start += count
    return mapping


def _mutation_plan(global_index: int) -> tuple[str, ...]:
    _, plan_position, _, _ = _plan_assignment(global_index)
    count = 2 + (plan_position // len(MUTATION_FAMILIES))
    primary = plan_position % len(MUTATION_FAMILIES)
    offsets = (0, 3, 7, 9)
    selected: list[str] = []
    for offset in offsets:
        value = MUTATION_FAMILIES[(primary + offset) % len(MUTATION_FAMILIES)]
        if value not in selected:
            selected.append(value)
        if len(selected) == count:
            break
    return tuple(selected)


def _event_ledger(spec: TopicSpec, global_index: int, local_index: int, seed: int) -> dict[str, str]:
    event_seed = _stable_int(f"{seed}:event:{spec.slug}:{local_index}")
    rng = random.Random(event_seed)
    topic_index, plan_position, occurrence, _ = _plan_assignment(global_index)
    schedule_position = occurrence % len(EVENT_STATUS_SCHEDULE)
    event_type_index, status_index = EVENT_STATUS_SCHEDULE[schedule_position]
    type_rank = _event_type_rank(occurrence, event_type_index)
    institution_stem_base = 2 * ((topic_index + plan_position) % 6)
    institution_stem_index = (institution_stem_base + type_rank) % len(ORG_STEMS)
    lead = f"{ORG_STEMS[institution_stem_index]} {spec.institution_types[event_type_index]}"
    project_stem = ORG_STEMS[(global_index * 17 + 9) % len(ORG_STEMS)]
    project = f"{project_stem} {spec.initiative_names[event_type_index]}"
    event_date = _event_date(topic_index, plan_position, occurrence)
    quantity = 100 + type_rank
    sequence_index = (2 * ((topic_index + plan_position) % 4) + occurrence) % len(MILESTONES)
    sequence_pair = (sequence_index // 2) * 2
    if sequence_index % 2:
        first, second = MILESTONES[sequence_pair + 1], MILESTONES[sequence_pair]
    else:
        first, second = MILESTONES[sequence_pair], MILESTONES[sequence_pair + 1]
    action = spec.actions[event_type_index]
    publication_stem = ORG_STEMS[(global_index * 19 + 5) % len(ORG_STEMS)]
    status = STATUSES[status_index]
    if status in {"approved", "fully authorised", "completed"}:
        result = spec.results[event_type_index]
    elif status in {"withdrawn", "cancelled", "not started"}:
        result = spec.reverse_results[event_type_index]
    elif status == "scheduled":
        result = PENDING_RESULT
    else:
        result = REVIEW_RESULT
    return {
        "lead": lead,
        "site": _location_from_pool(2 * (topic_index * MUTATION_PLAN_COUNT + plan_position) + occurrence),
        "date": event_date.isoformat(),
        "date_human": event_date.strftime("%d %B %Y").lstrip("0"),
        "time": TIMES[(2 * ((topic_index + plan_position) % 4) + occurrence) % len(TIMES)],
        "quantity": f"{quantity} {spec.units[event_type_index]}",
        "result": result,
        "attribution": _person_from_pool(2 * (topic_index * MUTATION_PLAN_COUNT + plan_position) + occurrence),
        "rationale": RATIONALES[(2 * ((topic_index + plan_position) % 4) + occurrence) % len(RATIONALES)],
        "status": status,
        "sequence": f"{first} before {second}",
        "certainty": CERTAINTIES[(2 * ((topic_index + plan_position) % 3) + occurrence) % len(CERTAINTIES)],
        "project": project,
        "action": action,
        "action_short": ACTION_NOUN_PHRASES[action],
        "objective": spec.objectives[event_type_index],
        "role": rng.choice(spec.roles),
        "participants": rng.choice(spec.participants),
        "publication": f"{publication_stem} {rng.choice(PUBLICATION_TYPES)}",
        "milestone_first": first,
        "milestone_second": second,
        "topic": spec.display_name,
        "event_seed": str(event_seed),
    }


def _mutate_ledger(
    ledger: dict[str, str],
    spec: TopicSpec,
    global_index: int,
    families: tuple[str, ...],
    seed: int,
) -> dict[str, str]:
    account = dict(ledger)
    topic_index, plan_position, occurrence, plan_population = _plan_assignment(global_index)
    event_type_index = spec.actions.index(account["action"])
    type_rank = _event_type_rank(occurrence, event_type_index)
    institution_stem_base = 2 * ((topic_index + plan_position) % 6)
    institution_stem_index = (institution_stem_base + type_rank) % len(ORG_STEMS)
    location_index = 2 * (topic_index * MUTATION_PLAN_COUNT + plan_position) + occurrence
    attribution_index = location_index
    time_index = (2 * ((topic_index + plan_position) % 4) + occurrence) % len(TIMES)
    rationale_index = (2 * ((topic_index + plan_position) % 4) + occurrence) % len(RATIONALES)
    for family in families:
        if family == "entity_substitution":
            alternate_stem = ORG_STEMS[_paired_index(institution_stem_index)]
            account["lead"] = f"{alternate_stem} {spec.institution_types[event_type_index]}"
        elif family == "location_contradiction":
            account["site"] = _location_from_pool(_paired_index(location_index))
        elif family == "date_time_displacement":
            if occurrence < 16:
                paired_occurrence = (occurrence + 8) % 16
                shifted = _event_date(topic_index, plan_position, paired_occurrence)
                account["date"] = shifted.isoformat()
                account["date_human"] = shifted.strftime("%d %B %Y").lstrip("0")
            else:
                account["time"] = TIMES[_paired_index(time_index)]
        elif family == "quantity_change":
            _, unit = account["quantity"].split(" ", 1)
            population = _event_type_population(plan_population, event_type_index)
            changed_rank = (type_rank + population // 2) % population
            changed = 100 + changed_rank
            account["quantity"] = f"{changed} {unit}"
        elif family == "result_reversal":
            if account["result"] in spec.results:
                position = spec.results.index(account["result"])
                account["result"] = spec.reverse_results[position % len(spec.reverse_results)]
            elif account["result"] in spec.reverse_results:
                position = spec.reverse_results.index(account["result"])
                account["result"] = spec.results[position % len(spec.results)]
            elif account["result"] == PENDING_RESULT:
                account["result"] = spec.results[global_index % len(spec.results)]
            else:
                account["result"] = spec.reverse_results[global_index % len(spec.reverse_results)]
        elif family == "attribution_change":
            account["attribution"] = _person_from_pool(_paired_index(attribution_index))
        elif family == "causal_fabrication":
            account["rationale"] = RATIONALES[_paired_index(rationale_index)]
        elif family == "policy_status_inversion":
            account["status"] = INVERTED_STATUS[account["status"]]
        elif family == "sequence_reversal":
            first, second = account["sequence"].split(" before ", 1)
            account["sequence"] = f"{second} before {first}"
            account["milestone_first"], account["milestone_second"] = (
                account["milestone_second"],
                account["milestone_first"],
            )
        elif family == "unsupported_certainty":
            account["certainty"] = INVERTED_CERTAINTY[account["certainty"]]
        else:  # pragma: no cover - protected by the constant mutation inventory
            raise ValueError(f"Unsupported mutation family: {family}")

    # Outcome or status changes can otherwise leave the fictional account
    # internally impossible (for example, "scheduled" alongside an already
    # completed outcome). Keep the account coherent while retaining its
    # controlled disagreement with the reference ledger.
    if "policy_status_inversion" in families:
        event_type_index = spec.actions.index(account["action"])
        if account["status"] in {"approved", "fully authorised", "completed"}:
            account["result"] = spec.results[event_type_index]
        elif account["status"] in {"withdrawn", "cancelled", "not started"}:
            account["result"] = spec.reverse_results[event_type_index]
        elif account["status"] == "scheduled":
            account["result"] = PENDING_RESULT
        else:
            account["result"] = REVIEW_RESULT
    elif "result_reversal" in families:
        event_type_index = spec.actions.index(account["action"])
        account["status"] = INVERTED_STATUS[account["status"]]
        if account["status"] in {"approved", "fully authorised", "completed"}:
            account["result"] = spec.results[event_type_index]
        elif account["status"] in {"withdrawn", "cancelled", "not started"}:
            account["result"] = spec.reverse_results[event_type_index]
        elif account["status"] == "scheduled":
            account["result"] = PENDING_RESULT
        else:
            account["result"] = REVIEW_RESULT
    return account


def _fact_block(prefix: str, facts: dict[str, str]) -> str:
    ordered = "; ".join(
        f"{field}: {fact_value_code(field, facts[field])}"
        for field in (
            "lead", "site", "date", "time", "quantity", "result", "attribution",
            "rationale", "status", "sequence", "certainty",
        )
    )
    return f"{prefix} - {ordered}."


def _format_sentence(pool: tuple[str, ...], context: dict[str, str], rng: random.Random) -> str:
    return rng.choice(pool).format(**context)


def _render_article(
    ledger: dict[str, str],
    account: dict[str, str],
    *,
    template_family: str,
    render_seed: int,
) -> tuple[str, str]:
    rng = random.Random(render_seed)
    context = dict(ledger)
    context.update(account)
    context["date_human"] = account["date_human"]

    headline = HEADLINE_PATTERNS[render_seed % len(HEADLINE_PATTERNS)].format(**context)
    components = {
        "lead": " ".join(
            (
                _format_sentence(LEAD_SENTENCES, context, rng),
                f"The account lists the current status as {account['status']} and records that {account['result']}.",
            )
        ),
        "scene": " ".join(
            (
                _format_sentence(SCENE_SENTENCES, context, rng),
                f"The first listed activity is the {account['milestone_first']}, followed later by the {account['milestone_second']}.",
            )
        ),
        "record": "\n".join(
            (
                _format_sentence(RECORD_SENTENCES, context, rng),
                _fact_block("Reference note", ledger),
            )
        ),
        "account": "\n".join(
            (
                _fact_block("Article account", account),
                f"The narrative therefore attributes the plan to {account['attribution']} and gives {account['rationale']} as its stated basis.",
            )
        ),
        "operations": " ".join(
            (
                _format_sentence(OPERATIONS_SENTENCES, context, rng),
                f"The sequence places the {account['milestone_first']} before the {account['milestone_second']}, with the arrangement described as {account['certainty']}.",
            )
        ),
        "quote": " ".join(
            (
                _format_sentence(QUOTE_SENTENCES, context, rng),
                f"The statement linked the work to {account['rationale']} and repeated the listed allocation of {account['quantity']}.",
            )
        ),
        "context": " ".join(
            (
                _format_sentence(CONTEXT_SENTENCES, context, rng),
                "The filed note records the responsible body and location in the structured reference line above.",
            )
        ),
        "impact": " ".join(
            (
                _format_sentence(IMPACT_SENTENCES, context, rng),
                f"Any later assessment will compare observed operation with the dated reference note rather than rely on the headline alone.",
            )
        ),
        "close": _format_sentence(CLOSING_SENTENCES, context, rng),
    }

    paragraphs = [components[name] for name in STRUCTURE_ORDERS[template_family]]
    target = 190 + (render_seed % 221)
    extras = list(EXTRA_SENTENCES)
    rng.shuffle(extras)
    extra_index = 0
    while _words("\n\n".join(paragraphs)) < target and extra_index < len(extras):
        insertion = 1 + ((render_seed + extra_index * 3) % max(1, len(paragraphs) - 1))
        paragraphs.insert(insertion, extras[extra_index].format(**context))
        extra_index += 1
    text = "\n\n".join(paragraphs)
    if not 180 <= _words(text) <= 550:
        raise RuntimeError(f"Generated article length outside contract: {_words(text)} words")
    return headline, text


def _article_identifier(seed: int, event_id: str, variant: int) -> str:
    digest = hashlib.sha256(f"{seed}:{event_id}:{variant}".encode("utf-8")).hexdigest()
    return f"nlsa-{digest[:20]}"


def _event_identifier(seed: int, topic: str, local_index: int) -> str:
    digest = hashlib.sha256(f"{seed}:{topic}:{local_index}".encode("utf-8")).hexdigest()
    return f"nlse-{digest[:20]}"


def _selected_event_positions(event_count: int) -> list[tuple[int, int]]:
    if event_count == FINAL_EVENT_COUNT:
        return [(topic_index, local_index) for topic_index in range(len(TOPICS)) for local_index in range(1_000)]
    if event_count <= 0 or event_count > FINAL_EVENT_COUNT:
        raise ValueError(f"event_count must be between 1 and {FINAL_EVENT_COUNT}")
    base, remainder = divmod(event_count, len(TOPICS))
    positions: list[tuple[int, int]] = []
    for topic_index in range(len(TOPICS)):
        count = base + (1 if topic_index < remainder else 0)
        positions.extend((topic_index, local_index) for local_index in range(count))
    return positions


def build_dataset(
    *,
    event_count: int = FINAL_EVENT_COUNT,
    seed: int = RANDOM_SEED,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deterministic article rows and generation-only event records."""

    split_maps = {topic.slug: _split_map(topic, seed) for topic in TOPICS}
    articles: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for topic_index, local_index in _selected_event_positions(event_count):
        spec = TOPICS[topic_index]
        global_index = topic_index * 1_000 + local_index
        event_id = _event_identifier(seed, spec.slug, local_index)
        ledger = _event_ledger(spec, global_index, local_index, seed)
        mutation_families = _mutation_plan(global_index)
        mutated = _mutate_ledger(ledger, spec, global_index, mutation_families, seed)
        split = split_maps[spec.slug][local_index]
        event_seed = int(ledger["event_seed"])
        events.append(
            {
                "event_id": event_id,
                "topic": spec.slug,
                "split": split,
                "generator_version": GENERATOR_VERSION,
                "seed": event_seed,
                "mutation_families": list(mutation_families),
                "ledger": {key: value for key, value in ledger.items() if key != "event_seed"},
                "contradicted_account": {key: value for key, value in mutated.items() if key != "event_seed"},
            }
        )
        for variant, label in enumerate((1, 0)):
            facts = ledger if label == 1 else mutated
            render_seed = _stable_int(f"{seed}:render:{event_id}:{variant}")
            template_family = TEMPLATE_FAMILIES[render_seed % len(TEMPLATE_FAMILIES)]
            title, text = _render_article(
                ledger,
                facts,
                template_family=template_family,
                render_seed=render_seed,
            )
            articles.append(
                {
                    "article_id": _article_identifier(seed, event_id, variant),
                    "event_id": event_id,
                    "title": title,
                    "text": text,
                    "label": label,
                    "label_name": (
                        "synthetic_ledger_consistent"
                        if label == 1
                        else "synthetic_ledger_contradicting"
                    ),
                    "topic": spec.slug,
                    "template_family": template_family,
                    "mutation_family": "+".join(mutation_families),
                    "split": split,
                    "generator_version": GENERATOR_VERSION,
                    "seed": event_seed,
                    "content_sha256": _content_hash(title, text),
                }
            )

    row_rng = random.Random(_stable_int(f"{seed}:article-row-order:{event_count}"))
    row_rng.shuffle(articles)
    if len(articles) != event_count * 2 or len(events) != event_count:
        raise RuntimeError("Generator row count invariant failed.")
    return articles, events


def articles_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(ARTICLE_COLUMNS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def events_jsonl_bytes(events: list[dict[str, Any]]) -> bytes:
    lines = [json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for event in events]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dataset_card_text(audit: dict[str, Any]) -> str:
    counts = audit.get("split_counts", {})
    return f"""# {DATASET_NAME}

## Purpose

This package is an independently authored educational synthetic benchmark for
classifying fictional articles as **synthetic ledger-consistent** (`1`) or
**synthetic ledger-contradicting** (`0`).  These labels apply only inside the
package's fictional reference world.  They are not findings about real people,
organisations, locations, or events.

The benchmark is intended to demonstrate deterministic data generation,
grouped splitting, lightweight text classification, calibration, abstention,
and transparent limitations.  It is not a professional fact-checking source,
does not retrieve live evidence, and does not establish real-world
misinformation-detection performance.

## Composition

- Dataset identity: `{DATASET_ID}`
- Generator version: `{GENERATOR_VERSION}`
- Seed: `{RANDOM_SEED}`
- Fictional event ledgers: {audit.get('event_count', 0):,}
- Articles: {audit.get('article_count', 0):,}
- Labels: one ledger-consistent and one ledger-contradicting article per event
- Topics: {len(TOPICS)} neutral administrative and community subjects
- Article length contract: 180-550 words

## Grouped splits

| Split | Articles |
|---|---:|
| Training | {counts.get('training', 0):,} |
| Model validation | {counts.get('model_validation', 0):,} |
| Calibration | {counts.get('calibration', 0):,} |
| Abstention-policy selection | {counts.get('abstention_policy', 0):,} |
| Final test | {counts.get('final_test', 0):,} |

Paired articles from one event always remain in the same split.  The final test
is reserved for one locked evaluation after model, calibration, and threshold
decisions are complete.

## Generation

The package is generated without an external generative-AI API, paid service,
web scraping, or external dataset rows.  Project-authored fictional entity
lexicons, event ledgers, sentence components, structures, and mutation rules
produce both variants independently.  Both labels use the same fact fields,
template families, and punctuation conventions.  Contradicting variants alter
two to four material event facts.  Generation-only ledgers remain in
`events.jsonl`; model-visible inputs are title and article text.

Each article includes a structured `Reference note` and `Article account`.
Their eleven field values are displayed as stable ten-digit numeric codes,
while the surrounding narrative remains human-readable.  Matching codes mean
that the account agrees with the fictional ledger for that field; different
codes mark the controlled disagreement.  The codes are derived only from the
project-authored fictional values, are checked for collisions, and are mapped
to a neutral numeric token by model-text normalisation.  This prevents a raw
bag-of-words model from exploiting repeated names or status words while still
allowing a transparent, label-independent field comparison.

## Quality controls

The machine-readable `quality_audit.json` records schema, balance, duplicate,
group leakage, near-duplicate, forbidden-term, deny-list, distribution, and
metadata-only predictability checks.  Exact and normalized duplicate counts
must be zero, and event/content overlap across splits must be zero.

The fixed raw-text leakage ceiling is 0.75 balanced accuracy.  The packaged
audit records {audit.get('raw_text_surface_baseline', {}).get('balanced_accuracy', 0):.6f};
the metadata-only baseline records
{audit.get('metadata_only_predictability', {}).get('balanced_accuracy', 0):.6f}.

The structured reference/account fields support transparent consistency
signals.  This benchmark-specific structure is a limitation: performance does
not imply that the same classifier can verify an arbitrary real-world article.

## Responsible use

- Do not describe label `1` as objectively true or label `0` as objectively false.
- Do not use the benchmark as evidence about any real person or organisation.
- Do not treat model confidence as the probability that a real-world claim is true.
- Check important claims against authoritative sources and qualified reviewers.
- Report weak or failed counterfactual performance rather than hiding it.

## Licence and attribution

The dataset contents are offered under CC BY 4.0 to the extent applicable
rights subsist.  Attribute: **NewsLens Synthetic Article Benchmark v1.0.0,
Deven Sachin Gaikwad (2026)**.  See `LICENSE.txt`.  The licence does not remove
all legal, ethical, or suitability risk.
"""


def dataset_license_text() -> str:
    return """NEWSLENS SYNTHETIC ARTICLE BENCHMARK DATASET LICENCE

Dataset: NewsLens Synthetic Article Benchmark v1.0.0
Copyright (c) 2026 Deven Sachin Gaikwad
SPDX-License-Identifier: CC-BY-4.0

To the extent applicable copyright and related rights subsist in the original
synthetic dataset contents, the licensor makes those contents available under
the Creative Commons Attribution 4.0 International licence (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/legalcode

Attribution: "NewsLens Synthetic Article Benchmark v1.0.0, Deven Sachin
Gaikwad (2026)."

The repository's source code, application, documents, and other materials
remain under their separately stated licences or notices.  Third-party names,
marks, software, and licences remain the property of their respective owners.
This notice does not claim that a licence eliminates every legal, ethical,
privacy, or suitability risk.
"""


def provenance_payload(rows: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "dataset_name": DATASET_NAME,
        "generator_version": GENERATOR_VERSION,
        "seed": RANDOM_SEED,
        "creator": "Deven Sachin Gaikwad",
        "creation_method": (
            "Deterministic project-authored fictional event ledgers, entity lexicons, "
            "sentence components, article structures, and mutation rules"
        ),
        "external_generative_api_used": False,
        "web_scraping_used": False,
        "external_dataset_rows_used": False,
        "private_isot_material_used": False,
        "article_count": len(rows),
        "event_count": len(events),
        "content_scope": "Fictional educational synthetic benchmark",
        "licence": "CC-BY-4.0 to the extent applicable rights subsist",
        "source_files": [
            "synthetic_benchmark/generator.py",
            "synthetic_benchmark/signals.py",
            "scripts/generate_synthetic_benchmark.py",
        ],
    }


def _entry_manifest(entries: dict[str, bytes]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "dataset_id": DATASET_ID,
        "generator_version": GENERATOR_VERSION,
        "seed": RANDOM_SEED,
        "entries": [
            {
                "path": name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
            for name, payload in sorted(entries.items())
        ],
    }


def _checksums_text(entries: dict[str, bytes]) -> str:
    return "".join(
        f"{hashlib.sha256(payload).hexdigest()}  {name}\n"
        for name, payload in sorted(entries.items())
    )


def write_dataset_archive(
    path: Path,
    rows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    audit: dict[str, Any],
    *,
    extra_entries: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    """Write a byte-deterministic sorted ZIP with fixed metadata."""

    core = {
        "articles.csv": articles_csv_bytes(rows),
        "events.jsonl": events_jsonl_bytes(events),
        "DATASET_CARD.md": dataset_card_text(audit).encode("utf-8"),
        "LICENSE.txt": dataset_license_text().encode("utf-8"),
        "provenance.json": _json_bytes(provenance_payload(rows, events)),
        "quality_audit.json": _json_bytes(audit),
    }
    if extra_entries:
        core.update(extra_entries)
    manifest = _entry_manifest(core)
    entries = {**core, "manifest.json": _json_bytes(manifest)}
    entries["checksums.sha256"] = _checksums_text(entries).encode("utf-8")

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            archive.writestr(info, entries[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "entry_count": len(entries),
        "entries": sorted(entries),
    }


def summarize_inventory(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    return {
        "articles": len(rows),
        "labels": dict(sorted(Counter(str(row["label"]) for row in rows).items())),
        "splits": dict(sorted(Counter(str(row["split"]) for row in rows).items())),
        "topics": dict(sorted(Counter(str(row["topic"]) for row in rows).items())),
        "templates": dict(sorted(Counter(str(row["template_family"]) for row in rows).items())),
    }
