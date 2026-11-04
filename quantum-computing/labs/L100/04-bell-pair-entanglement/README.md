# Lab 04 — Entanglement with a Bell pair

H on qubit 0, CNOT 0→1, measure; only `'00'` and `'11'` may appear.

## Run
```bash
python crosscheck_numpy.py
python bell_lab.py
python try_it.py
python -m unittest -v
```

Windows (PowerShell): same commands; set `$env:PYTHONUTF8 = "1"` first so the circuit drawing (box-drawing characters) prints when output is piped. See `documentation/HARDWARE.md`.

## Expected output

**`python crosscheck_numpy.py`** — observed locally (numpy 2.5.3):
```
amplitudes: [0.7071+0.j 0.    +0.j 0.    +0.j 0.7071+0.j]
probabilities: {'00': 0.5, '11': 0.5}
```

**`python bell_lab.py`** — *pending CI*. Expected: circuit drawing, then
```
ideal probabilities: {'00': 0.5, '11': 0.5}
counts: {'00': ~500, '11': ~500}
only '00'/'11' seen: True
```

**`python -m unittest`** — observed locally without SDKs: `Ran 8 tests ... OK (skipped=5)` (includes `test_try_it.py`).

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
swapped_cx  numpy {'00': 0.5, '01': 0.5}  product test 0.0
x_after_cx  numpy {'01': 0.5, '10': 0.5}  product test 0.5
```
SDK-side output: *pending CI*.
