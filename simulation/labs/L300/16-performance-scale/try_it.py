"""tryIt experiments for lesson 16 (run: python try_it.py)."""
import numpy as np

import perf

if __name__ == "__main__":  # spawn-safe: the pools below re-import this file in every child
    # 1. Same 12 replications on 1, 2 and 3 workers. Predict: identical results, or different?
    tasks = list(enumerate(np.random.SeedSequence(perf.SEED).spawn(12)))  # one child stream per replication
    runs = {w: perf.run_parallel(tasks, w) for w in (1, 2, 3)}
    print("1 vs 2 vs 3 workers bit-identical:", all(np.array_equal(runs[1], r) for r in runs.values()),
          "| mean wait %.3f min" % runs[1].mean())

    # 2. The NumPy docs' UNSAFE pattern: seed = root + worker_id. Run once with root 16, then 'a new run' with root 17.
    a = [perf.draws(np.random.SeedSequence(16 + i), n=1_000)[0][0] for i in range(8)]
    b = [perf.draws(np.random.SeedSequence(17 + i), n=1_000)[0][0] for i in range(8)]
    print(f"root+id seeding: {len(set(a) & set(b))} of 8 replications of run B repeat run A")
    c = [perf.draws(s, n=1_000)[0][0] for s in np.random.SeedSequence(17).spawn(8)]
    print(f"SeedSequence(17).spawn(8): {len(set(a) & set(c))} of 8 repeat run A")
