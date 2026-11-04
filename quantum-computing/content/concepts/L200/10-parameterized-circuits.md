# Concept: parameterized circuits

## Why it matters
Variational algorithms, calibration scans and quantum machine learning run **one circuit shape with many angle values**. Rebuilding the circuit per value is slow and hard to read. Parameters keep one template; primitives sweep it in one call.

## Mental model
A parameterized circuit is a template: fixed gates, symbolic angles. Binding gives a concrete copy; the template is unchanged. A primitive takes the template plus an array of values and returns an array of results.

```
template: |0⟩ ─RY(θ)─        PUB = (circuit, observables, θ-values)
θ-values: 21 angles 0..2π  ──▶ Estimator ──▶ evs shape (2, 21): ⟨Z⟩, ⟨X⟩
                           ──▶ Sampler   ──▶ 21 counts dicts ──▶ ⟨Z⟩ = (n0 − n1)/shots
```

## How it works
1. **Parameters and binding.** `Parameter("theta")` goes into `qc.ry`. `assign_parameters({theta: π/3})` returns a bound copy with 0 free parameters, and the template keeps 1 → see lab step 2.
2. **One sweep, one call.** `StatevectorEstimator` takes `(qc, [[Z],[X]], thetas.reshape(-1, 1))`. Observable shape (2,1) broadcasts against 21 bindings → see lab step 3.
3. **Shots turn exact values into estimates.** The Sampler gives counts per angle via `get_counts(i)`. One ⟨Z⟩ estimate from 400 shots has standard deviation up to 1/√400 = 0.05 → see lab step 4.
4. **Fit the curve, not the points.** RY gives ⟨Z⟩ = cos θ. A least-squares fit of a·cos θ + b·sin θ + c uses all 21 points. Worked example (`research/L200_worked_examples.py`): exact [1, 0, 0]; 400 shots [0.987, −0.004, −0.005]; 25 shots [0.969, 0.069, −0.044] → see lab steps 4–5.
5. **Expressions.** `ry(theta + phi)` makes a ParameterExpression. Binding only `phi` leaves `theta` free, and the fit recovers phi = atan2(−b, a) = 0.3 → see lab step 6.

## Trade-offs
| | Use when | Avoid when |
|---|---|---|
| Parameters + one sweep PUB | Scans, optimisers, many values of one shape | The structure itself changes per value (build separate circuits) |
| Estimator (exact here) | You need ⟨O⟩ directly | You need bitstrings or the distribution |
| Sampler + fit | Hardware-like workflow; shot noise visible | Few angles and few shots |

## Common mistakes
- Passing a flat (21,) array for a one-parameter circuit. Use shape (21, 1).
- Assuming list-binding order is insertion order. It is `qc.parameters`, sorted by name.
- Reading single noisy points instead of fitting the known curve shape.
