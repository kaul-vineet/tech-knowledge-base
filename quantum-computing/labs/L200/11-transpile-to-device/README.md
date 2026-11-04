# Lab 11 — Transpiling to a device layout

Transpile a 5-qubit GHZ "star" for three fake devices (all-to-all, line, heavy-hex) at optimization levels 0–3, and compare depth and two-qubit gate counts before and after. `GenericBackendV2` ships with Qiskit: no account, no network.

## Run
```bash
python crosscheck_numpy.py
python transpile_lab.py
python try_it.py
python solution_chain.py
python -m unittest -v
```

## Expected output

**`python crosscheck_numpy.py`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
{'H == RZ.SX.RZ (global phase)': True, 'X == SX.SX': True, 'SWAP == 3 CX': True}
star CX pairs not on the all-to-all map: []
star CX pairs not on the ring map: [(0, 2), (0, 3)]
star CX pairs not on the line map: [(0, 2), (0, 3), (0, 4)]
heavy-hex distance 3 has 19 qubits
star GHZ probabilities: {'00000': 0.5, '11111': 0.5}
```

**`python transpile_lab.py`** — *pending CI*. Expected shape (exact numbers come from the CI run):
```
before: {'depth': ..., '2q': 4, '2q_depth': 4}
all-to-all: basis ['cx', 'delay', 'id', 'measure', 'reset', 'rz', 'sx', 'x']
  level 0: {... '2q': 4 ...} ... GHZ outcomes only: True
line: ...
  level 0: {... '2q': more than 4 (SWAPs = 3 CX each) ...} GHZ outcomes only: True
heavy-hex: ...
```

**`python -m unittest`** — observed locally without SDKs: `Ran 12 tests ... OK (skipped=6)`.

## Try it
**`python try_it.py`** — observed locally without SDKs:
```
ring_vs_line  local {'all-to-all': 0, 'ring': 2, 'line': 3}
h_in_basis    local {'gates': ['rz', 'sx', 'rz'], 'equals_H_up_to_phase': True, 'global_phase_turns': -0.125}
```

## Build task — make the circuit fit the device
Add `ghz_chain(n)`: CX(0,1), CX(1,2), … instead of the star. Same state, but every CX is a line edge. Check yours with `BUILD_TASK_MODULE=my_chain python -m unittest test_build_task -v`; the SDK test expects exactly 4 two-qubit gates on the line at every level. Reference **`python solution_chain.py`** observed locally:
```
chain vs star (numpy): {'same_state_as_star': True, 'non_adjacent_on_line': []}
```
