# Simulation — concepts primer (read before lesson 1)

## What simulation is for
Simulation answers engineering questions by running a model of a system instead of the system itself: "How many workers keep p90 wait under a minute?", "How fast does this parcel land?", "How likely is the release to slip?". Typical uses:
- **Capacity planning:** queues for checkouts, call centres, API worker pools (SimPy).
- **Risk and estimation:** Monte Carlo schedules and cost ranges (numpy).
- **Physical behaviour:** motion, heat, control loops (SciPy `solve_ivp`, Modelica/OpenModelica, FMI/FMPy).
- **Many interacting individuals:** traffic, evacuation, epidemics (Mesa, NetLogo).

## One mental model
Every simulation is **state + a rule for how state changes + a clock + an experiment around it**. The four L100 styles differ only in the clock:

```
              ┌───────── experiment: seeds, replications, parameter sweeps ─────────┐
              │                                                                      │
 inputs ──> model state ──rule──> new state ──> outputs ──> estimate ± uncertainty
              ▲            │
              └── clock ───┘   Monte Carlo : no clock, independent samples
                               Discrete-event: jump to next event (heap)
                               Time-stepped : advance by dt
                               Agent-based  : every agent acts each tick
```
Verification asks whether the code implements the rule; validation asks whether the outputs are close enough to reality, or to a trusted result, for the question asked.

## Concept map
| Level | Core concepts | Local agent (code stays the judge) |
|---|---|---|
| **L100** run it | Monte Carlo + confidence intervals; event list and clock jumps; Euler vs RK4 step error; agents and emergence; seeds, unit tests, analytic checks, one-parameter sensitivity | Proposes a sweep; code validates, runs, checks quoted numbers (lesson 6) |
| **L200** build it | Fitting input distributions (MLE, KS, Q-Q); c-server resources and Erlang C; adaptive ODE solvers, tolerances, stiffness; warm-up, replications, CIs; (s, S) inventory with common random numbers | Proposes an input distribution and explains the fit table; code fits, decides by KS and checks quoted numbers (lesson 7) |
| **L300** harden it | Variance reduction; calibration + holdout; Morris/Sobol' sensitivity; FMI co-simulation step stability; vectorised, reproducible parallel runs | Ranks inputs; code checks against Sobol' ST (lesson 14) |
| **L400** design it | Twins (Kalman + CUSUM); OCBA optimisation; guarded surrogates; checkpointed sweeps; checked model cards | Drafts card text, explains staffing; code checks (21, 22) |
| **L500** rigour | Probability, numerics and RNG proofs; ethics; readings | - |

## Glossary
| Term | Meaning |
|---|---|
| model | Simplified, runnable description of a system for one question |
| state | Variables that describe the system now (queue length, height) |
| seed | Starting value that makes a random stream repeatable |
| replication | One independent run with its own seed |
| confidence interval | Range likely to contain the true mean (mean ± 1.96·s/√N) |
| event list | Future events ordered by time |
| time step (dt) | How far a time-stepped model advances per update |
| agent | Individual with state and a behaviour rule |
| emergence | Global pattern not written in any individual rule |
| verification / validation | Code matches model / model matches reality for its purpose |

## Common misconceptions
1. **"More decimal places means more accurate."** Monte Carlo error falls only like 1/√N, and no N fixes wrong input distributions.
2. **"If the tests pass, the model is right."** Tests verify the code; only comparison with data or a trusted result validates the model.
3. **"A smaller time step is always enough."** It helps Euler slowly (error ∝ dt); a better method (RK4, adaptive solvers) is often the real fix, and round-off grows with step count.
