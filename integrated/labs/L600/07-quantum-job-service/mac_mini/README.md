# 07 on the Mac mini — a real Qiskit Aer backend, the qubit walls, and the load test over many seeds

The lab's three backends are numpy density-matrix simulations behind one interface (`backends.Backend`). On the Mac
mini you can put **Qiskit Aer** behind the same interface and run the unchanged job service on it, find how many qubits
each backend kind can take before RAM or time runs out (computed from the Mac's RAM), and run the load test for 40
seeds and larger fleets overnight.

| File | What it does |
|---|---|
| `aer_backend.py` | `AerBackend(backends.Backend)`: only `exact_probs` and `execute` change (Aer density matrix with the same three noise channels as quantum L300 #12, readout via `ReadoutError`, `seed_simulator` derived from the same tuple as the numpy backend); `conformance()` = the interface contract the service relies on; the 240-job load test with `slow-clean` on Aer |
| `qubit_sweep.py` | GHZ-n on numpy statevector, numpy density matrix (the service's path) and, with `--aer`, Aer statevector / density_matrix; walls computed from `mac_profile.py` |
| `overnight_load.py` | `loadtest.run()` unchanged for many seeds and fleets of 3, 6, 12 backends (renamed copies), one process per run |
| `ci.sh` | medium-size Mac runs for `.github/workflows/mac-mini.yml`: installs the pinned Qiskit wheels, Aer adapter, sweeps with a 120 s cap, 4 seeds × 1,000 jobs |
| `tests/test_mac_mini.py` | 7 tests (one runs only with Aer installed) |

## Run
```bash
# macOS (zsh), from integrated/labs/L600/07-quantum-job-service, inside the lab venv
pip install qiskit==2.6.1 qiskit-aer==0.18.2
python mac_mini/aer_backend.py --out ~/kb-runs/07-aer.jsonl
python mac_mini/qubit_sweep.py --aer --out ~/kb-runs/07-sweep.jsonl
caffeinate -i python mac_mini/overnight_load.py --seeds 40 --jobs 5000 --copies 1 2 4 --out ~/kb-runs/07-load.jsonl
python -m unittest discover -s mac_mini/tests -t mac_mini/tests
```

## Real output here (Linux sandbox, 2026-11-02 — sandbox values, NOT Mac values)
```
$ python mac_mini/aer_backend.py --here
{"conformance": "numpy backends.Backend (proves the checks)", "counts_sum_to_shots": true, "keys_are_n_bit_strings": true, "same_attempt_same_counts": true, "next_chunk_new_samples": true, "exact_probs_normalised": true, "samples_match_exact_tvd<0.03": true, "old_version_unchanged_after_recalibration": true, "new_version_differs": true, "pass": true}
{"aer": "skipped", "install": "pip install qiskit==2.6.1 qiskit-aer==0.18.2", "pendingMac": true}
$ python mac_mini/qubit_sweep.py --here      (selected lines)
{"walls": "computed from mac_profile budgets", "by_ram_GB": {"16": {"statevector_c128": 29, "density_matrix_c128": 14}, "24": {30, 15}, "32": {30, 15}, "64": {31, 15}}}
{"sweep": "numpy statevector", "n": 18, "seconds": 0.3994, "peak_traced_B": 19137992, "bytes_per_entry": 73.0}
{"sweep": "numpy density matrix (job service path)", "n": 6, "seconds": 0.5744, "peak_traced_B": 420184, "bytes_per_entry": 102.6}
$ python mac_mini/overnight_load.py --here
{"copies": 1, "backends": 3, "seed": 7, ..., "p95_queue_s": 18.38, "ci95_coverage": 0.9362, "fitness_pass": true}
{"copies": 1, "backends": 3, "seed": 8, ..., "lease_expiries": 29, "breaker_opens": 10, "p95_queue_s": 170.49, "fitness_pass": false}
{"copies": 2, "backends": 6, "seed": 8, ..., "p95_queue_s": 19.2, "fitness_pass": true}
{"summary": "3 backends", "runs": 2, "fitness_pass_rate": 0.5, "worst_p95_queue_s": 170.49, "contract_violations": 0, ...}
```
The overnight script already found something here: the scorecard's p95 fitness function (≤ 30 s) passes for the
shipped seed 7 and **fails for seed 8** (p95 170 s) with the same 3-backend fleet, while every contract invariant
(exact shots, no cache crossing, fenced commits) holds. One seed is a sample, not a capacity guarantee.

## Experiments (what you should see on the Mac and how to read it)
1. **Aer behind the interface.** Expect every conformance check true for all three backends and
   `exact_tvd_vs_numpy` ≤ 1e-6: both compute the same channel exactly. A larger value means the two noise models
   differ (order of depolarising and damping, the readout matrix orientation, or a qubit-order flip) — fix the adapter,
   not the service. Then the load-test line must pass with `slow-clean` on Aer: the scheduler, leases, fencing tokens
   and cache cannot tell the implementations apart. This closes "SDK cross-checks not run: Qiskit (07)" for macOS.
2. **Qubit walls → admission rule.** Expect Aer statevector to run up to the computed wall (16 B × 2^n ≤ budget:
   29 qubits on 16 GB, 30 on 24/32 GB, 31 on 64 GB) and Aer density matrix to 14–15 qubits (16 B × 4^n), each refusing
   the next size with an error instead of swapping (`max_memory_mb` = the budget). The numpy density-matrix path stops
   on time first (~×8 per qubit). Decision: the job service refuses at submit any job wider than the wall of the
   backend kind it would run on (today's circuits use ≤ 4 qubits, so the rule costs nothing yet).
3. **Load at scale.** Expect `contract_violations` 0 in every run and `fitness_pass_rate` to rise with the fleet
   size. If the 3-backend pass rate over 40 seeds is well below 1, the 30 s p95 budget is not met by this capacity: the
   fitness function should be judged over seeds (e.g. ≥ 95 % of seeds) and the ADR should record the capacity needed.

## Overnight
`overnight_load.py --seeds 40 --jobs 5000 --copies 1 2 4` (120 runs, one per performance core in parallel; `spawn`
start method as macOS uses by default). It reveals tail behaviour a single seeded run cannot: how often the breaker
opens, how many lease expiries end in a fenced (rejected) commit, and the seed-to-seed spread of p95.

Sources and verification notes: `integrated/research/mac-mini-evidence.md`, section 07.
