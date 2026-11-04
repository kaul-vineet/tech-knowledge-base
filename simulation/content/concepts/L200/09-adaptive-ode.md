**Concept: adaptive ODE solvers, tolerances and stiffness**

## Why it matters
A fixed time step wastes effort where nothing happens and loses accuracy where everything does. SciPy's `solve_ivp` picks its own steps from a tolerance. You need to know what that tolerance controls, and when a different kind of solver is needed.

## Mental model
A careful driver who estimates the error of every move: long strides on straight roads, short ones in bends, and backing up to retry when a move went wrong.

```
step h ─> 5th-order y_new + error estimate e
          e <= 1 ? accept, grow h : reject, shrink h
          next h = h · 0.9 · e^(-1/5)   (x0.2 .. x10)
```

## How it works
1. **Embedded pair.** Dormand–Prince computes a 5th-order and a 4th-order answer from the same stages. Their difference is the error estimate → see lab step 2.
2. **Tolerance scale.** The error is divided by atol + rtol·|y| and combined as an RMS. Tighter rtol means more steps and less error → see lab step 2.
3. **Step control.** Error scales like h⁵, so the next step is h·0.9·e^(−1/5). For example, e = 0.5 gives ×1.03, and e = 4 gives ×0.68 plus a retry → see lab step 3.
4. **Stiffness.** When the fastest time constant is tiny but the solution moves slowly, stability limits an explicit method's step, not accuracy. Implicit methods avoid that limit → see lab step 4.

**Worked example (lab run):** an RC filter with τ = 1 ms, run for 10 s. Explicit RK45 needed 3,027 steps at rtol 1e-3 and 3,586 at 1e-6. That is an average step of 3.3 ms ≈ 3.3τ, whatever the tolerance. Backward Euler with dt = 10 ms took 1,000 steps and matched the exact −0.83961.

## Trade-offs
| Solver | Use when | Avoid when |
|---|---|---|
| Explicit adaptive (RK45) | Non-stiff: motion, cooling, populations | Step counts explode at any tolerance |
| Implicit (Radau, BDF) | Stiff: fast circuits, chemistry | Cheap non-stiff problems |
| Fixed-step RK4 | Real-time loops with a constant cost per tick | You need guaranteed accuracy |

## Common mistakes
- Setting rtol while leaving atol larger than the values you care about.
- Tightening tolerances to "fix" a stiff problem. Only the run time changes.
- Skipping an invariant or exact check. The predator–prey invariant drifted 0.14 at rtol 1e-3.
