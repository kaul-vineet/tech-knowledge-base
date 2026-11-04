**Concept: global sensitivity analysis (OAT, Morris screening, Sobol' indices)**

## Why it matters
Before you spend money measuring inputs, or drop inputs to simplify a model, you need to know which ones drive the output. The usual quick answer is to wiggle one input at a time around a nominal point. That answer is local. It can miss an input whose effect depends on another, such as open windows, which only matter when it is warmer or colder outside than inside.

## Mental model
Ask how much of the output's spread would vanish if you knew this input exactly, averaged over everything else.

```
Var(E) = V_out + V_occ + V_light + V_window×out
         └ S1: alone ┘                └ interaction
ST_window = (V_window + V_window×out) / Var(E)   (alone + every interaction)
```

## How it works
1. **One-at-a-time (OAT).** Swing each input over its range with the others at nominal. It is cheap (2d runs) and blind to anything that is zero at the nominal point → see lab step 2.
2. **Morris screening.** Use r random trajectories on a grid, moving one input per step. μ* (mean absolute elementary effect) ranks importance, and a large σ flags nonlinearity or interaction. It costs r(d+1) runs → see lab step 3.
3. **Sobol' indices.** Use two sample matrices A and B, plus d matrices ABᵢ (A with column i taken from B), for N(d+2) runs. First order: Sᵢ ≈ mean(f_B·(f_ABᵢ − f_A))/Var (Saltelli 2010). Total order: STᵢ ≈ ½·mean((f_A − f_ABᵢ)²)/Var (Jansen) → see lab step 4.
4. **Read S1 against ST.** ST − S1 is the input's share in interactions, and 1 − ΣS1 is the variance from all interactions → see lab step 4.
5. **Screen with ST.** An input with small ST can be frozen at nominal. Check it by measuring how much output variance the reduced model keeps → see lab step 5.
6. **Report uncertainty.** Bootstrap the N rows for intervals, and claim an order only where the intervals separate → see lab step 9 (stretch).

**Worked example (lab run):** analytically Var(E) = 3,793.3 (kWh/day)², with ST_window = 0.152 and S1_window = 0. OAT gives window_open a swing of 0.0 kWh/day and ranks it last. Morris gives μ* = 100.8 with σ = 107.4, a clear interaction flag. Sobol', with N = 8,192 and 49,152 runs, estimates ST = 0.155 and S1 = 0.005. Keeping the OAT top two (outdoor, occupants) preserves 84.1% of the variance; the ST top two (outdoor, window) preserve 96.1%.

## Failure modes
- **OAT's nominal point decides the answer.** At 26 °C outside, the same window swings 96 kWh/day (tryIt 1). Nothing tells you which nominal is right.
- **Too few runs.** At N = 32 the bootstrap intervals for window_open and occupants overlap, so the order is noise.
- **Correlated inputs.** Sobol' indices assume independent inputs and are misleading otherwise.
- **Small negative S1 estimates** (lights −0.001 at N = 4,096 before centring) are sampling noise, not physics.

## Common mistakes
- Calling the OAT "tornado chart" a global sensitivity analysis.
- Ranking by S1 alone, which hides inputs that act only through interactions.
- Screening inputs out without re-running the reduced model to check what it lost.
