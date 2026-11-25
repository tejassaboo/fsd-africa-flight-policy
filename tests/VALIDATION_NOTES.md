# Validation notes: fsd-africa-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/fsd-africa-flight-policy@w3/`,
arm `full`, DeepSeek V4 Flash (Nebius fp8), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at
plugin head 5a6ac6b. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

19/24 valid (79.2%), mean field score 0.951, **easy 5/5**. By category: boundary 5/6, distractor 1/2, easy 5/5,
flag 2/3, hidden 1/2, multi 3/4, refusal 2/2. $0.00119 billed per run, 3.9 calls per run, 8,061 prompt tokens per
call, no run over the hosted 65,536 cap. Every run submitted.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| ebony-strand | multi_rule | Emirates refundable one-stop RMDR-L3LC (£780); key Kenya Airways refundable nonstop SYQ3-PKWE (£890) | model slip | It quoted the rule and set it aside: "Wait, but the policy also says flights should be based on the principle of the lowest cost direct flight ... Among refundable options, the lowest is Emirates at 78000 (1 stop)." Lines 119-121 ask for the lowest cost direct flight where direct flights are readily available; two refundable nonstops were listed (KQ £890, BA £935). The flexible-fare sign-offs (lines 122-123) were read right. The flag twin weaver-cove and guava-terrace passed. |
| lobelia-spur | hidden_clause | BA business UHYQ-2MZS (£2,950); key Kenya Airways business VVZT-BCJ3 (£3,120) | model slip | It never read section 6.2: "The traveller wants to join them on the BA evening flight in Business." Three Board colleagues are on that flight (request and `colleagues_booked`), and lines 277-279 allow no more than three ExCo or Board members on one flight "where possible". The KQ nonstop is open and lands 08:25 for a 10:00 meeting, so it is possible. |
| papyrus-knoll | boundary_twin | KLM economy nonstop PZJ8-DRQV (£570); key Kenya Airways economy nonstop FWJJ-LSW9 (£545) | model slip (misread fare list) | Cabin and grade right (JG5, lines 134-136). Then: "among direct flights, KLM is the only direct economy at £570." The same search lists KQ 1433 economy, nonstop, seats available, £545, landing 06:00 for a 10:00 forum. The twin jacaranda-weir (JG6, KQ business) passed. |
| quagga-mesa | distractor | KLM one-stop QTZE-XDQ2 (£510, lands 08:15); key BA nonstop LWZX-F2W7 (£635, lands 07:10) | model slip | It filtered on arrival time correctly (Emirates 13:10 and KQ 09:20 are late) and then took the cheapest timely offer: "the cheapest compliant option ... lowest-cost compliant direct-enough option." It never weighed lines 119-121; the BA nonstop is the one direct flight that is readily available and on time. The request's "cheapest way" is the distractor. The KLM connection would also leave 45 minutes to go "straight from the airport" to a 09:00 workshop. |
| zebu-lagoon | flag | BOOK KQ business, SENIOR_ROLE_ENTITLEMENT, NONE; key FLAG (KQ business or economy), UNCLEAR_POLICY_TEXT or APPROVAL_REQUIRED | model slip | It saw the conflict: "So there's a conflict. 'All flights within Africa Economy' vs 'Executive directors Business' ... which takes precedence?", then settled it ("I think the Executive director entitlement overrides"). It never read lines 150-152: where there is any doubt about the class, consult the DCS in advance. The held offer was accepted. The other flag umbra-kopje passed. |

## Fixes

None. All five failures are slips; nothing was loosened. Four of them are offer choices that ignore or misread the
"lowest cost direct flight" principle of lines 119-121 (ebony-strand, papyrus-knoll, quagga-mesa) or the group-travel
limit (lobelia-spur); in each the keyed offer was in the search the model received.

## Q2

The always-cheapest agent passes **3/24 (12.5%)**: baobab-crest, fynbos-gate, marula-quay (`MAX_PASS_ALWAYS_LOWEST = 3`,
unchanged).

## Re-score

Stored answers against this head: 19/24, easy 5/5 (no key changed).

## Re-run

Required: none (no record or request changed, and every easy case passed). Optional (variance only): papyrus-knoll
(fare-list misread), zebu-lagoon.

## Checks

`uv run pytest -q` (210 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, `tools/stock_verify.py` (24
scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
