# Cross-platform check: same seeds, same results on Linux, macOS and Windows

`fingerprints.py` imports every L100 lab and records its seeded results at the precision the lab READMEs print
(plus a SHA-256 of the final Schelling grid). `golden.json` was written on Linux x86_64 (Python 3.12.15, numpy 2.5.3).
CI runs the test on `ubuntu-latest`, `macos-latest` (Apple silicon) and `windows-latest`.

```bash
python fingerprints.py          # print this machine's fingerprints
python -m unittest -v           # compare with golden.json
```
Observed locally (Linux): `Ran 1 test ... OK`. macOS and Windows: expected, pending CI.
If a value ever differs, the subTest message names the lab and the machine; see `../../../documentation/HARDWARE.md` for why floating point can differ.
