"""Numerical checks for the lesson 24 theorems. Run: python check_quality.py  (exit 0 = every check holds)."""
import itertools
import math
import random
import sys

import availability as av
import tradeoff as tr

FAILURES = []


def check(label, ok):
    print(f"  [{'OK' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILURES.append(label)


def exact_by_enumeration(comps, structure):
    """Sum the probability of every up/down state in which the structure works (2^n states, exact)."""
    names, total = list(comps), 0.0
    for bits in itertools.product([True, False], repeat=len(names)):
        state = dict(zip(names, bits))
        if structure(state):
            total += math.prod(comps[n] if state[n] else 1 - comps[n] for n in names)
    return total


def theorem_series_parallel(rng):
    print("T1/T2 series = product, parallel = 1 - product of unavailabilities (independent components)")
    c = av.LIBRARY_LOANS
    comps = {"load balancer": c["load balancer"], "api 1": c["api instance"], "api 2": c["api instance"],
             "database": c["database"], "identity provider": c["identity provider"]}
    formula = av.library_loans(2)
    exact = exact_by_enumeration(comps, av.library_loans_structure)
    check(f"Library Loans (LB, 2 API replicas, DB, IdP): formula {formula:.6%} = enumeration of 32 states "
          f"{exact:.6%} (|diff| {abs(formula - exact):.1e})", abs(formula - exact) < 1e-12)
    trials = 400_000
    mc = av.monte_carlo(av.library_loans_structure, comps, trials, rng)
    sigma = math.sqrt(formula * (1 - formula) / trials)
    check(f"Monte Carlo {trials:,} trials: {mc:.4%} within 4 sigma ({4 * sigma:.4%}) of the formula",
          abs(mc - formula) < 4 * sigma)
    serial = [c["load balancer"], c["api instance"], c["database"], c["identity provider"]]
    a = av.series(serial)
    check(f"one API instance: series {a:.4%}; union bound {av.union_bound(serial):.4%} <= A <= min {min(serial):.2%}",
          av.union_bound(serial) <= a <= min(serial))
    print(f"      adding the 2nd API replica: {a:.4%} -> {formula:.4%}; a 3rd: {av.library_loans(3):.4%} "
          f"(the database is now the limit: {c['database']:.2%})")
    for k in (1, 2, 3):
        comps3 = {f"r{i}": 0.99 for i in range(3)}
        exact3 = exact_by_enumeration(comps3, lambda s, k=k: sum(s.values()) >= k)
        check(f"{k}-of-3 replicas at 99%: binomial {av.k_of_n(k, 3, 0.99):.6%} = enumeration {exact3:.6%}",
              abs(av.k_of_n(k, 3, 0.99) - exact3) < 1e-12)
    check("1-of-n equals parallel([a]*n)", abs(av.k_of_n(1, 3, 0.99) - av.parallel([0.99] * 3)) < 1e-15)


def theorem_nines(rng):
    print("T3 nines -> downtime, and steady-state availability = MTTF / (MTTF + MTTR)")
    print(f"      {'SLO':>8}{'min / 30 days':>15}{'h / year':>10}")
    table = av.nines_table()
    for a, month, year in table:
        print(f"      {a:>8.3%}{month:>15.2f}{year:>10.3f}")
    ratios = [table[i][2] / table[j][2] for i, j in ((0, 1), (1, 3), (3, 4))]
    check(f"each extra nine divides allowed downtime by 10: ratios {[round(r, 6) for r in ratios]}",
          all(abs(r - 10) < 1e-9 for r in ratios))
    budget = av.downtime_minutes(0.9999)
    check(f"CACM example: 3 outages x 20 min = 60 min > {budget:.2f} min allowed by 99.99%/year", 60 > budget)
    mttf, mttr = 720.0, 1.0
    formula = mttf / (mttf + mttr)
    for repair in ("exponential", "uniform"):
        sim = av.simulate_up_fraction(mttf, mttr, 20_000_000, rng, repair)
        check(f"MTTF 720 h, MTTR 1 h, {repair} repair: simulated up fraction {sim:.5%} vs formula {formula:.5%}",
              abs(sim - formula) < 2e-4)


def theorem_break_even(rng):
    print("T4 two criteria, weights (w, 1-w): at most one break-even weight w*; preference flips there")
    x, y = tr.SINGLE_SQLITE, tr.REPLICATED_POSTGRES
    w_star = tr.break_even(x, y)
    flips = [i / 10_000 for i in range(1, 10_001)
             if (tr.weighted_score(x, i / 10_000) > tr.weighted_score(y, i / 10_000)) !=
             (tr.weighted_score(x, (i - 1) / 10_000) > tr.weighted_score(y, (i - 1) / 10_000))]
    check(f"SQLite {x} vs replicated PostgreSQL {y}: w* = {w_star:.4f}; sweep flips at {flips}",
          len(flips) == 1 and abs(flips[0] - w_star) <= 1e-4)
    mismatches = 0
    for _ in range(2000):
        p, q = (rng.random(), rng.random()), (rng.random(), rng.random())
        grid = [tr.weighted_score(p, i / 1000) - tr.weighted_score(q, i / 1000) for i in range(1001)]
        sign_changes = sum(1 for a, b in zip(grid, grid[1:]) if (a > 0) != (b > 0))
        mismatches += sign_changes != (1 if tr.break_even(p, q) is not None else 0)
    check(f"2,000 random option pairs: sign changes match the formula ({mismatches} mismatches)", mismatches == 0)
    print("      utility tree, highest priority first (importance, difficulty):")
    for attr, _, scenario, imp, dif in tr.prioritise()[:3]:
        print(f"        ({imp},{dif}) {attr}: {scenario[:70]}...")


if __name__ == "__main__":
    rng = random.Random(2400)
    theorem_series_parallel(rng)
    theorem_nines(rng)
    theorem_break_even(rng)
    print("ALL CHECKS OK" if not FAILURES else f"FAILED: {FAILURES}")
    sys.exit(1 if FAILURES else 0)
