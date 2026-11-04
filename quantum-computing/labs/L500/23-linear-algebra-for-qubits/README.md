# Lesson 23 — Foundations I: linear algebra for qubits — theorem checks

Numerical checks for the theorems proved in `content/L500.json` (lesson 23): T23.1-T23.4: unitaries preserve norm, tensor-product rules, the Born rule and global phase, Bell-state statistics in rotated bases.
Each check prints what it verified and raises `AssertionError` if the theorem's prediction fails. numpy and the shared
simulator `labs/_shared/qsim` only — no quantum SDK. Seeds are fixed and only rounded values are printed, so the output
should be identical on macOS, Windows and Linux.

## Run
```bash
python theorems.py            # all checks
python theorems.py T23.1      # one check (the `check` field of each theorem names its id)
python -m unittest -v         # every check passes and the output is deterministic
```
From the topic folder, `python research/l500_checks.py` re-runs every check, compares it with the `checkOutput` stored in
`content/L500.json`, and recomputes every problem-set number.

## Expected output

Observed locally (Python 3.12.15, numpy 2.5.3, Linux). `python theorems.py`:
```
[T23.1] Unitaries preserve inner products, norms and total probability
  1000 random unitaries (dims 2,4,8,16): max |<Ua|Ub> - <a|b>| < 1e-12: True
  max | ||Ua|| - 1 | < 1e-12: True
  qsim circuit H, CX, RY(0.7), CP(0.3) on 3 qubits: U^dagger U = I within 1e-12: True
  probabilities after the circuit sum to 1.000000
  non-unitary [[1,1],[0,1]] maps |1> to a vector of norm 1.4142 (probabilities would sum to 2.0)
[T23.2] Tensor products: (A x B)(C x D) = AC x BD, <a x b|c x d> = <a|c><b|d>, U x V is unitary
  mixed-product rule on 200 random 2x2 pairs: max error < 1e-10: True
  inner product of product states factorises (200 cases): max error < 1e-12: True
  U (x) V for random 2x2 and 4x4 unitaries is an 8x8 unitary: True
  |+> (x) |1> = [0.0, 0.7071, 0.0, 0.7071] (basis 00,01,10,11) = qsim H on q1, X on q0: True
[T23.3] Born rule in any orthonormal basis; global phase unobservable, relative phase observable
  300 random states and bases (dims 2,4,8): sum_k |<b_k|psi>|^2 = 1 within 1e-12: True
  multiplying by a random global phase changes no probability (within 1e-12): True
  Z basis: |+> gives {'0': 0.5, '1': 0.5}, |-> gives {'0': 0.5, '1': 0.5} (identical)
  X basis (H then measure): |+> gives {'0': 1.0}, |-> gives {'1': 1.0} (relative phase is visible)
[T23.4] Bell state statistics: P(same outcome) = cos^2(a - b), E = cos 2(a - b)
  computational basis: {'00': 0.5, '11': 0.5}
  a = 0.0000, b = 0.0000: P(same) = 1.0000, cos^2(a-b) = 1.0000, E = 1.0000; 20000 sampled shots within 4 sigma: True
  a = 0.0000, b = 0.3927: P(same) = 0.8536, cos^2(a-b) = 0.8536, E = 0.7071; 20000 sampled shots within 4 sigma: True
  a = 0.0000, b = 0.7854: P(same) = 0.5000, cos^2(a-b) = 0.5000, E = 0.0000; 20000 sampled shots within 4 sigma: True
  a = 0.3927, b = -0.3927: P(same) = 0.5000, cos^2(a-b) = 0.5000, E = 0.0000; 20000 sampled shots within 4 sigma: True
  a = 0.3000, b = 1.1000: P(same) = 0.4854, cos^2(a-b) = 0.4854, E = -0.0292; 20000 sampled shots within 4 sigma: True
  the four Bell states are orthonormal (Gram matrix = I): True
  CX then H maps them to 00, 01, 10, 11 with probability 1 (Bell measurement)
```
`python -m unittest`:
```
Ran 2 tests in 1.779s
OK
```

## How to use it with the problem set
Change a parameter (an angle, N, M, φ, t, N to factor) in the matching check, predict the printed value from the theorem
first, then run. Problem-set answers in `content/L500.json` quote these outputs; do not type numbers by hand.
