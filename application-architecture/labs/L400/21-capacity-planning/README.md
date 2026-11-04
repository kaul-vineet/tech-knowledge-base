# Lab 21 – Cost and capacity planning: load model, Little's law, benchmark, headroom, cost per request

Library Loans grows from one library to 400. `capacity.py` builds a **load model** from the lesson 15 request log (route mix, service times), scales it by the stated growth (400 libraries, daily **peak** = 3 x average), applies **Little's law** (L = λW), and **benchmarks one instance**: a seeded queue simulation (4 workers, FCFS, Poisson arrivals) fed with the logged service times; the highest arrival rate whose **p99 ≤ 300 ms** (the lesson 15 SLO) is the instance's capacity. Three options are compared: confirmation email **inside** POST /loans, **async** via the outbox, async **+ an LRU cache** for GET /books (hit ratio measured on a seeded Zipf-like popularity). The plan uses **80 % headroom** and **N+1**; **cost per million requests** uses a hypothetical price (0.10 USD per instance-hour, not a vendor quote). A **local model** may draft the capacity memo; code checks every number. The shipped `instances_needed()` sizes on the average at 100 % utilization.

## Files
| File | Purpose |
|---|---|
| `capacity.py` | Load model, Little's law, simulation, benchmark, options, `instances_needed` (**seeded weakness**) (lesson code) |
| `l300_log.py` | Reuses `labs/L300/15-slo-error-budgets/traffic.py` (healthy days, no incident) |
| `app.py` | The plan: model, Little's law, one JSON line per option (`out/capacity.jsonl`) |
| `failure_lab.py` | Average sizing vs peak + headroom + N+1 |
| `fitness_capacity.py` | Fitness function: p99 with one instance down ≤ SLO, peak ≤ 80 % of capacity |
| `agent_assist.py` | Local model drafts the memo; `check_memo()` verifies each number |
| `adr/0005-capacity-plan.md` | Decision record |
| `test_capacity.py` / `test_build_task.py` / `solution/capacity.py` | Tests / build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/21-capacity-planning
python app.py                    # shipped sizing (average, 100 %)
python failure_lab.py
python app.py --solution
python fitness_capacity.py --solution
python agent_assist.py           # fake model; --real for Ollama
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
The simulation is seeded (`random.Random`), so every number repeats exactly.
```
$ python app.py
load model : {'avg_rps': 40.0, 'peak_rps': 120.0, 'mix': {'GET /books': 0.449, 'GET /loans': 0.351, 'POST /loans': 0.2}, 'mean_service_ms': 45.2}
Little's law: 120.0 req/s x 45.2 ms = 5.4 requests in flight at peak; emails 3.6 in flight -> 5 sender slots
{"option": "sync email", "mean_service_ms": 75.1, "capacity_rps": 35, "instances": 1, "p99_at_peak_ms": 207855.2, "p99_one_down_ms": 207855.2, "cost_per_million_usd": 0.69}
{"option": "async email", "mean_service_ms": 45.2, "capacity_rps": 75, "instances": 1, "p99_at_peak_ms": 58210.3, "p99_one_down_ms": 58210.3, "cost_per_million_usd": 0.69}
{"option": "async email + cache", "mean_service_ms": 32.6, "capacity_rps": 105, "instances": 1, "p99_at_peak_ms": 999.8, "p99_one_down_ms": 999.8, "cost_per_million_usd": 0.69}
$ python app.py --solution
load model : {'avg_rps': 40.0, 'peak_rps': 120.0, 'mix': {'GET /books': 0.449, 'GET /loans': 0.351, 'POST /loans': 0.2}, 'mean_service_ms': 45.2}
Little's law: 120.0 req/s x 45.2 ms = 5.4 requests in flight at peak; emails 3.6 in flight -> 5 sender slots
{"option": "sync email", "mean_service_ms": 75.1, "capacity_rps": 35, "instances": 6, "p99_at_peak_ms": 230.8, "p99_one_down_ms": 239.1, "cost_per_million_usd": 4.17}
{"option": "async email", "mean_service_ms": 45.2, "capacity_rps": 75, "instances": 3, "p99_at_peak_ms": 102.4, "p99_one_down_ms": 130.4, "cost_per_million_usd": 2.08}
{"option": "async email + cache", "mean_service_ms": 32.6, "capacity_rps": 105, "instances": 3, "p99_at_peak_ms": 94.7, "p99_one_down_ms": 100.5, "cost_per_million_usd": 2.08}
$ python fitness_capacity.py --solution
{"gate": "capacity-n-plus-1", "ok": true, "budget": "p99 <= 300 ms with one down, peak <= 80% of capacity with one down", "value": {"instances": 3, "p99_one_down_ms": 130.4, "peak_share_one_down": 0.8}}
exit 0
```
Raw c / S = 4 / 45.2 ms = 88.5 req/s is the instance at 100 % busy; the SLO-safe capacity is 75 req/s (p99 245.2 ms; at 80 req/s it is 342.3 ms).

## failureLab: sized on the average, broken at the peak
```
$ python failure_lab.py
demand: avg 40.0 req/s, peak 120.0 req/s; one instance meets the SLO up to 75 req/s; raw c/S = 88.5 req/s
base    : 1 instance(s) -> at peak 120 req/s each, utilization 1.35, p99 58210.3 ms; one instance down: p99 58210.3 ms (SLO 300 ms)
solution: 3 instance(s) -> at peak 40 req/s each, utilization 0.45, p99 102.4 ms; one instance down: p99 130.4 ms (SLO 300 ms)
$ python fitness_capacity.py
{"gate": "capacity-n-plus-1", "ok": false, "budget": "p99 <= 300 ms with one down, peak <= 80% of capacity with one down", "value": {"instances": 1, "p99_one_down_ms": 58210.3, "peak_share_one_down": 1.6}}
exit 1
```

## Agent assist (fake model server, observed 2026-10-28)
Code computes the plan and the instance count; the model only words the memo. The fake server's first draft is wrong on purpose (documented in `labs/_shared/local_agent/fake_model_server.py`, rule `[[CAPACITY-MEMO]]`): it plans on the average.
```
$ python agent_assist.py
model: fake model server (deterministic stand-in, not a language model)
facts (computed by code): peak_rps=120.0, avg_rps=40.0, mean_service_ms=45.2, in_flight_at_peak=5.4, capacity_rps=75, instances=3, p99_at_peak_ms=102.4, p99_one_down_ms=130.4, cost_per_million_usd=2.08, email_senders=5, rejected_option=sync email, rejected_instances=6
attempt 1: REJECTED
  - number 1.8 is not in the facts
  - peak_rps is 120.0, the memo says 40.0
  - in_flight_at_peak is 5.4, the memo says 1.8
  - the plan is 3 instances, the memo says 1
  - missing peak_rps 120.0
  - missing instances 3
  - missing p99_one_down_ms 130.4
attempt 2: OK
accepted memo (a human reviews and signs it):
  Capacity memo: plan for a peak of 120.0 req/s (average 40.0 req/s). With a mean service time of 45.2 ms, Little's law gives 5.4 requests in flight at peak. One instance meets the p99 SLO up to a capacity of 75 req/s, so we recommend 3 instances (N+1): p99 102.4 ms at peak and 130.4 ms with one instance down, at a cost of 2.08 USD per million requests. Confirmation emails move to the outbox with 5 sender slots; the sync email option would need 6 instances.
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_six_instances_if_email_stays_synchronous (test_build_task.SizingTest.test_six_instances_if_email_stays_synchronous) ... ok
test_slo_holds_with_one_instance_down (test_build_task.SizingTest.test_slo_holds_with_one_instance_down) ... ok
test_three_instances_for_the_async_option (test_build_task.SizingTest.test_three_instances_for_the_async_option) ... ok
test_fake_model_loop (test_capacity.AgentMemoTest.test_fake_model_loop) ... ok
test_wrong_peak_is_rejected (test_capacity.AgentMemoTest.test_wrong_peak_is_rejected) ... ok
test_benchmark_capacity_per_instance (test_capacity.ModelTest.test_benchmark_capacity_per_instance) ... ok
test_cache_hit_ratio_is_measured (test_capacity.ModelTest.test_cache_hit_ratio_is_measured) ... ok
test_littles_law (test_capacity.ModelTest.test_littles_law) ... ok
test_load_model_from_the_l300_log (test_capacity.ModelTest.test_load_model_from_the_l300_log) ... ok
test_symptom_average_sizing_collapses_at_peak (test_capacity.ModelTest.test_symptom_average_sizing_collapses_at_peak) ... ok

----------------------------------------------------------------------
Ran 10 tests in 15.812s

OK
```
About 10–16 s: each test file re-reads the 3-day log and runs the simulations.

## Build task (the hardening change)
Rewrite `instances_needed(model, capacity_rps)`: `ceil(peak_rps / (capacity_rps x HEADROOM)) + 1`.
- Solution: `solution/capacity.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged capacity.py
FAIL: test_six_instances_if_email_stays_synchronous
FAIL: test_slo_holds_with_one_instance_down
FAIL: test_three_instances_for_the_async_option
FAILED (failures=3)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] 800 libraries (peak 240.0 req/s), async email: 5 instances, 1.74 USD per million requests
[1] 800 libraries (peak 240.0 req/s), async email + cache: 4 instances, 1.39 USD per million requests
[2] 2 instances (no spare), one down at peak: 120 req/s on the survivor, utilization 1.35, p99 58210.3 ms
```

## Confirm with a real load test (pending a manual run)
The simulation is a model. Confirm the per-instance capacity against the real service with Grafana k6 (`brew install k6` / `winget install k6 --source winget`) at a constant arrival rate, for example against lesson 16's `http_api.py`, and compare the rate at which p(99) crosses 300 ms.

## Mac mini and Windows
Same commands inside the venv; no network, no packages. The agent assist with `--real` needs Ollama on either machine (`LOCAL_MODEL_URL`, `LOCAL_MODEL`).

## Troubleshooting
| Symptom | Action |
|---|---|
| Capacity changes after you edit `traffic.py` in lesson 15 | Expected: the plan is derived from that log; re-run the fitness gate. |
| p99 explodes between two neighbouring rates | That is the knee of the queue (utilization near 1); plan below it. |
| The memo is rejected on a real model | Read the problems: a number not in the facts, or a labelled number that differs. Write it by hand if the retry fails. |
