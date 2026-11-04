# L300 cross-platform fingerprints

`fingerprints.py` imports every L300 lab (shipped file and buildTask solution) and records its seeded results at the precision the READMEs print. `golden.json` was written on Linux x86_64 (Python 3.12.15, numpy 2.5.3). CI runs `python -m unittest -v` here on ubuntu-latest, macos-latest (Apple silicon) and windows-latest. The same seeds must give the same results on every OS. Timings are excluded.

```bash
python fingerprints.py           # print this machine's fingerprints
python fingerprints.py --write   # rewrite golden.json after an intended lab change
python -m unittest -v
```
