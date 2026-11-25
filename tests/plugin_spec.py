"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "fsd-africa" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no rule on overnight stops,
# so that overlay is not required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "africa", "african", "intercontinental", "grade", "jg", "director", "directors", "executive", "board", "exco",
    "chair", "ceo", "cfo", "dcs", "pillar", "consultant", "remote", "training", "flexible", "refund", "direct",
    "nonstop", "connection", "lounge", "legroom", "premium", "business", "economy", "guest", "spouse", "husband",
    "wife", "holiday", "personal", "group", "together", "emissions", "carbon", "night",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Role, contract.Purpose, contract.SignOffSubject]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 3

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear).
DURATION_CASES = [
    ("long-flight", [421], [], True),  # strict: "more than 7 hours"
    ("long-flight", [420], [], False),
    ("long-flight", [505, 450], [90], True),  # every flight over 7 hours
    ("long-flight", [200, 150], [60], False),  # the whole journey, layover included, within 7 hours
    ("long-flight", [285, 335], [110], None),  # each flight within, the journey over: unclear
    ("long-flight", [505, 95], [80], None),  # one flight over, one within: unclear
    ("lounge", [241], [], True),  # strict: "more than 4 hours"
    ("lounge", [240], [], False),
    ("lounge", [270, 60], [75], None),
    ("lounge", [120, 90], [30], False),
]
