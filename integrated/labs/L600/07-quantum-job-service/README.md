# L600 #07 — A reliable quantum-job service on unreliable backends

Combines **quantum-computing**, **distributed-systems** and **application-architecture**. A job service accepts
OpenQASM 2/3 circuits, canonicalises them, checks a versioned result cache, lets a scheduler pick one of three simulated
backends (different noise, latency, failure rate, capacity), runs the shots in 1000-shot chunks under leases with
fencing tokens, retries transient failures, and returns counts **with error bars** (raw and readout-mitigated) tied to
one calibration version. Everything runs on a fake clock (discrete-event simulation): no sleeps, identical output on
every run.

Reused, not copied (`_kb.py` loads them from their own folders):

| From | Module | Used for |
|---|---|---|
| quantum-computing L100 #5 | `crosscheck_qasm_numpy.parse` | OpenQASM 2/3 subset reader (front end of `canon.py`) |
| quantum-computing `_shared/qsim` | `statevector`, `density` | unitary checks, density-matrix execution, readout matrix, sampling |
| quantum-computing L300 #12 | `noise_lab.noisy_steps` | backend noise model (depolarising, damping, readout flips) |
| quantum-computing L300 #13 | `mitigation_lab.mitigate` | readout-error mitigation (inverse assignment matrix) |
| quantum-computing L400 #17 | `backend.FakeClock`, `TransientBackendError` | the clock and the retryable error |
| distributed-systems L200 #7 | `election.FencedStorage` | per-chunk fenced result slot (the fix) |
| application-architecture L300 #13 | `resilience.CircuitBreaker` | one breaker per backend (fake-clock injected) |
| application-architecture L300 #15 / L400 #21 | `slo.percentile`, `capacity.littles_law` | p95 queue time, Little's law |

## Run it

| | 🍎 macOS (zsh) | 🪟 Windows 11 (PowerShell) |
|---|---|---|
| venv | `python3.12 -m venv .venv && source .venv/bin/activate` | `py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1` |
| deps | `pip install numpy==2.5.3` | `pip install numpy==2.5.3` |
| scorecard | `python run_project.py` | `python run_project.py` |
| failure lab | `python run_project.py --inject lease-expiry` | `python run_project.py --inject lease-expiry` |
| tests | `python -m unittest discover -s tests -v` | `python -m unittest discover -s tests -v` |
| build task | `BUILD_TARGET=mine python -m unittest discover -s tests -p "test_build_task.py" -v` | `$env:BUILD_TARGET = "mine"; python -m unittest discover -s tests -p "test_build_task.py" -v` |

Run every command from this folder. Python 3.12 + numpy only; no quantum SDK needed.

## Expected output (observed, Python 3.12.15, numpy 2.5.3, Linux)

`python run_project.py` (exit 0):
```
{"milestone": "M1 intake: canonicalise + idempotent submit", "pass": true, "measure": {"families": 4, "one_hash_per_family": true, "distinct_across_families": true, "unitary_preserved": true, "replayed_submissions": 29, "conflict": "job id j000 already used with a different request"}}
{"milestone": "M2 noisy backends + scheduler", "pass": true, "measure": {"tvd_sample_vs_exact": 0.0088, "below_floor": 0, "per_backend": {"fast-noisy": 6, "slow-clean": 70, "flaky-mid": 164}}}
{"milestone": "M3 reliable execution: retries, leases, breaker, bulkhead", "pass": true, "measure": {"completed": 240, "attempts": 405, "lease_expiries": 15, "rejected_commits": 2, "breaker_opens": 4, "max_in_flight": {"fast-noisy": 4, "slow-clean": 2, "flaky-mid": 3}}}
{"milestone": "M4 results with error bars + readout mitigation", "pass": true, "measure": {"tvd_raw_vs_pre_readout": 0.0653, "tvd_mitigated_vs_pre_readout": 0.0098, "stderr_00_raw": 0.007898, "stderr_00_mitigated": 0.008486, "contract_violations": 0}}
{"milestone": "M5 versioned result cache", "pass": true, "measure": {"cache_hits": 108, "variant_hits": 46, "cache_crossings": 0}}
{"seam": "retries <-> shot accounting", "pass": true, "measure": {"requested": 2000, "returned": 2000, "lease_expiries": 2, "commits": [[0, 3, "accepted"], [1, 4, "accepted"], [0, 1, "REJECTED (token 1 < 3)"], [1, 2, "REJECTED (token 2 < 4)"]], "partial_retry_returned": 4000, "load_shots": [590000, 590000]}}
{"seam": "canonicalisation <-> cache key", "pass": true, "measure": {"unitary_preserved": true, "variant_hits": 46}}
{"seam": "noise <-> result contract (uncertainty)", "pass": true, "measure": {"contract_violations": 0, "ci95_coverage": 0.9362}}
{"seam": "calibration drift <-> cached results", "pass": true, "measure": {"cache_crossings": 0, "mid_job_restarts": 1, "drift_job_version": 2, "load_restarts": 1}}
{"fitness": "shots returned == shots requested for 100% of jobs", "pass": true, "measure": {"exact": 240, "jobs": 240, "threshold": "100%"}}
{"fitness": "cache hit never crosses calibration versions", "pass": true, "measure": {"crossings": 0, "hits": 108, "threshold": 0}}
{"fitness": "p95 queue time under budget", "pass": true, "measure": {"p95_queue_s": 18.38, "p50_queue_s": 0.0, "budget_s": 30.0}}
{"scorecard": {"milestone": "5/5", "seam": "4/4", "fitness": "3/3"}, "fault": null, "all_pass": true}
```
(p50 is 0.0 s because 108 of 240 jobs are cache hits, which never queue.)

`--inject` (each exits 1; failing lines only):
```
lease-expiry  M3 ... "pass": false      seam retries <-> shot accounting: "requested": 2000, "returned": 4000,
              commits [[0, 3, "accepted"], [1, 4, "accepted"], [0, 1, "accepted"], [1, 2, "accepted"]], "load_shots": [604000, 590000]
              M4 / seam noise <-> result contract: "contract_violations": 14     fitness shots: "exact": 226 of 240
              {"scorecard": {"milestone": "3/5", "seam": "2/4", "fitness": "2/3"}, "fault": "lease-expiry", "all_pass": false}
stale-cache   M5 / seam drift / fitness: "cache_hits": 128, "variant_hits": 53, "cache_crossings": 28
              {"scorecard": {"milestone": "4/5", "seam": "3/4", "fitness": "2/3"}, "fault": "stale-cache", "all_pass": false}
text-key      M5 / seam canonicalisation: "cache_hits": 70, "variant_hits": 0
              {"scorecard": {"milestone": "4/5", "seam": "3/4", "fitness": "3/3"}, "fault": "text-key", "all_pass": false}
```

`python scenarios.py`:
```
lease_expiry (fixed) {"requested": 2000, "returned": 2000, "attempts": 4, "lease_expiries": 2, "commits": [[0, 3, "accepted"], [1, 4, "accepted"], [0, 1, "REJECTED (token 1 < 3)"], [1, 2, "REJECTED (token 2 < 4)"]], "restarts": 0, "calibration_version": 1, "done_at": 13.0}
lease_expiry (shipped ledger) {"requested": 2000, "returned": 4000, "attempts": 4, "lease_expiries": 2, "commits": [[0, 3, "accepted"], [1, 4, "accepted"], [0, 1, "accepted"], [1, 2, "accepted"]], "restarts": 0, "calibration_version": 1, "done_at": 13.0}
drift_mid_job {"requested": 4000, "returned": 4000, "attempts": 6, "lease_expiries": 0, "commits": [[0, 1, "accepted"], [1, 2, "accepted"], [2, 3, "accepted"], [3, 4, "accepted"], [0, 5, "accepted"], [1, 6, "accepted"]], "restarts": 1, "calibration_version": 2, "done_at": 9.0}
partial_retry {"requested": 4000, "returned": 4000, "attempts": 13, "lease_expiries": 0, "commits": [[1, 1, "accepted"], [3, 2, "accepted"], [0, 3, "accepted"], [2, 4, "accepted"]], "restarts": 0, "calibration_version": 1, "done_at": 52.0}
```

`python try_it/try_it.py`:
```
{"lease_s": 10.0, "lease_expiries": 15, "rejected_commits": 2, "attempts": 405, "p95_queue_s": 18.38, "shots_exact": 240}
{"lease_s": 20.0, "lease_expiries": 0, "rejected_commits": 0, "attempts": 400, "p95_queue_s": 15.55, "shots_exact": 240}
{"policy": "floor+budget", "p95_queue_s": 18.38, "mean_est_fidelity": 0.8852, "below_floor": 0, "per_backend": {"fast-noisy": 6, "slow-clean": 70, "flaky-mid": 164}}
{"policy": "best-fidelity", "p95_queue_s": 1163.38, "mean_est_fidelity": 0.9078, "below_floor": 0, "per_backend": {"fast-noisy": 0, "slow-clean": 240, "flaky-mid": 0}}
{"policy": "fastest", "p95_queue_s": 0.0, "mean_est_fidelity": 0.8522, "below_floor": 46, "per_backend": {"fast-noisy": 150, "slow-clean": 34, "flaky-mid": 56}}
```

`python -m unittest discover -s tests -v` → `Ran 35 tests ... OK` (run 3 times, identical: everything is seeded and on a fake clock).

## Failure lab — duplicate execution after a lease expiry
1. **Inject**: `python run_project.py --inject lease-expiry` swaps in the shipped `ledger.py`, which merges every chunk report.
2. **Symptom**: a 2000-shot job returns 4000 shots; in the load test 14 of 240 jobs return 1000 extra shots
   (604,000 vs 590,000) and their error bars are too narrow (computed from the inflated N).
3. **Diagnose**: the commit log shows two `accepted` commits per chunk with different tokens (3 and 1, 4 and 2): the
   original attempt ran 15 s on a 10 s lease, the chunk was redelivered (at-least-once), and both attempts reported.
4. **Fix**: `solution/ledger.py` — each chunk slot is the L200 #7 `FencedStorage`: a write replaces the value and a
   lower token is rejected (`REJECTED (token 1 < 3)`); chunk seeds never depend on the attempt.
5. **Test**: `tests/test_failure_lab.py` (fault reproduces; fix exact 3 times) and the build task below.

## Build task
Copy `ledger.py` to `my_ledger.py`, then make `new_slot` / `write` / `read` idempotent and fenced.
`BUILD_TARGET=mine` makes every scenario and the build-task tests use your ledger. Observed: an unmodified copy fails
3 of 4 tests (`test_lease_expiry_exact_shots`, `test_replayed_attempt_is_idempotent`, `test_stale_token_rejected`);
a copy of the solution passes 4/4.
Solution: `solution/ledger.py`.

## Files
`jobservice.py` (main: submit, schedule, dispatch, lease expiry, commit) · `canon.py` · `backends.py` · `jobstore.py` ·
`ledger.py` (shipped, unfixed) · `solution/ledger.py` · `ledger_loader.py` · `cachekeys.py` · `results.py` ·
`loadtest.py` · `scenarios.py` · `run_project.py` · `_kb.py` · `tests/` · `try_it/try_it.py` · `decisions/` (3 ADRs) ·
`architecture.mmd`.

## Simulator vs real
Backends are the numpy density-matrix simulator with illustrative noise values and modelled latencies; nothing here is
a vendor's device or price. A real provider adds compile steps, per-qubit (not uniform) calibration data published on
its own schedule, and job APIs with their own retry semantics; the seams stay the same. Pending CI: the same job
through Qiskit Aer (`AerSimulator` with a `NoiseModel`) behind the `Backend` interface — not built or run here.
