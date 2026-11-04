# Concept: same circuit, two frameworks

## Why it matters
You port a Qiskit circuit to Cirq. The Bell pair matches, but a later circuit "disagrees" and you hunt a physics bug for a day. The cause: the frameworks write bitstrings in **opposite orders**.

## Mental model
Like **CPU byte order**: same number, bytes printed in opposite orders. Gates and physics are shared; result formatting, qubit naming and RNGs are local conventions.

```
same physics: X on qubit 0 of 2
Qiskit counts     q1 q0 ─▶ '01'  (little-endian)
Cirq histogram    q0 q1 ─▶ '10'  (big-endian)
reverse Cirq      ─▶ '01'  ✔ compare
```

## How it works
1. **Same gates, different result shapes.** `qc.h(0)`/`qc.cx(0, 1)` are `cirq.H(q0)`/`cirq.CX(q0, q1)`. Qiskit puts qubit 0 on the right; Cirq's `histogram` makes the first measured qubit the highest bit. numpy predicts both forms → see lab step 1.
2. **Normalise, then compare distributions.** Reverse Cirq's strings: `{'10': 1000}` becomes `{'01': 1000}`. Compare with tolerances, not exact counts: each simulator has its own RNG → see lab step 2.
3. **Probe with asymmetry.** Bell results `'00'`/`'11'` read the same in both orders and hide the bug; X on one qubit exposes it (3 qubits, X on q0: Qiskit `'001'`, Cirq `'100'`, from `research/concepts_worked_examples.py`) → see lab step 3.

## Common mistakes
- Validating a port only with symmetric circuits such as Bell or GHZ.
- Comparing raw dictionaries from two frameworks with `==`.
- Swapping `cirq.measure(q0, q1)` for `cirq.measure(q1, q0)`; order sets bit order.
