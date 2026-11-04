"""Night scheduler: a greedy dispatcher (baseline) and a seeded local search over request order.

Both use the same feasibility matrix from sky.py (airmass <= 2, Moon >= 30 deg, Sun <= -18 deg at every block
boundary) and output slot-aligned blocks. The local search maximises the EXPECTED priority-weighted value under the
weather model (weather.p_complete), so it knows a 3-hour block is a riskier promise than two 1-hour ones.
python scheduler.py          (prints both plans for the night of 2026-11-19 at Gurgaon)
"""
import hashlib
import json

import numpy as np

import sky
import weather


def greedy(reqs, ok, x):
    """Baseline: at each free slot start the highest-priority feasible request (ties: lower airmass, then name)."""
    k, done, blocks = 0, set(), []
    while k < ok.shape[1]:
        ready = [i for i in range(len(reqs)) if i not in done and ok[i, k]]
        if not ready:
            k += 1
            continue
        i = min(ready, key=lambda j: (-reqs[j].priority, x[j, k], reqs[j].name))
        n = reqs[i].exp_min // sky.STEP_MIN
        blocks.append((k, n, i))
        done.add(i)
        k += n
    return blocks


def decode(order, reqs, ok):
    """Order -> schedule: each request in turn takes its EARLIEST feasible start whose slots are still free."""
    free, blocks = np.ones(ok.shape[1], dtype=bool), []
    for i in order:
        n = reqs[i].exp_min // sky.STEP_MIN
        for s in np.flatnonzero(ok[i]):
            if free[s:s + n].all():
                free[s:s + n] = False
                blocks.append((int(s), n, i))
                break
    return sorted(blocks)


def value(blocks, reqs):
    """Expected priority-weighted value: the number the optimiser maximises and the scheduler promises."""
    return weather.expected([(s, n, reqs[i].priority) for s, n, i in blocks])


def local_search(reqs, ok, x, seed=2026, iters=3000):
    """First-improvement hill climbing on the request order (swap or move one), plateau moves allowed.

    Starts from the greedy plan's order so it can never end below the baseline it is compared with."""
    rng = np.random.default_rng(seed)
    start = [i for _, _, i in greedy(reqs, ok, x)]
    order = start + sorted(set(range(len(reqs))) - set(start), key=lambda i: -reqs[i].priority)
    best = value(decode(order, reqs, ok), reqs)
    for _ in range(iters):
        cand = list(order)
        a, b = (int(v) for v in rng.choice(len(cand), 2, replace=False))
        if rng.random() < 0.5:
            cand[a], cand[b] = cand[b], cand[a]
        else:
            cand.insert(b, cand.pop(a))
        v = value(decode(cand, reqs, ok), reqs)
        if v >= best - 1e-12:
            order, best = cand, max(best, v)
    return decode(order, reqs, ok)


def as_rows(blocks, reqs, slots, x):
    """Typed output: UTC ISO start/end (machines), local HH:MM (people), worst airmass inside the block."""
    rows = []
    for s, n, i in blocks:
        rows.append({"target": reqs[i].name, "priority": reqs[i].priority, "start_utc": slots[s].utc.iso(),
                     "end_utc": slots[s].utc.plus(n * sky.STEP_MIN).iso(), "start_local": slots[s].local.strftime("%H:%M"),
                     "max_airmass": round(float(x[i, s:s + n + 1].max()), 3),
                     "p_complete": round(weather.p_complete(n), 4)})
    return rows


def plan_hash(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def build(seed=2026, fault=None, reqs=None):
    """Everything the scorecard needs: slots, feasibility, both plans (as rows), and their expected values."""
    reqs = reqs or sky.REQUESTS
    slots = sky.night_slots()
    ok, x = sky.feasibility(reqs, slots, fault)
    g, ls = greedy(reqs, ok, x), local_search(reqs, ok, x, seed)
    return {"reqs": reqs, "slots": slots, "ok": ok, "x": x, "greedy": g, "local": ls,
            "greedy_rows": as_rows(g, reqs, slots, x), "local_rows": as_rows(ls, reqs, slots, x),
            "greedy_value": value(g, reqs), "local_value": value(ls, reqs)}


if __name__ == "__main__":
    r = build()
    for name in ("greedy", "local"):
        print(f"{name}: expected value {r[name + '_value']:.3f}  hash {plan_hash(r[name + '_rows'])}")
        for row in r[name + "_rows"]:
            print("  " + json.dumps(row))
