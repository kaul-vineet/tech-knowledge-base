# Lesson 24 — Foundations II: quantum information basics — theorem checks

Numerical checks for the theorems proved in `content/L500.json` (lesson 24): T24.1-T24.4: no-cloning, teleportation and superdense coding, Deutsch-Jozsa correctness, density matrices and no-signalling.
Each check prints what it verified and raises `AssertionError` if the theorem's prediction fails. numpy and the shared
simulator `labs/_shared/qsim` only — no quantum SDK. Seeds are fixed and only rounded values are printed, so the output
should be identical on macOS, Windows and Linux.

## Run
```bash
python theorems.py            # all checks
python theorems.py T24.1      # one check (the `check` field of each theorem names its id)
python -m unittest -v         # every check passes and the output is deterministic
```
From the topic folder, `python research/l500_checks.py` re-runs every check, compares it with the `checkOutput` stored in
`content/L500.json`, and recomputes every problem-set number.

## Expected output

Observed locally (Python 3.12.15, numpy 2.5.3, Linux). `python theorems.py`:
```
[T24.1] No-cloning: no unitary U and blank |e> give U|psi>|e> = |psi>|psi> for all psi
  CNOT copier clones |0> and |1> exactly (fidelity 1)
  theta = 0.0000: joint fidelity 1.0000 = (c^3 + s^3)^2 = 1.0000; copy alone 1.0000 = c^4 + s^4
  theta = 1.0472: joint fidelity 0.5999 = (c^3 + s^3)^2 = 0.5999; copy alone 0.6250 = c^4 + s^4
  theta = 1.5708: joint fidelity 0.5000 = (c^3 + s^3)^2 = 0.5000; copy alone 0.5000 = c^4 + s^4
  theta = 2.0944: joint fidelity 0.5999 = (c^3 + s^3)^2 = 0.5999; copy alone 0.6250 = c^4 + s^4
  theta = 3.1416: joint fidelity 1.0000 = (c^3 + s^3)^2 = 1.0000; copy alone 1.0000 = c^4 + s^4
  minimum fidelity 0.5000 at theta = pi/2 (|+> becomes a Bell state, not |+>|+>)
  500 random unitaries keep <0,e|+,e> = 0.7071; perfect clones would need <0|+>^2 = 0.5000: impossible
[T24.2] Teleportation and superdense coding are exact for every input
  200 random states x 4 outcomes: each outcome has probability 0.25 (within 1e-12) and Bob's corrected qubit has fidelity 1 (within 1e-12): True
  psi = cos(pi/8)|0> + sin(pi/8)|1>: outcome probabilities [0.25, 0.25, 0.25, 0.25]
  superdense coding, message ab -> Bob decodes (q0 q1): 00 -> 00, 01 -> 01, 10 -> 10, 11 -> 11 with probability 1
[T24.3] Deutsch-Jozsa: P(0^n) = 1 if f is constant and 0 if f is balanced, with one query
  n = 3: both constant functions give P(000) = 1.0000, 1.0000
  all 70 balanced functions give P(000) = 0.0000 (max)
  ancilla circuit for f = x0 XOR x2 (|-> ancilla, phase kickback): P(inputs 000) = 0.0000
  a deterministic classical algorithm needs 2^(n-1) + 1 = 5 queries in the worst case
[T24.4] Density matrices: trace 1, PSD, purity; partial trace of a Bell pair is I/2; no signalling
  Bell pair: global purity Tr(rho^2) = 1.0000; rho_A = rho_B = I/2: True; Tr(rho_B^2) = 0.5000
  200 random 2-qubit pure states: Hermitian, eigenvalues >= 0, trace 1: True
  no signalling: Alice's random unitary or unread measurement changes rho_B by < 1e-12: True
  mixture 1/2|0><0| + 1/2|+><+|: eigenvalues [0.8536, 0.1464], purity 0.7500
```
`python -m unittest`:
```
Ran 2 tests in 4.570s
OK
```

## How to use it with the problem set
Change a parameter (an angle, N, M, φ, t, N to factor) in the matching check, predict the printed value from the theorem
first, then run. Problem-set answers in `content/L500.json` quote these outputs; do not type numbers by hand.
