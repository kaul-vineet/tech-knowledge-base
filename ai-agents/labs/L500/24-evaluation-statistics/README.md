# 24 – Foundations II: statistics for evaluating agents

Wilson and Wald intervals with exact coverage, sample size and exact binomial power, McNemar's exact test, family-wise error and Bonferroni - Python standard library only. `check T1..T4` prints the numerical check of each theorem in lesson 24.

Concept note: `../../../content/concepts/L500/24-evaluation-statistics.md` · lesson object: `content/L500.json` #24 (theorems, proofs, problem set)
Dependencies: Python 3.12, standard library only. No model server is needed: L500 labs check mathematics, not model output.

## Run
macOS / Linux (zsh, bash):
```bash
python3 eval_stats.py            # demo
python3 eval_stats.py check T1   # numerical check of theorem T1 (T1, T2, T3, T4)
python3 -m unittest -v
```
Windows (PowerShell):
```powershell
py -3.12 eval_stats.py
py -3.12 eval_stats.py check T1
py -3.12 -m unittest -v
```

### Expected output – demo (observed 2026-10-30, Python 3.12.15, Linux sandbox)
```
lesson 12 golden set (20 cases):
  20/20 = 100%  Wilson 95 % [0.839, 1.000]
  18/20 = 90%  Wilson 95 % [0.699, 0.972]
  cases to detect a 5-point drop from 90 %: 253
  v1 vs v2 paired (2 regressions, 0 fixes): McNemar exact p = 0.500
  checking 6 categories at 0.05 each: P(any false alarm) = 0.265
```

### Expected output – `check T1` (observed 2026-10-30)
```
20/20: Wilson [0.8389, 1.0000]  bisection [0.8389, 1.0000]  Wald [1.0000, 1.0000]  agree to 1e-9: True
18/20: Wilson [0.6990, 0.9721]  bisection [0.6990, 0.9721]  Wald [0.7685, 1.0315]  agree to 1e-9: True
180/200: Wilson [0.8506, 0.9343]  bisection [0.8506, 0.9343]  Wald [0.8584, 0.9416]  agree to 1e-9: True
4000 simulated suites, n=50, p=0.9: mean p_hat 0.8995; var 0.00182 vs p(1-p)/n = 0.00180
exact coverage of nominal 95 %: n= 20 p=0.95  Wald 0.6389  Wilson 0.9245
exact coverage of nominal 95 %: n= 20 p=0.90  Wald 0.8760  Wilson 0.9568
exact coverage of nominal 95 %: n= 50 p=0.95  Wald 0.9199  Wilson 0.9622
exact coverage of nominal 95 %: n=200 p=0.95  Wald 0.9256  Wilson 0.9672
```
All four checks' outputs are recorded in `content/L500.json` (`theorems[].checkOutput`); `python research/l500_checks.py` re-runs them and fails on any difference. Numbers are printed to 4 decimals with seeded generators so macOS and Windows should print the same text (status `expected` until the CI matrix runs).

### Tests
`python -m unittest` -> `Ran 6 tests ... OK`.

## How to use this lab with the lesson
1. Read the theorem statement in the lesson and try the proof yourself.
2. Predict the check's output before running it (which way should each number move?).
3. Run the check; change one parameter in the `check_T*` function (seed, dimension, probability) and explain the new output.
4. Use the module's functions to verify your numerical answers in the problem set.
