# L600 #02 — Quantum-safe migration: from Shor in a simulator to a crypto inventory

Combines **quantum-computing** (order finding on a statevector, published resource estimates), **cryptography**
(inventory, hybrid X25519MLKEM768, ML-DSA-65) and **application-architecture** (ports and adapters, a registry,
owned/expiring feature flags, fitness functions). Read first: `content/concepts/L600/02-quantum-safe-migration.md`;
full lesson: `content/parts/02.json`. Diagram: `architecture.mmd`; decisions: `decisions/ADR-0001..0004`.

## Design brief
Six services, three config files. Which public-key uses are exposed to harvest-now-decrypt-later, in what order do we
migrate them, and how do we move one service (messaging, 12-year patient data) to a quantum-safe handshake without
breaking a mixed v1/v2 fleet, overrunning a 1,400 B / 6,144 B handshake budget, or over-claiming what a 15-qubit
simulation proves?

## Layout
| Path | What |
|---|---|
| `run_project.py` | end-to-end runner: milestones, seams, fitness functions as JSON lines; `--inject bypass|downgrade` |
| `shor_sim.py` | order finding for N = 15, 21 on `quantum-computing/labs/_shared/qsim` (+ CX/CCX oracle for N = 15) |
| `estimates.py` | published RSA-2048 estimates (cited), GE2019 formulas via quantum L400 #19, NIST IR 8547 timeline |
| `inventory.py` | AST + config scanner (reuses quantum L400 #21 `solution_scanner.scan_python`) |
| `migration_plan.py` | Mosca's inequality with a labelled horizon, priorities P1-review/P1/P2/done/none |
| `crypto_registry.py`, `adapters.py` | ports by purpose; the only module naming primitives; flags from app-arch L400 #20 |
| `wire.py`, `fleet.py` | wire format + tap; v1/v2 servers and rollout phases |
| `migrated/messaging/channel.py` | the migrated service (names no algorithm) |
| `faults/messaging_bypass/`, `faults/messaging_downgrade/` | seeded faults for the failure lab and the rollout fault |
| `fitness.py`, `seams.py` | F1-F4 and S1-S4 |
| `sample_repo/` | the fake codebase + `services.json` (owner, x, y) |
| `solution/inventory_dynamic.py` | build-task reference: report crypto modules loaded by name |
| `try_it/experiments.py` | horizon sweep, bigger signature |
| `shor_qiskit.py` | Qiskit cross-check (pending CI) |
| `tests/` | one test per milestone, seam, fitness function, failure lab, build task, try it, end to end |

Reused, not copied (`_kb.py` appends the folders to `sys.path`): quantum `_shared/qsim`, L500 #25 `theorems`,
L400 #19 `estimate_lab`, L400 #21 `solution_scanner`; cryptography L400 #18 `pq_hybrid` + `solution_strict`,
L400 #17 `agility_lint`; application-architecture L400 #20 `flags`.

## Run
macOS (zsh) and Windows (PowerShell) use the same commands inside the activated venv (`source .venv/bin/activate` /
`.venv\Scripts\Activate.ps1`); only `cryptography==50.0.2` and `numpy` are needed.
```bash
python run_project.py
python run_project.py --inject bypass
python run_project.py --inject downgrade
python -m unittest discover -s tests
python try_it/experiments.py
```

## Expected output
Observed locally (Python 3.12, numpy, cryptography 50.0.2, Linux sandbox; seed 2026; fake clock 2026-10-30).
`python run_project.py` (exit 0):
```
{"milestone": "M1 Shor order finding on a statevector (N = 15, 21)", "pass": true, "measure": {"N=15": {"qubits": 12, "p_success": 0.5, "successes": "101/200", "factors": [3, 5], "oracle_gates": {"controlled_mult_permutations": 8}}, "N=15 gate-level": {"qubits": 12, "p_success": 0.5, "successes": "101/200", "factors": [3, 5], "oracle_gates": {"cx": 14, "ccx": 5}}, "N=21": {"qubits": 15, "p_success": 0.3222, "successes": "66/200", "factors": [3, 7], "oracle_gates": {"controlled_mult_permutations": 10}}}}
{"milestone": "M2 published estimates, labelled", "pass": true, "measure": {"RSA-2048": {"GE2019": "20 million noisy qubits, 8 hours", "G2025": "less than a million noisy qubits, less than a week"}, "GE2019_formula_logical_qubits": 6190, "NIST_IR_8547": "deprecated after 2030, disallowed after 2035"}}
{"milestone": "M3 crypto inventory (code + config)", "pass": true, "measure": {"findings_before": 10, "recall": 1.0, "precision": 1.0, "findings_after": 10}}
{"milestone": "M4 Mosca risk + prioritised plan", "pass": true, "measure": {"z": 10, "before": {"P1": 3, "P2-kex": 2, "P2-sig": 3, "none": 2}, "after": {"P1": 2, "P2-kex": 2, "P2-sig": 2, "done": 2, "none": 2}, "first_P1": "messaging X25519 (x+y-z = 4)"}}
{"milestone": "M5 hybrid X25519MLKEM768 + ML-DSA-65 behind the registry, flag-driven rollout", "pass": true, "measure": {"sessions": {"all-v1": {"X25519": 6}, "mixed": {"X25519MLKEM768": 4, "X25519": 2}, "all-v2": {"X25519MLKEM768": 6}, "rollback-v1": {"X25519MLKEM768": 4}}, "refused": {"all-v1": 0, "mixed": 0, "all-v2": 0, "rollback-v1": 2}}}
{"seam": "S1 quantum -> risk model: no extrapolation, z is a labelled assumption", "pass": true, "measure": {"bad_claims": 0, "sim_result_as_z_refused": true, "z_source": "planning-assumption"}}
{"seam": "S2 inventory -> plan: every finding owned and planned", "pass": true, "measure": {"findings": 10, "plan_rows": 10, "unowned": 0, "stray_file_priority": "P1-review"}}
{"seam": "S3 agility layer <-> wire format: offers and sizes match the registry", "pass": true, "measure": {"all-v1": "ok", "mixed": "ok", "all-v2": "ok", "rollback-v1": "ok", "adapters_match_advertised": true}}
{"seam": "S4 rollout flags <-> crypto policy: no downgrade when PQ is required", "pass": true, "measure": {"classical_sessions": 0, "refused": 2, "flip_gate_allows_pq_required": false}}
{"fitness": "F1 no classical-only key exchange for data with x + y > z (outside the dated baseline)", "pass": true, "measure": {"violations": [], "baseline_used": 2, "threshold": "0 outside baseline"}}
{"fitness": "F2 handshake byte budget", "pass": true, "measure": {"client_flight_bytes": 1352, "handshake_bytes": 5871, "threshold": {"client_flight_bytes": 1400, "handshake_bytes": 6144}}}
{"fitness": "F3 every service resolves algorithms via the registry", "pass": true, "measure": {"static_violations": 0, "handshakes": 24, "client_kex_resolutions": 58}}
{"fitness": "F4 feature flags owned and not expired", "pass": true, "measure": {"expired": [], "unowned": [], "threshold": "0 expired, 0 unowned"}}
{"scorecard": {"milestones": "5/5", "seams": "4/4", "fitness": "4/4"}, "inject": null, "all_pass": true, "decided_by": "code"}
```
`python run_project.py --inject bypass` (exit 1; only failing lines + scorecard shown):
```
{"milestone": "M5 hybrid X25519MLKEM768 + ML-DSA-65 behind the registry, flag-driven rollout", "pass": false, "measure": {"sessions": {"all-v1": {"X25519": 6}, "mixed": {"X25519": 6}, "all-v2": {}, "rollback-v1": {"X25519": 2}}, "refused": {"all-v1": 0, "mixed": 0, "all-v2": 6, "rollback-v1": 4}}}
{"seam": "S3 agility layer <-> wire format: offers and sizes match the registry", "pass": false, "measure": {"all-v1": ["offered ['X25519'], registry says ['X25519MLKEM768', 'X25519']"], "mixed": ["offered ['X25519'], registry says ['X25519MLKEM768', 'X25519']"], "all-v2": ["offered ['X25519'], registry says ['X25519MLKEM768']"], "rollback-v1": ["offered ['X25519'], registry says ['X25519MLKEM768']"], "adapters_match_advertised": true}}
{"seam": "S4 rollout flags <-> crypto policy: no downgrade when PQ is required", "pass": false, "measure": {"classical_sessions": 2, "refused": 4, "flip_gate_allows_pq_required": false}}
{"fitness": "F3 every service resolves algorithms via the registry", "pass": false, "measure": {"static_violations": 0, "handshakes": 24, "client_kex_resolutions": 0}}
{"scorecard": {"milestones": "4/5", "seams": "2/4", "fitness": "3/4"}, "inject": "bypass", "all_pass": false, "decided_by": "code"}
```
`python run_project.py --inject downgrade` (exit 1):
```
{"seam": "S3 agility layer <-> wire format: offers and sizes match the registry", "pass": false, "measure": {"all-v1": "ok", "mixed": "ok", "all-v2": ["offered ['X25519MLKEM768', 'X25519'], registry says ['X25519MLKEM768']"], "rollback-v1": ["offered ['X25519MLKEM768', 'X25519'], registry says ['X25519MLKEM768']"], "adapters_match_advertised": true}}
{"seam": "S4 rollout flags <-> crypto policy: no downgrade when PQ is required", "pass": false, "measure": {"classical_sessions": 2, "refused": 0, "flip_gate_allows_pq_required": false}}
{"scorecard": {"milestones": "5/5", "seams": "2/4", "fitness": "4/4"}, "inject": "downgrade", "all_pass": false, "decided_by": "code"}
```
`python shor_sim.py`:
```
{"N": 15, "a": 7, "order_r": 4, "qubits": 12, "counting_qubits": 8, "work_qubits": 4, "gates": {"h": 16, "x": 1, "iqft_cp": 28, "iqft_swap_cx": 12, "controlled_mult_permutations": 8}, "oracle": "permutation (compiled)", "p_success_per_run": 0.5, "shots": 200, "successes": 101, "factors": [3, 5], "statevector_bytes": 65536, "scope": "toy N = 15; mechanism only - says nothing about when RSA-2048 falls", "matches_L500_fft": true}
{"N": 15, "a": 7, "order_r": 4, "qubits": 12, "counting_qubits": 8, "work_qubits": 4, "gates": {"h": 16, "x": 1, "iqft_cp": 28, "iqft_swap_cx": 12, "cx": 14, "ccx": 5}, "oracle": "gate-level CX/CCX (compiled with known period)", "p_success_per_run": 0.5, "shots": 200, "successes": 101, "factors": [3, 5], "statevector_bytes": 65536, "scope": "toy N = 15; mechanism only - says nothing about when RSA-2048 falls", "matches_L500_fft": true}
{"N": 21, "a": 2, "order_r": 6, "qubits": 15, "counting_qubits": 10, "work_qubits": 5, "gates": {"h": 20, "x": 1, "iqft_cp": 45, "iqft_swap_cx": 15, "controlled_mult_permutations": 10}, "oracle": "permutation (compiled)", "p_success_per_run": 0.3222, "shots": 200, "successes": 66, "factors": [3, 7], "statevector_bytes": 524288, "scope": "toy N = 21; mechanism only - says nothing about when RSA-2048 falls", "matches_L500_fft": true}
```
`python try_it/experiments.py`:
```
{"horizon_sweep": {"5": ["edge:ECDHE X25519/P-256", "messaging:X25519", "payments:ECDHE X25519/P-256", "payments:RSA-3072", "records:ECDH P-384"], "10": ["messaging:X25519", "payments:ECDHE X25519/P-256", "payments:RSA-3072"], "15": []}}
{"bigger_signature": {"sig": "ML-DSA-87", "delivered": 6, "ok": false, "client_flight_bytes": 1308, "handshake_bytes": 7145, "threshold": {"client_flight_bytes": 1400, "handshake_bytes": 6144}}}
```
`python -m unittest discover -s tests`: `Ran 45 tests in 236.136s ... OK (skipped=1)` - the skip is the Qiskit cross-check.
Wall time here was dominated by the network-mounted file system (imports across seven reused lab folders); CPU time
for `run_project.py` was under 1 s.

## Failure lab (seeded): a hard-coded fast path bypasses the registry
`faults/messaging_bypass/channel.py` loads `cryptography.hazmat.primitives.asymmetric.x25519` from a config string with
`importlib.import_module` and builds the class name at run time. The inventory reports messaging as `done`, F1 passes,
the agility lint finds 0 violations - but S3 sees `offered ['X25519']` on the wire and F3 counts 0 registry resolutions
for 24 handshakes. Fail before / pass after:
```bash
cd tests
INJECT=bypass python -m unittest test_seam_wire_contract   # FAILED (failures=2)
python -m unittest test_seam_wire_contract                 # OK
```
(PowerShell: `$env:INJECT="bypass"; python -m unittest test_seam_wire_contract; Remove-Item Env:INJECT`.)
Fix: route the key exchange through `registry.kex_offers()` (the migrated channel). Defence in depth: the build task.

## Build task
Extend the inventory so `importlib.import_module` / `__import__` of a cryptography module (a constant, or a module-level
name bound to a constant or an `os.environ.get` default) is reported. Reference: `solution/inventory_dynamic.py`, which finds:
```
{"file": "faults/messaging_bypass/channel.py", "line": 24, "algorithm": "dynamic: cryptography.hazmat.primitives.asymmetric.x25519", "usage": "key-establishment", "service": "messaging", "pq": false, "classical_fallback": false}
```
```bash
cd tests
python -m unittest test_build_task                                   # reference solution: OK
BUILD_TASK_MODULE=inventory python -m unittest test_build_task       # shipped scanner: FAILED (failures=2)
BUILD_TARGET=mine python -m unittest test_build_task                 # your ../my_inventory.py
```

## Pending CI
`shor_qiskit.py` / `tests/test_pending_ci.py` (Qiskit), macOS and Windows runs, Wireshark capture of a real
X25519MLKEM768 handshake, import-linter contract - see `validation.pendingCi` in the lesson.
