"""Lesson 24 - availability maths: series, parallel, k-of-n, nines -> downtime, steady state MTTF/(MTTF+MTTR).

Assumption everywhere (and the reason the formulas can fail in production): component failures are independent.
"""
import math
import random

MINUTES_PER_YEAR = 365 * 24 * 60   # 525,600 (non-leap year)
MINUTES_PER_30_DAYS = 30 * 24 * 60  # 43,200 - the SLO window used in lesson 15


def series(avails):
    """All parts are needed: A = product of A_i."""
    return math.prod(avails)


def parallel(avails):
    """Any one part is enough: A = 1 - product of (1 - A_i)."""
    return 1 - math.prod(1 - a for a in avails)


def k_of_n(k, n, a):
    """At least k of n identical independent replicas up (binomial tail)."""
    return sum(math.comb(n, j) * a ** j * (1 - a) ** (n - j) for j in range(k, n + 1))


def union_bound(avails):
    """Lower bound for a series system without independence: 1 - sum of unavailabilities."""
    return 1 - sum(1 - a for a in avails)


def downtime_minutes(avail, period_minutes=MINUTES_PER_YEAR):
    return (1 - avail) * period_minutes


def nines(avail):
    """Number of nines: -log10(unavailability), e.g. 0.999 -> 3.0."""
    return -math.log10(1 - avail)


def nines_table(levels=(0.99, 0.999, 0.9995, 0.9999, 0.99999)):
    return [(a, downtime_minutes(a, MINUTES_PER_30_DAYS), downtime_minutes(a) / 60) for a in levels]


# Library Loans production sketch (stated, hypothetical component availabilities - not measurements)
LIBRARY_LOANS = {"load balancer": 0.9999, "api instance": 0.995, "database": 0.999, "identity provider": 0.9995}


def library_loans(api_replicas=2, comps=LIBRARY_LOANS):
    api = parallel([comps["api instance"]] * api_replicas)
    return series([comps["load balancer"], api, comps["database"], comps["identity provider"]])


def monte_carlo(structure, comps, trials, rng):
    """Sample every component up/down independently and evaluate the structure function."""
    up = 0
    for _ in range(trials):
        state = {name: rng.random() < a for name, a in comps.items()}
        up += structure(state)
    return up / trials


def library_loans_structure(state):
    api = state["api 1"] or state["api 2"]
    return state["load balancer"] and api and state["database"] and state["identity provider"]


def simulate_up_fraction(mttf, mttr, horizon, rng, repair="exponential"):
    """Alternating up/down periods; long-run fraction of time up should approach MTTF / (MTTF + MTTR)."""
    t = up_time = 0.0
    while t < horizon:
        up = rng.expovariate(1 / mttf)
        down = rng.expovariate(1 / mttr) if repair == "exponential" else rng.uniform(0, 2 * mttr)
        up_time += min(up, horizon - t)
        t += up + down
    return up_time / horizon
