# Concept: QAOA on MaxCut

## Why it matters
QAOA is the standard example of a quantum heuristic for combinatorial optimisation. MaxCut stands in for scheduling, clustering and partitioning problems. The quantum circuit is short. The hard part is the classical loop around it: choose angles, avoid bad local minima, and prove the answer is any good. For small graphs you can brute-force the optimum, so every QAOA result can be graded.

## Mental model
Prepare all bitstrings in superposition, then alternate two layers p times. The cost layer adds a phase proportional to each bitstring's cut size. The mixer layer (RX on every qubit) moves amplitude between bitstrings. A classical optimiser tunes the 2p angles (γ, β) to maximise the expected cut ⟨C⟩.

```
|+>^5 ─▶ [ e^{-iγ1 C} ─ RX(2β1)^⊗5 ] ─▶ [ e^{-iγ2 C} ─ RX(2β2)^⊗5 ] ─▶ measure ─▶ cut sizes
           cost (diagonal)  mixer             p = 2 layers         ratio = <C> / brute-force max
```

## How it works
1. **Brute force first.** 2⁵ = 32 bitstrings. The IBM tutorial's 6-edge graph has maximum cut 5, reached by `01001`, `01011`, `10100` and `10110` → see lab step 1.
2. **Cost layer.** C = Σ(1 − ZᵢZⱼ)/2 over edges, so e^{−iγC} is one RZZ(−γ) per edge up to a global phase. On a simulator it is just a phase vector over the 32 basis states → see lab steps 1–2.
3. **Landscape.** For p = 1, a 41×21 grid over γ ∈ [0, π], β ∈ [0, π/2] finds γ = 0.6283, β = 0.3927 with ratio 0.8188. Local descent from there reaches 0.822 → see lab step 2.
4. **Local optimisers find the nearest basin.** Worked example (`qaoa_lab.py`): p = 2 from random seed 0 converges to ratio 0.7002, worse than p = 1. Of 8 random starts, only 2 reach 0.9247 → see lab steps 3 and 5.
5. **Warm start and restarts.** Interpolate the p = 1 answer into [γ/2, γ, β, β/2], add three seeded random starts and keep the best. p = 2 then reaches 0.9247 every time → see lab step 6.
6. **Read samples, not only ⟨C⟩.** At the p = 2 optimum, P(any optimal cut) = 0.707. 20 shots contained 13 optimal cuts, so the best sample was optimal → see lab steps 4–5.

## Failure modes
- **Stuck in a local minimum.** The gradient is zero there, so the optimiser reports success at ratio 0.70. Only a grid, restarts or brute force reveal it; log the ratio of every start.
- **Deeper looks worse.** p = 2 should never be worse than p = 1 (set the extra angles to 0). If it is, the optimiser failed, not the circuit.
- **Large learning rate.** Steps of half a radian jump between basins. Our first p = 1 run dropped from 0.8188 to 0.7841 that way before the rate was lowered to 0.05.

## Common mistakes
- Reporting ⟨C⟩ as "the answer". The answer is the best sampled bitstring; ⟨C⟩ is an average over all of them.
- Comparing QAOA with nothing. Brute force solves 5 nodes instantly; larger graphs have strong classical heuristics.
- Ignoring periodicity. The angles repeat, so bound the search (IBM's tutorial uses β ∈ [0, π], γ ∈ [0, 2π]).
