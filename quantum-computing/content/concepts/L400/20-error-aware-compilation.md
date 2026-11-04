# Concept: Error-aware compilation

## Why it matters
Real devices are uneven. Two-qubit error rates differ several-fold between couplers, readout differs between qubits,
and the numbers drift from day to day. A compiler that maps qubits blindly can route the busiest interactions over the
worst coupler, and that alone can cost more fidelity than every other choice combined. Compilation is also where depth
is won or lost: every SWAP adds three CX gates and stretches the circuit past its coherence budget.

## Mental model
Compilation is three decisions plus a score.

```
logical circuit ─▶ layout ─────────▶ routing ───────────▶ optimisation ─▶ physical circuit
 (5 qubits,        which physical     SWAPs along a path:    cancel CX·CX,   score: ESP = Π(1 − error),
  12 CX, depth 17)  qubit for each     shortest or most       resynthesis     CX count, depth ≤ budget
                    logical one        reliable (−log(1−e))
```

ESP, the estimated success probability, multiplies (1 − error) over every gate and measurement (Nishio et al. 2020).
It is pessimistic in absolute terms, because not every error changes the output. It is cheap, though, and it ranks
options the way a full noisy simulation does: in the lab, ESP 0.2084 versus 0.7835 matched simulated output
fidelities of 0.8959 versus 0.9878.

## Design space
- **Trivial layout + hop-count routing** (Qiskit level 0 style). Predictable, fast, and blind to errors.
- **Connectivity-based layout + cancellation** (DenseLayout, levels 1–2 style). It places busy qubits on
  well-connected hardware and removes back-to-back CX pairs, but it still ignores the error map.
- **Noise-aware layout + reliability-weighted routing** (level 3 style; VF2PostLayout rescoring with the target's
  error rates). Better results, at the cost of compile time that grows quickly with qubit count. The lab brute-forces
  all 8P5 = 6720 placements.

Forces: fidelity versus depth, which a SWAP along a reliable path can trade; compile time versus quality; and
freshness, because a layout is only as good as today's calibration.

## How to decide
Score every option by ESP, CX count and depth on today's calibration. Accept only compilations within the depth
budget (22 layers here, the logical 17 plus room for one SWAP). Prove noiseless equivalence before trusting any score.

Worked example (8-qubit ladder, lesson 14's 5-node QAOA, edge (1,2) drifted to 15 %):

| Option | Calibrated ESP / CX / depth | Drifted ESP / CX / depth |
|---|---|---|
| A trivial | 0.5763 / 27 / 32 | 0.2084 / 27 / 32 |
| B degree-based + cancel | 0.7315 / 19 / 24 | 0.3059 / 19 / 24 |
| C noise-aware | 0.7925 / 13 / 18 | 0.7835 / 19 / 21 |

Only C meets the depth budget, and it survives the drift by routing around the bad edge. Recorded in ADR 0001,
guarded by a fitness test that rejects depth above 22, ESP below 0.75 or any change to the noiseless output.

## Failure modes at scale
- **Stale calibration.** A layout chosen yesterday uses today's bad edge. The signal: ESP from the current error map
  drops while the circuit is unchanged. Recompile on calibration change (try it 1 moves the layout away from a newly
  drifted (5,6) edge).
- **Search explosion.** Brute force is 6720 candidates for 5 of 8 qubits and impossible at 50 of 127. Switch to
  subgraph isomorphism (VF2) or SABRE-style heuristics and sample candidates (the capstone samples 200).
- **Infeasible budgets.** On a ladder, a triangle needs at least one SWAP. Demanding depth 17 fails loudly (try it 2)
  instead of silently returning depth 21.
- **Correlated errors.** Crosstalk and leakage are not in a per-gate product. ESP can then rank options wrongly;
  validate against measured results.

## Common mistakes
- Comparing compilations by depth alone. A shallower circuit on a bad coupler can be the worse choice.
- Trusting a router without an equivalence check. A SWAP bookkeeping bug produces plausible-looking wrong answers.
- Optimising once and caching forever. Cache per calibration snapshot, which lesson 17's key includes in the target.
