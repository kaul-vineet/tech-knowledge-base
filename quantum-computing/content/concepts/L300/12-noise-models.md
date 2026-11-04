# Concept: noise models

## Why it matters
Every L100 and L200 check assumed a perfect simulator: a Bell pair gives only `00` and `11`. Real devices, and any simulator with a noise model, also give `01` and `10`. If your tests and dashboards still expect perfection, a correct circuit looks broken. Worse, a check that is relaxed carelessly will also miss a broken circuit. A noise model lets you predict how good a result *should* be before you trust or reject it.

## Mental model
A noise model attaches an error channel to gate names and to measurement. The state is no longer one vector but a **density matrix** ρ, a weighted mix of the states the device might really be in. Measured probabilities are the diagonal of ρ, then passed through a classical readout-flip matrix.

```
H ─▶ depol(p1) ─▶ CX ─▶ depol(p2) + damping(γ) ─▶ ρ ─▶ diag(ρ) ─▶ readout matrix ─▶ counts
                              quantum errors                         classical errors
```

## How it works
1. **Depolarizing.** Aer's `depolarizing_error(p, k)` maps ρ to (1 − p)ρ + p·I/2^k. For a Bell pair, fidelity becomes 1 − p + p/4 → see lab step 1.
2. **Amplitude damping.** Kraus operators move |1⟩ toward |0⟩ (a T1 process). It is asymmetric: all-ones outcomes decay, all-zeros do not → see lab step 3.
3. **Readout error.** A classical matrix of P(recorded | true) per qubit. With n qubits it is the Kronecker product, so 5% flips cost 1 − 0.95ⁿ of the success → see lab step 5.
4. **Metrics as JSON lines.** Fidelity ⟨ψ|ρ|ψ⟩ is the quantum metric; success P(all 0) + P(all 1) is what you can actually measure. One line per (n, p2) keeps them greppable → see lab step 2.
5. **Worked example** (`noise_lab.py`, seed 7, 2000 shots, p1 0.002, p2 0.02, damping 0.01, readout 0.02/0.04): counts `{'00': 962, '01': 82, '10': 70, '11': 886}`. Model values: Bell fidelity 0.9719, success 0.925. GHZ-4 at p2 = 0.1 drops to fidelity 0.7473 → see lab steps 1–2.
6. **Test against the model, not perfection.** Compare the observed success with the model value minus Z binomial standard errors. Check the 0/1 balance too: a missing H gives almost only `00`, so its success looks excellent → see lab step 6.

## Failure modes
- **Exact-outcome assertions fail on correct circuits.** The naive `bell_check` returns False on the noisy counts above. You notice it when tests start flaking the day noise is switched on.
- **Over-relaxed checks pass broken circuits.** A check that tests only "success ≥ 0.8" accepts a circuit with H missing. You notice it only through the balance test in the build task.
- **The noise model drifts from the device.** Calibrations change daily. Fidelities from an old model are too optimistic, so mismatches between predicted and observed success grow.

## Common mistakes
- Comparing fidelity (needs ρ) with success (needs only counts) as if they were one number: readout lowers success but not fidelity.
- Forgetting that error rates multiply with circuit size: at p2 = 0.05 the Bell pair keeps success 0.912, GHZ-4 only 0.7818.
- Using a tolerance without a statistical reason. Derive it from the shot count and the model, and record the false-alarm rate you accept.
