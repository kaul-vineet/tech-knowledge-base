# 1. Compile with a noise-aware layout, reliability-weighted routing and CX cancellation, under a depth budget

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py`.

## Context
The service maps a 5-qubit QAOA circuit (lesson 14's graph, 12 CX, logical depth 17) onto an 8-qubit ladder whose
calibration changes daily. Today edge (1, 2) drifted to a 15 % CX error. Options measured by expected fidelity
(ESP = product of (1 − error) over gates and readouts), CX count and depth; `noisy_check.py` simulated the output
fidelity (Hellinger) with depolarizing noise at the same rates:

| Option | Calibrated ESP / CX / depth | Drifted ESP / CX / depth | Drifted simulated fidelity |
|---|---|---|---|
| A trivial layout + hop routing | 0.5763 / 27 / 32 | 0.2084 / 27 / 32 | 0.8959 |
| B degree-based layout + hop routing + cancel | 0.7315 / 19 / 24 | 0.3059 / 19 / 24 | 0.9169 |
| C noise-aware layout + reliable routing + cancel | 0.7925 / 13 / 18 | 0.7835 / 19 / 21 | 0.9878 |

ESP is pessimistic in absolute terms (not every error changes the output) but it ranks the options the same way as
the simulation, which is what a compiler needs.

## Decision
Compile with option C: search placements by ESP (brute force here; Qiskit's level 3 + VF2PostLayout on real devices),
route along the most reliable path, cancel adjacent CX pairs. Reject any compilation deeper than 22 layers or with ESP
below 0.75; recompile when the calibration changes.

## Consequences
- Drift on one edge no longer collapses fidelity (0.2084 → 0.7835 ESP); routing avoids the bad edge.
- Brute-force layout search is 8P5 = 6720 candidates here; it grows factorially - use subgraph isomorphism (VF2)
  or heuristics (SABRE) beyond ~10 qubits.
- A depth budget can be infeasible (try 2: 17 layers on this ladder); the fitness test then fails loudly instead of
  shipping a worse circuit.
