# FSD Africa Travel Policy Flight Booking

**Source of the handbook:** https://fsdafrica.org/wp-content/uploads/2025/07/24-04-10-Travel-Policy.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with FSD Africa.** The handbook is FSD Africa's *Travel & Expense Policy*, version 4.0
(CORP-POL-006, approved March 2024), marked OFFICIAL (the UK's unrestricted marking) and distributed "Extenal"
by its own document control, bundled verbatim for research. The public URL was not recorded when the PDF was
collected (`pilot_work/originals/MANIFEST.md`): confirm it before publishing this plugin.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the organisation's real
travel policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 3,143 words, 310 lines, 19,949 bytes, sha256 `ba74787a...a366c8`,
equal to `pilot_work/originals/fsd-africa/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no
rule. The PDF extraction left about 80 stray mid-word spaces ("w ith", "a pproved"); they are kept, and every
`must_keep` quote copies them. Under stock NanoAgent the agent does not see the text: the plugin then runs as the
`off` baseline. The `harness.policy` switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch
`policy-switch`) adds it to the system prompt: `harness.policy: full` adds all of it, and the selection methods add
parts of it. These plugins are meant to run with `query: instructions+input`, so a selector sees the traveller's
request.

**Size.** At 1.33 tokens a word the policy alone is about 4,200 tokens; calibrated on the paid Thornton and NJC runs
(about 0.2 tokens a character plus 1,800) the first `full` call is about 5,800 input tokens. A run makes 3 calls
(`get_trip`, `search_flights`, `submit`) of about 5,800, 6,300 and 7,000: about 19,000 input tokens per run, far
under the hosted cap of 65,536.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date (every case buys one one-way ticket),
  then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's shared list plus
  three codes of this policy (`DIRECT_FLIGHT_PREFERRED`, `FLEXIBLE_FARE_APPROVED`, `ECONOMY_CLASS_LIMIT`) and
  thirteen decoy codes from other handbooks' rules. Fares are in pence (`currency: GBP`).
- **Success:** every field is one the answer key accepts; the cabin is graded as the chosen offer's own. Score =
  fields right / 6.
- **Reasons on a declined request.** When the booking is not what the traveller asked for, the reason must name
  the policy's ground, not `LOWEST_FARE`: business declined accepts `UPGRADE_NOT_ELIGIBLE`,
  `ECONOMY_CLASS_LIMIT` or `TRAVELER_PAYS_UPGRADE` (and `LONG_FLIGHT_CONDITION_NOT_MET` where the long-flight row is
  not met); the flexible fare declined accepts `REFUNDABLE_FARE_NOT_ALLOWED`.
- **No hidden facts:** no scenario has `answer_key_inputs`.

| Scenario | Category | Expected decision (offer; cabin) | Frozen lines |
|---|---|---|---|
| `acacia-drift` | easy | BOOK (airfrance-economy; ECONOMY): JG6 chooses economy | 107-110, 118, 119-121, 134-136 |
| `baobab-crest` | easy | BOOK (morning-economy; ECONOMY) | 118, 119-121, 128 |
| `kudu-lantern` | easy | BOOK (kenya-premium; PREMIUM_ECONOMY): JG8 chooses premium economy | 107-110, 119-121, 134-136 |
| `marula-quay` | easy | BOOK (amsterdam-economy; ECONOMY): no direct flight | 118, 119-121 |
| `sisal-harbour` | easy | BOOK (kenya-business; BUSINESS): executive director's 8th flight | 119-121, 124-127, 132-133 |
| `tamarind-ridge` | boundary_twin | BOOK (kenya-business; BUSINESS), 421 minutes | 119-121, 134-136 |
| `cassava-ledge` | boundary_twin | BOOK (kenya-economy; ECONOMY), 420 minutes | 118, 119-121, 134-136 |
| `jacaranda-weir` | boundary_twin | BOOK (kenya-business; BUSINESS), JG6 | 119-121, 134-136 |
| `papyrus-knoll` | boundary_twin | BOOK (kenya-economy; ECONOMY), JG5 | 118, 119-121, 134-136 |
| `dik-dik-meadow` | boundary_twin | BOOK (emirates-economy; ECONOMY): nonstops have seats | 118, 119-121 |
| `fynbos-gate` | boundary_twin | BOOK (doha-economy; ECONOMY): nonstops sold out | 118, 119-121 |
| `ebony-strand` | multi_rule | BOOK (kenya-flex; ECONOMY): flexible fare, DCS and CFO approved | 118, 119-121, 122-123 |
| `guava-terrace` | multi_rule | BOOK (kenya-economy; ECONOMY): flexible fare not justified | 118, 119-121, 122-123 |
| `hibiscus-ford` | multi_rule | BOOK (kenya-economy; ECONOMY): training trip | 119-121, 134-136, 137 |
| `ibis-causeway` | multi_rule | BOOK (egyptair-economy; ECONOMY): 8 hours within Africa | 119-121, 128, 134-136 |
| `lobelia-spur` | hidden_clause | BOOK (kenya-business; BUSINESS): three Board members already on the BA flight | 119-121, 130-131, 277-279 |
| `namib-orchard` | hidden_clause | BOOK (kenya-economy; ECONOMY): remote worker to a staff event | 119-121, 134-136, 138-140 |
| `okapi-bridge` | distractor | BOOK (kenya-economy; ECONOMY): consultant asks for lounge and legroom | 118, 119-121, 129 |
| `quagga-mesa` | distractor | BOOK (british-economy; ECONOMY): cheaper nonstop lands after the workshop | 118, 119-121 |
| `rooibos-haven` | refusal | REFUSE: family holiday | 71-72, 242 |
| `veld-pavilion` | refusal | REFUSE: a staff member's husband | 242, 243 |
| `weaver-cove` | flag | FLAG_FOR_APPROVAL (kenya-flex; ECONOMY), APPROVAL_REQUIRED, CHIEF_FINANCIAL_OFFICER | 119-121, 122-123 |
| `umbra-kopje` | flag | FLAG_FOR_APPROVAL (kenya-business or emirates-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 114-115, 132-133, 150-152 |
| `zebu-lagoon` | flag | FLAG_FOR_APPROVAL (kenya-business or kenya-economy), UNCLEAR_POLICY_TEXT (or APPROVAL_REQUIRED) | 124-128, 132-133, 150-152 |

Every accepted reason, approver and section per case is in the scenario files and `tests/BUILD_NOTES.md`.

**Duration (`rules.over`).** Lines 134-136 give business on "Intercontinental flights of more than 7 hours'
duration" for JG6 and above (strict, 420 minutes); lines 143-144 allow lounges and extra-legroom economy seats "For
flights of more than 4 hours' duration" (strict, 240 minutes). A nonstop is over the limit when its scheduled
minutes exceed it; a connection whose every flight is over is over; one whose whole elapsed journey is within is
not; anything else is unclear (`None`), and no scenario uses it.

**The lowest cost direct flight.** Lines 119-121 book "the lowest cost direct flight ... (where direct flights are
readily available)": the cheapest nonstop with seats that lands by the time the trip record says the traveller is
due (`work_starts`), else the cheapest itinerary. Most cases list a cheaper connection beside the nonstops.

**Approvers.** Staff and consultant trips carry the pillar head's trip approval (lines 145-146), so their bookings
accept `NONE` and `PILLAR_HEAD` (SYNC_NOTES 4'); `ebony-strand` also accepts the DCS and CFO, whose flexible-fare
approvals it relies on. `weaver-cove` waits on the CFO only. The two unclear holds accept `NOT_NAMED`, the DCS
(lines 150-151: in doubt over the class, consult the DCS) and the CEO (lines 151-152: class exceptions).

Degenerate agents (`tests/test_verifier.py`): always holding the right offer as unclear passes 2 cases (the two
unclear flags); always booking the cheapest seat with `LOWEST_FARE`, `NONE` and the right section passes 3.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, role, job grade, route, date, when they are due, purpose, requested cabin and fare type, earlier business flights, colleagues booked, sign-offs | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the scenario's pinned offers; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-fsd-africa-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, reason codes
  and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design choices, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/fsd-africa-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
