# Concept: transpiling to a device layout

## Why it matters
Hardware runs only its **basis gates**, on qubit pairs that are physically linked (the **coupling map**). The transpiler rewrites your circuit to fit. Every added two-qubit gate costs fidelity, so measure what it did.

## Mental model
Transpiling is compiling for a target: place virtual qubits on physical ones (layout), insert SWAPs for unlinked pairs (routing), translate to basis gates, optimize. Behaviour stays; cost changes.

```
your circuit ─▶ layout ─▶ routing (+SWAP = 3 CX) ─▶ basis (rz, sx, x, cx) ─▶ optimize (level 0–3)
line:      0─1─2─3─4          star CX(0,2),(0,3),(0,4) not linked → routing
heavy-hex: 19 qubits (d=3), every qubit ≤ 3 neighbours
```

## How it works
1. **Basis translation keeps the unitary.** H = RZ(π/2)·SX·RZ(π/2) up to a global phase of −1/8 turn, and X = SX·SX → see lab step 1.
2. **Routing costs CX.** A SWAP is 3 CX. Worked example (`research/L200_worked_examples.py`): the 5-qubit GHZ star has 3 CX pairs that are not on a line, 2 on a ring and 0 all-to-all. `CouplingMap.from_heavy_hex(3)` has (5·9 − 6 − 1)/2 = 19 qubits → see lab steps 1 and 3.
3. **Measure before and after.** Compare `depth()`, the two-qubit count and the two-qubit depth (`depth(lambda i: i.operation.num_qubits == 2)`) per coupling map and per optimization level → see lab steps 2–3.
4. **Levels trade compile time for gates.** Level 0: trivial layout, no optimization. Levels 1–3 search layouts and cancel or resynthesise gates. `seed_transpiler` makes the stochastic parts repeatable → see lab step 3.
5. **Check behaviour, not text.** The transpiled GHZ must still give only `00000` or `11111` → see lab step 4.

## Trade-offs
| | Use when | Avoid when |
|---|---|---|
| Level 0 | Debugging, hardware characterization, seeing raw routing cost | Production runs |
| Level 2 (default) / 3 | Real targets; level 3 for small, deep circuits | Huge circuits where compile time dominates |
| Rewriting for the map (chain, not star) | Known topology; beats any router | Code for unknown devices |
| GenericBackendV2 | Offline tests, CI | Calibrated error estimates |

## Common mistakes
- Comparing total depth only; two-qubit count and depth matter most.
- Forgetting `seed_transpiler`, then chasing counts that change between runs.
- Reading physical qubit indices as your own; use the layout (measured bits are mapped back).
