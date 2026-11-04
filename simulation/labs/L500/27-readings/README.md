# 27 · Reading seminar companion

Metropolis & Ulam's 'chains of events' as a branching process: Monte Carlo extinction probability vs the analytic fixed point (an operational-validity check in Sargent's sense).

Read the concept note first: `../../../content/concepts/L500/27-readings.md`; the statements, proofs and problem set are in `../../../content/L500.json` (lesson 27). Needs only Python 3.12 + numpy (same commands on macOS and Windows; use `cd labs\L500\27-readings` on Windows).

## Run
```bash
python branching_process.py
python -m unittest -v      # runs every script, checks exit code and (on Linux) the exact recorded output
```

## Expected output (real runs, Python 3.12.15 + numpy 2.5.3, Linux)

### `branching_process.py` - Reading companion: Metropolis & Ulam's chains of events as a Galton-Watson branching process; Monte Carlo extinction probability checked against the analytic fixed point (an operational-validity test in Sargent's sense).
```
analytic extinction probability q = 0.6863 (smallest root of q = exp(1.2(q - 1)))
Monte Carlo, 20,000 chains: 0.6842 +/- 0.0064 (95% CI); contains q: True
capped chains contribute bias < q^500 = 1.8e-82
```

## Notes
- Every generator is seeded; outputs are identical run to run. On macOS/Windows the asserts must pass; last digits of a few floating-point values may differ with a different libm (pending CI).
- Run time: a few seconds per script (the M/M/1 simulation in lesson 23 and the RANDU loops in lesson 25 are pure-Python loops).
