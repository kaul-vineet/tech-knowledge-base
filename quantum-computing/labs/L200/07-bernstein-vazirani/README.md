# Lab 07 — Bernstein–Vazirani as a pattern

Find a hidden bit-string `s` with **one** oracle query (a classical program needs `n`). The reusable part is the pattern: ancilla in |−⟩, H on the inputs, one query, H again, measure.

## Run
```bash
python crosscheck_numpy.py
python bv_lab.py
python try_it.py
python solution_bias.py
python -m unittest -v
```
Windows (PowerShell): same commands; set `$env:PYTHONUTF8 = "1"` first so the circuit drawing prints when output is piped.

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
secret 1011: {'1011': 1.0}
secret 110101: {'110101': 1.0}
all 16 four-bit secrets recovered with probability 1: True
```

**`python bv_lab.py`** — *pending CI*. Expected (StatevectorSampler, 100 shots, seed 11), then a circuit drawing:
```
secret 1011: quantum counts {'1011': 100} (1 query), classical 1011 (4 queries)
secret 110101: quantum counts {'110101': 100} (1 query), classical 110101 (6 queries)
```

**`python -m unittest`** — observed locally without SDKs: `Ran 10 tests ... OK (skipped=5)` (includes `test_try_it.py` and `test_build_task.py`).

## Try it
**`python try_it.py`** — observed locally without SDKs:
```
no_kickback  numpy {'0000': 1.0}
unreversed   numpy {'1101': 1.0}
```
SDK-side output: *pending CI*. Tasks and predictions: the lesson's `tryIt` field in `content/L200.json`.

## Build task — add a bias bit
Extend the oracle to `f(x) = s·x ⊕ b`. Write your version (for example `my_bias.py` with `recovered_numpy(secret, bias)` and `bv_oracle_with_bias(secret, bias)`), then check it:
```bash
BUILD_TASK_MODULE=my_bias python -m unittest test_build_task -v        # macOS
$env:BUILD_TASK_MODULE = "my_bias"; python -m unittest test_build_task -v   # Windows
```
Reference solution `solution_bias.py` — **`python solution_bias.py`** observed locally:
```
secret 1011 bias 0: numpy {'1011': 1.0}
secret 1011 bias 1: numpy {'1011': 1.0}
```
