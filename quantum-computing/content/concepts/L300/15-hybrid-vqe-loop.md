# Concept: the hybrid variational loop (VQE)

## Why it matters
VQE, QAOA and quantum classifiers share one loop: a classical optimiser proposes parameters, a quantum estimator returns a noisy number, repeat. On hardware every number is an average over finitely many shots. An optimiser that works perfectly on an exact simulator can wander or diverge as soon as shot noise appears. Without logs you will not see why.

## Mental model
The estimator is a noisy function E(θ) + ε, with ε shrinking like 1/√shots. The optimiser only ever sees E + ε. Anything that divides ε by a small number, such as a finite-difference step h, turns noise into fake gradients.

```
θ ─▶ ansatz (RY, CX, RY) ─▶ measure Z basis (II, ZI, IZ, ZZ) + X basis (XX) ─▶ E(θ)+ε ─▶ optimiser ─▶ θ'
                                                                                   │
                                                                     logs/vqe_<opt>_<shots>.jsonl
```

## How it works
1. **Hamiltonian as a Pauli sum.** H = −1.05·II + 0.39·ZI − 0.39·IZ − 0.01·ZZ + 0.18·XX (toy, H2-like). Its exact ground energy from `eigvalsh` is −1.8405. That is the referee, not something the optimiser sees → see lab step 1.
2. **Measurement grouping.** Commuting terms share shots: one Z-basis circuit gives II, ZI, IZ and ZZ; H on both qubits gives XX. That is two circuits per energy, not five → see lab step 1.
3. **Finite differences under shots.** The gradient error is about ε/h. With h = 10⁻³ and 1000 shots, the log shows a median gradient norm of 15.5 in the last 20 steps, where the exact run had 0.007 → see lab steps 2–3.
4. **SPSA.** Perturb all parameters at once by ±c_k and use two evaluations per step, whatever the dimension. With c_k ≈ 0.1–0.2 the noise is divided by 2c_k, not by h. Gains follow Spall's α = 0.602, γ = 0.101 → see lab step 5.
5. **Worked example** (`vqe_lab.py`, `solution_spsa.py`, seed 0): finite differences reach error 0.0 exactly but 1.5645 at 1000 shots. SPSA at 1000 shots reaches 0.0064 with 900,000 shots in total. Finite differences need 10⁶ shots per term (1.8·10⁹ in total) to reach 0.0076 → see lab steps 2, 4 and 5.
6. **Logs as evidence.** One JSON line per iteration (energy estimate, gradient norm or step, evaluations) lets code, and an agent, diagnose a run after the fact → see lab step 6.

## Failure modes
- **Divergence under shot noise.** In the last 20 iterations the energy estimate has std 0.39 and the gradient norm stays above 5, where the exact run converged. You see it in `tail_energy_std` and `tail_grad_norm_median`.
- **Reporting the minimum noisy estimate.** 8 of 150 logged SPSA estimates lie *below* the exact ground energy. min(energy_est) is biased low, so re-estimate the final parameters with many shots instead.
- **Silent budget blow-up.** "Just add shots" works only at a thousand times the cost. Track total shots per run.

## Common mistakes
- Tuning an optimiser on an exact statevector and shipping it to a shot-based backend unchanged.
- Choosing COBYLA or SPSA by habit. COBYLA is derivative-free and copes with moderate noise (IBM's QAOA tutorial). SPSA was designed for noisy measurements. Both need sensible step sizes.
- Logging only the final energy. Without per-iteration lines you cannot tell noise from a bad learning rate.
