# Lab 02 — Qubits and gates in code

Build circuits with X, H and measure, run them on Qiskit's reference sampler `StatevectorSampler` (seed 7, 1000 shots; Aer's `SamplerV2` is an equivalent), read the counts.

## Run
```bash
python crosscheck_numpy.py
python gates_lab.py
python try_it.py
python -m unittest -v
```

Windows (PowerShell): same commands; set `$env:PYTHONUTF8 = "1"` first so the circuit drawing (box-drawing characters) prints when output is piped. See `documentation/HARDWARE.md`.

## Expected output

**`python crosscheck_numpy.py`** — observed locally (numpy 2.5.3):
```
nothing        {'0': 1.0}
x              {'1': 1.0}
h              {'0': 0.5, '1': 0.5}
h_h            {'0': 1.0}
x_on_q0_of_2   {'01': 1.0}
```

**`python gates_lab.py`** — *pending CI*. Expected (from the probabilities above; `h` varies around 500/500):
```
nothing        {'0': 1000}
x              {'1': 1000}
h              {'0': ~500, '1': ~500}
h_h            {'0': 1000}
x_on_q0_of_2   {'01': 1000}
```
`'01'` means qubit 0 = 1: Qiskit writes qubit 0 as the **rightmost** bit.

**`python -m unittest`** — observed locally without SDKs: `Ran 6 tests ... OK (skipped=3)` (includes `test_try_it.py`).

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
h_x_h         numpy {'0': 1.0}
x_on_q1_of_2  numpy {'10': 1.0}
```
SDK-side output: *pending CI*.
