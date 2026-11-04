"""Build-task solution for lab 18: a fair comparison harness. Run: python solution_fair.py

Rules it enforces (the fitness test checks them): every solver gets the SAME budget and the SAME seed list;
each run must report used <= budget (else BudgetViolation); results are medians over all seeds, never the best.
"""
import json
import time

import bench_lab as lab


class BudgetViolation(RuntimeError):
    pass


def compare(n, solvers=lab.S.BUDGETED, budget=lab.BUDGET, seeds=lab.SEEDS, edges=None):
    edges, opt = (edges, lab.S.exact(n, edges)["cut"]) if edges else lab.instance(n)
    rows = []
    for name, solve in solvers.items():
        t = time.perf_counter()
        results = [solve(n, edges, budget, s) for s in seeds]           # same budget, same seeds
        over = [r["used"] for r in results if r["used"] > budget]
        if over:
            raise BudgetViolation(f"{name} spent {max(over)} > budget {budget}")
        rows.append(lab.summarise(n, name, results, opt, budget, (time.perf_counter() - t) / len(seeds)))
    return rows, lab.decide(rows)


if __name__ == "__main__":
    for n in lab.SIZES:
        rows, winner = compare(n)
        for r in rows:
            print(json.dumps(r))
        print(json.dumps({"n": n, "winner": winner, "method": "fair (same budget, same 10 seeds, medians)"}))
