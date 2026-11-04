"""Overnight: 100,000 simulated nights of weather for tonight's two plans, on every core - and a cloudier-site check.

Night r uses the SAME stream as weather.clear_matrix (child r of SeedSequence(seed)), so chunks computed in parallel
give exactly the rows a single 100,000-run clear_matrix would (a test checks this on 2,000 nights). Per plan:
mean value with its 95 % CI, P(value = 0), 5/50/95 % quantiles, P(optimised < greedy), and every block's empirical
completion rate against the analytic promise p_complete(n) (z score). Then the same plans on sites where clouds
arrive more often than the model assumes (P_CLEAR_TO_CLOUD 0.02 / 0.04 / 0.08): does FF2 (optimised >= 1.15 x greedy)
still hold when the weather model is wrong?

python weather_overnight.py --here            2,000 nights, 2 workers (sandbox)
python weather_overnight.py --nights 100000   the Mac (workers = performance cores from mac_profile.py)
"""
import argparse
import json
import multiprocessing as mp
import sys
import time

import numpy as np

import _lab
import weather

SEED = 7  # run_project.py's Monte Carlo seed: the first 1,000 nights here ARE the scorecard's nights
MARGIN = 0.15


def clear_rows(seed, start, stop, n_slots, a=weather.P_CLEAR_TO_CLOUD, b=weather.P_CLOUD_TO_CLEAR):
    """Rows start..stop-1 of weather.clear_matrix(stop, n_slots, seed, a, b) without generating the earlier rows."""
    u = np.array([np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(r,))).random(n_slots)
                  for r in range(start, stop)])
    clear = np.empty(u.shape, dtype=bool)
    clear[:, 0] = u[:, 0] < weather.pi_clear(a, b)
    for s in range(1, n_slots):
        clear[:, s] = np.where(clear[:, s - 1], u[:, s] >= a, u[:, s] < b)
    return clear


def _chunk(task):
    seed, start, stop, n_slots, plans, a, b = task
    clear = clear_rows(seed, start, stop, n_slots, a, b)
    vals = {k: weather.realised(blocks, clear) for k, blocks in plans.items()}
    done = {k: [clear[:, s:s + n].all(axis=1).sum() for s, n, _ in blocks] for k, blocks in plans.items()}
    return vals, done


def simulate(plans, n_slots, nights, workers, seed=SEED, a=weather.P_CLEAR_TO_CLOUD, chunk=5000):
    tasks = [(seed, s, min(s + chunk, nights), n_slots, plans, a, weather.P_CLOUD_TO_CLEAR) for s in range(0, nights, chunk)]
    if workers == 1:
        parts = [_chunk(t) for t in tasks]
    else:
        with mp.get_context("spawn").Pool(workers) as pool:
            parts = pool.map(_chunk, tasks)
    vals = {k: np.concatenate([p[0][k] for p in parts]) for k in plans}
    done = {k: np.sum([p[1][k] for p in parts], axis=0) for k in plans}
    return vals, done


def summarise(plans, vals, done, nights, a):
    out = {"nights": nights, "p_clear_to_cloud": a}
    for k, v in vals.items():
        m, h = weather.summary(v)
        out[k] = {"mean": round(float(m), 4), "ci95": round(float(h), 4), "p_zero": round(float((v == 0).mean()), 4),
                  "q05_q50_q95": [float(x) for x in np.quantile(v, [0.05, 0.5, 0.95])]}
        if abs(a - weather.P_CLEAR_TO_CLOUD) < 1e-12:  # promises are made under the model's own parameters
            blocks = []
            for (s, n, w), c in zip(plans[k], done[k]):
                p = weather.p_complete(n)
                z = (c / nights - p) / np.sqrt(p * (1 - p) / nights)
                blocks.append({"start": s, "slots": n, "promise": round(p, 4), "observed": round(c / nights, 4),
                               "z": round(float(z), 2)})
            out[k]["blocks"] = blocks
    g, lo = vals["greedy"], vals["local"]
    out["ratio_local_greedy"] = round(float(lo.mean() / g.mean()), 4)
    dm, dh = weather.summary(lo - g)
    out["paired_diff"] = [round(float(dm), 4), round(float(dh), 4)]
    out["p_local_below_greedy"] = round(float((lo < g).mean()), 4)
    out["ff2_holds"] = bool(lo.mean() >= (1 + MARGIN) * g.mean() and dm - dh > 0)
    return out


def plans_of(r):
    return {k: [(int(s), int(n), int(r["reqs"][i].priority)) for s, n, i in r[k]] for k in ("greedy", "local")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--nights", type=int, default=100_000)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--cloudier", type=float, nargs="*", default=[0.02, 0.04, 0.08])
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.here:
        a.nights, a.workers = 2000, a.workers or 2
    if not a.workers:
        import mac_profile
        a.workers = mac_profile.profile()["workers"]
    r, t0 = _lab.build(), time.perf_counter()
    plans, n_slots, rows = plans_of(r), len(r["slots"]), []
    for p in a.cloudier:
        vals, done = simulate(plans, n_slots, a.nights, a.workers, a=p, chunk=max(500, a.nights // (a.workers * 4)))
        rows.append(summarise(plans, vals, done, a.nights, p))
        print(json.dumps(rows[-1]))
    rows.append({"meta": True, "workers": a.workers, "seconds": round(time.perf_counter() - t0, 1), "seed": SEED,
                 "expected_values": {"greedy": round(r["greedy_value"], 4), "local": round(r["local_value"], 4)}})
    print(json.dumps(rows[-1]))
    path = _lab.write_jsonl(_lab.runs_dir(a.out) / "05-weather-overnight.jsonl", rows)
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
