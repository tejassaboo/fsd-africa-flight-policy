# Build notes: fsd-africa-flight-policy (wave 3, 2026-11-24)

Built from `_template` with `instantiate.py` (slug `fsd-africa`, `--task-id book-fsd-africa-flight`, `--currency GBP`,
`--background 0`, `--scenarios 24`). Frozen handbook: `pilot_work/originals/fsd-africa/frozen/fsd-africa_policy.txt`,
3,143 words (under 10,000, so 24 scenarios), 310 lines, sha256 `ba74787a...a366c8`. Decisions were taken without
asking (the lead was away); each is recorded here.

## 1. What the handbook supports

Mandatory or checkable flight clauses (frozen line numbers; the text keeps the PDF's stray mid-word spaces, and every
`must_keep` quote copies them as they are):

| Lines | Clause | Operator / force | Used by |
|---|---|---|---|
| 118 | "The default class of travel for all flights is Economy." | mandatory | every economy booking |
| 119-121 | "the principle of the lowest cost direct flight consistent w ith this policy (where direct flights are readily available)" | mandatory principle | every booking |
| 122-123 | fully flexible tickets "only in excepti onal circumstances and only with approval from the DCS and CFO in advance of booking" | mandatory, two approvers | ebony-strand, guava-terrace, weaver-cove |
| 127-128 | class table: "All flights within Africa Economy" | maximum class | baobab-crest, ibis-causeway, zebu-lagoon |
| 129 | "All consultants' travel Economy" | maximum class | okapi-bridge |
| 130-131 | non-executive directors: Business "(not expected to be more than 3 flights per year)" | grant; soft count | lobelia-spur |
| 132-133 | executive directors: Business "(not expected to be more than 8 flights per year)" | grant; soft count | sisal-harbour, umbra-kopje, zebu-lagoon |
| 134-136 | "Intercontinental flights of more than 7 hours' duration for employees in JG6 and above" Business | strict (7 h), inclusive (JG6) | tamarind-ridge, cassava-ledge, jacaranda-weir, papyrus-knoll, kudu-lantern, acacia-drift |
| 137 | "All flights to attend training, regardless of duration Economy" | maximum class | hibiscus-ford |
| 138-140 | "Remote workers travelling to attend work events, regardless of country of residence" Economy | maximum class | namib-orchard |
| 107-110 | premium economy/business on long flights; staff "may choose a lower class of travel" | permission | kudu-lantern, acacia-drift |
| 143-144 | lounges and extra-legroom economy seats on flights of more than 4 hours | permission inside economy | okapi-bridge (distractor) |
| 150-152, 114-115 | in doubt over the class consult the DCS; class exceptions need the CEO | process | the two unclear flags |
| 242-243 | non-business travel expenses and costs for personal guests are not reimbursed | mandatory | rooibos-haven, veld-pavilion |
| 277-279 | "Where possible, no more than three members of FSD Africa's Executive Committee or Board should travel together on the same flig ht" | soft, outside the air section | lobelia-spur |

Not used: the 4-hour lounge rule decides no booking (the world sells cabins, not seats or lounges); the extra night
in-country (141-142), the pillar-head trip approval (145-146, routine and always on file), the rail, taxi, hotel and
expense sections. There is no advance-purchase or day-count rule: the `date_arithmetic` overlays are an overnight
arrival against a deadline across a month end (quagga-mesa, lobelia-spur) and counting a director's earlier
business flights this calendar year (sisal-harbour, umbra-kopje). No rule on overnight stops, so no overnight
overlay.

## 2. Unclear points and how they are handled

- **The class table's rows overlap** (zebu-lagoon). An executive director flying Nairobi-Johannesburg is described
  by "All flights within Africa: Economy" and by "Executive directors: Business"; the table is a list of "Maximum
  permitted class" rows and gives no order. Lines 150-151 tell staff in doubt over the class to consult the DCS. Flag;
  phrase "All flights within Africa"; held offers: the cheapest direct business or economy fare. Twins: sisal-harbour
  (executive director, intercontinental: business) and ibis-causeway (JG7 within Africa: economy).
- **"not expected to be more than 8 flights per year"** (umbra-kopje): the ninth business flight of the year, on a
  flight under 7 hours so no other row grants business. An expectation for budgeting, or a limit? Flag; twins
  sisal-harbour (the eighth: business; one-fact twin) and dik-dik-meadow (economy).
- **Approval required** (weaver-cove): a flexible ticket on moving plans with the DCS's approval and not yet the
  CFO's. Hold the flexible fare for the CFO only (SYNC_NOTES 4'). Twins ebony-strand (both approved: book the flexible
  fare) and guava-terrace (fixed plans, no approval, fallback in the request: book the non-flexible fare).
- **"readily available"** is avoided as a flag: a nonstop with seats that lands in time is available; a sold-out
  nonstop is not (fynbos-gate); a nonstop that lands after the traveller is due is of no use (quagga-mesa), and no
  case puts only late nonstops beside a timely connection (rules raise).
- **"direct"** is read as nonstop (the world has no through-flights with stops). Every keyed nonstop is also the
  answer on the "same flight number" reading.
- **Duration on connections**: no business case uses a connection whose flights straddle 7 hours (rules raise).
- **Premium economy for a traveller not entitled to business** is avoided (lines 107 and 143-144 could be read as
  allowing it on any flight over 4 hours): premium economy is requested only by a JG8 on a 480-minute
  intercontinental flight, and no ineligible case lists a premium economy offer.

Numeric twin pairs: 421/420 scheduled minutes (strict "more than 7 hours"), JG6/JG5 (inclusive "JG6 and above"),
nonstop economy seats available/sold out (the direct-flight principle). The director counts are a flag pair (8th
against 9th), since the flag side must be category `flag`.

## 3. Choices made without asking

1. **Currency GBP.** The policy prices in pounds (lines 157, 193, 200); FSD Africa is UK-funded. Fares are pence.
2. **Airports.** The shared world has three African airports (NBO, JNB, CAI) and their carriers (KQ, SA, MS). Every
   case uses them and European, Gulf and Turkish hubs. See the template change request below.
3. **A `work_starts` field** (when the traveller is due, local at the destination) gives every booking a stated
   deadline (lesson 4); the same field and request wording in each twin.
4. **The pillar head's trip approval** (lines 145-146) is on file for every staff and consultant trip, so their
   bookings accept `PILLAR_HEAD` beside `NONE` (4' and 4(b)); directors' and refused trips have none on file (`NONE`).
5. **Reason codes.** Handbook codes: `DIRECT_FLIGHT_PREFERRED` (the first name tried, `LOWEST_COST_DIRECT_FLIGHT`,
   failed the lint: it is a 4-word phrase of lines 119-121), `FLEXIBLE_FARE_APPROVED`, `ECONOMY_CLASS_LIMIT`.
   Economy bookings accept `LOWEST_FARE` and `DIRECT_FLIGHT_PREFERRED` (the direct-flight principle is the lowest-cost
   principle itself), plus `ECONOMY_CLASS_LIMIT` where a table row caps the traveller (baobab-crest, okapi-bridge).
   Declined business requests accept `UPGRADE_NOT_ELIGIBLE` and `ECONOMY_CLASS_LIMIT`, plus
   `LONG_FLIGHT_CONDITION_NOT_MET` when the long-flight row is the ground (420 minutes, JG5, within Africa); no
   `LOWEST_FARE` (lesson 12). Business by grade accepts `INTERNATIONAL_LONG_FLIGHT`, `LONG_FLIGHT_APPROVED` and
   `SENIOR_ROLE_ENTITLEMENT`; directors `SENIOR_ROLE_ENTITLEMENT` (plus `INTERNATIONAL_LONG_FLIGHT` on a flight over
   7 hours). The declined flexible fare accepts `REFUNDABLE_FARE_NOT_ALLOWED` only.
6. **Decoys** (grepped; none has a subject in the text): WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED,
   NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING,
   EXTENDED_TRAVEL_SAVINGS, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED,
   PRIVATE_AIRCRAFT_NOT_APPROVED, CANDIDATE_TRIP_NOT_COVERED, SAME_CLASS_AS_CUSTOMER. Approver decoys: SUPERVISOR,
   VICE_PRESIDENT, TRAVEL_MANAGER (LINE_MANAGER, DIRECTOR_HR and OFFICE_ADMINISTRATOR are roles the text names).
7. **Clauses.** `TRANSPORTATION` (section 3) is accepted beside `AIR_TRAVEL` (3.1) everywhere; `SAFETY_AND_SECURITY`
   beside `GROUP_TRAVEL`; `EXPENSES` beside `NON_REIMBURSABLE`; `OPERATING_PRINCIPLES` where lines 107-110 or 114-115
   are used.
8. **The group rule** ("Where possible") picks among offers but never refuses: lobelia-spur's other nonstop lands in
   time, so it is possible. Accepted reasons include `TRAVELLER_LIMIT_PER_FLIGHT`.
9. **The CEO's class exceptions** (lines 114-115, 151-152) get no booking scenario (no slot left in the mix); they
   appear only as an approver on the unclear holds.
10. **Background offers 0** on every search: a background nonstop could change the lowest cost direct flight.

## 4. Mix and overlays

5 easy, 6 boundary_twin, 4 multi_rule, 2 hidden_clause, 2 distractor, 2 refusal, 3 flag (12.5%). Decisions: 19 BOOK
(4 business, 1 premium economy, 14 economy), 2 REFUSE, 3 FLAG. Overlays: multi_leg 16, date_arithmetic 4 (month_end
1), personal_travel 2, multi_traveller 2, dearer_option 16, upgrade_not_taken 2, outside_air_section 3 (lobelia-spur
6.2, both refusals 5.6). Degenerate agents: always-flag passes 2 (umbra-kopje, zebu-lagoon), always-cheapest passes 3
(baobab-crest, fynbos-gate, marula-quay); `MAX_PASS_ALWAYS_LOWEST = 3`.

## 5. Independent blind read (non-flag scenarios)

Re-derived from the frozen text and the tool outputs only (the `get_trip` record and the `search_flights` listing,
dumped per scenario), not from rules.py, then compared with `expected`.

| Scenario | My reading from text + offers | Agrees |
|---|---|---|
| acacia-drift | JG6, 495-min NBO-CDG nonstops: business allowed (134-136) but traveller chooses economy (108-110); cheapest direct economy AF £560, not TK via IST £465 | yes |
| baobab-crest | within Africa, economy (128); three nonstops, cheapest KQ 08:30 £385 | yes |
| cassava-ledge | 420 min is not "more than 7 hours": economy; cheapest direct KQ £520, not EK via DXB £445 | yes |
| dik-dik-meadow | JG3 economy; nonstops have seats: cheapest direct EK £410, not QR via DOH £352 | yes |
| ebony-strand | meeting may move, DCS and CFO approved before booking (122-123): cheapest direct flexible KQ £890, not EK flexible via DXB £780 | yes |
| fynbos-gate | both nonstops sold out: no direct flight available; QR via DOH £352 lands 09:40 on the 7th | yes |
| guava-terrace | plans fixed, no approvals: no flexible ticket; traveller asks for what the policy allows: KQ non-flexible £540 | yes |
| hibiscus-ford | training, "regardless of duration" economy (137) beats the JG7 long-flight row; KQ economy £540 | yes |
| ibis-causeway | JNB-CAI is within Africa (128): economy despite 480 min; cheapest direct MS £460, not KQ via NBO £410 | yes |
| jacaranda-weir | JG6 is "JG6 and above", 505 min intercontinental: business; cheapest direct KQ £2,360 | yes |
| kudu-lantern | JG8, 480 min intercontinental: business allowed; premium economy chosen (107-110): KQ £1,125 | yes |
| lobelia-spur | NED, 2nd business flight of the year (≤3): business; three Board members on BA 19:30, so KQ 20:45 (lands 08:25, meeting 10:00) £3,120, not KL business via AMS £2,700 | yes |
| marula-quay | economy; no nonstop to EDI: cheapest itinerary KL via AMS £498, lands 08:00 on the 13th | yes |
| namib-orchard | remote worker to a staff retreat (138-140): economy; cheapest direct KQ £585, not KL via AMS £490 | yes |
| okapi-bridge | consultant: economy (129); lounge/legroom do not change the class; cheapest direct KQ £545 | yes |
| papyrus-knoll | JG5 below JG6: economy; cheapest direct KQ £545 | yes |
| quagga-mesa | KQ nonstop lands 09:20, after the 09:00 workshop; BA lands 07:10: cheapest timely direct BA £635, not KL via AMS £510 | yes |
| rooibos-haven | family holiday: non-business travel not reimbursed (242): refuse | yes |
| sisal-harbour | executive director, 7 earlier business flights this year, so the 8th: within "not more than 8"; cheapest direct business KQ £1,580 | yes |
| tamarind-ridge | 421 min is more than 7 hours, JG8, intercontinental: business; KQ £2,190 | yes |
| veld-pavilion | a staff member's husband: costs for personal guests not reimbursed (243): refuse | yes |

21 of 21 non-flag scenarios agree. The read caught no key error. Points I weighed: (a) whether CAI and DXB routes
are "intercontinental" (DXB is in Asia; JNB-CAI is within Africa; neither needs outside knowledge beyond the
airports' countries, which the tools show); (b) whether a careful reader would prefer a cheaper connection as
"best value" (lines 74-75) over the explicit direct-flight principle of lines 119-121: no, the specific rule
governs, and the declined connection is never in the accept set.

## 6. Hosted-cap estimate

Full-handbook prompt: 19,949 bytes; about 4,200 tokens at 1.33 a word, about 5,800 on the Thornton/NJC calibration
(0.2 a character plus 1,800). A 3-call run is about 19,000 input tokens before the final message (about 26,000 with
it): far under the 65,536 cap.

## 7. Template change requests

1. **More African airports and carriers in the shared `world.py`.** FSD Africa's work is across Africa; the world has
   only NBO, JNB and CAI (carriers KQ, SA, MS). Requested (no new hubs on existing carriers, so no existing route's
   offers move; run `tools/world_diff.py`): ADD Addis Ababa (ET, `ET` Ethiopian Airlines, hub ADD), LOS Lagos (NG),
   ACC Accra (GH), KGL Kigali (RW), DAR Dar es Salaam (TZ), EBB Entebbe (UG), CPT Cape Town (ZA), DKR Dakar (SN),
   LUN Lusaka (ZM), CMN Casablanca (MA, `AT` Royal Air Maroc). Worked around: every case flies NBO, JNB or CAI.
2. Observation, no change needed: the skeleton's `search-flights` task text says "one-way"; every FSD Africa case
   is one-way.

## 8. Acceptance outputs

```
$ uv run pytest -q
210 passed
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 9ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .            (stock checkout)
exit 0
$ nanoagent plugin pack . <scratch>/fsd-africa-flight-policy.tar.gz
packed . into .../fsd-africa-flight-policy.tar.gz (154189 bytes)
$ python ../_template/tools/stock_verify.py .   (stock checkout's Python)
acacia-drift         right=True score=1.00 identical=True wrong-decision-rejected=True
baobab-crest         right=True score=1.00 identical=True wrong-decision-rejected=True
cassava-ledge        right=True score=1.00 identical=True wrong-decision-rejected=True
dik-dik-meadow       right=True score=1.00 identical=True wrong-decision-rejected=True
ebony-strand         right=True score=1.00 identical=True wrong-decision-rejected=True
fynbos-gate          right=True score=1.00 identical=True wrong-decision-rejected=True
guava-terrace        right=True score=1.00 identical=True wrong-decision-rejected=True
hibiscus-ford        right=True score=1.00 identical=True wrong-decision-rejected=True
ibis-causeway        right=True score=1.00 identical=True wrong-decision-rejected=True
jacaranda-weir       right=True score=1.00 identical=True wrong-decision-rejected=True
kudu-lantern         right=True score=1.00 identical=True wrong-decision-rejected=True
lobelia-spur         right=True score=1.00 identical=True wrong-decision-rejected=True
marula-quay          right=True score=1.00 identical=True wrong-decision-rejected=True
namib-orchard        right=True score=1.00 identical=True wrong-decision-rejected=True
okapi-bridge         right=True score=1.00 identical=True wrong-decision-rejected=True
papyrus-knoll        right=True score=1.00 identical=True wrong-decision-rejected=True
quagga-mesa          right=True score=1.00 identical=True wrong-decision-rejected=True
rooibos-haven        right=True score=1.00 identical=True wrong-decision-rejected=True
sisal-harbour        right=True score=1.00 identical=True wrong-decision-rejected=True
tamarind-ridge       right=True score=1.00 identical=True wrong-decision-rejected=True
umbra-kopje          right=True score=1.00 identical=True wrong-decision-rejected=True
veld-pavilion        right=True score=1.00 identical=True wrong-decision-rejected=True
weaver-cove          right=True score=1.00 identical=True wrong-decision-rejected=True
zebu-lagoon          right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
