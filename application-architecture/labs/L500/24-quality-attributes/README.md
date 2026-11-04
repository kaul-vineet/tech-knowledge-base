# Lab 24 – Foundations II: quality attributes and trade-off analysis – ISO/IEC 25010, ATAM and availability maths

Quality attributes as testable scenarios (ISO/IEC 25010:2023 vocabulary, SEI ATAM utility trees), and the probability behind availability: series, parallel, k-of-n, nines → downtime, MTTF/(MTTF+MTTR), and break-even weights.

L500 labs are **numerical checks of theorems**: each `check_*.py` prints one line per check, `[OK]` or `[FAIL]`, and exits 1 if any check fails. Proofs are in `content/L500.json` (`theorems`) and the concept note `content/concepts/L500/24-quality-attributes-tradeoffs.md`.

## Theorems checked
- **T24.1 Series composition and its bounds** – A service that needs all of n components, component i up with probability Aᵢ, has availability A = ∏Aᵢ if failures are independent. Without independence, 1 − Σ(1 − Aᵢ) ≤ A ≤ minᵢ Aᵢ.
- **T24.2 Parallel redundancy and k-of-n** – With independent replicas, the 'any one is enough' structure has A = 1 − ∏(1 − Aᵢ). For n identical replicas of availability a and a requirement of at least k up, A = Σ_{j=k..n} C(n, j) aʲ (1 − a)ⁿ⁻ʲ.
- **T24.3 Nines, downtime and steady-state availability** – Over a period T the allowed downtime is (1 − A)·T, so each extra nine divides it by 10. If a component alternates i.i.d. up periods (mean MTTF) and repair periods (mean MTTR), the long-run fraction of time up is MTTF / (MTTF + MTTR), whatever the distributions.
- **T24.4 Break-even weight between two options** – Two options x, y are scored on two criteria with weights (w, 1 − w). With d = x − y, the score difference Δ(w) = w·d₁ + (1 − w)·d₂ is affine, so there is at most one break-even weight w* = d₂ / (d₂ − d₁) in (0, 1); it exists iff d₁ and d₂ have opposite signs, and the preferred option flips there.

## Files
| File | Purpose |
|---|---|
| `availability.py` | series, parallel, k-of-n, nines, Monte Carlo, renewal simulation |
| `tradeoff.py` | Library Loans utility tree and break-even weight |
| `check_quality.py` | numerical checks for T24.1-T24.4 |
| `test_quality.py` | unittest suite |

## Run (Mac mini zsh or Windows PowerShell; stdlib only)
```bash
cd labs/L500/24-quality-attributes
python check_quality.py
python -m unittest -v
```
On Windows use `py -3.12` if `python` is not on PATH.

## Expected output (observed 2026-10-30, Python 3.12.15, Linux)
All random draws are seeded, so the numbers repeat exactly.
```
$ python check_quality.py
T1/T2 series = product, parallel = 1 - product of unavailabilities (independent components)
  [OK] Library Loans (LB, 2 API replicas, DB, IdP): formula 99.837569% = enumeration of 32 states 99.837569% (|diff| 1.1e-16)
  [OK] Monte Carlo 400,000 trials: 99.8363% within 4 sigma (0.0255%) of the formula
  [OK] one API instance: series 99.3409%; union bound 99.3400% <= A <= min 99.50%
      adding the 2nd API replica: 99.3409% -> 99.8376%; a 3rd: 99.8401% (the database is now the limit: 99.90%)
  [OK] 1-of-3 replicas at 99%: binomial 99.999900% = enumeration 99.999900%
  [OK] 2-of-3 replicas at 99%: binomial 99.970200% = enumeration 99.970200%
  [OK] 3-of-3 replicas at 99%: binomial 97.029900% = enumeration 97.029900%
  [OK] 1-of-n equals parallel([a]*n)
T3 nines -> downtime, and steady-state availability = MTTF / (MTTF + MTTR)
           SLO  min / 30 days  h / year
       99.000%         432.00    87.600
       99.900%          43.20     8.760
       99.950%          21.60     4.380
       99.990%           4.32     0.876
       99.999%           0.43     0.088
  [OK] each extra nine divides allowed downtime by 10: ratios [10.0, 10.0, 10.0]
  [OK] CACM example: 3 outages x 20 min = 60 min > 52.56 min allowed by 99.99%/year
  [OK] MTTF 720 h, MTTR 1 h, exponential repair: simulated up fraction 99.86079% vs formula 99.86130%
  [OK] MTTF 720 h, MTTR 1 h, uniform repair: simulated up fraction 99.86142% vs formula 99.86130%
T4 two criteria, weights (w, 1-w): at most one break-even weight w*; preference flips there
  [OK] SQLite (0.4, 0.9) vs replicated PostgreSQL (0.95, 0.5): w* = 0.4211; sweep flips at [0.4211]
  [OK] 2,000 random option pairs: sign changes match the formula (0 mismatches)
      utility tree, highest priority first (importance, difficulty):
        (H,H) availability: Primary database fails at peak; service restored within 5 min, no comm...
        (H,M) availability: Identity provider is down; members already signed in can still renew l...
        (H,M) interaction capability: A screen-reader user completes 'borrow a book' with keyboard only; WCA...
ALL CHECKS OK
$ python -m unittest
Ran 7 tests ... OK
```

## If a check fails
| Symptom | Action |
|---|---|
| `ModuleNotFoundError` | Run from this folder; the lab imports its neighbours by file name. |
| Numbers differ from above | You edited an earlier lab (L100 #2, L200 #7, L200 #8); the checks read that code live – re-run and explain the difference, that is the point. |
