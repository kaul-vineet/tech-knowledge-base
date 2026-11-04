# Lab 15 – SLOs and error budgets: burn-rate alerts from request logs

`traffic.py` writes three days of seeded Library Loans request logs (25,920 JSON lines, one request every 10 s). `slo.py` turns them into **SLIs** (good events / valid events), compares them with **SLOs**, computes the **error budget** and **burn rates**, and evaluates the multiwindow, multi-burn-rate alerts from the Google SRE Workbook (page 1h/5m ≥ 14.4, page 6h/30m ≥ 6, ticket 3d/6h ≥ 1). The base latency check is an **average**. From 10:30 UTC, one POST /loans in five takes about 3 s, and the average hides it.

## Files
| File | Purpose |
|---|---|
| `slo.py` | SLIs, windows, burn rate, budget consumed, alerts, latency report (lesson code) |
| `traffic.py` | Seeded request log; `incident=True` adds the slow tail from 10:30 UTC |
| `app.py` | Writes `out/requests.jsonl` and prints the SLO report at 12:00 UTC |
| `failure_lab.py` | Mean check vs latency SLI, base vs solution |
| `agent_assist.py` | Local model drafts the incident summary; code checks every number |
| `test_slo.py` / `test_agent_assist.py` | Burn-rate maths, windows, symptom / number checker + fake-model loop |
| `test_build_task.py` / `solution/slo.py` | Build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L300/15-slo-error-budgets
python app.py
python failure_lab.py
python agent_assist.py          # fake model; --real for Ollama
python -m unittest -v           # 10-30 s: the 3-day log is parsed several times
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
The log is seeded, so these numbers repeat exactly.
```
$ python app.py
log        : out/requests.jsonl, 25920 requests, 2026-10-25T12:00:00Z .. 2026-10-28T11:59:50Z
availability: SLI 3d 99.9884% vs SLO 99.9%; budget used in 3d: 1.2% of 30 days; burn rates {'5m': 0.0, '1h': 0.0, '6h': 0.0, '3d': 0.1}
latency 1h : {'mean': 147.9, 'p50': 42.9, 'p95': 94.3, 'p99': 2846.3, 'requests': 360}
mean check : OK
alerts     : none
```
Read the log the SLIs come from: `tail -5 out/requests.jsonl` (zsh) or `Get-Content out\requests.jsonl -Tail 5` (PowerShell). Each line looks like `{"ts": "2026-10-25T12:00:00Z", "route": "POST /loans", "status": 200, "ms": 91.2}`.

## failureLab: average latency looks fine while p99 is broken
```
$ python failure_lab.py
last hour  : mean 147.9 ms, p95 94.3 ms, p99 2846.3 ms
base     slo.py (mean <= 200 ms): latency problems none; alerts none
solution slo.py (latency SLI): latency problems ['latency page: burn 19.7 over 1h/5m']; alerts [{'sli': 'latency', 'severity': 'page', 'windows': '1h/5m', 'burn_long': 19.7, 'burn_short': 33.3, 'threshold': 14.4}]
```
19.7 % of POST /loans were slower than 300 ms against a 1 % budget, so the burn rate is 19.7. That hour used 19.7 / 720 = 2.7 % of the 30-day budget. The overall p95 (94.3 ms) misses the incident too, because only about 4 % of all requests are slow.

## Agent assist (fake model server, observed 2026-10-28)
Code computes the facts and decides the page; the model only words the summary. `check_summary()` rejects any number that is not a fact, and any labelled number (p99, p95, mean, burn rate) that is not *that* fact. The fake server's first draft is wrong on purpose (documented in `labs/_shared/local_agent/fake_model_server.py`): it quotes the mean as the p99.
```
$ python agent_assist.py
model: fake model server (deterministic stand-in, not a language model)
facts (computed by code): evaluated_at=12:00 UTC, alert=latency page, windows=1h/5m, burn_rate=19.7, slow_since=10:34 UTC, p99_ms=2846.3, p95_ms=94.3, mean_ms=147.9, budget_used_1h=2.7%, availability_3d=99.9884%
attempt 1: REJECTED
  - number 1.97 is not in the facts
  - p99 is 2846.3, the draft says 147.9
  - burn rate is 19.7, the draft says 1.97
  - missing p99_ms 2846.3
  - missing burn_rate 19.7
attempt 2: OK
accepted draft (a human posts it):
  Incident summary: the latency page fired at 12:00 UTC (1h/5m windows, burn rate 19.7). From 10:34 UTC some POST /loans requests took seconds: p99 2846.3 ms in the last hour, while the mean was 147.9 ms and p95 94.3 ms. The last hour used 2.7% of the 30-day latency error budget. Availability stayed at 99.9884%.
```
`slow_since` is 10:34 because that is the first slow request in the seeded log (the slow path starts at 10:30 with a 20 % chance per request). With a real model: `ollama pull qwen2.5:1.5b`, then `python agent_assist.py --real` (`LOCAL_MODEL_URL`, `LOCAL_MODEL`). Not run here.

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_correct_summary_passes (test_agent_assist.CheckSummaryTest...) ... ok
test_facts_come_from_code (test_agent_assist.CheckSummaryTest...) ... ok
test_invented_number_is_rejected (test_agent_assist.CheckSummaryTest...) ... ok
test_mean_quoted_as_p99_is_rejected (test_agent_assist.CheckSummaryTest...) ... ok
test_first_draft_rejected_then_fixed (test_agent_assist.FakeModelLoopTest...) ... ok
test_main_returns_zero (test_agent_assist.FakeModelLoopTest...) ... ok
test_latency_slo_is_99_percent_of_post_loans_under_300_ms (test_build_task.LatencySliTest...) ... ok
test_quiet_before_the_incident_and_on_healthy_traffic (test_build_task.LatencySliTest...) ... ok
test_slow_tail_pages_on_the_latency_sli (test_build_task.LatencySliTest...) ... ok
test_healthy_traffic_is_quiet (test_slo.FailureLabTest...) ... ok
test_symptom_mean_looks_fine_while_p99_is_broken (test_slo.FailureLabTest...) ... ok
test_budget_consumed_is_burn_times_window_over_period (test_slo.SliTest...) ... ok
test_burn_rate_is_bad_ratio_over_budget (test_slo.SliTest...) ... ok
test_mean_check_flags_a_uniformly_slow_service (test_slo.SliTest...) ... ok
test_ongoing_outage_pages (test_slo.SliTest...) ... ok
test_page_needs_both_windows (test_slo.SliTest...) ... ok
test_percentile_nearest_rank (test_slo.SliTest...) ... ok
----------------------------------------------------------------------
Ran 17 tests in 26.471s

OK
```

## Build task (the hardening change)
Add a latency SLI, "99 % of POST /loans succeed in under 300 ms", to `SLIS` and `SLOS` in `slo.py`. `alerts()` then covers it.

- Solution: `solution/slo.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged slo.py
ERROR: test_latency_slo_is_99_percent_of_post_loans_under_300_ms   (KeyError: 'latency')
FAIL: test_slow_tail_pages_on_the_latency_sli
FAILED (failures=1, errors=1)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
```
$ python try_it.py
[1] incident starts 10:30 -> first alert at 11:27 UTC (57 min later): [{'sli': 'latency', 'severity': 'page', 'windows': '1h/5m', 'burn_long': 16.4, 'burn_short': 20.0, 'threshold': 14.4}]
[2] 5% slow instead of 20%: latency burn rates {'5m': 0.0, '1h': 1.4, '6h': 0.2, '3d': 0.0}; alerts none
```
The workbook formula predicts (1 − 0.99) / 0.197 × 60 min × 14.4 = 43.9 min. The page came later because the 5-minute window holds only about 6 POST /loans requests and must also be above 14.4.

## Mac mini and Windows
Same commands in zsh and PowerShell. The log uses UTC timestamps and `encoding="utf-8"`, so results are identical on both machines. On a network drive, writing the 2 MB log can take several seconds.

## Troubleshooting
| Symptom | Action |
|---|---|
| Alerts flap on a quiet route | Short windows hold few requests: group low-traffic routes or lengthen the short window. |
| Dashboard green, users report slowness | Replace mean-latency checks with a threshold SLI (share of requests under X ms). |
| Agent assist prints `draft rejected` | Read the listed problems; with `--real`, try a larger model. The checks, not the model, decide. |
