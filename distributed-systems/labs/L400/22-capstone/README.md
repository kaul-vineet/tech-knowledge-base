# 22 · Capstone: an order pipeline that survives chaos and proves it

One integrated system built from the earlier labs, imported rather than copied (`reuse.py`): a **gateway** with a bounded queue that sheds with 503 + Retry-After (L300 #16) and idempotency keys (L100 #5) -> workers -> the **orchestrated saga** with compensation and `recover()` (L300 #14) -> every state change and its event in one **outbox** transaction -> relay -> at-least-once **bus** -> **idempotent consumers** (L200 #8) for email and revenue. Every order carries a **W3C trace context** (L300 #15) through the outbox to the consumers. The gateway's queue bound is **replicated config committed through Raft** (L300 #12). A **chaos campaign** (lesson 20's bounded cohorts) runs every fault alone and all at once on 3 seeds; **checks.py** decides pass/fail; `run_capstone.py` prints the **scorecard** as JSON lines; an optional local model **explains** the results and code checks its claims.

Architecture: `architecture.mmd` (Mermaid). Decisions: `adr/ADR-022-1..4`. Files: `pipeline.py` (main) · `outbox.py` · `checks.py` · `chaos_campaign.py` · `run_capstone.py` · `agent_assist.py` · `reuse.py` · `try_it.py` · `test_m1_outbox.py` ... `test_m6_chaos.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python pipeline.py
python run_capstone.py                    # exit code 0 only if every criterion passes
python run_capstone.py --explain --fake   # + the agent explanation against the bundled fake model server
```

## Expected output (real run, Python 3.12.15, Linux - identical on every run; seeded)
```
ticks 33, sagas {'completed': 60}, events published 180, delivered 360, spans 660, config {'version': 2, 'max_queue': 12}, audit: OK
```
`run_capstone.py --explain --fake` (27 experiment lines first; the last three shown, then the scorecard and the agent check):
```
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 108, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 48}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 118, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 43}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 104, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 43}
{"criterion": "money invariant (audit)", "measure": "passes in 27/27 runs (baseline: 0 violations)", "pass": true}
{"criterion": "no lost orders", "measure": "passes in 27/27 runs (baseline: 60/60 final)", "pass": true}
{"criterion": "one order and one charge per key", "measure": "passes in 27/27 runs (baseline: max created 1, max charges 1)", "pass": true}
{"criterion": "exactly-once effects", "measure": "passes in 27/27 runs (baseline: max emails per event 1, revenue mismatches 0)", "pass": true}
{"criterion": "outbox delivered", "measure": "passes in 27/27 runs (baseline: 180 events, 180 publishes)", "pass": true}
{"criterion": "one trace per order", "measure": "passes in 27/27 runs (baseline: split 0, orphans 0, bad headers 0)", "pass": true}
{"criterion": "bounded queue", "measure": "passes in 27/27 runs (baseline: over bound 0, p99 wait 2 ticks)", "pass": true}
{"criterion": "config via Raft", "measure": "passes in 27/27 runs (baseline: safety violations 0, committed versions [2])", "pass": true}
{"criterion": "chaos hypotheses held", "measure": "27/27 experiments", "pass": true}
{"criterion": "blast radius of order faults", "measure": "max 10.0% (limit 10%)", "pass": true}
{"scorecard": "10/10", "pass": true}
agent check baseline            agent: ('yes', 0) code: ('yes', 0) OK
agent check shipping-outage     agent: ('yes', 0) code: ('yes', 0) OK
agent check crash-after-charge  agent: ('yes', 0) code: ('yes', 0) OK
agent check relay-crash         agent: ('no', 0) code: ('yes', 0) WRONG
agent check bus-duplicates      agent: ('yes', 0) code: ('yes', 0) OK
agent check lost-acks           agent: ('yes', 0) code: ('yes', 0) OK
agent check burst               agent: ('yes', 3) code: ('yes', 0) WRONG
agent check raft-leader-crash   agent: ('yes', 0) code: ('yes', 0) OK
agent check everything          agent: ('yes', 0) code: ('yes', 0) OK
agent summary (number OK): idempotent consumers absorbed 586 duplicate deliveries; the relay crash is the weak spot.
agent verdict IGNORED (code decides): PASS - safe to release
```
The agent got two claims wrong on purpose (the fake model reports relay-crash as not held and invents 3 harmed orders for burst) and volunteered a release verdict; code flags the claims and ignores the verdict. With a real model (`LOCAL_MODEL_URL`, Ollama `qwen2.5:1.5b`) the explanation differs, the checks do not.

## Milestones and tests
```bash
python -m unittest -v     # Ran 15 tests ... OK
```
| # | Milestone | Test |
|---|---|---|
| 1 | Outbox + at-least-once bus + idempotent consumers | `test_m1_outbox.py` |
| 2 | Saga with compensation and recovery on the outbox | `test_m2_saga.py` |
| 3 | One W3C trace per order, through events and consumers | `test_m3_tracing.py` |
| 4 | Bounded admission, 503 + Retry-After, idempotent retries | `test_m4_backpressure.py` |
| 5 | Queue bound as Raft-committed, versioned config | `test_m5_config.py` |
| 6 | Chaos campaign, scorecard, checked agent explanation | `test_m6_chaos.py` |

## What the checks caught while building
The `raft-leader-crash` experiment first failed "config via Raft" (`committed versions [1]`): the run ended at tick 33, before the operator's re-proposed change committed on the new leader. Fix (ADR-022-3): the run is not done until the wanted config version is committed (that run now ends at tick 48).

## Try it (real run - `python try_it.py`)
```
tryIt 1: consumers without dedupe, bus-duplicates: failed checks {'exactly-once effects': 'max emails per event 2, revenue mismatches 14'}
tryIt 2: gateway without idempotency keys, lost-acks: failed checks {'one order and one charge per key': 'max created 2, max charges 1', 'exactly-once effects': 'max emails per event 2, revenue mismatches 0'}
```
Switch one mechanism off and the scorecard names what broke: without consumer dedupe, duplicate deliveries send second emails and book revenue twice (14 mismatches); without idempotency keys at the gateway, lost acknowledgements create second orders.

## Platform notes
Pure computation on simulated ticks; the agent assist uses a local HTTP fake server on 127.0.0.1 (tests) or your local model. Seeded: identical output on macOS, Windows and Linux (CI matrix pending). Never send secrets or customer data to a model; this one sees only experiment results.
