# Lab 09 — The QFT as a building block

Build the 3-qubit quantum Fourier transform from H, controlled-phase and SWAP gates, prove it equals numpy's DFT matrix, and undo it with the inverse.

## Run
```bash
python crosscheck_numpy.py
python qft_lab.py
python try_it.py
python solution_period.py
python -m unittest -v
```
Windows (PowerShell): set `$env:PYTHONUTF8 = "1"` first (circuit drawing).

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
QFT gates vs numpy DFT, max |difference|: 0.0
inverse QFT gates vs numpy DFT^-1 (np.fft.fft ortho): 0.0
QFT|5> magnitudes: [0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536]
QFT|5> phases (turns): [0.0, 0.625, 0.25, 0.875, 0.5, 0.125, 0.75, 0.375]
```

**`python qft_lab.py`** — *pending CI*. Expected, then a circuit drawing:
```
hand-built QFT == numpy DFT: True
hand-built QFT == QFTGate: True
QFT then inverse QFT == identity: True
QFT|5> magnitudes: [0.3536, ... 8 values]
QFT|5> phases (turns): [0.0, 0.625, 0.25, 0.875, 0.5, 0.125, 0.75, 0.375]
same as numpy ifft of |5>: True
```

**`python -m unittest`** — observed locally without SDKs: `Ran 12 tests ... OK (skipped=6)`.

## Try it
**`python try_it.py`** — observed locally without SDKs:
```
no_swaps        numpy {'max_error_vs_dft': 0.7071, 'after_bit_reversing_rows': 0.0}
negated_angles  numpy {'max_error_vs_dft': 0.7071, 'max_error_vs_np_fft_fft': 0.0}
```

## Build task — read a period with the QFT
Add `period_numpy(n, period, offset)` (and `period_qiskit`) that prepares |offset⟩ + |offset+r⟩ + …, applies the QFT and returns r from the spacing of the peaks. Check yours with `BUILD_TASK_MODULE=my_period python -m unittest test_build_task -v`. Reference **`python solution_period.py`** observed locally:
```
period 2 offset 0: QFT probabilities {'000': 0.5, '100': 0.5} -> period 2
period 2 offset 1: QFT probabilities {'000': 0.5, '100': 0.5} -> period 2
period 4 offset 0: QFT probabilities {'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25} -> period 4
period 4 offset 3: QFT probabilities {'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25} -> period 4
```
