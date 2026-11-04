# 1. One HTTP service, batched jobs behind a backend adapter

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py::test_execution_budget` and milestone M2.

## Context
Lesson 17 measured, for the same SPSA workload, 486.8 s (sync loop), 66.8 s (batched) and 11.7 s (session, billed for
its whole window) of modelled wall time. The capstone must also survive transient backend failures and swap the ideal
simulator for a noisy one without touching the optimiser.

## Decision
`service.py` exposes POST /solve on 127.0.0.1; it validates and hands the request to `pipeline.solve`. The quantum path
uses lesson 17's Orchestrator in batched mode with the structural transpile cache and retries, talking to a
`NoisyBackend` that subclasses the simulator adapter and overrides only `transpile()` and `sample()`.

## Consequences
- Observed per request: 10 jobs, 1 transpile, 2 retries for the 2 injected failures, 28.8 s modelled wall.
- Results with and without the injected failures are identical (per-circuit seeds).
- A real provider plugs in as another adapter; queue times then come from the provider, not the FakeClock.
