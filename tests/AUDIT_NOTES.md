# Independent audit: fsd-africa-flight-policy (2026-11-25)

I audited the builder's commit 76d4b13 against `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`,
`WAVE3_BUILD_BRIEF.md` (lessons 1-12), MASTER_PLAN section 4, EDGE_CASES sections 1-3 and 5, and the worked audits
(georgia-sao, fedex-office, goodman-networks, hillrom). No money was spent and nothing was pushed. Line numbers refer to
the frozen handbook (`src/plugin/data/policy.txt`).

## Method

I printed each scenario's `get_trip` record and its pinned `search_flights` result through the plugin's own tools. I
then answered each case from section 3.1 (lines 117-152), the operating principles (lines 98-115), 5.6 (lines
236-245) and 6.2 (lines 276-279) alone. Only after that did I compare my answers with the key, field by field:
decision, offer, cabin, reason, approver and clause.

## Verdict

**Pass after fixes.** On all 21 non-flag cases, the key's decision and offer match my own reading. The three flags
are sound. Each twin pair differs in exactly one fact; I diffed the request, trip and world of every pair:

- 420 against 421 scheduled minutes;
- JG6 against JG5;
- nonstop seats available against sold out;
- 7 against 8 earlier business flights.

Traveller names differ too, but they decide nothing. No request leaks rule wording. The decline sentence is the last
line of the task instructions. Every request that names a cabin the policy may refuse has a fallback ("otherwise
economy", "book what the policy allows").

## The builder's open items, settled

- **"direct" read as nonstop.** Kept. The world has no through-flight with a stop, so the only other reading is "the
  most direct routing". Every keyed nonstop is also the most direct routing, so both readings give the same offer.
  - In the two cases with no bookable nonstop:
    - `fynbos-gate` has one bookable offer.
    - In `marula-quay`, the keyed KLM offer via AMS is both the cheapest and tied for the shortest elapsed time
      (680 minutes, against BA's 680 and EK's 855).
  - So no case needs the record to be more explicit.
- **A nonstop that lands after the traveller is due is not "readily available".** Kept.
  - `quagga-mesa` is the only case with a late nonstop: KQ lands at 09:20 for a 09:00 workshop, and the traveller
    goes "straight from the airport".
  - No reading books a flight that lands after the event begins. The BA nonstop lands at 07:10, so a direct flight
    is available on any reading.
  - `rules.timely` raises on the only open combination (only late nonstops beside a timely connection), and no
    scenario uses it.
- **`work_starts` is visible and consistent.**
  - It is a `Trip` field with its own description. `get_trip` returns it, and `booking_requirements` lists it.
  - Every booking has one, and each request says the same thing ("the next morning", "at nine", "the next
    afternoon"), or says nothing where the margin is many hours (`ebony-strand`, `weaver-cove`, `kudu-lantern`).
  - Both twins of every pair carry the same value.
  - I found one tight margin (fixed below, `namib-orchard`).
- **Premium economy is never offered to a traveller who is not entitled.** Confirmed. Only `kudu-lantern` lists
  premium economy offers (JG8, 480-minute intercontinental flight). `rules.premium` raises on a premium economy request
  without a business entitlement.
- **Reason codes.** The builder's sets were sound. I added five further codes that a correct answer can reasonably
  use (see fix 3).
- **`umbra-kopje` (the ninth business flight) is genuinely two-reading.** Kept.
  - "(not expected to be more than 8 flights per year)" is the language of expectation, not prohibition. That reading
    books business.
  - It is also the only number the table gives for directors. Read as a cap, it puts the ninth flight in economy, or
    makes it an exception for the CEO (lines 151-152).
  - Lines 150-151 say that in doubt over the class one consults the DCS in advance, so holding is the careful
    answer. Both held offers are accepted.
  - `earlier_business_flights` is defined as this calendar year's one-way tickets, so the count itself is not in
    doubt. A rolling 12-month reading would need data the record does not give.
- **`zebu-lagoon` (overlapping rows in the class table) is genuinely two-reading.** Kept.
  - The table is a list of "Maximum permitted class" rows with no order.
  - One reading: every row is a cap, so the strictest applicable row binds. "All flights within Africa" gives
    economy, a director's flights included.
  - The other reading: the director rows are personal entitlements, so the director flies business.
  - Other rows overlap without the same doubt:
    - In `hibiscus-ford`, the training row says "regardless of duration", which answers the long-flight row
      directly.
    - In `namib-orchard`, the remote-worker row says "regardless of country of residence", which is aimed at the
      long-haul case.
  - Both of those give economy on either reading, so they are correctly BOOK cases.
- **Baseline.** The always-cheapest agent passes 3 of 24: `baobab-crest`, `fynbos-gate` and `marula-quay`. The
  always-flag agent passes 2 (the two unclear flags).

## Defects found and fixed

1. **`namib-orchard`: the keyed flight landed 35 minutes before the event.**
   - The KQ nonstop lands at NBO at 08:25 for an all-staff retreat at 09:00. A careful agent could reject it as
     unrealistic (immigration, then the drive) and book the BA nonstop (07:10, £605), which the key does not accept.
   - Fix: the retreat now starts at ten (request "starts at ten the next morning", `work_starts` 2027-04-13 10:00).
     This is the same 95-minute margin `lobelia-spur` uses on the same flight.
   - Offers, ids and the key (KQ economy £585) are unchanged.
2. **`tamarind-ridge` / `cassava-ledge`: the keyed business fare was open on lines 125-126.**
   - Lines 125-126: "approval of a higher class of travel will depend on the time of flights being taken and the
     activities being undertaken on arrival".
   - The keyed KQ business fare was a daytime flight (09:05-14:06) with the presentation the next morning. On that
     sentence, a careful reader could decline business for a daytime flight with an evening free to rest.
   - Fix: in both twins, the request now reads "I'm presenting to investors in Rome at a dinner that evening", and
     `work_starts` is 2027-01-26 19:00. That is an activity on arrival, so the higher class is supported. The
     cheaper EK connection still lands in time (13:40).
   - Twins still differ only in 420/421. Keys and ids are unchanged.
   - The other business and premium economy bookings already fit the sentence:
     - `jacaranda-weir`, `lobelia-spur` and `kudu-lantern` are overnight flights with work the next morning.
     - `sisal-harbour` lands at 22:30, before talks the next morning.
3. **Reason codes a correct answer may give.**
   - `kudu-lantern` adds `LONG_FLIGHT_APPROVED` and `SENIOR_ROLE_ENTITLEMENT`. Premium economy is permitted by the
     same long-flight row (JG6 and above) that the business-by-grade bookings cite with these codes.
   - `lobelia-spur` adds `LONG_FLIGHT_APPROVED` beside `INTERNATIONAL_LONG_FLIGHT`, which was already accepted on
     this 520-minute flight.
   - Every declined business request adds `TRAVELER_PAYS_UPGRADE` (`cassava-ledge`, `papyrus-knoll`,
     `ibis-causeway`, `hibiscus-ford`, `namib-orchard`). The key's own explanation cites lines 102-105 (a higher
     class is the traveller's cost), and georgia-sao accepts the same code. `LOWEST_FARE` stays out (lesson 12).
   - `veld-pavilion` adds `OUTSIDE_POLICY_SCOPE` and the `POLICY_STATEMENT` clause. Lines 68-70 apply the policy to
     "all personnel", and a staff member's husband is not one. `rooibos-haven` already accepted both.
   - `weaver-cove` adds `REFUNDABLE_FARE_NOT_ALLOWED` beside `APPROVAL_REQUIRED`: the reason that calls for the
     missing sign-off (as `answer.shape_problem` allows). The approver stays CFO only (4').
4. **Schema hint toward a cabin sign-off.**
   - The `SignOffSubject.CABIN` description read "a cabin above economy". No case ever carries such a sign-off, so
     the description invited a reader to hold every permitted business or premium economy booking for a sign-off
     that is never on file. Taken with lines 125-126, that could happen in five BOOK cases.
   - The description now reads "a class of travel above the one the policy permits for the trip (an exception)",
     which matches lines 151-152. The enum value itself is unchanged.

`MAX_PASS_ALWAYS_LOWEST`: **3 -> 3** (unchanged).

## Seen and kept

- `quagga-mesa` asks for "the cheapest way". The key books the dearer BA nonstop and accepts both
  `DIRECT_FLIGHT_PREFERRED` and `LOWEST_FARE`. The ground for declining is the "lowest cost direct flight" principle,
  so under lesson 12 it is the lowest-fare rule itself. The KLM connection lands at 08:15 for 09:00; it is not keyed,
  and a reader who finds that margin too tight books BA anyway.
- `guava-terrace` books the non-flexible fare. The request carries the fallback ("If that needs a sign-off I don't
  have, book what the policy allows"), so no hold is needed.
- Director bookings (`sisal-harbour`, `lobelia-spur`) carry no sign-off. The table grants directors business
  outright, and the handbook names no approver of directors' trips, so the approver is `NONE` only.
- Unclear holds accept `NOT_NAMED`, the DCS and the CEO. `BOARD_CHAIR` (line 114, exceptions that relate to the CEO)
  is not added: neither director's title is CEO.
- `okapi-bridge`'s "lounge access and a seat with more legroom" paraphrases the distractor's subject, not its
  wording or threshold.
- The builder's template change request (more African airports) stands.

## Files changed

- `src/plugin/rules.py` and `verifier/rules.py` (byte-identical): the reason and clause sets above.
- `tests/build_scenarios.py`: the accept sets, the FCO request and deadline, namib's deadline, tamarind's note.
- 10 scenario JSON files, regenerated.
- `contract.py`: the sign-off subject description.
- `README.md`: the declined-business reason line.

## Check outputs (audit commit)

- `uv run pytest -q`: 210 passed.
- `uv run ruff check .`: all checks passed.
- `uv lock --check`: resolved 42 packages.
- `python3 ../_template/check_shared.py .`: ok.
- `tools/stock_verify.py .` (stock Python): 24 scenarios, 0 failures.
- Stock `nanoagent plugin inspect .`: exit 0.
