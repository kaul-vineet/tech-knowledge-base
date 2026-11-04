"""buildTask solution (lesson 16): tasks_for() spawns one SeedSequence child per replication. Otherwise identical
to the lab file.

L300 performance and scale: many replications of a help-desk queue - loop vs numpy vs worker processes.

M/M/1 at 80% load, 20,000 tickets per replication, starting empty. Mean wait per replication is the output.
The serial benchmark spawns one SeedSequence child per replication; the parallel version gets its seeds from tasks_for().
python solution/perf.py
"""
import json
import math
import multiprocessing as mp
import os
import time
from pathlib import Path

import numpy as np

LAM, MU, CUSTOMERS, SEED = 0.8, 1.0, 20_000, 16
HERE = Path(__file__).resolve().parent


def draws(seed_seq, n=CUSTOMERS):
    rng = np.random.default_rng(seed_seq)  # one independent stream per replication
    return rng.exponential(1 / MU, n), rng.exponential(1 / LAM, n)  # service times, inter-arrival gaps


def mean_wait_loop(service, gaps):
    """Reference model: Lindley's recursion, one ticket at a time in pure Python."""
    w, total = 0.0, 0.0
    for s, a in zip(service[:-1].tolist(), gaps[1:].tolist()):
        total += w
        w = max(0.0, w + s - a)
    return (total + w) / len(service)


def mean_wait_vectorised(service, gaps):
    """Same recursion without a loop: W_n = S_n - min(0, min_k S_k), S = cumulative sum of (service - gap)."""
    steps = service[..., :-1] - gaps[..., 1:]
    s = np.concatenate([np.zeros(steps.shape[:-1] + (1,)), np.cumsum(steps, axis=-1)], axis=-1)
    return (s - np.minimum.accumulate(np.minimum(s, 0.0), axis=-1)).mean(axis=-1)


def tasks_for(reps):
    """One task per replication: (replication index, the seed its worker draws from)."""
    return list(enumerate(np.random.SeedSequence(SEED).spawn(reps)))  # FIX: one child stream per replication


def one_replication(task):
    """Worker: top-level function (picklable for 'spawn'). task = (replication index, its seed)."""
    rep, seed = task
    service, gaps = draws(seed)
    return {"rep": rep, "spawn_key": list(getattr(seed, "spawn_key", ())),
            "mean_wait": float(mean_wait_vectorised(service, gaps)), "pid": os.getpid()}


def run_parallel(tasks, workers, worker=one_replication, log_path=None):
    with mp.get_context("spawn").Pool(workers) as pool:  # spawn: the default on Windows and macOS
        results = pool.map(worker, tasks)
    if log_path:  # one JSON line per replication: what ran where, with which stream
        Path(log_path).write_text("".join(json.dumps(r) + "\n" for r in results), encoding="utf-8")
    return np.array([r["mean_wait"] for r in results])


def ci(x):
    return float(np.mean(x)), 1.96 * float(np.std(x, ddof=1)) / math.sqrt(len(x))


def timed(fn):
    start = time.perf_counter()
    out = fn()
    return out, time.perf_counter() - start


def main(reps=40, workers=2):
    children = np.random.SeedSequence(SEED).spawn(reps)
    data = [draws(c) for c in children]
    loop, t_loop = timed(lambda: np.array([mean_wait_loop(s, g) for s, g in data]))
    vec, t_vec = timed(lambda: mean_wait_vectorised(np.array([s for s, _ in data]), np.array([g for _, g in data])))
    par, t_par = timed(lambda: run_parallel(tasks_for(reps), workers, log_path=HERE / "runs.jsonl"))
    print(f"{reps} replications x {CUSTOMERS:,} tickets, M/M/1 at 80% load (true mean wait 4.0 min, from empty)")
    print(f"largest difference loop vs numpy: {np.max(np.abs(loop - vec)):.1e}; numpy vs {workers} workers: "
          f"{np.max(np.abs(vec - par)):.1e}")
    print("TIMING (machine-dependent):")
    for name, t in (("python loop", t_loop), ("numpy vectorised", t_vec), (f"{workers} spawn workers", t_par)):
        print(f"  {name:18s} {t:8.3f} s   speed-up x{t_loop / t:6.1f}")
    print("mean wait %.3f +/- %.3f min" % ci(par))
    print(f"distinct replication results {len(set(par.tolist()))} of {reps} (one line each in runs.jsonl)")

if __name__ == "__main__":  # required with 'spawn': children re-import this file and must not start new pools
    main()
