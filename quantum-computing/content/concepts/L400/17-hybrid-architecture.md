# Concept: Hybrid quantum-classical architecture

## Why it matters
Every useful near-term quantum program is a loop: a classical optimiser proposes parameters, a quantum backend runs
circuits, and the results steer the next proposal. On a laptop simulator that loop costs milliseconds. On a shared
device each job waits in a queue, every new circuit structure has to be compiled for the target, and jobs sometimes
fail and must be retried. The architecture around the loop, not the circuit, decides whether a run takes one minute
or ten, and whether you pay for seconds of device time or for a reserved window.

## Mental model
Separate three concerns. The optimiser only sees "evaluate these circuits". The orchestrator owns the job queue
policy, the transpile cache and retries. The backend adapter hides the provider behind a small interface:
transpile, run, and optionally open or close a session.

```
optimiser ──circuits──▶ orchestrator ──jobs──▶ backend adapter ──▶ simulator | cloud QPU
  (SPSA)    ◀─values──   cache · retries · mode   transpile / run / session
```

Because circuits carry their own seeds, the execution mode is invisible to the optimiser: in the lab the sync loop,
batched jobs and a session all end at the same ratio, 0.6922. This is an architecture property worth testing.

## Design space
- **Synchronous loop.** One job per circuit. Simplest to write and debug, and it maps directly onto most tutorials.
  It pays the queue wait once per circuit.
- **Batched jobs.** One job per optimiser step, carrying every circuit of that step. Qiskit Runtime's batch mode and
  a primitive call with several parameter sets (PUBs) are the same idea. It needs an optimiser whose step produces
  several independent circuits, such as SPSA's ± pair, multi-start searches or gradient components.
- **Session.** A reserved window: jobs after the first skip the queue, but you are billed for the window, including
  your classical think time, and it expires after an interactive time-to-live. IBM's documentation adds that sessions
  give no benefit for a single job, and that Open Plan users cannot open them.

Two forces cut across all three designs. The **transpile cache** must key on circuit structure, target and compiler
settings, never on bound parameter values. **Retries** must be idempotent: the same circuit seed must give the same
samples, so a retried job cannot change the optimiser's path.

## How to decide
Measure the same workload under each design with a fake clock, so the numbers are deterministic. Criteria: modelled
wall time, billed device time, number of jobs and transpiles, and sensitivity to queue length and classical step time.

Worked example (`solution_cache_key.py`, 4 starts × 30 SPSA iterations = 240 circuits, 2 s queue, 0.5 s transpile):
the sync loop takes 486.8 s, batched jobs 66.8 s, a session 11.7 s. Billed time is 4.8 s for the first two and 11.7 s
for the session. With the naive cache key, every design transpiles 240 times, and batched jobs rise to 186.3 s.
The decision (ADR 0001) is batched jobs by default, with sessions as an opt-in for interactive work. Try it 1 shows why
the decision must be re-checked when conditions change: with a 30 s queue, batched jobs take 906.8 s and a session
takes 39.7 s.

## Failure modes at scale
- **Queue-dominated wall time.** If jobs × queue ≫ execution, the signal is a large gap between wall time and billed
  time in the JSON lines. Batch more per job, or consider a session.
- **Batch limits.** Providers cap circuits per job (`max_circuits`). The adapter raises before submitting; the fix is
  chunking, which costs one more queue wait per chunk.
- **Session expiry.** If a classical step exceeds the interactive TTL (try it 2: 70 s versus 60 s), every job queues
  again while the bill keeps running: 2165.3 s billed for no gain in wall time.
- **Cache growth.** Adaptive ansätze create new structures every iteration. A hit rate falling below ~0.99 is the signal.

## Common mistakes
- Putting parameter values in the cache key, so nothing is ever reused.
- Retrying with fresh randomness, so a transient failure silently changes the result.
- Choosing a session because it is "faster" without counting what the open window costs.
