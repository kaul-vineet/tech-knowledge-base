"""Try-it checks for lab 18. Run: python try_it.py   (numpy only)"""
import bench_lab as lab
import solution_fair as fair


def other_instances(n=12, graphs=range(1, 6)):
    """Try 1: QAOA 'won' n = 12 on graph 0. Re-run the fair comparison on five other 12-node graphs."""
    winners = {}
    for g in graphs:
        edges, opt = lab.instance(n, seed=g)
        rows = []
        for name, solve in lab.S.BUDGETED.items():
            results = [solve(n, edges, lab.BUDGET, s) for s in lab.SEEDS]
            rows.append(lab.summarise(n, name, results, opt, lab.BUDGET, 0.0))
        winners[g] = lab.decide(rows)
    return winners


def exact_in_budget(n=12):
    """Try 2: give exact enumeration the same kind of budget (2**n evaluations). Who wins now?"""
    solvers = {**lab.S.BUDGETED, "exact": lab.S.exact}
    rows, winner = fair.compare(n, solvers, budget=2 ** n, seeds=lab.SEEDS[:3])
    return {r["solver"]: r["success"] for r in rows}, winner


if __name__ == "__main__":
    print("other_instances", other_instances())
    print("exact_in_budget", exact_in_budget())
