# Capstone: an end-to-end quantum optimisation service

## Overview
The capstone turns the topic into one small service. A client posts a MaxCut request. The service decides whether a
quantum path is even possible, runs a noisy QAOA on the simulator next to classical solvers at the same budget, and
lets code pick the winner. It then returns a report that a local model may explain, but never change. Everything runs
here with seeded faults: two failing backend jobs, a drifted coupler and readout errors. `run_capstone.py` prints a
scorecard of six milestones and six rubric lines. All of them pass, and the winner for the default request is
simulated annealing.

## Architecture walkthrough
`architecture.mmd` draws the flow.

1. **API** (`service.py`): POST /solve on 127.0.0.1. Invalid input, such as n = 30, returns HTTP 400 before any work.
2. **Feasibility gate** (lesson 19): a resource estimate plus a device-size check. A 12-node request is answered
   classically with the reason "needs 12 qubits > 8 on the device".
3. **Orchestrator** (lesson 17): batched jobs, a structural transpile cache and idempotent retries. Per request: 10
   jobs, 1 transpile, 2 retries, 28.8 s modelled wall time. Results are identical to a fault-free run.
4. **Backend adapter** (lessons 12 and 20): `NoisyBackend` subclasses the simulator adapter. It routes the circuit on
   the fake ladder with a noise-aware layout search (ESP 0.5072, 52 CX, depth 42, within the 60-layer budget) and
   samples from a white-noise-plus-readout model. That model is within TVD 0.0213 of lesson 20's density-matrix
   simulation, against 0.073 for the ideal distribution.
5. **Mitigation** (lesson 13): tensored readout calibration and constrained least squares move the ⟨C⟩ estimate from
   6.774 to 6.8549, next to the gate-noise-only value of 6.8418. The remaining gap to the ideal 7.3525 is gate noise,
   which readout mitigation cannot remove.
6. **Fair benchmark and decision** (lesson 18): greedy, annealing and QAOA get 2000 samples and the same 5 seeds. All
   three find the optimum cut of 10; annealing needs 13 samples, greedy 32 and QAOA 1013. Code decides; ties would go
   classical.
7. **Agent assist**: the explanation is checked for the winner's name, every number and hype. The "quantum advantage"
   pitch is rejected.

## How it ties L100–L400
- L100 gave the vocabulary: shots, counts, seeds, Bell-pair checks and portable circuits.
- L200 built and transpiled circuits; their routing ideas return in the compiler.
- L300 broke things on purpose: noise models, mitigation under small budgets, restarts and shot-noise-aware
  optimisers, and baselines against hype.
- L400 made design decisions under constraints: execution modes, honest benchmarks, resource and feasibility gates,
  noise-aware compilation, and crypto migration.

The capstone imports those labs instead of copying them, so every component keeps its own tests. Its four ADRs record
the service-level decisions, and its fitness tests keep them true.

The result is deliberately unglamorous. For the problem sizes a simulator can hold, a classical solver wins, and the
service says so with evidence. When hardware, problem size or noise change, the same harness will tell you whether
the answer changes.
