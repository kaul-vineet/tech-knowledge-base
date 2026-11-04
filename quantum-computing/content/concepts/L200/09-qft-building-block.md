# Concept: the QFT as a building block

## Why it matters
The quantum Fourier transform (QFT) is a step inside phase estimation, period finding (Shor) and arithmetic circuits. You rarely call it alone, but you must trust it: its sign convention, its bit order, and its inverse.

## Mental model
The QFT is the discrete Fourier transform applied to the 2ⁿ amplitudes. In numpy it is `np.fft.ifft(..., norm="ortho")`: it has the **+i** sign and 1/√N scaling. A basis state turns into equal magnitudes whose phases rotate at a speed set by the input.

```
q2 ─H─P(π/2)─P(π/4)──────────────X─   per qubit: H, then phases that halve
q1 ───●──────┼─────H─P(π/2)──────┼─   with distance; final SWAP = bit reversal
q0 ──────────●───────●──────H────X─
```

## How it works
1. **Gate recipe.** For each qubit, from most to least significant: one H, then controlled phases π/2, π/4, …. Three qubits need 3 H, 3 CP and 1 SWAP (n(n−1)/2 CPs in general) → see lab step 2.
2. **Compare with numpy.** The circuit's matrix equals `np.fft.ifft(np.eye(8), axis=0, norm="ortho")`. Max difference 1.2e−16 in the cross-check; Qiskit's `QFTGate` matches too → see lab steps 1–2.
3. **What it does to a state.** Worked example (`research/L200_worked_examples.py`): QFT|5⟩ has every magnitude 0.3536 (1/√8). The phases are 0, 0.625, 0.25, 0.875, … turns, which is 5k/8 mod 1 → see lab step 3.
4. **Swaps and signs.** Dropping the swaps gives the DFT with bit-reversed rows (error 0.7071 until you reorder). Negating the angles gives `np.fft.fft`, the inverse → see lab step 4.
5. **Inverse.** `qc.inverse()` reverses the gates and negates the angles. QFT followed by its inverse is the identity → see lab step 2.

## Trade-offs
| | Use when | Avoid when |
|---|---|---|
| Exact QFT | Few qubits, phase estimation or period finding where precision matters | Deep circuits on noisy devices: n(n−1)/2 two-qubit phases add up |
| No final swaps | The QFT is last and you can reverse the bits classically | Another block consumes the output in order |
| `QFTGate` (library) | Production code: the transpiler picks a synthesis | Teaching or auditing the gates themselves |

## Common mistakes
- Comparing with `np.fft.fft`: that is the inverse sign.
- Forgetting that the matrix row index is little-endian (q0 = lowest bit).
- Using the deprecated `QFT` class (since Qiskit 2.1) instead of `QFTGate` or `synth_qft_full`.
