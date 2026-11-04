# 02 on the Mac mini — the Qiskit cross-check, PQ timings for the ADRs, and the order-finding memory wall

The lab runs order finding on the quantum topic's numpy simulator and ships `shor_qiskit.py` as a cross-check that the
sandbox could not run (no Qiskit). On the Mac mini you can install the official arm64 wheels, run that cross-check plus
an Aer sampling check, time the post-quantum algorithms the ADRs choose between, and push order finding to the largest
N that fits in RAM — with the wall computed from what the simulator really allocates.

| File | What it does |
|---|---|
| `qiskit_crosscheck.py` | C1: `shor_qiskit.counting_probs` == `shor_sim` (exact, N = 15, 21, 35); C2: the same circuit sampled on `AerSimulator(method="statevector")`, 100,000 shots, total-variation distance ≤ 0.025. Skips cleanly without Qiskit (`--here` → exit 0, otherwise exit 2) |
| `pq_bench.py` | ML-KEM-768/1024 keygen/encaps/decaps, ML-DSA-44/65/87 keygen/sign/verify, X25519 / Ed25519 / ECDSA P-256 / RSA-2048 baselines; sizes read from the library; ADR-0001 decision line (client-flight bytes, server µs per handshake, cores at an assumed peak) |
| `order_wall.py` | runs `shor_sim.shor` for semiprimes N = 15 … 3599 (12 … 36 qubits = 3 per bit of N), measures bytes per amplitude with tracemalloc, predicts the wall for 16/24/32/64 GB from `mac_profile.py`, then runs every N that fits this machine |
| `ci.sh` | medium-size Mac runs for `.github/workflows/mac-mini.yml`: installs the pinned Qiskit wheels (wheels only), cross-check, PQ benchmark, order finding up to N = 143 (`--max-n`) |
| `tests/test_mac_mini.py` | 12 tests (one runs only where Qiskit is installed) |

## Run
```bash
# macOS (zsh), from integrated/labs/L600/02-quantum-safe-migration, inside the lab venv
pip install --dry-run --only-binary=:all: qiskit==2.6.1 qiskit-aer==0.18.2   # fails if no arm64 wheel exists (no compiling)
pip install qiskit==2.6.1 qiskit-aer==0.18.2          # pins of quantum-computing/documentation/README.md
python mac_mini/qiskit_crosscheck.py --out ~/kb-runs/02-qiskit.jsonl
python mac_mini/pq_bench.py --out ~/kb-runs/02-pq.jsonl
caffeinate -i python mac_mini/order_wall.py --out ~/kb-runs/02-wall.jsonl      # overnight: stops before the wall
python -m unittest discover -s mac_mini/tests -t mac_mini/tests
```
Windows (PowerShell): same commands (qiskit 2.6.1 ships a win_amd64 wheel; Aer lists Windows in its classifiers).

## Real output here (Linux sandbox, 2026-11-02 — sizes exact, timings are NOT Mac timings)
```
$ python mac_mini/qiskit_crosscheck.py --here
{"experiment": "02 Qiskit cross-check", "status": "skipped", "missing": ["qiskit", "qiskit_aer"], "install": "pip install qiskit==2.6.1 qiskit-aer==0.18.2", "machine": "x86_64", "pendingMac": true}
$ python mac_mini/pq_bench.py --here          (selected lines)
{"alg": "ML-KEM-512", "available": false, "note": "cryptography 50.0.2 has no MLKEM512PrivateKey"}
{"alg": "ML-KEM-768", "available": true, "ek_B": 1184, "ct_B": 1088, "ss_B": 32, ...}
{"alg": "ML-DSA-65", "pk_B": 1952, "sig_B": 3309, ...}
{"decision": "ADR-0001 budgets", "client_flight_budget_B": 1400, ... {"kem": "ML-KEM-1024", "sig": "ML-DSA-65", "client_key_share_B": 1600, "share_fits_client_flight": false, ...}
$ python mac_mini/order_wall.py --here
{"run": "order finding", "N": 35, "a": 2, "bits": 6, "qubits": 18, "order_r": 12, "p_success_per_run": 0.3248, "factors": [5, 7], "seconds": 1.16, "peak_traced_B": 31757432, "bytes_per_amplitude": 121.1, ...}
{"wall": "predicted from measured bytes/amplitude", "bytes_per_amplitude": 121.9, "textbook_bytes_per_amplitude": 16, "by_ram_GB": {"16": {"largest_N": 143, "qubits": 24, "need_GB": 2.045, "next_N": 323, "next_need_GB": 16.36}, "24": {"largest_N": 323, "qubits": 27, "need_GB": 16.361, "next_N": 899, "next_need_GB": 130.89}, "32": {...323...}, "64": {...323...}}}
```
The wall is not where the textbook's 16 B/amplitude puts it: `shor_sim` keeps index arrays and a permuted copy next to
the state, ~122 B per amplitude. Each extra bit of N adds 3 qubits = ×8 memory, so 24, 32 and 64 GB all stop at
N = 323 (27 qubits, 16.4 GB); N = 899 would need ~131 GB.

## Experiments (what you should see on the Mac and how to read it)
1. **Qiskit + Aer cross-check.** Expect `"machine": "arm64"`, the pinned versions, and for every N
   `C1_statevector_equal: true` and `C2_aer_tvd` around 0.005–0.015 (sampling noise only). C1 false = a bit-order or
   oracle mismatch between `shor_qiskit.py` and `shor_sim.py` (fix the code, the numpy result is the reference that the
   scorecard already checks against the L500 FFT formula). C2 above 0.025 with C1 true = an Aer/transpile problem.
   This closes the "SDK cross-checks not run: Qiskit (02)" line of `documentation/KNOWN-GAPS.md` for macOS.
2. **PQ algorithm costs for ADR-0001.** Expect ML-KEM operations in tens of µs and ML-DSA-65 signing to be the
   largest server cost. ML-DSA signing uses rejection sampling, so single runs vary — use the default 200 × 7 runs.
   Read the decision line: options with `share_fits_client_flight: false` (ML-KEM-1024: 1,600 B > 1,400 B) are out by
   bytes whatever their speed; for the rest, `cores_at_peak` > 1 means the handshake needs its own capacity line in
   ADR-0001 (the peak of 500 handshakes/s is an assumption — put yours in `PEAK_HANDSHAKES_PER_S`).
3. **The memory wall.** Expect the measured `bytes_per_amplitude` to stay near the sandbox value and every N up to
   the predicted `largest_N` to factor. Watch `seconds` grow ~×8–10 per bit. The run stops before `next_N`; forcing it
   (`--ram` larger than the machine) is exactly the swap storm the script avoids.

## Overnight
`caffeinate -i python mac_mini/order_wall.py` — the larger N take minutes to hours each. It shows the two walls that
decide what a laptop-scale simulator may claim: memory (×8 per bit) and time. The result belongs in the lesson's
`scalingLimits`, never in an RSA estimate (`estimates.py` rule: the simulator only speaks about the N it ran).

Sources and verification notes: `integrated/research/mac-mini-evidence.md`, section 02.
