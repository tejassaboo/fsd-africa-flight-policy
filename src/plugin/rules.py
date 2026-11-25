"""The answer key's rules for the FSD Africa Travel & Expense Policy, version 4.0 (CORP-POL-006, approved March
2024), as exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules
a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. The frozen text keeps the PDF's
stray mid-word spaces ("w ith", "a pproved"); quotations below are copied as they stand. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each unclear
phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a new scenario
cannot fall silently into untested logic.

The duration hook. Lines 134-136 give business class on "Intercontinental flights of more than 7 hours' duration"
(strict), and lines 143-144 allow lounges and extra-legroom economy seats "For flights of more than 4 hours'
duration" (strict). Both speak of a flight's duration. A nonstop is over the limit when its scheduled minutes
exceed it. For a connection, "flight" may mean each segment or the whole journey: when every segment is over the
limit every reading agrees (over); when the whole elapsed journey is within the limit every reading agrees (not
over); otherwise the reading is unclear (None), and no scenario relies on such an itinerary.
"""

from contract import Approver, Cabin, Clause, Decision, Purpose, ReasonCode, Role, SignOffSubject

from .world import utc_minute, utc_offset

HANDBOOK = "FSD Africa, Travel & Expense Policy, version 4.0 (CORP-POL-006), March 2024"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.POLICY_SUMMARY: "Policy Summary",
    Clause.DOCUMENT_CONTROL: "Document Control",
    Clause.POLICY_STATEMENT: "1. POLICY STATEMENT",
    Clause.OPERATING_PRINCIPLES: "2. OPERATING PRINCIPLES & PRACTICE",
    Clause.TRANSPORTATION: "3. TRANSPORTATION",
    Clause.AIR_TRAVEL: "3.1. Air Travel",
    Clause.RAIL_TRAVEL: "3.2. Rail Travel",
    Clause.TAXI_CAR_TRAVEL: "3.3. Taxi/Car Travel",
    Clause.ACCOMMODATION: "4. ACCOMMODATION",
    Clause.ACCOMMODATION_GENERAL: "4.1. General",
    Clause.MAJOR_CITIES: "4.2. Accommodation in London and other major cities",
    Clause.EXPENSES: "5. EXPENSES",
    Clause.HOTEL_COSTS: "5.1. Hotel costs",
    Clause.SUBSISTENCE: "5.2. Subsistence",
    Clause.PHONE_CALLS: "5.3. Phone Calls",
    Clause.FOREIGN_CURRENCY: "5.4. Foreign Currency",
    Clause.PASSPORT_RENEWAL: "5.5. Passports",
    Clause.NON_REIMBURSABLE: "5.6. Non-Reimbursable Expenses",
    Clause.BUSINESS_HOSPITALITY: "5.7. Business Hospitality",
    Clause.STAFF_ENTERTAINMENT: "5.8. Staff Entertainment",
    Clause.SAFETY_AND_SECURITY: "6. TRAVELLER SAFETY AND SECURITY",
    Clause.EMERGENCIES: "6.1. Emergencies",
    Clause.GROUP_TRAVEL: "6.2. Group Travel",
    Clause.VISAS_AND_MEDICAL: "6.3. Passports, Visas & Medical expenses",
    Clause.HEALTH_AND_SAFETY: "6.4. Health and Safety While Travelling",
    Clause.CARBON_FOOTPRINT: "7. CARBON FOOTPRINT STATEMENT",
}

# The handbook's duration thresholds (the per-handbook duration hook; tests/test_duration.py tests both sides of
# each). ">" is strict ("more than").
DURATION_RULES = (
    {"name": "long-flight", "minutes": 420, "operator": ">", "lines": [134, 136],
     "quote": "Intercontinental flights of more than 7 hours' duration for employees in JG6 and above Business"},
    {"name": "lounge", "minutes": 240, "operator": ">", "lines": [143, 144],
     "quote": "For flights of more than 4 hours' duration, access to airport lounges and booking of seats with greater "
              "legroom in Economy is allowable."},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# The countries of the world's African airports (NBO Kenya, JNB South Africa, CAI Egypt). Lines 128 ("All flights
# within Africa") and 134 ("Intercontinental flights"): a flight between two of them is within Africa; a flight
# between one of them and an airport elsewhere is intercontinental.
AFRICA = frozenset({"KE", "ZA", "EG"})
# Lines 134-136: "employees in JG6 and above" (inclusive).
JOB_GRADE_FLOOR = 6
# Lines 130-133: business for non-executive directors "not expected to be more than 3 flights per year" and for
# executive directors "not expected to be more than 8 flights per year". This flight is within the number when the
# earlier business flights of the calendar year plus this one come to no more than it; a flight beyond it is the
# unclear case (a soft expectation, or a limit?).
DIRECTOR_FLIGHTS = {Role.NON_EXECUTIVE_DIRECTOR: 3, Role.EXECUTIVE_DIRECTOR: 8}
# Lines 278-279: "no more than three members of FSD Africa's Executive Committee or Board should travel together on
# the same flig ht" ("Where possible"): a flight on which three are already booked is avoided when another is open.
GROUP_LIMIT = 3

AFRICA_PHRASE = "All flights within Africa"
DIRECTOR_PHRASES = {
    Role.NON_EXECUTIVE_DIRECTOR: "not expected to be more than 3 flights per year",
    Role.EXECUTIVE_DIRECTOR: "not expected to be more than 8 flights per year",
}

# Who a hold over unclear words may name. Lines 150-151: "Where there is any doubt as to whether to book a
# particular class of travel ... all personnel must consult with the DCS in advance"; lines 151-152: "Exceptions to
# the classes of travel described above will need to be approved by the CEO" (also lines 114-115).
UNCLEAR_ROLES = [Approver.NOT_NAMED, Approver.DIRECTOR_CORPORATE_SERVICES, Approver.CHIEF_EXECUTIVE]
# Such a hold also waits on that sign-off, so APPROVAL_REQUIRED may stand beside UNCLEAR_POLICY_TEXT.
UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
# Lines 122-123: fully flexible tickets "only with approval from the DCS and CFO in advance of booking".
FLEXIBLE_ROLES = [Approver.DIRECTOR_CORPORATE_SERVICES, Approver.CHIEF_FINANCIAL_OFFICER]

AIR = [Clause.AIR_TRAVEL, Clause.TRANSPORTATION]


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s outbound flights are over the handbook's ``rule``
    (long-flight: more than 420 minutes; lounge: more than 240 minutes)."""
    if rule not in LIMITS:
        raise ValueError(f"unknown duration rule {rule!r}")
    limit = LIMITS[rule]
    if all(segment.scheduled_minutes > limit for segment in offer.segments):
        return True
    if offer.elapsed_minutes <= limit:
        return False
    return None


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reasons, clauses, why):
    return answer(Decision.REFUSE, [], reasons, [Approver.NONE], clauses, why)


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def in_cabin(offers, cabin):
    return [offer for offer in offers if offer.cabin == cabin]


def signed(trip, subject, roles):
    return by_value(record.role for record in trip.sign_offs if record.subject == subject and record.role in roles)


def unused_sign_offs(trip):
    """Approvers a decision that relies on no special sign-off accepts: NONE, and the role of any sign-off on file
    (the trip approval by the pillar head, lines 145-146, is routine; SYNC_NOTES 4' and 4(b))."""
    return [Approver.NONE, *(record.role for record in trip.sign_offs)]


def where(trip):
    """'africa' for a flight within Africa (line 128), 'intercontinental' for one between Africa and elsewhere
    (line 134)."""
    inside = [trip.origin.country in AFRICA, trip.destination.country in AFRICA]
    if all(inside):
        return "africa"
    if any(inside):
        return "intercontinental"
    raise ValueError("a trip with neither end in Africa is not modelled")


def start_utc(trip):
    return utc_minute(trip.work_starts) - utc_offset(trip.destination.code)


def in_time(trip, offers):
    """The offers that land by the time the traveller is due at the work (the trip record's work_starts)."""
    due = start_utc(trip)
    return [offer for offer in offers if utc_minute(offer.segments[-1].arrive_utc) <= due]


def group_full(trip, offer):
    """Lines 276-279: whether ``offer``'s first flight already carries three ExCo or Board members."""
    if not trip.exco_or_board_member:
        return False
    first = offer.segments[0]
    return any(booking.members >= GROUP_LIMIT and booking.carrier == offer.carrier
               and booking.depart_local == first.depart_local for booking in trip.colleagues_booked)


def direct_choice(trip, offers):
    """Lines 119-121: 'the principle of the lowest cost direct flight consistent w ith this policy (where direct
    flights are readily available)'. ``offers`` are the bookable, timely offers of the cabin and fare type: the
    cheapest nonstop when there is one, else the cheapest itinerary. Returns (offers, notes, decided), ``decided``
    True when the direct-flight principle or the group rule passed over a cheaper itinerary of the cabin."""
    open_offers = [offer for offer in offers if not group_full(trip, offer)]
    grouped = len(open_offers) < len(offers)
    nonstops = [offer for offer in open_offers if offer.stops == 0]
    notes = []
    if nonstops:
        chosen = cheapest(nonstops)
        notes.append("lines 119-121: the lowest cost direct flight, since direct flights are readily available")
    else:
        chosen = cheapest(open_offers)
        notes.append("lines 119-121: no direct flight is available, so the lowest cost itinerary")
    if not chosen:
        raise ValueError("no bookable offer is left")
    if grouped:
        if not nonstops:
            raise ValueError("the group rule with no other nonstop is not modelled")
        notes.append("lines 276-279: three ExCo or Board members are already booked on the other nonstop, so this "
                     "traveller takes another flight")
    passed_over = any(offer.fare_cents < chosen[0].fare_cents for offer in offers)
    return chosen, notes, passed_over or grouped


def timely(trip, seated, cabin):
    """The bookable offers of ``cabin`` that land in time. A nonstop that lands late while a connection lands in
    time is not modelled (both readings of 'readily available' would be needed)."""
    offered = in_cabin(seated, cabin)
    usable = in_time(trip, offered)
    if any(offer.stops == 0 for offer in offered) and not any(offer.stops == 0 for offer in usable) and usable:
        raise ValueError("only late nonstops beside a timely connection is not modelled")
    if not usable:
        raise ValueError(f"no {cabin.value} offer lands in time")
    return usable


def fixed_fares(offers):
    return [offer for offer in offers if not offer.refundable]


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys a one-way ticket")
    seated = [offer for offer in offers if offer.seats_available]
    if trip.role == Role.RELATIVE_OF_STAFF:
        if not trip.accompanies:
            raise ValueError("a relative travelling with nobody is not modelled")
        return refuse([ReasonCode.COMPANION_NOT_COVERED, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Clause.NON_REIMBURSABLE, Clause.EXPENSES],
                      "Line 243: costs for personal guests are not reimbursed (also line 242, non-business travel "
                      "expenses). FSD Africa buys no ticket for a staff member's relative.")
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.NON_REIMBURSABLE, Clause.EXPENSES, Clause.POLICY_STATEMENT],
                      "Line 242: non-business travel expenses are not reimbursed; lines 71-72: travel must be "
                      "necessary for the conduct of FSD Africa's business. FSD Africa buys no ticket for a holiday.")
    if trip.wants_flexible_fare:
        return flexible(trip, seated)
    if trip.dates_may_move:
        raise ValueError("plans that may move without a flexible-fare request are not modelled")
    if trip.requested_cabin == Cabin.BUSINESS:
        return business(trip, seated)
    if trip.requested_cabin == Cabin.PREMIUM_ECONOMY:
        return premium(trip, seated)
    if trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError(f"a {trip.requested_cabin.value} request is not modelled")
    return economy(trip, seated)


def economy_row(trip):
    """The rows of the class table (lines 127-140) that cap this traveller at economy whatever the flight's length,
    as (reason codes beside UPGRADE_NOT_ELIGIBLE, note), or None."""
    if trip.role == Role.CONSULTANT:
        return [ReasonCode.ECONOMY_CLASS_LIMIT], "line 129: all consultants' travel is economy"
    if trip.purpose_kind == Purpose.TRAINING_COURSE:
        return [ReasonCode.ECONOMY_CLASS_LIMIT], "line 137: all flights to attend training, regardless of duration, economy"
    if trip.works_remotely:
        if trip.purpose_kind != Purpose.STAFF_EVENT:
            raise ValueError("a remote worker travelling for anything but a work event is not modelled")
        return [ReasonCode.ECONOMY_CLASS_LIMIT], ("lines 138-140: remote workers travelling to attend work events, "
                                                  "regardless of country of residence, economy")
    if where(trip) == "africa" and trip.role == Role.STAFF:
        return ([ReasonCode.ECONOMY_CLASS_LIMIT, ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET],
                "line 128: all flights within Africa are economy; line 134's business row is for intercontinental flights")
    return None


def director_entitlement(trip):
    """Lines 130-133 for a Board director: 'ok', or an unclear answer key's phrase."""
    if where(trip) == "africa":
        # Line 128 ("All flights within Africa: Economy") and lines 130-133 (directors: business) both describe
        # this flight, and the table gives no order between its rows.
        return AFRICA_PHRASE
    if len(trip.earlier_business_flights) + 1 > DIRECTOR_FLIGHTS[trip.role]:
        return DIRECTOR_PHRASES[trip.role]
    return "ok"


def unclear_hold(trip, seated, phrase, why):
    """Hold either reading's offer: the cheapest direct business fare, or the cheapest direct economy fare."""
    business_pick, _, _ = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.BUSINESS)))
    economy_pick, _, _ = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.ECONOMY)))
    return answer(Decision.FLAG_FOR_APPROVAL, [*business_pick, *economy_pick], UNCLEAR_REASONS, UNCLEAR_ROLES,
                  [*AIR, Clause.OPERATING_PRINCIPLES], why, phrase=phrase)


def business(trip, seated):
    """A business request: granted by the class table's director rows (lines 130-133) or its long-flight row
    (lines 134-136), and capped at economy by its other rows."""
    if trip.role in DIRECTOR_FLIGHTS:
        if trip.job_grade or trip.works_remotely or trip.purpose_kind == Purpose.TRAINING_COURSE:
            raise ValueError("a director with a job grade, remote or on a training trip is not modelled")
        verdict = director_entitlement(trip)
        if verdict == AFRICA_PHRASE:
            return unclear_hold(trip, seated, verdict,
                                "Line 128: 'All flights within Africa' are economy at most, while lines 130-133 give an "
                                "executive or non-executive director business; the table does not say which row wins for "
                                "a director flying within Africa, and lines 150-151 send a doubt over the class to the DCS: "
                                "hold the business fare or the economy fare.")
        if verdict != "ok":
            return unclear_hold(trip, seated, verdict,
                                f"Lines 130-133: the director's business flights are '{verdict}'. This flight is beyond "
                                "that number; the text does not say whether the number is a soft expectation (book "
                                "business) or a limit (book economy, or ask the CEO for an exception, lines 151-152): hold.")
        chosen, notes, decided = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.BUSINESS)))
        reasons = [ReasonCode.SENIOR_ROLE_ENTITLEMENT]
        if where(trip) == "intercontinental" and all(over("long-flight", offer) for offer in chosen):
            reasons.append(ReasonCode.INTERNATIONAL_LONG_FLIGHT)
        clauses = list(AIR)
        if decided:
            reasons.append(ReasonCode.DIRECT_FLIGHT_PREFERRED)
        if any(group_full(trip, offer) for offer in in_cabin(seated, Cabin.BUSINESS)):
            reasons.append(ReasonCode.TRAVELLER_LIMIT_PER_FLIGHT)
            clauses += [Clause.GROUP_TRAVEL, Clause.SAFETY_AND_SECURITY]
        count = len(trip.earlier_business_flights) + 1
        return answer(Decision.BOOK, chosen, reasons, unused_sign_offs(trip), clauses,
                      f"Lines 130-133: a {trip.role.value.lower().replace('_', '-')} may fly business, and this is "
                      f"business flight number {count} of the year, within the number the table expects; "
                      + "; ".join(notes) + ".")
    if trip.role not in (Role.STAFF, Role.CONSULTANT):
        raise ValueError(f"a {trip.role.value} traveller is not modelled")
    row = economy_row(trip)
    if row is not None:
        return declined_business(trip, seated, row[0], row[1])
    if where(trip) != "intercontinental":
        raise ValueError("a staff flight that is neither within Africa nor intercontinental is not modelled")
    business_offers = fixed_fares(timely(trip, seated, Cabin.BUSINESS))
    lengths = {over("long-flight", offer) for offer in business_offers}
    if None in lengths or len(lengths) != 1:
        raise ValueError("business offers of unclear or mixed length are not modelled")
    if trip.job_grade < JOB_GRADE_FLOOR:
        return declined_business(trip, seated, [ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET, ReasonCode.ECONOMY_CLASS_LIMIT],
                                 f"lines 134-136: business is for employees in JG6 and above, and the traveller is JG"
                                 f"{trip.job_grade}; line 118: the default class is economy")
    if lengths != {True}:
        return declined_business(trip, seated, [ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET, ReasonCode.ECONOMY_CLASS_LIMIT],
                                 "lines 134-136: business is for intercontinental flights of more than 7 hours, and this "
                                 "flight is not more than 420 minutes; line 118: the default class is economy")
    chosen, notes, decided = direct_choice(trip, business_offers)
    # "employees in JG6 and above" is an entitlement by seniority, so SENIOR_ROLE_ENTITLEMENT also names it.
    reasons = [ReasonCode.INTERNATIONAL_LONG_FLIGHT, ReasonCode.LONG_FLIGHT_APPROVED, ReasonCode.SENIOR_ROLE_ENTITLEMENT]
    if decided:
        reasons.append(ReasonCode.DIRECT_FLIGHT_PREFERRED)
    return answer(Decision.BOOK, chosen, reasons, unused_sign_offs(trip), AIR,
                  "Lines 134-136: an intercontinental flight of more than 7 hours (over 420 minutes) for an employee in "
                  f"JG6 or above (JG{trip.job_grade}) may be business; " + "; ".join(notes) + ".")


def declined_business(trip, seated, codes, note):
    """Business is not permitted: book economy. The reason names why the request is declined, so LOWEST_FARE is
    not accepted."""
    chosen, notes, _ = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.ECONOMY)))
    return answer(Decision.BOOK, chosen, [ReasonCode.UPGRADE_NOT_ELIGIBLE, *codes], unused_sign_offs(trip), AIR,
                  note.capitalize() + ", so business is not permitted; " + "; ".join(notes)
                  + ". Lines 102-105: anything above the policy is the traveller's own cost.")


def business_permitted(trip, seated):
    """Whether business would be permitted (for a lower-class request: lines 108-110 let staff choose lower)."""
    if trip.role != Role.STAFF or economy_row(trip) is not None or trip.job_grade < JOB_GRADE_FLOOR:
        return False
    if where(trip) != "intercontinental":
        return False
    offered = in_cabin(seated, Cabin.BUSINESS)
    return bool(offered) and all(over("long-flight", offer) is True for offer in offered)


def premium(trip, seated):
    """A premium economy request where business is permitted: lines 107-110, premium economy/business on long
    flights, and staff 'may choose a lower class of travel at thei r own discretion'."""
    if not business_permitted(trip, seated):
        raise ValueError("a premium economy request without a business entitlement is not modelled")
    chosen, notes, decided = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.PREMIUM_ECONOMY)))
    reasons = [ReasonCode.PREMIUM_ECONOMY_ALLOWED, ReasonCode.INTERNATIONAL_LONG_FLIGHT]
    if decided:
        reasons.append(ReasonCode.DIRECT_FLIGHT_PREFERRED)
    return answer(Decision.BOOK, chosen, reasons, unused_sign_offs(trip), [*AIR, Clause.OPERATING_PRINCIPLES],
                  "Lines 134-136: business is permitted on this intercontinental flight of more than 7 hours for JG"
                  f"{trip.job_grade}; lines 107-110: premium economy is permitted on long flights and staff may choose a "
                  "lower class than business; " + "; ".join(notes) + ".")


def economy(trip, seated):
    """An economy request: line 118, the default class, at the lowest cost direct flight (lines 119-121)."""
    chosen, notes, _ = direct_choice(trip, fixed_fares(timely(trip, seated, Cabin.ECONOMY)))
    reasons = [ReasonCode.LOWEST_FARE, ReasonCode.DIRECT_FLIGHT_PREFERRED]
    clauses = list(AIR)
    lead = "Line 118: the default class is economy"
    row = economy_row(trip)
    if row is not None:
        # A row of the class table caps this traveller at economy (consultants, within Africa, ...), so a reader
        # may name that cap as the reason for the economy fare.
        reasons.append(ReasonCode.ECONOMY_CLASS_LIMIT)
        lead += "; " + row[1]
    if business_permitted(trip, seated):
        clauses.append(Clause.OPERATING_PRINCIPLES)
        lead = ("Lines 134-136 would permit business, but lines 108-110 let staff choose a lower class at their own "
                "discretion: economy")
    if any(group_full(trip, offer) for offer in in_cabin(seated, Cabin.ECONOMY)):
        raise ValueError("the group rule on an economy request is not modelled")
    late = [offer for offer in in_cabin(seated, Cabin.ECONOMY) if offer not in in_time(trip, seated)]
    if late:
        notes.append("the cheaper flights that land after the traveller is due at the work are of no use to the trip")
    if all(over("lounge", offer) is True for offer in chosen):
        notes.append("lines 143-144: a flight of more than 4 hours allows a lounge and an extra-legroom economy seat, "
                     "which changes neither the class nor the fare")
    return answer(Decision.BOOK, chosen, reasons, unused_sign_offs(trip), clauses, lead + "; " + "; ".join(notes) + ".")


def flexible(trip, seated):
    """Lines 122-123: 'Fully flexible tickets are permitted only in excepti onal circumstances and only with approval
    from the DCS and CFO in advance of booking.' A flexible fare is one that can be refunded or changed without a
    fee."""
    if trip.requested_cabin != Cabin.ECONOMY or trip.role != Role.STAFF or business_permitted(trip, seated):
        raise ValueError("a flexible-fare request outside a plain economy staff trip is not modelled")
    usable = timely(trip, seated, Cabin.ECONOMY)
    roles = signed(trip, SignOffSubject.FLEXIBLE_FARE, FLEXIBLE_ROLES)
    if not trip.dates_may_move:
        if roles:
            raise ValueError("approvals for a flexible fare on fixed plans are not modelled")
        chosen, notes, _ = direct_choice(trip, fixed_fares(usable))
        # The reason names why the flexible fare is declined, so LOWEST_FARE is not accepted.
        return answer(Decision.BOOK, chosen, [ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED], unused_sign_offs(trip), AIR,
                      "Lines 122-123: a fully flexible ticket needs exceptional circumstances and the DCS's and CFO's "
                      "approval before booking; the plans are fixed and neither approval is on file, and the traveller "
                      "asked for what the policy allows otherwise: the non-flexible fare; " + "; ".join(notes) + ".")
    flexible_offers = [offer for offer in usable if offer.refundable]
    chosen, notes, _ = direct_choice(trip, flexible_offers)
    if roles == by_value(FLEXIBLE_ROLES):
        return answer(Decision.BOOK, chosen,
                      [ReasonCode.FLEXIBLE_FARE_APPROVED, ReasonCode.DIRECT_FLIGHT_PREFERRED, ReasonCode.LOWEST_FARE],
                      [*unused_sign_offs(trip), *roles], AIR,
                      "Lines 122-123: the meeting may still move (an exceptional circumstance) and both the DCS and the "
                      "CFO approved the flexible ticket before booking: the flexible fare; " + "; ".join(notes) + ".")
    if not roles:
        raise ValueError("a flexible fare on moving plans with no approval at all is not modelled")
    missing = [role for role in FLEXIBLE_ROLES if role not in roles]
    return answer(Decision.FLAG_FOR_APPROVAL, chosen, [ReasonCode.APPROVAL_REQUIRED], missing, AIR,
                  "Lines 122-123: a fully flexible ticket needs approval from the DCS and the CFO in advance of booking; "
                  f"only {roles[0].value} has approved, so hold the flexible fare for "
                  f"{missing[0].value}; " + "; ".join(notes) + ".")
