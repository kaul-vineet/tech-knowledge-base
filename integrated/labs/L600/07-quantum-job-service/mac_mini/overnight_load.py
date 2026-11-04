"""Experiment 3 / overnight - the project's load test at fleet scale and over many seeds (one process per seed).

python mac_mini/overnight_load.py --here                       2 seeds x 240 jobs, fleets of 3 and 6 backends
python mac_mini/overnight_load.py --seeds 40 --jobs 5000 --copies 1 2 4      the overnight run (Mac mini, all cores)

A fleet of 'copies' x 3 backends = backends.fleet() plus renamed copies (same calibrations, latency, slots, failure
rates; separate random streams). Arrival rate scales with the fleet (0.8 jobs/s x copies) so every size runs at the
same offered load per backend. Everything else is loadtest.run() unchanged: the flaky-backend outage, slow chunks
that outlive their lease, client retries, recalibrations, the fenced ledger and the cache.
Per (copies, seed) one JSON line; per copies a summary with the worst p95 and the pass rate of the three
fitness functions the scorecard uses (shots exact, no cache crossing, p95 queue <= 30 s).
"""
import argparse
import multiprocessing as mp
import statistics
import sys
import time

import _mac

KEYS = ("jobs", "completed", "shots_exact", "contract_violations", "cache_crossings", "lease_expiries",
        "rejected_commits", "breaker_opens", "p95_queue_s", "max_queue_s", "ci95_coverage", "makespan_s")


def one(args):
    copies, seed, jobs = args
    import backends as bk
    import loadtest
    original = bk.fleet

    def fleet(s=7):
        base = original(s)
        out = list(base)
        for c in range(1, copies):
            out += [bk.Backend(f"{b.name}-{c}", dict(b.cal), b.latency_s, b.slots, b.fail_rate, b.slow_rate,
                               b.slow_factor, seed=s + 1000 * c) for b in original(s)]
        return out
    loadtest.bk.fleet = fleet
    t0 = time.perf_counter()
    try:
        m = loadtest.run(jobs=jobs, rate=0.8 * copies, seed=seed)
    finally:
        loadtest.bk.fleet = original
    row = {"copies": copies, "backends": 3 * copies, "seed": seed, "wall_s": round(time.perf_counter() - t0, 1),
           **{k: m[k] for k in KEYS}}
    row["fitness_pass"] = (m["shots_exact"] == m["jobs"] and m["cache_crossings"] == 0
                           and m["p95_queue_s"] <= m["budget_p95_s"])
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=5000)
    ap.add_argument("--copies", type=int, nargs="+", default=[1, 2, 4])
    ap.add_argument("--workers", type=int, help="default: mac_profile workers (performance cores)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    seeds, jobs, copies = (range(7, 9), 240, [1, 2]) if a.here else (range(7, 7 + a.seeds), a.jobs, a.copies)
    workers = 1 if a.here else (a.workers or _mac.profile(None)["workers"])
    tasks = [(c, s, jobs) for c in copies for s in seeds]
    _mac.emit({"experiment": "07 overnight load", "tasks": len(tasks), "workers": workers, "jobs_per_run": jobs,
               "mode": "here" if a.here else "mac", "at": _mac.stamp()}, a.out)
    if workers == 1:
        rows = [one(t) for t in tasks]
    else:
        with mp.get_context("spawn").Pool(workers) as pool:   # spawn: the macOS default start method
            rows = pool.map(one, tasks)
    for r in rows:
        _mac.emit(r, a.out)
    ok = True
    for c in copies:
        rs = [r for r in rows if r["copies"] == c]
        summary = {"summary": f"{3 * c} backends", "runs": len(rs), "fitness_pass_rate": sum(r["fitness_pass"] for r in rs) / len(rs),
                   "worst_p95_queue_s": max(r["p95_queue_s"] for r in rs),
                   "median_p95_queue_s": statistics.median(r["p95_queue_s"] for r in rs),
                   "contract_violations": sum(r["contract_violations"] for r in rs),
                   "mean_ci95_coverage": round(statistics.fmean(r["ci95_coverage"] for r in rs), 4)}
        ok &= summary["contract_violations"] == 0
        _mac.emit(summary, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
