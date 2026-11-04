**Concept: the simulation workbench**

## Why it matters
A colleague reruns your capacity simulation and gets a different answer. Was it a bug, a library upgrade, or just different random numbers? Without pinned versions and seeds you cannot tell.

## Mental model
A workbench is an interpreter, a random-number source and one tool per modelling style. Same inputs + same seed + same versions = same output.

```
model code ─┐
seed ───────┼─> Python 3.12 + numpy ──> results (repeatable)
pins ───────┘      ├─ SimPy  : discrete events
                   ├─ SciPy  : ODE solvers
                   └─ Mesa   : agents
```

## How it works
1. **Local core:** Python 3.12 and numpy run every main lab; SimPy, SciPy and Mesa are library equivalents pinned in `requirements.txt` and run in CI → see lab step 1.
2. **Pins:** `==` versions (numpy 2.5.3, simpy 4.1.2, scipy 1.18.1, mesa 3.5.1) make every machine run the same code → see lab step 2.
3. **Seeds:** a seeded generator replays the same stream. `default_rng(42)` starts 0.773956, 0.438878, 0.858598, matching NumPy's documentation example → see lab step 3.

## Common mistakes
- Seeding a generator but drawing from a different, unseeded one elsewhere.
- Comparing results across library upgrades: NumPy states `Generator` has no cross-version stream guarantee.
- Using simulation randomness for passwords or tokens; use `secrets`.
