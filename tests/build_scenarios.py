"""Writes the FSD Africa scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Expected answers are hand-written here; tests/test_scenarios.py checks them against rules.solve. Every quote is
copied from the frozen text as it stands, stray mid-word spaces included ("w ith", "a pproved").
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
DEFAULT = keep(118, 118, None, "the default class for all flights is economy")
DIRECT = keep(119, 121, None, "book the lowest cost direct flight where direct flights are readily available")
FLEX = keep(122, 123, None, "fully flexible tickets only in exceptional circumstances, with DCS and CFO approval before "
            "booking")
TABLE = keep(124, 127, None, "the class table: maximum permitted class by description")
AFRICA = keep(128, 128, None, "all flights within Africa: economy")
CONSULTANTS = keep(129, 129, None, "all consultants' travel: economy")
NED = keep(130, 131, None, "non-executive directors: business, not expected to be more than 3 flights a year")
EXEC = keep(132, 133, None, "executive directors: business, not expected to be more than 8 flights a year")
LONG = keep(134, 136, None, "intercontinental flights of more than 7 hours for JG6 and above: business")
TRAINING = keep(137, 137, None, "all flights to attend training, regardless of duration: economy")
REMOTE = keep(138, 140, None, "remote workers travelling to attend work events: economy")
DOUBT = keep(150, 152, None, "in doubt over the class, consult the DCS in advance; class exceptions need the CEO")
OWN_COST = keep(102, 105, None, "anything above the policy is paid by the traveller")
LOWER = keep(107, 110, None, "premium economy/business on long flights; staff may choose a lower class")
CEO = keep(114, 115, None, "the CEO approves exceptions where absolutely necessary")
NONBUSINESS = keep(242, 242, None, "non-business travel expenses are not reimbursed")
GUESTS = keep(243, 243, None, "costs for personal guests are not reimbursed")
NECESSARY = keep(71, 72, None, "travel must be reasonable and necessary for FSD Africa's business")
GROUP = keep(277, 279, None, "where possible, no more than three ExCo or Board members on the same flight")

# ----- nearby clauses that must not change the answer -----
LOUNGE = aside(143, 144, "For flights of more than 4 hours' duration, access to airport lounges and booking of seats "
               "with greater legroom in Economy is allowable.",
               "a lounge and an extra-legroom economy seat, not a higher class")
LOUNGE_FEES = aside(239, 240, "Fees or dues for airline VIP lounges (except for flights of more than 4 hours' "
                    "duration, as above)", "a lounge fee rule, not a fare rule")
EXTRA_NIGHT = aside(141, 142, "Allowance may be made for an extra night in-country in the case of long-distance travel "
                    "ahead of next-day work commitments.", "a hotel night, not the flight")
RAIL = aside(154, 155, "Standard class of travel (or the equivalent of Premium Economy, if FSD Africa work needs to be "
             "done)", "a rail rule; it does not set the flight's class")
PILLAR = aside(145, 146, "with travel approved by the pillar head", "the routine trip approval, on file")
TAXI = aside(168, 169, "Airport transfers from UK, European or US airports, except w here services are very infrequent",
             "an airport-transfer rule, not a flight rule")
CONSULTANT_BUDGET = aside(148, 149, "Costs of consultants' and invited guests' travel will be itemised within project "
                          "budgets", "how consultants' travel is budgeted, not its class")
EMERGENCY = aside(267, 268, "In emergencies, the normal travel policies are waived",
                  "no emergency here; the normal policy applies")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "role": "STAFF", "accompanies": "", "job_grade": 0,
        "works_remotely": False, "exco_or_board_member": False, "origin": "", "destination": "", "travel_date": "",
        "booking_date": "", "work_starts": "", "purpose": "", "purpose_kind": "PROGRAMME_WORK",
        "requested_cabin": "ECONOMY", "wants_flexible_fare": False, "dates_may_move": False,
        "earlier_business_flights": [], "colleagues_booked": [], "sign_offs": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def sign(role, name, subject):
    return {"role": role, "name": name, "subject": subject}


def pillar(name):
    return sign("PILLAR_HEAD", name, "TRIP")


def offer(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": reasons,
            "approvers": approvers, "clauses": clauses, "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=0):
    # handbook.json background_offers is 0: a search the scenario does not pin lists nothing. No pinned search here
    # adds background offers, since a background nonstop could change the lowest cost direct flight.
    return {"name": "main", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


S = []


def scenario(id, category, overlays, request, trip_, search_spec, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": [search_spec]}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


AIR = ["AIR_TRAVEL", "TRANSPORTATION"]
LOW = ["DIRECT_FLIGHT_PREFERRED", "LOWEST_FARE"]
LOW_CAPPED = [*LOW, "ECONOMY_CLASS_LIMIT"]
STAFF_OK = ["NONE", "PILLAR_HEAD"]
UNCLEAR_ROLES = ["CHIEF_EXECUTIVE", "DIRECTOR_CORPORATE_SERVICES", "NOT_NAMED"]
UNCLEAR_REASONS = ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"]

# Shared worlds.
DXB_FLIGHTS = {
    "emirates": {"carrier": "EK", "depart": "10:20"},
    "kenya": {"carrier": "KQ", "depart": "16:45"},
}
DXB_DIRECTOR_OFFERS = [
    offer("emirates-economy", "emirates", "ECONOMY", 43000),
    offer("emirates-business", "emirates", "BUSINESS", 162000),
    offer("kenya-economy", "kenya", "ECONOMY", 45500),
    offer("kenya-business", "kenya", "BUSINESS", 158000),
]
EXEC_TRIP = {"traveller_name": "Wanjiru Mbugua", "traveller_title": "Executive Director, Board member",
                 "role": "EXECUTIVE_DIRECTOR", "exco_or_board_member": True, "origin": "NBO", "destination": "DXB",
                 "travel_date": "2026-12-14", "booking_date": "2026-11-24", "work_starts": "2026-12-15 09:30",
                 "purpose": "Co-investment talks with a Gulf development fund in Dubai", "purpose_kind": "PARTNER_MEETING",
                 "requested_cabin": "BUSINESS"}
SEVEN_FLIGHTS = ["2026-01-21", "2026-02-24", "2026-04-08", "2026-05-19", "2026-07-07", "2026-09-15", "2026-10-27"]

DXB_STAFF_FLIGHTS = {
    "emirates": {"carrier": "EK", "depart": "10:20"},
    "kenya": {"carrier": "KQ", "depart": "16:45"},
    "doha": {"carrier": "QR", "via": ["DOH"], "depart": "01:55", "minutes": [270, 60], "layovers": [75]},
}


def dxb_staff_offers(seats):
    return [
        offer("emirates-economy", "emirates", "ECONOMY", 41000, seats=seats),
        offer("kenya-economy", "kenya", "ECONOMY", 44500, seats=seats),
        offer("doha-economy", "doha", "ECONOMY", 35200),
    ]


DXB_STAFF_TRIP = {"traveller_name": "Faith Chepkoech", "traveller_title": "Finance Assistant", "job_grade": 3,
                      "origin": "NBO", "destination": "DXB", "travel_date": "2027-01-07", "booking_date": "2026-12-14",
                      "work_starts": "2027-01-08 09:00", "purpose": "Africa fintech conference in Dubai",
                      "purpose_kind": "CONFERENCE", "sign_offs": [pillar("Samuel Kiprono")]}
DXB_STAFF_REQUEST = ("Please book me economy from Nairobi to Dubai on 7 January for the fintech conference, which "
                     "opens the next morning.")

FCO_REQUEST = ("Business class from Nairobi to Rome on 26 January if the policy allows it for this flight; if not, "
               "economy. I'm presenting to investors in Rome the next morning.")


def fco_world(minutes):
    return search("NBO", "FCO", "2027-01-26", {
        "kenya": {"carrier": "KQ", "depart": "09:05", "minutes": [minutes]},
        "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "03:30", "minutes": [285, 335], "layovers": [110]},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 52000),
        offer("kenya-business", "kenya", "BUSINESS", 219000),
        offer("dubai-economy", "dubai", "ECONOMY", 44500),
    ])


FCO_TRIP = {"traveller_name": "Otieno Odhiambo", "traveller_title": "Senior Investment Manager", "job_grade": 8,
                "origin": "NBO", "destination": "FCO", "travel_date": "2027-01-26", "booking_date": "2027-01-05",
                "work_starts": "2027-01-27 09:30", "purpose": "Investor presentation in Rome", "purpose_kind": "PARTNER_MEETING",
                "requested_cabin": "BUSINESS", "sign_offs": [pillar("Mark Napier")]}

AMS_REQUEST = ("Could you book me business class to Amsterdam on 9 February for the impact investors' forum, if the "
               "policy allows it? Otherwise economy. The forum opens the next morning.")
AMS_FLIGHTS = {
    "klm": {"carrier": "KL", "depart": "08:25"},
    "kenya": {"carrier": "KQ", "depart": "23:35"},
    "istanbul": {"carrier": "TK", "via": ["IST"], "depart": "04:15", "layovers": [95]},
}
AMS_OFFERS = [
    offer("klm-economy", "klm", "ECONOMY", 57000),
    offer("klm-business", "klm", "BUSINESS", 241000),
    offer("kenya-economy", "kenya", "ECONOMY", 54500),
    offer("kenya-business", "kenya", "BUSINESS", 236000),
    offer("istanbul-economy", "istanbul", "ECONOMY", 46000),
]
AMS_TRIP = {"traveller_name": "Amina Yusuf", "traveller_title": "Investment Manager", "origin": "NBO", "destination": "AMS",
                "travel_date": "2027-02-09", "booking_date": "2027-01-18", "work_starts": "2027-02-10 10:00",
                "purpose": "Impact investors' forum in Amsterdam", "purpose_kind": "CONFERENCE", "requested_cabin": "BUSINESS",
                "sign_offs": [pillar("Evans Mwangi")]}

LHR_FLIGHTS = {
    "kenya": {"carrier": "KQ", "depart": "23:15"},
    "british": {"carrier": "BA", "depart": "22:05"},
    "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "04:00", "minutes": [285, 420], "layovers": [120]},
}
LHR_FLEX_OFFERS = [
    offer("kenya-economy", "kenya", "ECONOMY", 54000),
    offer("kenya-flex", "kenya", "ECONOMY", 89000, refundable=True),
    offer("british-economy", "british", "ECONOMY", 57500),
    offer("british-flex", "british", "ECONOMY", 93500, refundable=True),
    offer("dubai-economy", "dubai", "ECONOMY", 47000),
    offer("dubai-flex", "dubai", "ECONOMY", 78000, refundable=True),
]

NBO_FROM_LHR = {
    "british": {"carrier": "BA", "depart": "19:30"},
    "kenya": {"carrier": "KQ", "depart": "20:45"},
    "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "17:05", "minutes": [80, 505], "layovers": [90]},
}

# ===== easy (5) =====

scenario(
    "baobab-crest", "easy", [],
    "I need to fly from Nairobi to Johannesburg on 8 December for the pension-fund workshop the next morning. "
    "Economy is fine.",
    trip(traveller_name="Brian Kamau", traveller_title="Programme Officer, Capital Markets", job_grade=4,
         origin="NBO", destination="JNB", travel_date="2026-12-08", booking_date="2026-11-24",
         work_starts="2026-12-09 09:00", purpose="Pension-fund workshop with a South African partner",
         purpose_kind="PARTNER_MEETING", sign_offs=[pillar("Grace Wambui")]),
    search("NBO", "JNB", "2026-12-08", {
        "morning": {"carrier": "KQ", "depart": "08:30"},
        "midday": {"carrier": "SA", "depart": "13:10"},
        "evening": {"carrier": "KQ", "depart": "18:45"},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 38500),
        offer("midday-economy", "midday", "ECONOMY", 41200),
        offer("evening-economy", "evening", "ECONOMY", 39900),
    ]),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], LOW_CAPPED, STAFF_OK, AIR),
    [DEFAULT, DIRECT, AFRICA],
    "A flight within Africa in economy (lines 118, 128); every offer is a nonstop, so the lowest cost direct flight "
    "(lines 119-121) is the 08:30 Kenya Airways fare. The pillar head's trip approval is routine (lines 145-146).",
    distractors=[PILLAR])

scenario(
    "kudu-lantern", "easy", ["dearer_option", "upgrade_not_taken"],
    "Nairobi to Frankfurt on 19 January for the green bond conference. Premium economy please; I don't need "
    "business.",
    trip(traveller_name="Daniel Mutua", traveller_title="Head of Climate Finance", job_grade=8, origin="NBO",
         destination="FRA", travel_date="2027-01-19", booking_date="2026-12-21", work_starts="2027-01-20 14:00",
         purpose="Green bond conference in Frankfurt", purpose_kind="CONFERENCE", requested_cabin="PREMIUM_ECONOMY",
         sign_offs=[pillar("Mark Napier")]),
    search("NBO", "FRA", "2027-01-19", {
        "lufthansa": {"carrier": "LH", "depart": "22:40"},
        "kenya": {"carrier": "KQ", "depart": "23:55"},
    }, [
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 61000),
        offer("lufthansa-premium", "lufthansa", "PREMIUM_ECONOMY", 118000),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 285000),
        offer("kenya-economy", "kenya", "ECONOMY", 58500),
        offer("kenya-premium", "kenya", "PREMIUM_ECONOMY", 112500),
        offer("kenya-business", "kenya", "BUSINESS", 271000),
    ]),
    expected("BOOK", ["kenya-premium"], ["PREMIUM_ECONOMY"], ["INTERNATIONAL_LONG_FLIGHT", "PREMIUM_ECONOMY_ALLOWED"],
             STAFF_OK, [*AIR, "OPERATING_PRINCIPLES"]),
    [LONG, LOWER, DIRECT],
    "An intercontinental flight of 480 minutes for a JG8 employee: business is the maximum (lines 134-136). Lines "
    "107-110 permit premium economy on long flights and let staff choose a lower class, so the premium economy the "
    "traveller asks for; the cheaper direct fare is Kenya Airways.")

scenario(
    "acacia-drift", "easy", ["multi_leg", "dearer_option", "upgrade_not_taken"],
    "Nairobi to Paris on 2 February for the meeting with the development finance institutions the next afternoon. "
    "Economy is fine for this one; I'd rather keep the emissions down.",
    trip(traveller_name="Lucy Njeri", traveller_title="Senior Manager, Financial Inclusion", job_grade=6,
         origin="NBO", destination="CDG", travel_date="2027-02-02", booking_date="2027-01-11",
         work_starts="2027-02-03 15:00", purpose="Meeting with development finance institutions in Paris",
         purpose_kind="PARTNER_MEETING", sign_offs=[pillar("Evans Mwangi")]),
    search("NBO", "CDG", "2027-02-02", {
        "airfrance": {"carrier": "AF", "depart": "23:30"},
        "kenya": {"carrier": "KQ", "depart": "22:50"},
        "istanbul": {"carrier": "TK", "via": ["IST"], "depart": "03:35", "layovers": [90]},
    }, [
        offer("airfrance-economy", "airfrance", "ECONOMY", 56000),
        offer("airfrance-business", "airfrance", "BUSINESS", 268000),
        offer("kenya-economy", "kenya", "ECONOMY", 59000),
        offer("kenya-business", "kenya", "BUSINESS", 255000),
        offer("istanbul-economy", "istanbul", "ECONOMY", 46500),
    ]),
    expected("BOOK", ["airfrance-economy"], ["ECONOMY"], LOW, STAFF_OK, [*AIR, "OPERATING_PRINCIPLES"]),
    [DEFAULT, DIRECT, LOWER, LONG],
    "JG6 on an intercontinental flight of 495 minutes may fly business (lines 134-136), but lines 108-110 let staff "
    "choose a lower class. Economy at the lowest cost direct flight (lines 119-121): Air France, not the cheaper "
    "Istanbul connection.")

scenario(
    "sisal-harbour", "easy", ["dearer_option", "date_arithmetic"],
    "Business class from Nairobi to Dubai on 14 December please, for the co-investment talks the next morning.",
    trip(**EXEC_TRIP, earlier_business_flights=SEVEN_FLIGHTS),
    search("NBO", "DXB", "2026-12-14", DXB_FLIGHTS, DXB_DIRECTOR_OFFERS),
    expected("BOOK", ["kenya-business"], ["BUSINESS"], ["SENIOR_ROLE_ENTITLEMENT"], ["NONE"], AIR),
    [EXEC, TABLE, DIRECT],
    "An executive director may fly business, 'not expected to be more than 8 flights per year' (lines 132-133). Seven "
    "business flights so far this year, so this is the eighth: within the number. The flight is under 7 hours, so the "
    "director row alone grants business. Cheapest direct business fare: Kenya Airways.",
    twin_of="umbra-kopje", twin_fact="earlier business flights this year: 7 or 8")

scenario(
    "marula-quay", "easy", ["multi_leg"],
    "Nairobi to Edinburgh on 12 January for the investor conference the next day, economy please.",
    trip(traveller_name="Peter Ouma", traveller_title="Programme Associate", job_grade=4, origin="NBO",
         destination="EDI", travel_date="2027-01-12", booking_date="2026-12-15", work_starts="2027-01-13 13:00",
         purpose="Investor conference in Edinburgh", purpose_kind="CONFERENCE", sign_offs=[pillar("Grace Wambui")]),
    search("NBO", "EDI", "2027-01-12", {
        "london": {"carrier": "BA", "via": ["LHR"], "depart": "23:05", "minutes": [520, 85], "layovers": [75]},
        "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "23:40", "minutes": [505, 95], "layovers": [80]},
        "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "05:10", "minutes": [285, 450], "layovers": [120]},
    }, [
        offer("london-economy", "london", "ECONOMY", 54000),
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 49800),
        offer("dubai-economy", "dubai", "ECONOMY", 57500),
    ]),
    expected("BOOK", ["amsterdam-economy"], ["ECONOMY"], LOW, STAFF_OK, AIR),
    [DEFAULT, DIRECT],
    "Economy (line 118). No direct flight is listed, so the principle of lines 119-121 falls back to the lowest cost "
    "flight: the KLM connection via Amsterdam.")

# ===== boundary twins (6) =====

scenario(
    "tamarind-ridge", "boundary_twin", ["dearer_option", "multi_leg"],
    FCO_REQUEST,
    trip(**FCO_TRIP),
    fco_world(421),
    expected("BOOK", ["kenya-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED", "SENIOR_ROLE_ENTITLEMENT"],
             STAFF_OK, AIR),
    [LONG, DIRECT],
    "The Kenya Airways nonstop is scheduled at 421 minutes: more than 7 hours, intercontinental, JG8, so business "
    "(lines 134-136); the only business fare is the direct one.",
    twin_of="cassava-ledge", twin_fact="nonstop scheduled at 421 or 420 minutes")

scenario(
    "cassava-ledge", "boundary_twin", ["multi_leg", "dearer_option"],
    FCO_REQUEST,
    trip(**{**FCO_TRIP, "traveller_name": "Joyce Akinyi", "traveller_title": "Senior Investment Manager"}),
    fco_world(420),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"],
             ["ECONOMY_CLASS_LIMIT", "LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], STAFF_OK, AIR),
    [LONG, DEFAULT, DIRECT],
    "The nonstop is scheduled at 420 minutes: exactly 7 hours, not 'more than 7 hours' (lines 134-136), so economy "
    "(line 118) at the lowest cost direct flight (lines 119-121): the Kenya Airways economy fare, not the cheaper "
    "Dubai connection.",
    twin_of="tamarind-ridge", twin_fact="nonstop scheduled at 420 or 421 minutes")

scenario(
    "jacaranda-weir", "boundary_twin", ["dearer_option", "multi_leg"],
    AMS_REQUEST,
    trip(**AMS_TRIP, job_grade=6),
    search("NBO", "AMS", "2027-02-09", AMS_FLIGHTS, AMS_OFFERS),
    expected("BOOK", ["kenya-business"], ["BUSINESS"], ["INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED", "SENIOR_ROLE_ENTITLEMENT"],
             STAFF_OK, AIR),
    [LONG, DIRECT],
    "JG6 is 'JG6 and above' (inclusive), and the nonstops are 505 minutes, intercontinental: business (lines "
    "134-136). Cheapest direct business fare: Kenya Airways.",
    twin_of="papyrus-knoll", twin_fact="job grade 6 or 5")

scenario(
    "papyrus-knoll", "boundary_twin", ["multi_leg", "dearer_option"],
    AMS_REQUEST,
    trip(**{**AMS_TRIP, "traveller_name": "Kevin Barasa"}, job_grade=5),
    search("NBO", "AMS", "2027-02-09", AMS_FLIGHTS, AMS_OFFERS),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"],
             ["ECONOMY_CLASS_LIMIT", "LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], STAFF_OK, AIR),
    [LONG, DEFAULT, DIRECT],
    "JG5 is below 'JG6 and above' (lines 134-136), so economy (line 118) at the lowest cost direct flight: Kenya "
    "Airways economy, not the cheaper Istanbul connection (lines 119-121).",
    twin_of="jacaranda-weir", twin_fact="job grade 5 or 6")

scenario(
    "dik-dik-meadow", "boundary_twin", ["multi_leg", "dearer_option"],
    DXB_STAFF_REQUEST,
    trip(**DXB_STAFF_TRIP),
    search("NBO", "DXB", "2027-01-07", DXB_STAFF_FLIGHTS, dxb_staff_offers(True)),
    expected("BOOK", ["emirates-economy"], ["ECONOMY"], LOW, STAFF_OK, AIR),
    [DEFAULT, DIRECT],
    "Economy (line 118). Two nonstops have seats, so direct flights are readily available: the lowest cost direct "
    "flight is Emirates (lines 119-121), not the cheaper Qatar connection via Doha.",
    twin_of="fynbos-gate", twin_fact="the nonstops' economy seats are available or sold out")

scenario(
    "fynbos-gate", "boundary_twin", ["multi_leg"],
    DXB_STAFF_REQUEST,
    trip(**{**DXB_STAFF_TRIP, "traveller_name": "Mercy Wanjala"}),
    search("NBO", "DXB", "2027-01-07", DXB_STAFF_FLIGHTS, dxb_staff_offers(False)),
    expected("BOOK", ["doha-economy"], ["ECONOMY"], LOW, STAFF_OK, AIR),
    [DEFAULT, DIRECT],
    "Economy (line 118). Both nonstops are sold out in economy, so no direct flight is readily available (lines "
    "119-121): the lowest cost flight is the Qatar connection via Doha, which lands in time.",
    twin_of="dik-dik-meadow", twin_fact="the nonstops' economy seats are sold out or available")

# ===== multi_rule (4) =====

scenario(
    "ebony-strand", "multi_rule", ["multi_leg", "dearer_option"],
    "I need a ticket from Nairobi to London on 16 February that I can change or refund without a fee: the FCDO "
    "meeting date isn't confirmed yet and may move. The DCS and the CFO have both approved that.",
    trip(traveller_name="Esther Nyambura", traveller_title="Policy Manager", job_grade=5, origin="NBO",
         destination="LHR", travel_date="2027-02-16", booking_date="2027-01-25", work_starts="2027-02-17 14:00",
         purpose="Meeting with the FCDO on the next funding round", purpose_kind="PARTNER_MEETING",
         wants_flexible_fare=True, dates_may_move=True,
         sign_offs=[pillar("Mark Napier"), sign("DIRECTOR_CORPORATE_SERVICES", "Jonathan Pike", "FLEXIBLE_FARE"),
                    sign("CHIEF_FINANCIAL_OFFICER", "Rose Kariuki", "FLEXIBLE_FARE")]),
    search("NBO", "LHR", "2027-02-16", LHR_FLIGHTS, LHR_FLEX_OFFERS),
    expected("BOOK", ["kenya-flex"], ["ECONOMY"], ["FLEXIBLE_FARE_APPROVED", *LOW],
             ["CHIEF_FINANCIAL_OFFICER", "DIRECTOR_CORPORATE_SERVICES", "NONE", "PILLAR_HEAD"], AIR),
    [FLEX, DIRECT, DEFAULT],
    "Lines 122-123: a fully flexible ticket in exceptional circumstances (the meeting may move) with the DCS's and the "
    "CFO's approval before booking, both on file. The lowest cost direct flexible fare (lines 119-121) is Kenya "
    "Airways, not the cheaper flexible connection via Dubai. JG5: economy (line 118).")

scenario(
    "guava-terrace", "multi_rule", ["multi_leg"],
    "Could you get me a ticket from Nairobi to London on 2 March that I can change or refund for free, just in case? "
    "If that needs a sign-off I don't have, book what the policy allows; I have to be at the conference the next "
    "afternoon.",
    trip(traveller_name="Collins Kiplagat", traveller_title="Programme Associate", job_grade=4, origin="NBO",
         destination="LHR", travel_date="2027-03-02", booking_date="2027-02-08", work_starts="2027-03-03 14:00",
         purpose="Conference on African capital markets in London", purpose_kind="CONFERENCE",
         wants_flexible_fare=True, sign_offs=[pillar("Grace Wambui")]),
    search("NBO", "LHR", "2027-03-02", LHR_FLIGHTS, LHR_FLEX_OFFERS),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["REFUNDABLE_FARE_NOT_ALLOWED"], STAFF_OK, AIR),
    [FLEX, DIRECT, DEFAULT],
    "Lines 122-123: a fully flexible ticket only in exceptional circumstances and with the DCS's and CFO's approval "
    "before booking; the conference is fixed and neither has approved, and the traveller asks for what the policy "
    "allows otherwise. The lowest cost direct non-flexible fare: Kenya Airways (lines 119-121).")

scenario(
    "hibiscus-ford", "multi_rule", ["multi_leg", "dearer_option"],
    "Business class from Nairobi to London on 8 March if the policy allows it, otherwise economy. The leadership "
    "training course starts at nine the next morning.",
    trip(traveller_name="Samuel Kiprono", traveller_title="Senior Manager, Digital Finance", job_grade=7,
         origin="NBO", destination="LHR", travel_date="2027-03-08", booking_date="2027-02-15",
         work_starts="2027-03-09 09:00", purpose="Leadership training course in London",
         purpose_kind="TRAINING_COURSE", requested_cabin="BUSINESS", sign_offs=[pillar("Mark Napier")]),
    search("NBO", "LHR", "2027-03-08", LHR_FLIGHTS, [
        offer("kenya-economy", "kenya", "ECONOMY", 54000),
        offer("kenya-business", "kenya", "BUSINESS", 238000),
        offer("british-economy", "british", "ECONOMY", 57500),
        offer("british-business", "british", "BUSINESS", 246000),
        offer("dubai-economy", "dubai", "ECONOMY", 47000),
    ]),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["ECONOMY_CLASS_LIMIT", "UPGRADE_NOT_ELIGIBLE"], STAFF_OK, AIR),
    [TRAINING, LONG, DIRECT],
    "JG7 on a 520-minute intercontinental flight would get business (lines 134-136), but the trip is to attend "
    "training: 'All flights to attend training, regardless of duration' are economy (line 137). The lowest cost "
    "direct economy fare: Kenya Airways (lines 119-121).")

scenario(
    "ibis-causeway", "multi_rule", ["multi_leg", "dearer_option"],
    "Business class from Johannesburg to Cairo on 23 February if the policy allows it; otherwise economy. The "
    "capital markets roundtable is the next morning.",
    trip(traveller_name="Thabo Nkosi", traveller_title="Senior Manager, Capital Markets", job_grade=7,
         origin="JNB", destination="CAI", travel_date="2027-02-23", booking_date="2027-02-01",
         work_starts="2027-02-24 09:00", purpose="Capital markets roundtable in Cairo", purpose_kind="PARTNER_MEETING",
         requested_cabin="BUSINESS", sign_offs=[pillar("Evans Mwangi")]),
    search("JNB", "CAI", "2027-02-23", {
        "southafrican": {"carrier": "SA", "depart": "10:45", "minutes": [480]},
        "egyptair": {"carrier": "MS", "depart": "13:30", "minutes": [480]},
        "nairobi": {"carrier": "KQ", "via": ["NBO"], "depart": "06:20", "minutes": [240, 285], "layovers": [90]},
    }, [
        offer("southafrican-economy", "southafrican", "ECONOMY", 48500),
        offer("southafrican-business", "southafrican", "BUSINESS", 196000),
        offer("egyptair-economy", "egyptair", "ECONOMY", 46000),
        offer("egyptair-business", "egyptair", "BUSINESS", 188000),
        offer("nairobi-economy", "nairobi", "ECONOMY", 41000),
    ]),
    expected("BOOK", ["egyptair-economy"], ["ECONOMY"],
             ["ECONOMY_CLASS_LIMIT", "LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"], STAFF_OK, AIR),
    [AFRICA, LONG, DIRECT],
    "Johannesburg to Cairo is a flight within Africa: economy (line 128). The 480-minute flight is over 7 hours, but "
    "the business row of lines 134-136 is for intercontinental flights. The lowest cost direct economy fare: "
    "EgyptAir, not the cheaper connection via Nairobi (lines 119-121).")

# ===== hidden_clause (2) =====

scenario(
    "lobelia-spur", "hidden_clause", ["multi_traveller", "outside_air_section", "dearer_option", "date_arithmetic"],
    "Business class from London to Nairobi on 15 March please, for the Board meeting at ten the next morning. Three "
    "of my Board colleagues are already booked on the BA evening flight.",
    trip(traveller_name="Helen Ashworth", traveller_title="Non-executive director", role="NON_EXECUTIVE_DIRECTOR",
         exco_or_board_member=True, origin="LHR", destination="NBO", travel_date="2027-03-15",
         booking_date="2027-02-22", work_starts="2027-03-16 10:00", purpose="FSD Africa Board meeting in Nairobi",
         purpose_kind="BOARD_MEETING", requested_cabin="BUSINESS", earlier_business_flights=["2027-01-20"],
         colleagues_booked=[{"carrier": "British Airways", "depart_local": "2027-03-15 19:30", "members": 3}]),
    search("LHR", "NBO", "2027-03-15", NBO_FROM_LHR, [
        offer("british-economy", "british", "ECONOMY", 61000),
        offer("british-business", "british", "BUSINESS", 295000),
        offer("kenya-economy", "kenya", "ECONOMY", 59000),
        offer("kenya-business", "kenya", "BUSINESS", 312000),
        offer("amsterdam-business", "amsterdam", "BUSINESS", 270000),
    ]),
    expected("BOOK", ["kenya-business"], ["BUSINESS"],
             ["DIRECT_FLIGHT_PREFERRED", "INTERNATIONAL_LONG_FLIGHT", "SENIOR_ROLE_ENTITLEMENT",
              "TRAVELLER_LIMIT_PER_FLIGHT"], ["NONE"], [*AIR, "GROUP_TRAVEL", "SAFETY_AND_SECURITY"]),
    [NED, GROUP, DIRECT],
    "A non-executive director may fly business (lines 130-131; this is her second business flight of the year, within "
    "the 3 expected). Three Board members are already on the BA 19:30 nonstop, and lines 277-279 ask that no more than "
    "three ExCo or Board members travel on the same flight where possible: the Kenya Airways 20:45 nonstop is "
    "possible and lands at 08:25, in time. Lowest cost direct (lines 119-121): not the cheaper KLM connection.")

scenario(
    "namib-orchard", "hidden_clause", ["multi_leg", "dearer_option"],
    "Business class from London to Nairobi on 12 April if the policy allows it; otherwise economy. The all-staff "
    "retreat starts at nine the next morning.",
    trip(traveller_name="Sarah Okafor", traveller_title="Senior Manager, Research (remote, London)", job_grade=7,
         works_remotely=True, origin="LHR", destination="NBO", travel_date="2027-04-12", booking_date="2027-03-22",
         work_starts="2027-04-13 09:00", purpose="FSD Africa all-staff retreat in Nairobi", purpose_kind="STAFF_EVENT",
         requested_cabin="BUSINESS", sign_offs=[pillar("Mark Napier")]),
    search("LHR", "NBO", "2027-04-12", NBO_FROM_LHR, [
        offer("british-economy", "british", "ECONOMY", 60500),
        offer("british-business", "british", "BUSINESS", 290000),
        offer("kenya-economy", "kenya", "ECONOMY", 58500),
        offer("kenya-business", "kenya", "BUSINESS", 305000),
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 49000),
    ]),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], ["ECONOMY_CLASS_LIMIT", "UPGRADE_NOT_ELIGIBLE"], STAFF_OK, AIR),
    [REMOTE, LONG, DIRECT],
    "JG7 on a 520-minute intercontinental flight would get business (lines 134-136), but the traveller is a remote "
    "worker travelling to a work event: economy 'regardless of country of residence' (lines 138-140). The lowest cost "
    "direct economy fare: Kenya Airways (lines 119-121).")

# ===== distractor (2) =====

scenario(
    "okapi-bridge", "distractor", ["multi_leg", "dearer_option"],
    "Nairobi to Amsterdam on 23 March for the evaluation workshop the next afternoon. I'd like lounge access and a "
    "seat with more legroom if that's allowed; otherwise book whatever the policy allows.",
    trip(traveller_name="Ian Fraser", traveller_title="Independent evaluation consultant", role="CONSULTANT",
         origin="NBO", destination="AMS", travel_date="2027-03-23", booking_date="2027-03-01",
         work_starts="2027-03-24 14:00", purpose="Programme evaluation workshop in Amsterdam",
         purpose_kind="PROGRAMME_WORK", sign_offs=[pillar("Evans Mwangi")]),
    search("NBO", "AMS", "2027-03-23", AMS_FLIGHTS, [
        offer("klm-economy", "klm", "ECONOMY", 57000),
        offer("kenya-economy", "kenya", "ECONOMY", 54500),
        offer("kenya-business", "kenya", "BUSINESS", 236000),
        offer("istanbul-economy", "istanbul", "ECONOMY", 46000),
    ]),
    expected("BOOK", ["kenya-economy"], ["ECONOMY"], LOW_CAPPED, STAFF_OK, AIR),
    [CONSULTANTS, DEFAULT, DIRECT],
    "All consultants' travel is economy (line 129). Lines 143-144 allow a lounge and an extra-legroom economy seat on "
    "a flight of more than 4 hours, which is a seat choice inside economy, not a class. The lowest cost direct economy "
    "fare: Kenya Airways (lines 119-121), not the cheaper Istanbul connection.",
    distractors=[LOUNGE, LOUNGE_FEES, CONSULTANT_BUDGET])

scenario(
    "quagga-mesa", "distractor", ["date_arithmetic", "month_end", "dearer_option", "multi_leg"],
    "I'm in London and need to be in Nairobi for the 9am workshop on Tuesday 1 December. Please book the cheapest "
    "way on Monday 30 November; I'll go straight from the airport to the workshop.",
    trip(traveller_name="Moses Kirui", traveller_title="Programme Officer, Agriculture Finance", job_grade=4,
         origin="LHR", destination="NBO", travel_date="2026-11-30", booking_date="2026-11-24",
         work_starts="2026-12-01 09:00", purpose="Agriculture finance workshop in Nairobi",
         purpose_kind="PROGRAMME_WORK", sign_offs=[pillar("Grace Wambui")]),
    search("LHR", "NBO", "2026-11-30", {
        "british": {"carrier": "BA", "depart": "19:30"},
        "kenya": {"carrier": "KQ", "depart": "21:40"},
        "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "18:00", "minutes": [80, 505], "layovers": [90]},
        "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "20:15", "minutes": [420, 285], "layovers": [130]},
    }, [
        offer("british-economy", "british", "ECONOMY", 63500),
        offer("kenya-economy", "kenya", "ECONOMY", 55500),
        offer("amsterdam-economy", "amsterdam", "ECONOMY", 51000),
        offer("dubai-economy", "dubai", "ECONOMY", 47500),
    ]),
    expected("BOOK", ["british-economy"], ["ECONOMY"], LOW, STAFF_OK, AIR),
    [DEFAULT, DIRECT],
    "Economy (JG4, line 118). The Kenya Airways nonstop lands at 09:20 on 1 December and the Dubai connection later, "
    "both after the 09:00 workshop; the lowest cost direct flight that gets the traveller there is BA, landing at "
    "07:10 (lines 119-121), not the cheaper KLM connection. The extra night in-country of lines 141-142 is a hotel "
    "allowance the traveller does not want; it does not change the flight.",
    distractors=[EXTRA_NIGHT, TAXI])

# ===== refusal (2) =====

scenario(
    "rooibos-haven", "refusal", ["personal_travel", "outside_air_section"],
    "Can FSD book my flight from Nairobi to Johannesburg on 21 December? It's our family Christmas holiday; I'll sort "
    "out the cost later.",
    trip(traveller_name="Alice Wairimu", traveller_title="Communications Officer", job_grade=5, origin="NBO",
         destination="JNB", travel_date="2026-12-21", booking_date="2026-11-24", work_starts="",
         purpose="Family Christmas holiday in Johannesburg", purpose_kind="PERSONAL"),
    search("NBO", "JNB", "2026-12-21", {
        "kenya": {"carrier": "KQ", "depart": "08:30"},
        "southafrican": {"carrier": "SA", "depart": "13:10"},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 39000),
        offer("southafrican-economy", "southafrican", "ECONOMY", 41500),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["EXPENSES", "NON_REIMBURSABLE", "POLICY_STATEMENT"]),
    [NONBUSINESS, NECESSARY],
    "Line 242: non-business travel expenses are not reimbursed; lines 71-72: travel must be necessary for FSD "
    "Africa's business. A family holiday is no business trip: FSD Africa buys no ticket.")

scenario(
    "veld-pavilion", "refusal", ["personal_travel", "outside_air_section", "multi_traveller"],
    "Please book my husband on the same flight as me from Nairobi to London on 11 January; he's coming along for the "
    "week while I'm at the conference.",
    trip(traveller_name="James Otieno", traveller_title="Husband of Achieng Otieno, Programme Manager",
         role="RELATIVE_OF_STAFF", accompanies="Achieng Otieno", origin="NBO", destination="LHR",
         travel_date="2027-01-11", booking_date="2026-12-14", work_starts="",
         purpose="Accompanying his wife on her conference trip", purpose_kind="PERSONAL"),
    search("NBO", "LHR", "2027-01-11", LHR_FLIGHTS, [
        offer("kenya-economy", "kenya", "ECONOMY", 54000),
        offer("british-economy", "british", "ECONOMY", 57500),
        offer("dubai-economy", "dubai", "ECONOMY", 47000),
    ]),
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["EXPENSES", "NON_REIMBURSABLE"]),
    [GUESTS, NONBUSINESS],
    "Line 243: costs for personal guests are not reimbursed, nor non-business travel expenses (line 242). FSD Africa "
    "buys no ticket for a staff member's husband.")

# ===== flag (3) =====

scenario(
    "weaver-cove", "flag", ["approval_required", "multi_leg", "dearer_option"],
    "I need a ticket from Nairobi to London on 22 February that I can change or refund without a fee: the investor "
    "meeting may still move. Our DCS has approved that; I'm still waiting to hear from the CFO.",
    trip(traveller_name="Patrick Mwangi", traveller_title="Investment Analyst", job_grade=5, origin="NBO",
         destination="LHR", travel_date="2027-02-22", booking_date="2027-02-01", work_starts="2027-02-23 14:00",
         purpose="Investor meeting in London", purpose_kind="PARTNER_MEETING", wants_flexible_fare=True,
         dates_may_move=True,
         sign_offs=[pillar("Evans Mwangi"), sign("DIRECTOR_CORPORATE_SERVICES", "Jonathan Pike", "FLEXIBLE_FARE")]),
    search("NBO", "LHR", "2027-02-22", LHR_FLIGHTS, LHR_FLEX_OFFERS),
    expected("FLAG_FOR_APPROVAL", ["kenya-flex"], ["ECONOMY"], ["APPROVAL_REQUIRED"], ["CHIEF_FINANCIAL_OFFICER"], AIR),
    [FLEX, DIRECT],
    "Lines 122-123: a fully flexible ticket needs the approval of the DCS and the CFO in advance of booking. The "
    "meeting may move (exceptional), the DCS has approved, the CFO has not: hold the lowest cost direct flexible fare "
    "(Kenya Airways) for the CFO. Approval required, not 'no compliant offer'.",
    flag_twins=["ebony-strand", "guava-terrace"],
    ambiguity="none: an approval is required and missing; the text is clear")

scenario(
    "umbra-kopje", "flag", ["unclear_phrase", "date_arithmetic"],
    "Business class from Nairobi to Dubai on 14 December please, for the co-investment talks the next morning.",
    trip(**{**EXEC_TRIP, "traveller_name": "Joseph Kimani"},
         earlier_business_flights=[*SEVEN_FLIGHTS, "2026-11-10"]),
    search("NBO", "DXB", "2026-12-14", DXB_FLIGHTS, DXB_DIRECTOR_OFFERS),
    expected("FLAG_FOR_APPROVAL", ["emirates-economy", "kenya-business"], ["BUSINESS", "ECONOMY"], UNCLEAR_REASONS,
             UNCLEAR_ROLES, [*AIR, "OPERATING_PRINCIPLES"],
             phrase="not expected to be more than 8 flights per year"),
    [EXEC, DOUBT, CEO],
    "Lines 132-133: executive directors fly business, 'not expected to be more than 8 flights per year'. Eight business "
    "flights so far this year, so this would be the ninth. The text does not say whether the number is an expectation "
    "for budgeting (book business) or a limit (economy, or a CEO exception, lines 151-152); the flight is under 7 "
    "hours, so no other row gives business. Lines 150-151: in doubt over the class, consult the DCS. Hold the business "
    "fare or the economy fare.",
    twin_of="sisal-harbour", twin_fact="earlier business flights this year: 8 or 7",
    flag_twins=["sisal-harbour", "dik-dik-meadow"],
    ambiguity={"phrase": "not expected to be more than 8 flights per year",
               "readings": ["an expectation for budgeting: the director may still fly business on a ninth flight",
                            ("a limit: beyond eight flights the director flies economy unless the CEO grants an "
                            "exception")]})

scenario(
    "zebu-lagoon", "flag", ["unclear_phrase"],
    "Business class from Nairobi to Johannesburg on 18 January please, for the meeting with the regulator the next "
    "morning.",
    trip(traveller_name="Wanjiru Mbugua", traveller_title="Executive Director, Board member", role="EXECUTIVE_DIRECTOR",
         exco_or_board_member=True, origin="NBO", destination="JNB", travel_date="2027-01-18",
         booking_date="2026-12-21", work_starts="2027-01-19 09:00",
         purpose="Meeting with the South African financial regulator", purpose_kind="PARTNER_MEETING",
         requested_cabin="BUSINESS"),
    search("NBO", "JNB", "2027-01-18", {
        "kenya": {"carrier": "KQ", "depart": "08:30"},
        "southafrican": {"carrier": "SA", "depart": "13:10"},
    }, [
        offer("kenya-economy", "kenya", "ECONOMY", 38500),
        offer("kenya-business", "kenya", "BUSINESS", 115000),
        offer("southafrican-economy", "southafrican", "ECONOMY", 41200),
        offer("southafrican-business", "southafrican", "BUSINESS", 124000),
    ]),
    expected("FLAG_FOR_APPROVAL", ["kenya-business", "kenya-economy"], ["BUSINESS", "ECONOMY"], UNCLEAR_REASONS,
             UNCLEAR_ROLES, [*AIR, "OPERATING_PRINCIPLES"], phrase="All flights within Africa"),
    [AFRICA, EXEC, TABLE, DOUBT],
    "The class table gives each row a 'Maximum permitted class': 'All flights within Africa' economy (line 128), and "
    "executive directors business (lines 132-133; no earlier business flight this year). Both rows describe this "
    "flight and the table gives no order between them. Lines 150-151: where there is any doubt over the class, consult "
    "the DCS in advance. Hold the business fare or the economy fare.",
    flag_twins=["sisal-harbour", "ibis-causeway"],
    ambiguity={"phrase": "All flights within Africa",
               "readings": ["the within-Africa row caps every flight in Africa at economy, a director's too",
                            "the director row is specific to the person: an executive director flies business"]})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
