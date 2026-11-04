# Lab 10 — Parameterized circuits

Build a circuit once with a `Parameter`, bind values, sweep 21 angles in one primitive call, and fit the expectation-value curve.

## Run
```bash
python crosscheck_numpy.py
python param_lab.py
python try_it.py
python solution_offset.py
python -m unittest -v
```

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
exact <Z> at theta = 0, pi/2, pi: [1.0, 0.0, -1.0]
fit exact <Z> [a, b, c]: [1.0, 0.0, 0.0]
fit exact <X> [a, b, c]: [0.0, 1.0, 0.0]
fit sampled <Z>, 400 shots, numpy seed 7: [0.987, -0.004, -0.005]
```

**`python param_lab.py`** — *pending CI*. Expected:
```
free parameters: [Parameter(theta)]
after binding pi/3: 0 free; 1 free in the template
exact <Z> at theta = 0, pi/2, pi: [1.0, 0.0, -1.0]
fit exact <Z> [a, b, c]: [1.0, 0.0, 0.0]
fit exact <X> [a, b, c]: [0.0, 1.0, 0.0]
fit sampled <Z>, 400 shots, seed 7: [~1.0, ~0.0, ~0.0]   (Qiskit's RNG: values differ from numpy's, within ~0.05)
```

**`python -m unittest`** — observed locally without SDKs: `Ran 12 tests ... OK (skipped=6)`.

## Try it
**`python try_it.py`** — observed locally without SDKs:
```
rx_instead_of_ry numpy {'fit_Z': [1.0, 0.0, 0.0], 'fit_X': [0.0, 0.0, 0.0]}
fewer_shots      numpy {25: {'fit': [0.969, 0.069, -0.044], 'worst_error': 0.069}, 400: {'fit': [0.987, -0.004, -0.005], 'worst_error': 0.013}}
```

## Build task — an offset parameter
Use `qc.ry(theta + phi, 0)`, bind only `phi = 0.3`, sweep `theta`, and recover `phi = atan2(-b, a)` from the fit. Check yours with `BUILD_TASK_MODULE=my_offset python -m unittest test_build_task -v`. Reference **`python solution_offset.py`** observed locally:
```
exact, phi = 0.3: 0.3
400 shots, phi = 0.3: 0.311
```
