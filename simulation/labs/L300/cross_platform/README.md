# Cross-platform check (L300): same seeds, same results on Linux, macOS and Windows

`fingerprints.py` imports every L300 lab and records its seeded or deterministic results at the precision the lab
READMEs print: variance-reduction estimates and ratios, calibration RMSEs and picks, Sobol' and Morris indices,
co-simulation metrics at 60 s and 900 s, and the lesson 16 mean wait from 40 spawned streams. Timings are excluded
because they depend on the machine. `golden.json` was written on Linux x86_64 (Python 3.12.15, numpy 2.5.3).

```bash
python fingerprints.py          # print this machine's fingerprints
python -m unittest -v           # compare with golden.json
```
Observed locally (Linux): `Ran 1 test ... OK`. macOS and Windows: expected, pending CI.
The values most likely to differ in the last printed digit are the antithetic `rho` and the Sobol' indices: they
rely on `log1p`/`exp` from the platform C library (see `../../../documentation/HARDWARE.md`).
