# Cross-platform check (L400 + capstone): same seeds, same results on Linux, macOS and Windows

`fingerprints.py` imports the fixed (solution) version of every L400 lab and the capstone pipeline. It records their seeded results at the precision the READMEs print:
- twin events, last-day RMSE and refit a (#17)
- the grid + OCBA pick for macro-replication 0 (#18)
- holdout RMSEs (#19)
- two sweep task results keyed on (scenario, rep) (#20)
- the validity envelope (#21)
- the capstone's fitted inputs and staffing plan

Timings are excluded. `golden.json` was written on Linux x86_64 (Python 3.12.15, numpy 2.5.3).

```bash
python fingerprints.py          # print this machine's fingerprints
python -m unittest -v           # compare with golden.json
```
Observed locally (Linux): `Ran 1 test ... OK`. macOS and Windows: expected, pending CI. The values most at risk in the last printed digit are the least-squares refit a (#17, LAPACK) and the GP length-scale choice (#19). Both are compared at the printed precision only.
