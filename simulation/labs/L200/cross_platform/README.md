# Cross-platform check (L200): same seeds, same results on Linux, macOS and Windows

`fingerprints.py` imports every L200 lab and records its seeded results at the precision the lab READMEs print
(KS distances, M/M/3 statistics, ODE step counts, the Welch warm-up proposal, the CRN comparison).
`golden.json` was written on Linux x86_64 (Python 3.12.15, numpy 2.5.3). CI runs the test on `ubuntu-latest`,
`macos-latest` (Apple silicon) and `windows-latest`.

```bash
python fingerprints.py          # print this machine's fingerprints
python -m unittest -v           # compare with golden.json
```
Observed locally (Linux): `Ran 1 test ... OK`. macOS and Windows: expected, pending CI.
If a value differs, the subTest message names the lab and the machine; see `../../../documentation/HARDWARE.md`
(libm `log`/`exp` in samplers can differ in the last bit; step counts of the adaptive solver are the most sensitive value).
