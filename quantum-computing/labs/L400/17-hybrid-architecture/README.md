# Lab 17 — Hybrid quantum-classical architecture

Design the loop around a variational algorithm: an **orchestrator** (job-queue policy, transpile cache, retries) between
a multi-start SPSA optimiser and a **backend adapter** (`backend.py`). Three execution designs — sync loop, batched jobs,
session — are compared on a **FakeClock** (2 s queue per job, 0.02 s per circuit, 0.5 s per transpile), so every number is
deterministic. Decision: `docs/adr/0001-batched-jobs.md`; fitness test: `test_fitness.py`.

## Run
```bash
python orchestrator.py          # shipped design (naive cache key)
python solution_cache_key.py    # decided design (structural cache key)
python try_it.py
python -m unittest -v
python sampler_qiskit.py        # SDK path: Qiskit StatevectorSampler (needs ../requirements-sdk.txt; CI)
```

## Expected output
**`python orchestrator.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs); `local_cpu_s` varies by machine:
```
{"mode": "sync", "wall_s": 606.3, "billed_s": 4.8, "jobs": 240, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
{"mode": "batched", "wall_s": 186.3, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
{"mode": "session", "wall_s": 131.2, "billed_s": 131.2, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
{"mode": "batched", "wall_s": 196.3, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 3, "best_ratio": 0.6922, "local_cpu_s": …, "note": "seeded transient failures on attempts 3, 4, 17"}
```
**`python solution_cache_key.py`**:
```
{"mode": "sync", "wall_s": 486.8, "billed_s": 4.8, "jobs": 240, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
{"mode": "batched", "wall_s": 66.8, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
{"mode": "session", "wall_s": 11.7, "billed_s": 11.7, "jobs": 30, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": …}
```
**`python -m unittest`**: `Ran 16 tests ... OK (skipped=1)` (the Qiskit test runs in CI).

**`python sampler_qiskit.py`** — *pending CI*. Expected: batched = 1 transpile and 1 job per SPSA step; sync = 8 jobs per step.

## Try it
```
busy_queue (wall_s, billed_s)         {'sync': (7206.8, 4.8), 'batched': (906.8, 4.8), 'session': (39.7, 39.7)}
slow_classical_step (wall_s, billed_s) {'sync': (2585.3, 4.8), 'batched': (2165.3, 4.8), 'session': (2165.3, 2165.3)}
```

## failureLab and build task — the transpile-cache key
Fault: `orchestrator.cache_key` includes the bound angles, so 240 circuits cause 240 transpiles (`cache_hits 0`).
Fix (build task): key on template structure + backend target + optimisation level (`solution_cache_key.py`; yours: `my_cache_key.py`).
```bash
BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v        # your my_cache_key.py
BUILD_TASK_MODULE=orchestrator python -m unittest test_build_task test_fitness   # the shipped (unfixed) lab file: must fail
```
```powershell
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task test_fitness -v; Remove-Item Env:BUILD_TARGET
```
Proof — observed locally on the shipped file:
```
FAIL: test_one_transpile_per_structure (test_build_task.CacheKey.test_one_transpile_per_structure)
AssertionError: 240 != 1
FAIL: test_same_structure_new_angles_same_key (test_build_task.CacheKey.test_same_structure_new_angles_same_key)
AssertionError: Tuples differ: (Temp[125 chars](6, 7)), p=1), (np.float64(0.1), np.float64(0.2)), 'line-8', 1) != (Temp[125 chars](6, 7)), p=1), (np.float64(0.7), np.float64(1.1)), 'line-8', 1)
FAIL: test_compile_once (test_fitness.ExecutionDesignFitness.test_compile_once)
AssertionError: 240 != 1
FAIL: test_wall_and_billing_budget (test_fitness.ExecutionDesignFitness.test_wall_and_billing_budget)
AssertionError: 186.3 not less than or equal to 90.0
Ran 7 tests in 1.875s
FAILED (failures=4)
```
Solution (default) and `BUILD_TARGET=mine` with a correct file: `Ran 7 tests ... OK`.
