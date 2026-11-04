# Lab 05 — Portable circuits with OpenQASM

Export a Bell circuit to OpenQASM 3 (`qiskit.qasm3.dumps`) and OpenQASM 2 (`qiskit.qasm2.dumps`), re-import, and check nothing changed. An independent mini-parser (numpy only) reads the same text to show the format is tool-neutral.

`qiskit.qasm3.loads` needs the `qiskit-qasm3-import` package (pinned in `../requirements.txt`).

## Run
```bash
python crosscheck_qasm_numpy.py                 # reads reference_bell_qasm3.qasm + reference_bell_qasm2.qasm
python qasm_lab.py                              # writes bell.qasm
python crosscheck_qasm_numpy.py bell.qasm       # independent parser reads Qiskit's export
python try_it.py
python agent_assist.py --fake                   # agent assist with the deterministic fake model
python -m unittest -v
```

## Expected output

**`python crosscheck_qasm_numpy.py`** — observed locally (numpy 2.5.3):
```
reference_bell_qasm3.qasm: {'00': 0.5, '11': 0.5}
reference_bell_qasm2.qasm: {'00': 0.5, '11': 0.5}
```

**`python qasm_lab.py`** — *pending CI*. Expected:
- OpenQASM 3 text beginning `OPENQASM 3.0;` and `include "stdgates.inc";`, containing `h q[0];` and `cx q[0], q[1];` and measurements;
- OpenQASM 2 text in the documented form (`OPENQASM 2.0; include "qelib1.inc"; qreg q[2]; ... cx q[0],q[1]; ...`);
- `qasm3 round-trip same unitary: True` and `qasm2 round-trip same unitary: True`;
- identical `original counts` and `re-imported counts` (same seed), only `'00'`/`'11'`.

**`python crosscheck_qasm_numpy.py bell.qasm`** — *pending CI*; expected `bell.qasm: {'00': 0.5, '11': 0.5}` (asserted by `test_exported_text_readable_by_independent_parser`).

**`python -m unittest`** — observed locally without SDKs: `Ran 18 tests ... OK (skipped=7)` (includes `test_try_it.py` and `test_agent_assist.py`).

## Try it
Two small changes to predict, then check. `try_it.py` applies them (numpy/parser part runs anywhere; the SDK part runs only when the SDKs are installed, i.e. in CI) and `test_try_it.py` asserts the results. Tasks and expected results: the lesson's `tryIt` field in `content/L100.json`.

**`python try_it.py`** — observed locally without SDKs (numpy 2.5.3):
```
swap_control parser {'00': 0.5, '01': 0.5}
add_s_gate   parser ValueError: unsupported statement: 's q[0]'
```
SDK-side output: *pending CI*.

## Agent assist (local model proposes, code decides)
A local model (Ollama on the Mac mini or Windows PC, OpenAI-compatible endpoint `http://localhost:11434/v1`) drafts OpenQASM 3 from a one-line description. The model never decides: `agent_assist.check()` extracts the program, reads it with this lab's own parser (`crosscheck_qasm_numpy.py`), computes exact probabilities with numpy and compares them with the spec in `TASKS` (Bell pair: only `'00'`/`'11'`). A draft the parser cannot read is rejected as unverifiable. Model text is never executed.

```bash
python agent_assist.py --fake            # deterministic fake server (127.0.0.1), no model download
python agent_assist.py --fake --show     # also print each raw reply
LOCAL_MODEL=qwen2.5:1.5b python agent_assist.py      # real local model (PowerShell: $env:LOCAL_MODEL="qwen2.5:1.5b"; python agent_assist.py)
```

**`python agent_assist.py --fake`** — observed locally (Python 3.12.15, numpy 2.5.3):
```
bell   ACCEPT  matches spec  counts(1000, seed 7) {'00': 502, '11': 498}
ghz3   REJECT  outcomes {'000': 0.5, '011': 0.5} != spec {'000': 0.5, '111': 0.5}
phase  REJECT  parser: unsupported statement: 'rz(pi/2) q[0]'
```
The fake replies (in `fake_qasm_rule.py`) include two typical mistakes: a GHZ circuit missing its second `cx`, and an `rz` gate outside the parser's subset. With a real model the replies vary; the verdict code does not. Tests use only the fake server. Never put secrets or tokens in a prompt. The helper is vendored at `../../_shared/local_agent/`.

## Why a neutral format
The `.qasm` file is plain text: reviewable in a pull request, diffable, and loadable by other tools (Cirq, PennyLane, Braket, QDK) without sharing Python objects.
