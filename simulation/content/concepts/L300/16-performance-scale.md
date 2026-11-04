**Concept: performance and scale (vectorisation, processes, parallel random streams)**

## Why it matters
Variance reduction (lesson 12) and sensitivity analysis (lesson 14) multiply run counts. Fifty thousand model runs are routine. Two levers make that affordable: do more work per Python instruction (vectorise) and use more cores (processes). Parallelism adds a quiet risk. If the workers draw the same random numbers, you get many identical runs and an absurdly tight confidence interval that looks like precision.

## Mental model
Vectorising is one long assembly line instead of a person carrying parts. Parallel replications are several lines, each needing its own non-overlapping supply of random numbers.

```
SeedSequence(16)
   ├─ spawn → child 0 → replication 0 ─┐
   ├─ spawn → child 1 → replication 1 ─┼─► any worker, any order → same results
   └─ spawn → child 39 → replication 39┘
```

## How it works
1. **Vectorise the model.** Lindley's recursion W(n+1) = max(0, W(n) + S(n) − A(n+1)) has the closed form W(n) = Sₙ − min(0, minₖ Sₖ) over the cumulative sum S. In numpy that is `cumsum` plus `minimum.accumulate`, with no Python loop → see lab step 2.
2. **Verify before timing.** Loop and vectorised results must agree to round-off (9.1e-14 here) before any speed-up counts → see lab step 2.
3. **Time honestly.** Use `time.perf_counter`, the same work, and a printed table. Timings depend on the machine → see lab step 3.
4. **Processes, spawn-safe.** `spawn` is the default start method on Windows and macOS. Children re-import your file, so the worker must be a top-level function and pool creation must sit under `if __name__ == "__main__":` → see lab step 4.
5. **Streams per replication.** `SeedSequence(root).spawn(n)` gives independent children (collision probability about n²·2⁻¹²⁸). Tie child i to replication i, not to a worker → see lab steps 5-6.
6. **Log what ran where.** One JSON line per replication (rep, spawn_key, result, pid) makes duplicated streams obvious → see lab step 5.

**Worked example (lab run):** 40 replications × 20,000 tickets is 800,000 Lindley steps. The numpy version was 10-26× faster than the Python loop across two runs on this machine. Two spawn workers were slower than numpy because process start-up dominates on a 1-CPU sandbox. With a shared seed, all 40 replications are identical: "4.240 ± 0.000 min". With spawned children: 4.042 ± 0.118 min, bit-identical on 1, 2 or 3 workers.

## Failure modes
- **Shared seed.** Identical replications give a zero-width CI. Look for repeated values in the log.
- **seed = root + worker_id.** The next run with root + 1 reuses 7 of 8 streams (tryIt 2). The NumPy docs call this unsafe.
- **Missing main guard.** Under spawn, every child tries to start its own pool, and the run fails or hangs on Windows and macOS.
- **Tiny tasks.** Pickling and start-up overhead exceeds the work. Chunk the replications (stretch task).

## Common mistakes
- Parallelising before vectorising, which multiplies slow code by the core count.
- Seeding per worker, so results change with the worker count.
- Reporting a speed-up measured on one machine as a property of the code.
