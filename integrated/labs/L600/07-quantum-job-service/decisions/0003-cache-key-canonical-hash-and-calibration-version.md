# 3. Result-cache key = canonical circuit hash + backend + calibration version + shots + seed

## Status
Accepted (2026-10-30). Guarded by `tests/test_fitness.py::Fitness::test_cache_hit_never_crosses_calibration_versions`
and `tests/test_seams.py::CanonicalisationCacheKey`.

## Context
Clients resubmit the same circuit as different text (OpenQASM 2 vs 3, register names, comments, cancelling pairs,
commuting gates in another order). Backends recalibrate (slow-clean at t = 150 s, fast-noisy at t = 220 s); a result
measured and readout-mitigated under calibration v1 describes a device that no longer exists. Measured on the seeded
load test (`python run_project.py --inject ...`):

| Key | cache hits | hits from a textual variant | hits across a calibration version |
|---|---|---|---|
| raw text hash + backend + version | 70 | 0 | 0 |
| canonical hash + backend (no version) | 128 | 53 | 28 |
| canonical hash + backend + version (chosen) | 108 | 46 | 0 |

## Decision
Key on the canonical form from `canon.py` (quantum L100 #5 reader; cancel adjacent self-inverse pairs; ASAP moments,
sorted inside a moment) plus backend name, calibration version, shots and seed. Every canonicalisation rule must keep the
unitary (checked with the statevector simulator for every workload variant). A recalibration changes the key, so old
entries are never read again (invalidation by versioning, distributed-systems L200 #10).

## Consequences
- 108 hits (45% of jobs) with 0 version crossings; the text key loses 38 hits.
- Old-version entries stay in memory until evicted; a real cache needs a size bound or a TTL.
- The canonicaliser is part of correctness: a rule that merges inequivalent circuits returns someone else's result.
