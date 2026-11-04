# Lab 16 — A quantum classifier vs a classical baseline (and flat gradients at scale)

A 2-qubit variational classifier (angle encoding, RY + CNOT layers, ⟨Z0⟩ + bias, parameter-shift gradients) on a tiny seeded dataset with a 40/20 train/test split, compared honestly with logistic regression in numpy. Then scale the circuit up with the textbook random initialisation and measure the gradients go flat (a barren plateau). Fix it with a near-identity initialisation and a local readout.

`circuit_model.py` is a batched numpy simulator for this circuit (all data points at once); `classifier_lab.py` is the lab.

## Run
```bash
python classifier_lab.py
python try_it.py
python solution_init.py
python -m unittest -v
python classifier_pennylane.py   # SDK path: PennyLane 0.45.1 default.qubit (needs ../requirements-extras.txt; CI job l300-extras)
```

## Expected output

**`python classifier_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
{"model": "quantum 2q x 2 layers (5 params)", "train_acc": 0.975, "test_acc": 0.9}
{"model": "logistic regression (3 params)", "train_acc": 0.975, "test_acc": 0.85}
test accuracy over 5 dataset seeds (quantum, classical): [(1.0, 1.0), (0.95, 0.95), (0.95, 0.95), (0.9, 0.85), (0.85, 0.8)]
shot-noise floor for one gradient at 1000 shots: 0.0224
{"n": 2, "layers": 2, "readout": "local", "median_abs_grad": 0.7171, "below_shot_floor": 0.0}
{"n": 6, "layers": 12, "readout": "local", "median_abs_grad": 0.1121, "below_shot_floor": 0.1}
{"n": 10, "layers": 20, "readout": "local", "median_abs_grad": 0.0208, "below_shot_floor": 0.55}
```
Honest reading: a tie. Out of 20 test points the models differ by at most one, and logistic regression trains in milliseconds; the quantum model needed 21,600 circuit evaluations (exact here; each would cost shots on hardware).

Training log `logs/train_2q_2l.jsonl` (observed, first and last line):
```
{"epoch": 0, "loss": 2.0398, "train_acc": 0.425, "grad_norm": 0.5546}
{"epoch": 59, "loss": 0.2661, "train_acc": 0.975, "grad_norm": 0.0116}
```

**`python classifier_pennylane.py`** — *pending CI*. Expected: same output as `circuit_model.outputs` for the test weights (to 1e-6) and train/test accuracy equal to the numpy lab (0.975 / 0.9) because the circuit, init and update rule are the same.

**`python -m unittest`** — observed locally without PennyLane: `Ran 10 tests ... OK (skipped=2)`.

## Try it
**`python try_it.py`** — observed locally:
```
global_readout_with_good_init {'local': 0.8742, 'global': 0.0303}
shot_noise_at_prediction      {'exact': 0.9, '100_shots': 0.85}
```

## failureLab and build task — near-identity initialisation
Fault: scale to 10 qubits × 20 layers with angles uniform in [0, 2π) (seeded). Symptom: median |∂⟨Z0⟩/∂w| = 0.0208, below the 1000-shot noise floor 0.0224 for 55% of random inits. Fix: `init_weights()` draws angles from N(0, 0.05²), so every layer starts close to the identity; keep the local ⟨Z0⟩ readout.

Reference **`python solution_init.py`** — observed locally:
```
{"n": 2, "layers": 2, "readout": "local", "median_abs_grad": 0.844, "below_shot_floor": 0.0}
{"n": 6, "layers": 12, "readout": "local", "median_abs_grad": 0.8312, "below_shot_floor": 0.0}
{"n": 10, "layers": 20, "readout": "local", "median_abs_grad": 0.863, "below_shot_floor": 0.0}
{"model": "quantum 2q x 2 layers, near-identity init", "train_acc": 0.95, "test_acc": 0.9}
```
Proof — observed locally:
```
$ BUILD_TASK_MODULE=classifier_lab python -m unittest test_build_task     # uniform random init
FAIL: test_wide_deep_model_has_usable_gradients ... AssertionError: 0.0163 not greater than np.float64(0.224)
FAILED (failures=1)
$ python -m unittest test_build_task                                     # solution_init
Ran 2 tests ... OK
```
(The test uses 10 random inits, so its median, 0.0163, differs from the 20-init scan above.)
