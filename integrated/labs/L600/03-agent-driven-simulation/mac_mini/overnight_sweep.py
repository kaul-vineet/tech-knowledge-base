"""Overnight: big seeded runs on every core - CI coverage of the verification check, and a large-N Sobol reference.

coverage  For rho in --rhos: E independent experiments of R replications each (M1's design: 20,000 customers, warm-up
          2,000, no backlog). Each experiment's 95 % CI either covers the M/M/1 formula or not. A correct model
          with an adequate warm-up covers ~95 % of the time; a clearly lower rate at high rho means the initial
          transient biases the estimate - the verified envelope (contract.RHO_MAX = 0.9) is then too generous.
sobol     The screening problem the agent asks for (pipeline._screening, CRN seed) at base sizes n/8, n/4, n/2, n:
          ST per input and the ranking. Reveals the smallest size whose ranking matches the large-n reference.

Reproducible by construction: replication r of experiment e at rho gets SeedSequence(root, spawn_key=(e, r)) via
model.seed_for, independent of how tasks are split over processes; results are returned in task order, so the
output hash is the same for 1 or 16 workers (a test checks 1 vs 2 here). Pool uses the "spawn" start method, the
macOS default, on every OS.

python overnight_sweep.py --here                      tiny sizes, 2 workers (sandbox, ~1 min)
python overnight_sweep.py coverage --experiments 2000 --reps 10      (Mac, all performance cores)
python overnight_sweep.py sobol --n 8192
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time

import numpy as np

import _lab
import model
import pipeline
import stats

M1 = {"mu": 1.0, "backlog": 0, "customers": 20_000, "warmup": 2_000}
ROOT = 600_003  # root seed of this study (distinct from the lab's seeds)


def _coverage_task(t):
    rho, e, r, customers = t
    return model.run_once({**M1, "lam": rho, "customers": customers}, model.seed_for(ROOT + int(round(rho * 1000)), e, r))


def _screen_task(t):
    lam, mu, backlog, warmup, seed = t
    return model.run_once({"lam": lam, "mu": mu, "backlog": backlog, "warmup": warmup,
                           "customers": pipeline.SCREEN_CUSTOMERS}, seed)


def _workers(n):
    if n:
        return n
    import mac_profile
    return mac_profile.profile()["workers"]


def coverage(rhos, experiments, reps, workers, customers=M1["customers"]):
    tasks = [(rho, e, r, customers) for rho in rhos for e in range(experiments) for r in range(reps)]
    with mp.get_context("spawn").Pool(workers) as pool:
        values = pool.map(_coverage_task, tasks, chunksize=max(1, len(tasks) // (workers * 8)))
    out, k = [], 0
    for rho in rhos:
        formula = model.mm1_wq(rho, 1.0)
        covered, means = 0, []
        for _ in range(experiments):
            xs = values[k:k + reps]
            k += reps
            m, h = stats.mean_ci(xs)
            covered += abs(m - formula) <= h
            means.append(m)
        rate = covered / experiments
        se = (0.95 * 0.05 / experiments) ** 0.5  # binomial SE if the true coverage were 0.95
        out.append({"rho": rho, "experiments": experiments, "reps": reps, "customers": customers,
                    "formula": round(formula, 4), "mean_of_means": round(float(np.mean(means)), 4),
                    "bias": round(float(np.mean(means)) - formula, 4), "coverage": round(rate, 4),
                    "z_vs_95": round((rate - 0.95) / se, 2)})
    return out, values


def sobol(n, workers, root=pipeline.DEFAULT_SEED):
    sens = pipeline.sensitivity
    seed = model.seed_for(root, 99, 0)  # the same CRN stream as pipeline._screening
    with mp.get_context("spawn").Pool(workers) as pool:
        def f(x):
            u = (x - sens.LOW) / (sens.HIGH - sens.LOW)
            rows = pipeline.SCREEN_LOW + u * (pipeline.SCREEN_HIGH - pipeline.SCREEN_LOW)
            tasks = [(float(r[0]), float(r[1]), int(round(r[2])), int(round(r[3])), seed) for r in rows]
            return np.array(pool.map(_screen_task, tasks, chunksize=max(1, len(tasks) // (workers * 8))))
        out, every = [], []
        for size in sorted({max(2, n // 8), max(2, n // 4), max(2, n // 2), n}):
            _, st = sens.sobol(n=size, f=f, seed=root)
            ranking = [pipeline.SCREEN_NAMES[i] for i in np.argsort(-st)]
            out.append({"n": size, "runs": size * (len(pipeline.SCREEN_NAMES) + 2),
                        "ST": {k: round(float(v), 4) for k, v in zip(pipeline.SCREEN_NAMES, st)}, "ranking": ranking})
            every.extend(st.tolist())
    ref = out[-1]["ranking"]
    for row in out:
        row["matches_reference"] = row["ranking"] == ref
    return out, every


def digest(values):
    return hashlib.sha256(b"".join(float(v).hex().encode() for v in values)).hexdigest()[:16]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", choices=["coverage", "sobol", "both"], default="both")
    ap.add_argument("--here", action="store_true", help="tiny sizes, 2 workers")
    ap.add_argument("--rhos", type=float, nargs="+", default=[0.5, 0.7, 0.8, 0.9])
    ap.add_argument("--experiments", type=int, default=2000)
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--customers", type=int, default=M1["customers"])
    ap.add_argument("--n", type=int, default=8192)
    ap.add_argument("--workers", type=int, default=0, help="0 = performance cores from mac_profile.py")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.here:
        a.experiments, a.reps, a.n, a.workers, a.customers, a.rhos = 6, 4, 16, a.workers or 2, 3_000, [0.5, 0.9]
    workers, rows, t0 = _workers(a.workers), [], time.perf_counter()
    if a.mode in ("coverage", "both"):
        cov, values = coverage(a.rhos, a.experiments, a.reps, workers, a.customers)
        rows += [{"study": "coverage", **r} for r in cov]
        rows.append({"study": "coverage", "values_sha256_16": digest(values), "tasks": len(values)})
    if a.mode in ("sobol", "both"):
        sob, every = sobol(a.n, workers)
        rows += [{"study": "sobol", **r} for r in sob]
        rows.append({"study": "sobol", "st_sha256_16": digest(every)})
    meta = {"study": "meta", "workers": workers, "seconds": round(time.perf_counter() - t0, 1), "here": a.here,
            "env": model.ENVIRONMENT, "model_version": model.VERSION}
    rows.append(meta)
    for r in rows:
        print(json.dumps(r))
    path = _lab.write_jsonl(_lab.runs_dir(a.out) / "03-overnight-sweep.jsonl", rows)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
