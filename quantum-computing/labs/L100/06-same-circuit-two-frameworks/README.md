# Lab 06 — Same circuit, two frameworks

Run a Bell pair and an asymmetric probe (X on qubit 0) in Qiskit (`StatevectorSampler`) and Cirq (`cirq.Simulator`), then compare after normalising bit order.

## Run
```bash
python crosscheck_numpy.py
python two_frameworks_lab.py
python try_it.py
python -m unittest -v
```

## Expected output

**`python crosscheck_numpy.py`** — observed locally (numpy 2.5.3):
```
bell     qiskit-order {'00': 0.5, '11': 0.5}  cirq-order {'00': 0.5, '11': 0.5}
x_on_q0  qiskit-order {'01': 1.0}  cirq-order {'10': 1.0}
```

**`python two_frameworks_lab.py`** — *pending CI*. Expected:
```
== bell
  qiskit                 {'00': ~500, '11': ~500}
  cirq_raw               {'00': ~500, '11': ~500}
  cirq_in_qiskit_order   {'00': ~500, '11': ~500}
== x_on_q0
  qiskit                 {'01': 1000}
  cirq_raw               {'10': 1000}
  cirq_in_qiskit_order   {'01': 1000}
```
Exact Bell counts differ between frameworks even with the same seed number: each simulator has its own RNG.

**`python -m unittest`** — observed locally without SDKs: `Ran 9 tests ... OK (skipped=4)` (includes `test_try_it.py`).

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
try 1 numpy {'qiskit': '001', 'cirq_raw': '100', 'cirq_in_qiskit_order': '001'}
try 2 numpy {'qiskit': '01', 'cirq_raw': '01', 'cirq_in_qiskit_order': '10'}
```
SDK-side output: *pending CI*.
