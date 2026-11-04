# Lesson 25 — Foundations III: algorithms and complexity — theorem checks

Numerical checks for the theorems proved in `content/L500.json` (lesson 25): T25.1-T25.4: Grover's sin^2((2k+1)θ) law, QFT unitarity and gate count, phase estimation's 4/π^2 bound, Shor's reduction with order finding.
Each check prints what it verified and raises `AssertionError` if the theorem's prediction fails. numpy and the shared
simulator `labs/_shared/qsim` only — no quantum SDK. Seeds are fixed and only rounded values are printed, so the output
should be identical on macOS, Windows and Linux.

## Run
```bash
python theorems.py            # all checks
python theorems.py T25.1      # one check (the `check` field of each theorem names its id)
python -m unittest -v         # every check passes and the output is deterministic
```
From the topic folder, `python research/l500_checks.py` re-runs every check, compares it with the `checkOutput` stored in
`content/L500.json`, and recomputes every problem-set number.

## Expected output

Observed locally (Python 3.12.15, numpy 2.5.3, Linux). `python theorems.py`:
```
[T25.1] Grover: P_k = sin^2((2k+1) theta), sin theta = sqrt(M/N); best k ~ (pi/4) sqrt(N/M)
  N =     4, M = 1: best k =   1 (floor(pi/(4 theta)) =   1, (pi/4) sqrt(N/M) =    1.57), P = 1.0000
  N =    16, M = 1: best k =   3 (floor(pi/(4 theta)) =   3, (pi/4) sqrt(N/M) =    3.14), P = 0.9613
  N =    64, M = 1: best k =   6 (floor(pi/(4 theta)) =   6, (pi/4) sqrt(N/M) =    6.28), P = 0.9966
  N =   256, M = 1: best k =  12 (floor(pi/(4 theta)) =  12, (pi/4) sqrt(N/M) =   12.57), P = 0.9999
  N =  1024, M = 1: best k =  25 (floor(pi/(4 theta)) =  25, (pi/4) sqrt(N/M) =   25.13), P = 0.9995
  N =  1024, M = 4: best k =  12 (floor(pi/(4 theta)) =  12, (pi/4) sqrt(N/M) =   12.57), P = 0.9999
  N =  4096, M = 1: best k =  50 (floor(pi/(4 theta)) =  50, (pi/4) sqrt(N/M) =   50.27), P = 0.9999
  statevector simulation matches sin^2((2k+1) theta) for every k tested (max error < 1e-9): True
  overshoot, N = 64: P at k = 6 is 0.9966, at k = 12 it is 0.0001 (rotation keeps turning)
[T25.2] The QFT matrix F_jk = e^{2 pi i jk/N}/sqrt(N) is unitary and is built by O(n^2) gates
  F^dagger F = I for N = 2 .. 256 (max error < 1e-10): True
  qsim circuit (H, CP, SWAP) equals F for n = 1 .. 5 (max error < 1e-10): True
  n = 1: 1 H + 0 controlled phases + 0 swaps = 1 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 2
  n = 2: 2 H + 1 controlled phases + 1 swaps = 4 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 8
  n = 3: 3 H + 3 controlled phases + 1 swaps = 7 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 24
  n = 4: 4 H + 6 controlled phases + 2 swaps = 12 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 64
  n = 5: 5 H + 10 controlled phases + 2 swaps = 17 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 160
[T25.3] Phase estimation: exact when phi = m/2^t; otherwise the nearest m has P >= 4/pi^2
  t = 3, phi = 0.1250: most likely m = 1 (m/8 = 0.1250), P = 1.0000
  t = 3, phi = 0.3333: most likely m = 3 (m/8 = 0.3750), P = 0.6878
  t = 3, phi = 0.3000: most likely m = 2 (m/8 = 0.2500), P = 0.5775
  t = 3, phi = 0.7071: most likely m = 6 (m/8 = 0.7500), P = 0.6719
  t = 3, phi = 0.5625 (halfway between 4/8 and 5/8): P(4) = P(5) = 0.4105
  simulated distribution equals |(1/T) sum_k e^{2 pi i k (phi - m/T)}|^2 for t = 3..6 (max error < 1e-10): True
  smallest P(most likely m) over all cases = 0.4054 >= 4/pi^2 = 0.4053: True
[T25.4] Shor's reduction: an even order r with a^(r/2) != -1 (mod N) yields gcd(a^(r/2) - 1, N)
  N = 15: 6/7 = 0.8571 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 4, gcd(2^2 - 1, 15) = 3, 15 = 3 x 5
  N = 21: 6/11 = 0.5455 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 6, gcd(2^3 - 1, 21) = 7, 21 = 7 x 3
  N = 33: 10/19 = 0.5263 of the coprime a in [2, N-1] succeed; e.g. a = 5, r = 10, gcd(5^5 - 1, 33) = 11, 33 = 11 x 3
  N = 35: 18/23 = 0.7826 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 12, gcd(2^6 - 1, 35) = 7, 35 = 7 x 5
  N = 91: 54/71 = 0.7606 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 12, gcd(2^6 - 1, 91) = 7, 91 = 7 x 13
  order finding, N = 15, a = 7, t = 8: outcomes {0: 0.25, 64: 0.25, 128: 0.25, 192: 0.25}; one run recovers r = 4 with P = 0.5000
  N = 21, a = 2, t = 9: a likely outcome m = 427, 427/512 -> continued fraction 5/6 -> r = 6; one run recovers r = 6 with P = 0.3084
```
`python -m unittest`:
```
Ran 2 tests in 1.492s
OK
```

## How to use it with the problem set
Change a parameter (an angle, N, M, φ, t, N to factor) in the matching check, predict the printed value from the theorem
first, then run. Problem-set answers in `content/L500.json` quote these outputs; do not type numbers by hand.
