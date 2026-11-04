# Lab 01 — Set up your quantum environment

Create a venv, install pinned SDKs, and run X + measure on Qiskit's built-in reference simulator (`StatevectorSampler`). No account or cloud access is needed. Full workstation setup (both machines, every topic): `../../../../shared/WORKSTATION-SETUP.md`; the commands below are the same.

## Run
Run from the `quantum-computing` folder first (venv + install), then inside this lab folder.

**macOS (Apple-silicon Mac mini, zsh)**
```bash
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r labs/L100/requirements.txt   # qiskit 2.6.1, qiskit-qasm3-import 0.6.0, cirq 1.7.0 (+ optional qiskit-aer 0.18.2)
cd labs/L100/01-setup-environment
python crosscheck_numpy.py                            # independent check, numpy only
python check_env.py                                   # the lab
python try_it.py                                      # the two tryIt changes
python -m unittest -v                                 # tests
```

**Windows 11 (PowerShell)**
```powershell
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"            # UTF-8 output (Qiskit circuit drawings use box characters)
python -m pip install -r labs\L100\requirements.txt
cd labs\L100\01-setup-environment
python crosscheck_numpy.py; python check_env.py; python try_it.py; python -m unittest -v
```
No WSL is needed: PyPI lists Windows support for every package used here (use a Windows x64 PC). Hardware notes: `../../../documentation/HARDWARE.md`.

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
numpy 2.5.3
P(X|0>): {'0': 0.0, '1': 1.0}
expected counts for 100 shots: {'1': 100}
```

**`python check_env.py`** — *pending CI* (Qiskit cannot be installed in the authoring sandbox). Expected shape, derived from the numpy check:
```
python 3.12.x
qiskit               2.6.1      OK
qiskit-qasm3-import  0.6.0      OK
cirq                 1.7.0      OK
qiskit-aer           0.18.2     OK (optional)
counts: {'1': 100}
```

**`python -m unittest`** — observed locally without SDKs: `Ran 7 tests ... OK (skipped=4)` (includes `test_try_it.py`). In CI (`REQUIRE_QUANTUM_SDKS=1`) nothing may be skipped.

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
try 1  X twice, numpy counts for 100 shots: {'0': 100}
try 2  n=1  statevector bytes=32 (2.98023e-08 GiB)
try 2  n=3  statevector bytes=128 (1.19209e-07 GiB)
try 2  n=30 statevector bytes=17179869184 (16 GiB)
```
SDK-side output: *pending CI*.

## Files
| file | purpose |
|---|---|
| check_env.py | version check + 1-qubit circuit, transpiled to rz/sx/x/cx and sampled with StatevectorSampler |
| crosscheck_numpy.py | independent numpy expectation |
| test_setup.py | unittest |
| try_it.py | runs the two tryIt changes |
| test_try_it.py | unittest for the tryIt expectations |
