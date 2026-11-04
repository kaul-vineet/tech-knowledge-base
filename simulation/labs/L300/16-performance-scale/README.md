# 16 · Performance and scale: vectorise, parallelise, keep streams independent

40 replications of a 20,000-ticket help-desk queue: a pure-Python loop, the same recursion vectorised with numpy, and a spawn-safe process pool - whose seeding you harden so every replication gets its own SeedSequence child.

Read the concept note first: `../../../content/concepts/L300/16-performance-scale.md`. Main lab: Python 3.12 + numpy only. The library equivalents need the L300 pins: `python -m pip install -r ../requirements.txt` (same command on macOS and Windows; adds SALib 1.6.0 and FMPy 0.3.32 to the L100 pins).

## Run
```bash
python perf.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L300\16-performance-scale` on Windows, `cd labs/L300/16-performance-scale` on macOS).

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
Timing lines vary by machine (numpy was 7-26x faster than the loop across runs on this busy 1-CPU sandbox); everything else is seeded and identical on every run. Shipped file:
```
40 replications x 20,000 tickets, M/M/1 at 80% load (true mean wait 4.0 min, from empty)
largest difference loop vs numpy: 9.1e-14; numpy vs 2 workers: 7.7e-01
TIMING (machine-dependent):
  python loop           2.051 s   speed-up x   1.0
  numpy vectorised      0.081 s   speed-up x  25.3
  2 spawn workers      12.987 s   speed-up x   0.2
mean wait 4.240 +/- 0.000 min
distinct replication results 1 of 40 (one line each in runs.jsonl)
```

## Observability: read the log
`runs.jsonl` holds one JSON line per replication (rep, spawn_key, mean_wait, pid). First lines observed from the shipped file (pid differs per run):
```
{"rep": 0, "spawn_key": [], "mean_wait": 4.240082576236665, "pid": 21195}
{"rep": 1, "spawn_key": [], "mean_wait": 4.240082576236665, "pid": 21195}
```
Every line repeats one mean_wait with an empty spawn_key: that is the diagnosis. After the fix (`solution/runs.jsonl`):
```
{"rep": 0, "spawn_key": [0], "mean_wait": 3.979126207296837, "pid": 21099}
{"rep": 1, "spawn_key": [1], "mean_wait": 3.9437397737421414, "pid": 21099}
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `perf.py`):** `tasks_for()` gives every parallel task the run's integer seed 16: all 40 replications are identical (distinct results 1 of 40), the 'confidence interval' is 4.240 +/- 0.000 - impossible precision - and the parallel results differ from the serial numpy run by 7.7e-01.
- **Fix (your build task):** `tasks_for()` returns child i of `SeedSequence(16).spawn(40)` with replication i: 40 of 40 distinct, 4.042 +/- 0.118 min, numpy vs 2 workers 0.0e+00, bit-identical on 1, 2 or 3 workers (`solution/perf.py`).
- **Proof:** `test_build_task.py` - 2 of 3 tests FAIL with `BUILD_TARGET=mine` on the shipped file (the 1-vs-2-worker equality passes either way), 3 of 3 PASS on the solution. `TestFailureLab` in `test_perf.py` keeps the fault reproducible (1 distinct value, half-width 0). `research/failure_proofs_L300.py`: shipped file FAIL, solution PASS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK` (about 2 minutes here: every pool starts fresh interpreters).

## Try it
```bash
python try_it.py
```
Observed:
```
1 vs 2 vs 3 workers bit-identical: True | mean wait 4.099 min
root+id seeding: 7 of 8 replications of run B repeat run A
SeedSequence(17).spawn(8): 0 of 8 repeat run A
```

## Build it (hardening task)
Fix `tasks_for()` in `perf.py` so each replication carries its own independent, reproducible stream, whatever worker runs it.

Hints:
- Spawn the children once, in the parent: `np.random.SeedSequence(SEED).spawn(reps)`.
- Tie child i to replication i (not to a worker id), so the worker count cannot change the results.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`, then `python -m unittest test_build_task -v`). Shipped file: `Ran 3 tests ... FAILED (failures=2)`; after the fix: `OK`. Without the variable the test checks `solution/perf.py` (observed: `Ran 3 tests ... OK`).
Reference solution output (`python solution/perf.py`, timing lines vary):
```
40 replications x 20,000 tickets, M/M/1 at 80% load (true mean wait 4.0 min, from empty)
largest difference loop vs numpy: 9.1e-14; numpy vs 2 workers: 0.0e+00
TIMING (machine-dependent):
  python loop           1.493 s   speed-up x   1.0
  numpy vectorised      0.212 s   speed-up x   7.0
  2 spawn workers      12.466 s   speed-up x   0.1
mean wait 4.042 +/- 0.118 min
distinct replication results 40 of 40 (one line each in runs.jsonl)
```

## Stretch (after the build task)
Add run_chunked(reps, workers, chunk_size): send replications in chunks (fewer pickled tasks), keep seed i tied to replication i, and prove the results are identical for any worker count and chunk size.

Hints:
- Spawn the children once in the parent, then slice the task list.
- Pool.map keeps the order of the chunks.
- Compute each chunk with mean_wait_vectorised() on a 2-D array.

Check: `python -m unittest test_stretch -v` (observed: `Ran 1 test ... OK`). The reference solution is `solution/chunked.py`; to test your own `chunked.py` in this folder, set `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`).
Reference solution output (`python solution/chunked.py`):
```
1 worker x 1 chunk vs 2 workers x chunks of 7: identical = True; mean wait 4.042 min
```

## Library equivalent (pending-ci)
No extra library: multiprocessing and numpy only. The timing table depends on your machine (this sandbox has 1 CPU, so 2 workers are slower than numpy: process start-up dominates).

## Files
- `perf.py` - main lab code (loop, numpy, spawn pool; ships the unfixed `tasks_for()`)
- `solution/perf.py` - buildTask solution (the fix)
- `solution/chunked.py` - stretch solution
- `try_it.py` - tryIt script (spawn-safe main guard)
- `test_perf.py` - unit tests + fault reproduction
- `test_build_task.py` - buildTask check (`BUILD_TARGET=mine` checks your file)
- `test_stretch.py` - stretch check

