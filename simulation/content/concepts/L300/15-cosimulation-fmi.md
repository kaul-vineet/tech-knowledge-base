**Concept: co-simulation with FMI (units, master algorithm, communication step)**

## Why it matters
Real systems are modelled by different teams in different tools: the building physics in Modelica, the controller in C, the occupancy in Python. Co-simulation runs them together without merging the code. Each model is packaged as a unit with its own solver. A master algorithm advances all units in steps and exchanges signals between them. The step at which they talk becomes a new source of error, and it can make a stable system look unstable.

## Mental model
Two people on walkie-talkies who may only speak every h seconds. If h is too long, each reacts to old news, and a heating controller overshoots back and forth.

```
t_i ──h──► t_i+1          master: get outputs → set inputs → do_step(t_i, h) on every unit
 room:  T(t_i) ─────────► RK4 inside, heater held constant (zero-order hold)
 ctrl:  heater(t_i) ────► PI acts on T(t_i): one step old
```

## How it works
1. **FMU.** A ZIP with modelDescription.xml (variables, value references, causality) plus binaries or C sources. FMI 2.0 and 3.0 (3.0.2 current) define Model Exchange and Co-Simulation, and 3.0 adds Scheduled Execution → see lab step 2.
2. **Unit lifecycle.** instantiate → setup experiment → enter/exit initialization mode → set/get by value reference → do_step(t, h) → terminate. FMPy's FMU2Slave uses the same calls → see lab step 2.
3. **Master algorithm.** A fixed-step Jacobi master reads all outputs at tᵢ, sets inputs, then steps every unit. Gauss–Seidel steps one unit first and passes the fresh value on → see lab step 3.
4. **Coupling delay.** Inputs are held constant over h, so feedback lags by up to one step. A high-gain loop with too large an h oscillates or diverges → see lab step 4.
5. **Observe the exchange.** Log one JSON line per communication step and compute health metrics (swing, on/off flips) from the log → see lab steps 3-4.
6. **Fix.** Use a smaller h, Gauss–Seidel ordering, a lower controller gain, or adapt h (stretch task) → see lab step 5.

**Worked example (lab run):** room τ = R·C = 1 h, loop gain K = Kp·Q·R = 0.5 × 3,000 W × 0.008 K/W = 12. With a one-step delay the loop is stable only if (1 − e^(−h/τ))·K < 1, i.e. h < τ·ln(12/11) = 313 s. The lab settles at 240 s (swing 0.01 °C) and oscillates from 300 s (1.57 °C). At 900 s the heater flips 9 times and the room swings 6.78 °C. Gauss–Seidel raises the bound to τ·ln(13/11) = 601 s: stable at 450 s, still unstable at 900 s.

## Failure modes
- **Communication-step instability.** It looks like a bad controller, but the plant and controller are both fine.
- **Algebraic loops.** Direct feedthrough on both sides has no consistent order of exchange.
- **Solver mismatch inside the FMU.** OpenModelica's default co-simulation FMU takes one forward-Euler step per communication step.
- **Silent unit errors.** Check every FMI status; never ignore a non-OK return.

## Common mistakes
- Picking h for speed without a stability check against the fastest loop.
- Changing the master's ordering and assuming the results are unchanged.
- Validating the coupled run only by eye instead of logged metrics with thresholds.
