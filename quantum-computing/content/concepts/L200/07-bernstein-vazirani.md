# Concept: Bernstein–Vazirani as a pattern

## Why it matters
Many quantum algorithms share one skeleton: superpose the inputs, ask an **oracle** once, let interference turn phases into an answer. Bernstein–Vazirani (BV) is the smallest place to build and test that skeleton and its oracle.

## Mental model
The oracle hides `s` in f(x) = s·x (mod 2). Classically you learn one bit per call. The circuit asks all inputs at once; answers become ± phases, and H turns them back into `s`.

```
inputs  |0…0⟩ ─H─┤        ├─H─ M ──▶ s (certain)
ancilla |1⟩   ─H─┤ oracle ├───      (|−⟩: flips become phases)
oracle = CX from every qubit where s has a 1
```

## How it works
1. **Oracle construction.** For each `1` in `s`, one CX from that input qubit to the ancilla computes the parity s·x. The string is written q(n−1)…q0, so the lab walks `reversed(secret)` → see lab step 3.
2. **Phase kickback.** With the ancilla in |−⟩, a CX flip becomes a −1 phase on the input state. Without the X, the ancilla is |+⟩, nothing kicks back, and you read `0000` → see lab step 4.
3. **Interference reads it out.** The second H layer maps the phase pattern (−1)^(s·x) onto exactly one basis state, |s⟩, so every shot returns `s` → see lab step 2.
4. **One query versus n.** Worked example (from `research/L200_worked_examples.py`): `1011` takes 1 quantum query and 4 classical ones; `110101` takes 1 and 6. All 16 four-bit secrets come back with probability 1.0 → see lab steps 1–2.
5. **Constants don't matter.** f(x) = s·x ⊕ 1 adds one X on the ancilla, which is only a global phase, so the answer is still `s` → see lab step 5.

## Trade-offs
| | Use when | Avoid when |
|---|---|---|
| BV pattern | Testing oracles, kickback, bit order; smoke-testing a backend (answer is certain) | Expecting a real speed-up: building the oracle already needs `s` |
| Deterministic check | Tests can assert counts == {s: shots} | Noisy hardware: assert "most frequent" instead |

## Common mistakes
- Forgetting `x` on the ancilla before H: the result is all zeros, not `s`.
- Building the oracle left to right, so the answer comes back reversed (`1101` for `1011`).
- Measuring the ancilla too, which adds a random extra bit.
