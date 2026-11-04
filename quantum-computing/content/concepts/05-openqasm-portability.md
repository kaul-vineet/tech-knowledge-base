# Concept: portable circuits with OpenQASM

## Why it matters
A colleague builds a circuit in one SDK, a reviewer uses another, and the hardware provider accepts a third. Python objects don't travel between tools; you need **plain text** that can be diffed in a pull request and loaded anywhere.

## Mental model
OpenQASM is to circuits what **SQL or JSON is to data**: an open, vendor-neutral text form that many engines read. Each SDK keeps its own objects; OpenQASM is the shared wire format.

```
Qiskit ─qasm3.dumps─▶ bell.qasm (text, in git) ─qasm3.loads─▶ Qiskit
                         └─▶ Cirq · PennyLane · lab 05's tiny numpy reader
```

## How it works
1. **Small, readable programs.** `OPENQASM 3.0;` plus `include "stdgates.inc";` brings in `h`, `x` and `cx`. Then `qubit[2] q;`, one statement per gate (`cx q[0], q[1];`) and `meas[0] = measure q[0];`. An 83-line parser reads the 203-byte reference file as `{'00': 0.5, '11': 0.5}` (from `research/concepts_worked_examples.py`) → see lab step 1.
2. **Round-trip, then compare behaviour.** Export and re-import with `qasm3.dumps`/`qasm3.loads` (or `qasm2`), then check unitary equivalence for gates, not text → see lab step 3.
3. **Any tool can read it.** Qiskit's exported `bell.qasm` goes into the independent parser and must give the same probabilities → see lab step 5.

## Common mistakes
- Comparing exported text byte-for-byte; formatting differs between exporters.
- Forgetting `qiskit-qasm3-import`, which `qasm3.loads` needs.
- Assuming every tool supports all of OpenQASM 3; many read only a subset.
