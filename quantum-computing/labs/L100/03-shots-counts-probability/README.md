# Lab 03 — Shots, counts and probability

Sample H|0> with 10…10000 shots, watch the estimate converge, and use a seed for repeatable runs.

## Run
```bash
python crosscheck_numpy.py
python shots_lab.py
python try_it.py
python -m unittest -v
```

## Expected output

**`python crosscheck_numpy.py`** — observed locally (numpy 2.5.3). This is classical sampling from the exact probabilities, so it shows the same shot-noise behaviour as the simulator:
```
exact: {'0': 0.5, '1': 0.5}
shots=10     counts={'0': 4, '1': 6}  P('1')~0.600  +/- 0.158
shots=100    counts={'0': 45, '1': 55}  P('1')~0.550  +/- 0.050
shots=1000   counts={'0': 513, '1': 487}  P('1')~0.487  +/- 0.016
shots=10000  counts={'0': 5091, '1': 4909}  P('1')~0.491  +/- 0.005
seed 2024 twice: {'0': 51, '1': 49} {'0': 51, '1': 49}
```

**`python shots_lab.py`** — *pending CI*. Exact numbers depend on `StatevectorSampler`'s RNG; expected behaviour:
- estimated P('1') moves toward 0.5 as shots grow (within about ±2 standard errors shown above);
- the two `unseeded` lines usually differ; the two `seeded 2024` lines are identical;
- the histogram shows two bars of about the same length (~500 each).

**`python -m unittest`** — observed locally without SDKs: `Ran 10 tests ... OK (skipped=6)` (includes `test_try_it.py`).

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
try 1  numpy shots=2500 counts={'0': 1294, '1': 1206}  P('1')~0.4824  standard error=0.010
try 2  numpy seed 2024 {'0': 51, '1': 49}  seed 2025 {'0': 52, '1': 48}  identical=False
```
SDK-side output: *pending CI*.
