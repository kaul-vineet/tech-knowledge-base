"""L200 supply chain: a bike shop's (s, S) reorder policy for inner tubes, compared fairly with common random numbers.

Demand ~ Poisson(8 x weekly weather factor, mean 1); lead time 1-4 days; unmet demand is lost.
Costs: holding 0.10/tube/day, 25 per order, 4.00 per lost sale.
python inventory.py
"""
import math

import numpy as np

DAYS, MEAN_DEMAND = 365, 8
HOLD, ORDER, LOST = 0.10, 25.0, 4.0
T975 = {29: 2.045}  # Student t quantile, 95% two-sided, 29 degrees of freedom (30 replications)


def streams(rep, days=DAYS):
    """Common random numbers: one stream per PURPOSE, so a policy change cannot shift who-gets-which-number."""
    rng = np.random.default_rng([rep, 0])  # [rep, purpose] seed list, as in the NumPy parallel-streams docs
    weather = np.repeat(rng.gamma(4.0, 0.25, days // 7 + 1), 7)[:days]  # one busy/quiet factor per week
    demand = rng.poisson(MEAN_DEMAND * weather)
    lead = np.random.default_rng([rep, 1]).integers(1, 5, days)  # lead time IF an order is placed on day t
    return demand, lead


def simulate(s, S, demand, lead):
    on_hand, arriving = S, np.zeros(len(demand) + 5, dtype=int)  # arriving[t]: tubes delivered on morning t
    cost = lost = orders = 0.0
    for t, d in enumerate(demand):
        on_hand += arriving[t]
        sold = min(on_hand, d)
        lost += d - sold  # lost sales, not backorders
        on_hand -= sold
        position = on_hand + arriving[t + 1:].sum()  # inventory position includes what is already on order
        if position <= s:
            arriving[t + lead[t]] += S - position  # order up to S; arrives lead[t] days later
            orders += 1
        cost += HOLD * on_hand
    cost += ORDER * orders + LOST * lost
    return {"cost_per_day": cost / len(demand), "orders": orders, "lost": lost}


def ci(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean()), T975[len(x) - 1] * float(x.std(ddof=1)) / math.sqrt(len(x))


def compare(a, b, reps=30, crn=True):
    """Cost difference b - a per day over `reps` replications; CRN: both policies see the same demand and lead times."""
    diffs = []
    for r in range(reps):
        cost_a = simulate(*a, *streams(r))["cost_per_day"]
        cost_b = simulate(*b, *streams(r if crn else r + 10_000))["cost_per_day"]  # independent: other numbers
        diffs.append(cost_b - cost_a)
    return ci(diffs)


def main():
    a, b = (30, 80), (30, 90)
    print(f"(s, S) policies over {DAYS} days, 30 replications: mean cost per day +/- 95% CI")
    for pol in ((20, 80), a, b):
        runs = [simulate(*pol, *streams(r)) for r in range(30)]
        m, h = ci([x["cost_per_day"] for x in runs])
        print(f"  s={pol[0]:2d} S={pol[1]:2d}: {m:6.2f} +/- {h:.2f}  orders/yr {np.mean([x['orders'] for x in runs]):5.1f}"
              f"  lost tubes/yr {np.mean([x['lost'] for x in runs]):6.1f}")
    for crn in (False, True):
        m, h = compare(a, b, crn=crn)
        verdict = "S=90 is cheaper" if m + h < 0 else "S=80 is cheaper" if m - h > 0 else "cannot tell"
        print(f"difference S=90 minus S=80, {'CRN        ' if crn else 'independent'}: {m:+.2f} +/- {h:.2f} -> {verdict}")


if __name__ == "__main__":
    main()
