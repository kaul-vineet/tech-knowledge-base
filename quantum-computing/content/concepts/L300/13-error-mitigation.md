# Concept: error mitigation

## Why it matters
Error correction needs many physical qubits per logical qubit, so today's results come from noisy hardware plus **mitigation**: classical post-processing and extra circuit runs that remove part of the bias from expectation values. Mitigation is cheap to switch on and easy to misuse. It trades bias for variance, and with too few shots it returns numbers that are not probabilities at all.

## Mental model
Two levers. Readout mitigation measures how the device mislabels basis states and undoes that matrix. Zero-noise extrapolation (ZNE) runs the circuit at several *amplified* noise levels and fits a curve back to noise zero.

```
readout:  calibrate |00>,|01>,|10>,|11>  ─▶ M (columns)  ─▶  p ≈ M⁻¹ · p_noisy   (quasi-probability!)
ZNE:      scale 1, 3, 5 (fold CX → CX·CX·CX)  ─▶  E(1), E(3), E(5)  ─▶  fit  ─▶  E(0)
```

## How it works
1. **Calibration matrix.** Prepare each basis state, record the observed distribution. Column j of M is "what you see when |j⟩ was prepared". Its own entries carry shot noise → see lab step 1.
2. **The inverse is a quasi-probability.** M⁻¹·p sums to 1 but can go negative where the true probability is 0, such as P(01) for a Bell pair → see lab step 2.
3. **Constrained least squares.** Minimise ‖M·p − p_noisy‖ with p ≥ 0 and Σp = 1, using projected gradient descent onto the simplex. This is the same idea as mthree's `nearest_probability_distribution()` → see lab step 6.
4. **Gate folding.** CX is its own inverse, so CX → CX·CX·CX is logically the same gate with three times the noise. Mitiq calls this local unitary folding; IBM's ZNE folds two-qubit gates the same way → see lab step 3.
5. **Extrapolation.** Linear fit or Richardson (the exact polynomial through all points). Worked example (`mitigation_lab.py`, depolarizing p2 = 0.03 per CX, mirror GHZ-3, ideal P(000) = 1): P(000) is 0.9039, 0.7474 and 0.6234 at scales 1, 3, 5. Linear ZNE gives 0.9687, Richardson 0.9944 → see lab step 4.
6. **Bias ↔ variance.** With 2000 shots per scale the raw estimate has std 0.0069 and Richardson 0.017: less bias, more spread → see lab step 5.

## Failure modes
- **Negative probabilities.** With 100 calibration and 200 run shots, the plain inverse gave P(01) = −0.0241. `numpy.random.choice` then raised "Probabilities are not non-negative". Any code that logs entropies or samples from the result fails the same way.
- **Over-correction.** The noise in M gets amplified by the inverse. At small budgets the mean TVD was 0.055 for the plain inverse and 0.0426 for the constrained fit.
- **Wrong noise model for ZNE.** Richardson assumes noise grows smoothly with the scale factor. Coherent errors or idle-time noise break that assumption, and the extrapolation can overshoot 1.0.

## Common mistakes
- Treating mitigated numbers as measured counts: report them as estimates with their own error bar.
- Clipping negatives to zero and moving on. It works roughly (TVD 0.0436 vs 0.0426 in tryIt 2), but it is not the closest valid distribution and hides how large the over-correction was.
- Calibrating once and reusing M for days, or calibrating with fewer shots than the experiment itself.
