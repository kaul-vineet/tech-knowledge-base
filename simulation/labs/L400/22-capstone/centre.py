"""Capstone DES core: a service centre (calls, agents, impatient callers) with hourly staffing.

Arrivals: non-homogeneous Poisson by thinning (Lewis & Shedler 1979). Service: lognormal (mean, cv).
Patience: exponential - a caller who waits longer than their patience hangs up (abandons).
Streams: one per PURPOSE (arrivals, service, patience) and call i always gets draw i -> common random numbers
stay aligned when the staffing changes. Service level (SL) = calls answered within SL_MIN / calls offered.
"""
import heapq
import itertools
import math
from collections import deque

import numpy as np

SL_MIN, OPEN_H, CLOSE_H = 1.0, 8, 20  # answer within 1 minute; open 08:00-20:00


def lognormal_params(mean, cv):
    s2 = math.log(1 + cv ** 2)
    return math.log(mean) - s2 / 2, math.sqrt(s2)


def simulate(rates, staff, mean_service, cv, patience, seed, warmup=0.0, horizon=None):
    """rates/staff: one value per hour (calls/min, agents). Returns per-hour metrics for calls arriving in each hour.
    cv=None: exponential service (the Erlang C check). warmup: minutes at hour 0's rate before t = 0, not counted."""
    hours = len(rates)
    horizon = horizon or 60.0 * hours
    rng_a, rng_s, rng_p = (np.random.default_rng([seed, k]) for k in range(3))
    lam_max = max(rates)
    rate_at = lambda t: rates[min(int(max(t, 0) // 60), hours - 1)]
    cap_at = lambda t: staff[min(int(max(t, 0) // 60), hours - 1)]
    mu_ln, sd_ln = lognormal_params(mean_service, cv or 1.0)
    service = (lambda: rng_s.exponential(mean_service)) if cv is None else (lambda: rng_s.lognormal(mu_ln, sd_ln))
    events, seq = [], itertools.count()
    t = -warmup
    while True:  # thinning: candidate at rate lam_max, accept with probability rate(t) / lam_max
        t += rng_a.exponential(1 / lam_max)
        if t >= horizon:
            break
        if rng_a.random() * lam_max <= rate_at(t):
            heapq.heappush(events, (t, next(seq), "arrive", None))
    for h in range(1, hours):
        heapq.heappush(events, (60.0 * h, next(seq), "shift", None))  # capacity may rise at the hour
    line, busy, call = deque(), 0, itertools.count()
    stats = [{"offered": 0, "answered_in_sl": 0, "abandoned": 0, "wait": 0.0} for _ in range(hours)]
    waiting = {}  # call id -> (arrival time, hour index) while in the line

    def start(now, cid, arrived, h):
        nonlocal busy
        busy += 1
        if arrived >= 0:
            stats[h]["answered_in_sl"] += (now - arrived) <= SL_MIN
            stats[h]["wait"] += now - arrived
        heapq.heappush(events, (now + service(), next(seq), "depart", None))

    def serve_line(now):
        while line and busy < cap_at(now):
            cid = line.popleft()
            if cid in waiting:  # skip callers who already hung up (lazy deletion)
                arrived, h = waiting.pop(cid)
                start(now, cid, arrived, h)

    while events:
        now, _, kind, cid = heapq.heappop(events)
        if kind == "arrive":
            cid, h = next(call), min(int(max(now, 0) // 60), hours - 1)
            patience_draw = rng_p.exponential(patience)  # drawn for every call, used or not: keeps CRN aligned
            if now >= 0:
                stats[h]["offered"] += 1
            if busy < cap_at(now) and not line:
                start(now, cid, now, h)
            else:
                line.append(cid)
                waiting[cid] = (now, h)
                heapq.heappush(events, (now + patience_draw, next(seq), "abandon", cid))
        elif kind == "abandon" and cid in waiting:
            arrived, h = waiting.pop(cid)
            if arrived >= 0:
                stats[h]["abandoned"] += 1
                stats[h]["wait"] += now - arrived
        elif kind == "depart":
            busy -= 1
            serve_line(now)
        elif kind == "shift":
            serve_line(now)
    return [{"offered": s["offered"], "sl": s["answered_in_sl"] / max(1, s["offered"]),
             "abandon": s["abandoned"] / max(1, s["offered"]), "mean_wait": s["wait"] / max(1, s["offered"])}
            for s in stats]


def period(rate, agents, mean_service, cv, patience, seed, warmup=30.0):
    """One stationary hour with a warm-up (the hour-by-hour staffing approximation)."""
    return simulate([rate], [agents], mean_service, cv, patience, seed, warmup=warmup)[0]
