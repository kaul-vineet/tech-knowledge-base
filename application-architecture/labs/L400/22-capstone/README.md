# Capstone 22 – Library Loans, production-ready

One integrated system that reuses the earlier labs instead of copying them (`reuse.py` imports them by path): the **strangler facade** and parallel run (lesson 17), the **tenant guard** (18), the **policy engine** and decision log (19), the **outbox**, relay and idempotent consumers (9), **consumer-driven contracts** (14), **SLIs and burn-rate alerts** (15) and the **capacity gate** (21). `run_capstone.py` runs it end to end on seeded traffic (5 libraries, 600 requests) and prints a **scorecard**: one JSON line per rubric criterion, then a summary with the verdict. **Code decides GO / NO-GO**; a local model may only explain the scorecard, and code checks its note. Four **seeded faults** each turn the verdict NO-GO.

## Files
| File | Purpose |
|---|---|
| `run_capstone.py` | Scorecard runner: criteria → JSON lines → verdict and exit code (capstone code) |
| `scorecard.py` | Builds the system (optionally with one fault), seeded workload, outbox relay, gates |
| `loans_service.py` | The service core: PEP → tenant-bound SQL → outbox; request log |
| `http_api.py` / `serve.py` | Member-portal HTTP adapter (127.0.0.1); `serve.py` serves it for Bruno/curl |
| `consumer.py` + `contracts/` | Consumer side of the member-portal contract (lesson-14 format) |
| `reuse.py` | Loads lessons 9, 14, 15, 17, 18, 19 and 21 by path |
| `agent_assist.py` | Local model explains the scorecard; `check_note()` rejects a wrong verdict or numbers |
| `architecture.mmd` | Architecture diagram (Mermaid flowchart) |
| `adr/0006`–`0009` + `adr/README.md` | Capstone ADRs and the topic's ADR log (0001–0009) |
| `test_milestones.py` / `test_faults.py` / `test_agent_assist.py` | One test class per milestone / every fault caught / note checker |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/22-capstone
python run_capstone.py                              # exit 0 = GO
python run_capstone.py --fault cross-tenant-policy  # exit 1 = NO-GO (also: fines-rounding, unscoped-query, duplicate-delivery)
python agent_assist.py --fault cross-tenant-policy  # fake model; --real for Ollama
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
Every value is seeded except the request `ms`, which only has to stay under 300 ms (0.1–1 ms here).
```
$ python run_capstone.py
{"milestone": "M1 strangle", "criterion": "fines parallel run", "measure": "mismatch rate over 2,000 shadow requests", "value": 0.0, "threshold": "<= 0.001", "pass": true}
{"milestone": "M1 strangle", "criterion": "fines cut over", "measure": "facade mode after the run", "value": "service", "threshold": "service", "pass": true}
{"milestone": "M1 strangle", "criterion": "no new legacy callers", "measure": "capstone files importing legacy_monolith", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M2 tenancy", "criterion": "tenant guard", "measure": "statements without the current tenant id", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M2 tenancy", "criterion": "tenant-scoped SQL", "measure": "loans queries without WHERE tenant_id", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M2 tenancy", "criterion": "cross-library reads", "measure": "rows of another library returned", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M3 policy", "criterion": "policy requirement cases", "measure": "cases decided as specified", "value": "14/14", "threshold": "14/14", "pass": true}
{"milestone": "M3 policy", "criterion": "cross-library probes denied", "measure": "probes allowed across libraries", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M3 policy", "criterion": "every entry point enforces policy", "measure": "public methods without _authorize", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M3 policy", "criterion": "decision log privacy", "measure": "decisions logged 615, with email", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M4 events", "criterion": "outbox completeness", "measure": "committed changes vs outbox rows", "value": "469/469", "threshold": "equal", "pass": true}
{"milestone": "M4 events", "criterion": "relay published", "measure": "unpublished outbox rows", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M4 events", "criterion": "idempotent consumers", "measure": "projection rows wrong after redelivering every event", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "availability SLI", "measure": "good / valid over 615 requests", "value": 1.0, "threshold": ">= 0.999", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "latency SLI", "measure": "good / valid over 615 requests", "value": 1.0, "threshold": ">= 0.99", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "burn-rate alerts", "measure": "alerts firing at the end of the run", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "consumer contract", "measure": "member-portal contract problems", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "capacity N+1", "measure": "p99 ms with one instance down", "value": 130.4, "threshold": "<= 300", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "ADR log", "measure": "ADRs in Nygard format of 9", "value": [], "threshold": "[]", "pass": true}
{"summary": true, "fault": null, "passed": 19, "total": 19, "failed": [], "verdict": "GO"}
exit 0
$ python run_capstone.py --fault unscoped-query
{"summary": true, "fault": "unscoped-query", "passed": 16, "total": 19, "failed": ["tenant guard", "tenant-scoped SQL", "cross-library reads"], "verdict": "NO-GO"}
exit 1
```
`out/requests.jsonl` holds one line per request (`{"ts": "2026-10-28T09:00:02Z", "route": "POST /loans", "status": 200, "ms": 0.34}`); `out/decisions.jsonl` holds 615 decisions, each with `"erased": ["/input/subject/email"]`.

## Seeded faults (observed 2026-10-28)
| `--fault` | What is injected | Criteria that fail |
|---|---|---|
| `fines-rounding` | lesson 17's unfixed fines service | fines parallel run (0.054), fines cut over (stays `shadow`) |
| `cross-tenant-policy` | lesson 19's unfixed policy | cross-library reads (5), policy requirement cases (13/14), cross-library probes denied (5) |
| `unscoped-query` | `MEMBER_LOANS` without `tenant_id` | tenant guard (135 statements), tenant-scoped SQL, cross-library reads (20) |
| `duplicate-delivery` | a consumer that ignores `eventId` | idempotent consumers (20 projection rows wrong) |

## Agent assist (fake model server, observed 2026-10-28)
```
$ python agent_assist.py --fault cross-tenant-policy
scorecard (computed by code): passed=16, total=19, failed=cross-library reads, policy requirement cases, cross-library probes denied, verdict=NO-GO
attempt 1: REJECTED
  - verdict is NO-GO, the note says GO
  - failed criterion not named: cross-library reads
  - failed criterion not named: policy requirement cases
  - failed criterion not named: cross-library probes denied
attempt 2: OK
accepted note (a human posts it):
  Release summary: NO-GO. 16 of 19 criteria passed; failed: cross-library reads, policy requirement cases, cross-library probes denied. Fix these before the release.
```
The fake server's first note says GO on purpose (`[[GO-NO-GO]]` rule in `labs/_shared/local_agent/fake_model_server.py`). The verdict stays the code's; nothing is posted.

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_fake_model_loop_ends_honest (test_agent_assist.CheckNoteTest.test_fake_model_loop_ends_honest) ... ok
test_invented_number_is_rejected (test_agent_assist.CheckNoteTest.test_invented_number_is_rejected) ... ok
test_optimistic_go_is_rejected (test_agent_assist.CheckNoteTest.test_optimistic_go_is_rejected) ... ok
test_each_fault_is_caught (test_faults.FaultTest.test_each_fault_is_caught) ... ok
test_cut_over_after_a_clean_parallel_run (test_milestones.M1StrangleTest.test_cut_over_after_a_clean_parallel_run) ... ok
test_guard_static_gate_and_probes (test_milestones.M2TenancyTest.test_guard_static_gate_and_probes) ... ok
test_member_cannot_read_another_members_loans (test_milestones.M3PolicyTest.test_member_cannot_read_another_members_loans) ... ok
test_policy_cases_pep_and_private_decision_log (test_milestones.M3PolicyTest.test_policy_cases_pep_and_private_decision_log) ... ok
test_outbox_relay_and_idempotent_consumers (test_milestones.M4EventsTest.test_outbox_relay_and_idempotent_consumers) ... ok
test_consumer_side_writes_the_contract (test_milestones.M5CiTest.test_consumer_side_writes_the_contract) ... ok
test_scorecard_is_go (test_milestones.M5CiTest.test_scorecard_is_go) ... ok
test_slo_contract_capacity_and_adrs (test_milestones.M5CiTest.test_slo_contract_capacity_and_adrs) ... ok

----------------------------------------------------------------------
Ran 12 tests in 32.407s

OK
```
Wall time 32–170 s on this sandbox's network-mounted disk (about 2 s of CPU): the module imports and file writes dominate.

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] librarian rule without the library check -> NO-GO, 16/19, failed ['cross-library reads', 'policy requirement cases', 'cross-library probes denied']
[2] cut-over budget 6 %, buggy fines service -> GO, mismatch rate 0.054, facade service
```
A gate is only as good as its threshold: at a 6 % budget the rounding bug ships.

## Explore by hand (pending a manual run)
`python serve.py` serves `http://127.0.0.1:8022/tenants/lib00/members/m1/loans`. With the header `X-Subject: {"id": "m1", "tenant": "lib00", "roles": ["member"]}` the answer is `200 {"memberId": "m1", "loans": [{"loanId": 1, "bookId": "b1"}]}`; as a librarian of lib01 it is `403 {"error": "view denied for s9 in lib00"}` (both observed with a scripted client here). `X-Subject` is a learning-only stand-in for the verified token of lesson 10.

## Mac mini and Windows
Same commands inside the venv; everything is stdlib and in memory, servers bind 127.0.0.1. Stop `serve.py` with Ctrl+C on both.

## Troubleshooting
| Symptom | Action |
|---|---|
| `ModuleNotFoundError` for a lesson module | Run from this folder; `reuse.py` finds the other labs relative to it (keep the `labs/` layout). |
| `consumer contract` fails with 403 | The provider state also sets the caller; check `POST /_contract/state` names the state in the contract. |
| A fault run says GO | A gate or threshold was weakened (see try-it 2); `test_faults.py` pins the expected failures. |
