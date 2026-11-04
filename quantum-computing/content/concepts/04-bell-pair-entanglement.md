# Concept: entanglement with a Bell pair

## Why it matters
Teleportation, error correction and most algorithms rely on qubits whose results are **linked**. If you can't see that link in counts, you can't verify them.

## Mental model
**One coin shared by two boxes**: each box alone shows a fair random result, yet the two always agree. The joint state (|00⟩ + |11⟩)/√2 cannot be split into one state per qubit.

```
q0: |0⟩ ─H─●─ M   ──▶ '00' or '11', 50/50
q1: |0⟩ ───X─ M       never '01' or '10'
amplitudes [00,01,10,11]: [1,0,0,0] ─H─▶ [0.7071,0.7071,0,0] ─CNOT─▶ [0.7071,0,0,0.7071]
```

## How it works
1. **H, then CNOT.** H on q0 gives a product state; CNOT (control first) flips q1 wherever q0 = 1. numpy shows [0.7071, 0, 0, 0.7071] → see lab step 1.
2. **Correlation, not signalling.** Each qubit alone is 50/50, but they always match: P(q0 = 1) = 0.5 and P(q1 = 1 | q0 = 1) = 1.0 (from `research/concepts_worked_examples.py`). Counts contain only `'00'` and `'11'` → see lab step 2.
3. **The link needs CNOT.** The product test a00·a11 − a01·a10 is 0.5 for the Bell state and 0 for any product state. Remove CNOT and `'01'` appears → see lab step 3.

## Common mistakes
- Swapping control and target: `cx(1, 0)` after `h(0)` gives `'00'`/`'01'`, not a Bell pair.
- Believing measuring q0 "sends" its value to q1.
- Failing a hardware test over a few `'01'` counts; that is noise.
