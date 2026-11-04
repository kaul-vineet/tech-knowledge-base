# 3. Mitigate readout error only; no zero-noise extrapolation in the service

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py::test_mitigation_helps` and milestone M4.

## Context
Lesson 13: constrained readout mitigation always returns a valid distribution; ZNE needs 3+ noise-scaled circuits per
estimate and raised the standard deviation from 0.0069 to 0.017 at 2000 shots. The service's budget is counted in
samples, so ZNE would triple the quantum solver's cost.

## Decision
Calibrate each measured qubit (2 × 2000 shots), build the tensored assignment matrix and apply lesson 13's
constrained least-squares mitigation to the final ⟨C⟩ estimate. Do not run ZNE.

## Consequences
- Observed: raw 6.774, mitigated 6.8549, gate-noise-only target 6.8418 (error 0.068 → 0.013); ideal 7.3525.
- Gate noise remains: the mitigated value is still 0.51 below the noiseless one. ZNE (or better hardware) is the only
  way to remove that, at several times the shots.
- Calibration costs 32,000 shots per device calibration (8 qubits), amortised across requests.
