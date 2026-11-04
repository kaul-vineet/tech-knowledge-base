# 26 · Ethics: models that make decisions about people

A SYNTHETIC illustration for the case analysis - not Ofqual's model and not 2020 data. It shows that matching a grade distribution exactly says little about individual accuracy, and how noisy small-cohort histories are.

Read the concept note first: `../../../content/concepts/L500/26-ethics.md`; the statements, proofs and problem set are in `../../../content/L500.json` (lesson 26). Needs only Python 3.12 + numpy (same commands on macOS and Windows; use `cd labs\L500\26-ethics` on Windows).

## Run
```bash
python aggregate_vs_individual.py
python -m unittest -v      # runs every script, checks exit code and (on Linux) the exact recorded output
```

## Expected output (real runs, Python 3.12.15 + numpy 2.5.3, Linux)

### `aggregate_vs_individual.py` - Synthetic illustration for the case: a rank-based model reproduces the grade distribution exactly yet disagrees with the exam for most individuals; small cohorts make centre histories noisy (Theorem 23.1).
```
teacher-exam correlation 0.80: distribution error 0.0000; same grade as exam 40.0%; within one grade 86.4%
teacher-exam correlation 0.90: distribution error 0.0000; same grade as exam 51.5%; within one grade 95.3%
exam vs an equally good re-sit: same grade 39.7%; within one 86.5%
small centres: a centre's top-two-grade share (true p = 0.26) estimated from 3 past years of n students each:
  n =   5: SD 0.113 (theory sqrt(p(1-p)/3n) = 0.113), relative error 43%
  n =   8: SD 0.090 (theory sqrt(p(1-p)/3n) = 0.090), relative error 34%
  n =  15: SD 0.065 (theory sqrt(p(1-p)/3n) = 0.065), relative error 25%
  n =  50: SD 0.036 (theory sqrt(p(1-p)/3n) = 0.036), relative error 14%
  n = 200: SD 0.018 (theory sqrt(p(1-p)/3n) = 0.018), relative error 7%
```

## Notes
- Every generator is seeded; outputs are identical run to run. On macOS/Windows the asserts must pass; last digits of a few floating-point values may differ with a different libm (pending CI).
- Run time: a few seconds per script (the M/M/1 simulation in lesson 23 and the RANDU loops in lesson 25 are pure-Python loops).
