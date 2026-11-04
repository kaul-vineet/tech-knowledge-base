# Concept: small Grover search

## Why it matters
Grover search is the standard example of **amplitude amplification**: it raises the probability of "good" answers that an oracle can recognise. Using it well means writing the oracle and choosing how often to repeat; too few or too many both fail.

## Mental model
Each iteration rotates the state a fixed angle 2θ toward the marked states, where sin θ = √(M/N). Stop near 90°. If you keep going, you rotate past it.

```
start (uniform) ──▶ oracle: marked × (−1) ──▶ diffusion: reflect about the mean ──▶ repeat k times
P(success) = sin²((2k+1)·θ)        N=8, M=1:  k=0 0.125 · 1 0.781 · 2 0.945 · 3 0.330
```

## How it works
1. **Phase oracle.** X on every qubit where the target bit is `0`, a multi-controlled Z, then X again. Only marked states get −1. The numpy diagonal for `011`,`100` is [1,1,1,−1,−1,1,1,1] → see lab step 1.
2. **Grover operator.** `grover_operator(oracle)` appends the diffusion (reflection about the uniform state). `.power(k)` repeats it → see lab step 2.
3. **How many iterations.** k = ⌊π / (4·asin√(M/N))⌋. Worked example (`research/L200_worked_examples.py`): N=8, M=1 gives θ = 0.3614 rad and k = 2, so P = 0.9453. One more iteration drops P to 0.3301 → see lab step 3.
4. **More marked states, fewer iterations.** With M=2 of 8, k=1 already gives 1.0, and k=2 falls to 0.25 → see lab step 3.
5. **Code decides, the model proposes.** In agent assist, a predicate written in code rebuilds the marked set and numpy recomputes P. A proposed k is overridden when it is worse → see lab step 5.

## Trade-offs
| | Use when | Avoid when |
|---|---|---|
| Grover / amplitude amplification | Good answers are rare (M ≪ N), checkable by a reversible oracle, and you know or can bound M | M ≥ N/2 (no gain: P stays 0.5 for 2 of 4), or M is unknown and you cannot estimate it |
| Small-n simulator demos | Learning, testing oracles | Expecting a speed-up: multi-controlled Z depth grows fast on noisy hardware |

## Common mistakes
- Writing marked strings with q0 first. Qiskit writes q0 rightmost, so `110` is not `011`.
- Assuming more iterations is always better (overshooting).
- Reusing the k for one marked state after the oracle starts marking several.
