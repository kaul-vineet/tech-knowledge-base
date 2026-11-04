# 4. Run the resource estimate and the device check before anything else

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py::test_feasibility_gate` and milestone M5.

## Context
Lesson 19 classifies workloads (simulate / NISQ candidate / fault-tolerant-feasible / infeasible) with a code distance
derived from the error budget. The fake device has 8 qubits; requests may ask for up to 16 nodes.

## Decision
`pipeline.feasibility()` runs first. The quantum path is offered only if the problem fits the device and the class is
"simulate" or "nisq-candidate"; otherwise the request is answered by the classical solvers and the report says why.

## Consequences
- n = 12: "needs 12 qubits > 8 on the device"; annealing answers it.
- The gate encodes policy (thresholds from lesson 19's ADR); changing it changes the pinned decision tests.
