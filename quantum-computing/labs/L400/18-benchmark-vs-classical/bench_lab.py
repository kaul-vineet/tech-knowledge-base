"""Lab 18 - benchmarking QAOA honestly against classical MaxCut solvers (simulator only).

Run:  python bench_lab.py          (numpy only; JSON lines)   Fair version: python solution_fair.py
Solvers (solvers.py): exact brute force (the reference), greedy local search, simulated annealing, QAOA p=1.
Quality = approximation ratio (best cut / exact optimum). Time-to-solution = samples until the best cut was
first seen, and TTS99 = budget x ln(0.01)/ln(1 - success rate). Local seconds are printed but never judged:
simulator time says nothing about hardware time.
The FAULT is this file's compare(): QAOA gets 4x the budget and its best of 10 seeds, the classical baselines
run once at a quarter budget, and nobody checks what a solver spent - the classic way a benchmark "shows" a quantum win.
SDK path (QAOA sampled with Qiskit StatevectorSampler): python bench_qiskit.py   (CI)
"""
import json
import math
import time

import numpy as np

import solvers as S

SIZES, SEEDS, BUDGET = (8, 12, 16), tuple(range(10)), 200
CLASSICAL = ("greedy", "annealing")


def instance(n, seed=0):
    edges = S.mc.regular_graph(n, 3, seed=100 + seed)
    return edges, S.exact(n, edges)["cut"]


def tts99(success_rate, samples_per_run):
    """Samples for 99 % confidence of seeing the optimum at least once (repeat-until-success)."""
    if success_rate == 0:
        return None                     # never found: no finite time-to-solution
    if success_rate == 1:
        return samples_per_run
    return round(samples_per_run * math.log(0.01) / math.log(1 - success_rate))


def summarise(n, name, results, opt, budget, seconds):
    ratios = [r["cut"] / opt for r in results]
    rate = float(np.mean([r["cut"] == opt for r in results]))
    return {"n": n, "solver": name, "budget": budget, "runs": len(results),
            "median_ratio": round(float(np.median(ratios)), 4), "success": rate,
            "median_first_best": int(np.median([r["first_best"] for r in results])),
            "tts99_samples": tts99(rate, budget), "local_s": round(seconds, 3)}


def decide(rows):
    """Code decides the winner: quality, then reliability, then speed; a tie goes to the classical baseline."""
    key = lambda r: (r["median_ratio"], r["success"], -r["median_first_best"], r["solver"] in CLASSICAL)  # noqa: E731
    return max(rows, key=key)["solver"]


BOOST = {"qaoa": 4, "greedy": 0.25, "annealing": 0.25}   # FAULT 1: QAOA tuned with 4x shots, baselines left at 50


def compare(n, solvers=S.BUDGETED, budget=BUDGET, seeds=SEEDS):
    edges, opt = instance(n)
    rows = []
    for name, solve in solvers.items():
        t = time.perf_counter()
        runs = seeds if name not in CLASSICAL else seeds[:1]     # FAULT 2: the baseline is run once
        results = [solve(n, edges, int(budget * BOOST.get(name, 1)), s) for s in runs]
        best = max(results, key=lambda r: r["cut"])              # FAULT 3: best seed reported as "the" result
        rows.append(summarise(n, name, [best], opt, budget, (time.perf_counter() - t) / len(runs)))
    return rows, decide(rows)                                    # FAULT 4: nobody checks r["used"] <= budget


if __name__ == "__main__":
    for n in SIZES:
        rows, winner = compare(n)
        for r in rows:
            print(json.dumps(r))
        print(json.dumps({"n": n, "winner": winner, "method": "naive (unequal budget, best seed)"}))
