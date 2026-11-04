# Concept: qubits, gates and measurement

## Why it matters
You review a circuit and must predict its output before running it. Without a model of X, H and measurement, a bug looks the same as normal randomness.

## Mental model
A qubit is a **pair of amplitudes** (a, b) with |a|² + |b|² = 1. A gate is a **2×2 matrix**; measurement is a **weighted coin flip** that reads 0 with probability |a|².

```
|0⟩=(1,0) ─X─▶ (0,1)                      → always 1
|0⟩=(1,0) ─H─▶ (0.7071, 0.7071)           → 50/50
|0⟩ ─H─▶ (0.7071, 0.7071) ─H─▶ (1,0)      → always 0
```

## How it works
1. **Gates are matrices.** X = [[0,1],[1,0]] swaps the amplitudes; H = (1/√2)[[1,1],[1,−1]] makes an equal superposition. numpy predicts each circuit → see lab step 1.
2. **Born rule and interference.** Each shot reads one bit with P = |amplitude|², so H gives about 500/500. H twice returns to (1, 0) because the amplitudes cancel, so `h_h` always reads `0` → see lab step 2.
3. **Bit order.** With several qubits, Qiskit writes qubit 0 as the rightmost character. X on qubit 0 of two lands on index 1, printed `'01'` (from `research/concepts_worked_examples.py`) → see lab step 3.

## Common mistakes
- Assuming H|0⟩ and H|1⟩ are the same state. They measure alike, but (0.7071, −0.7071) carries a minus sign that later gates notice.
- Expecting H to give exactly 500/500.
- Reading `'01'` as "qubit 0 is 0". In Qiskit the rightmost character is qubit 0.
