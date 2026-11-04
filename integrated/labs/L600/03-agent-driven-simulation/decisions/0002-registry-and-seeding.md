# ADR 0002: Append-only experiment registry keyed by model version, parameters and seed

## Status
Accepted (2026-10-30)

## Context
Every number we publish must lead back to the runs that produced it. Every run must be reproducible from its record alone. Options considered:
- (a) Log the results only. You cannot re-run them, and a code change silently changes their meaning.
- (b) A random seed per run, stored. Runs are reproducible, but extending 3 → 55 replications would give the first 3 different streams depending on call order.
- (c) A seed derived from (root seed, arm, replication) with `SeedSequence(root, spawn_key=(arm, rep))`, as in the simulation L400 #20 runner. The run id is sha256(model name + model version + canonical params + seed). The model version is a hash of the reused `warmup.py`, and the result is stored as `float.hex`.

Measured: 160 runs registered in the default session. All 160 reproduce bit-for-bit (`F2`). The first 3 replications of the 55-replication experiment have the same run ids as the 3-replication session (`tests/test_seam_replications.py`). With `--inject unseeded`, 0 of 156 reproduce.

## Decision
Option (c). The registry is JSON lines, append-only, with one `run` record per replication and one `experiment` record per job. Each experiment holds facts (name → value + run ids). The mean uses `math.fsum`, so the summation order cannot change the bits. The environment fingerprint (Python, numpy, machine) is stored with each run.

## Consequences
- Same environment ⇒ same bits. Across Python versions or C maths libraries, `random.expovariate` (it uses `math.log` from the platform libm) may differ in the last bit. Python only guarantees that `random()` keeps its sequence. The fingerprint tells you which promise applies. Cross-OS runs are pendingCi.
- If someone edits warmup.py, every old run_id stops matching this code: `reproduce()` returns False until you re-run. That is the intended behaviour.
- Fitness function: `tests/test_fitness.py::test_runs_reproducible`.
