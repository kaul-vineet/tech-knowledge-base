"""L200 resources and queues: a clinic reception with c desks and ONE shared line, built on heapq.

Poisson arrivals, exponential service -> M/M/c, so the Erlang C formula checks the simulation.
python mmc_queue.py
"""
import heapq
import itertools
import math
import random
from collections import deque

LAM, MU, C = 2.4, 1.0, 3  # 2.4 patients/min, each desk serves 1.0/min, 3 desks -> utilisation 80%


def simulate(n_customers, c=C, lam=LAM, mu=MU, seed=1):
    rng = random.Random(seed)
    events, seq = [], itertools.count()  # event list (min-heap); seq keeps equal times FIFO
    heapq.heappush(events, (rng.expovariate(lam), next(seq), "arrive", 0))
    busy, line, waits = 0, deque(), []
    area_line = area_busy = last = 0.0  # time-weighted integrals -> time-average queue length and utilisation
    while events:
        t, _, kind, cust = heapq.heappop(events)
        area_line += len(line) * (t - last)  # the line had len(line) people since the last event
        area_busy += busy * (t - last)
        last = t
        if kind == "arrive":
            if cust + 1 < n_customers:
                heapq.heappush(events, (t + rng.expovariate(lam), next(seq), "arrive", cust + 1))
            if busy < c:  # a desk is free: the resource is acquired immediately
                busy += 1
                waits.append(0.0)
                heapq.heappush(events, (t + rng.expovariate(mu), next(seq), "depart", cust))
            else:
                line.append(t)  # all c desks busy: join the shared FIFO line
        elif line:  # a desk is released and handed straight to the next in line
            waits.append(t - line.popleft())
            heapq.heappush(events, (t + rng.expovariate(mu), next(seq), "depart", None))
        else:
            busy -= 1
    return {"Wq": sum(waits) / len(waits), "Lq": area_line / last, "util": area_busy / (c * last),
            "P_wait": sum(w > 0 for w in waits) / len(waits)}


def erlang_c(c=C, lam=LAM, mu=MU):
    a = lam / mu  # offered load in Erlangs
    rho = a / c
    if rho >= 1:
        raise ValueError("unstable: lam >= c * mu, the line grows forever")
    top = a ** c / math.factorial(c) / (1 - rho)
    p_wait = top / (sum(a ** k / math.factorial(k) for k in range(c)) + top)  # Erlang C: P(an arrival waits)
    wq = p_wait / (c * mu - lam)
    return {"Wq": wq, "Lq": lam * wq, "util": rho, "P_wait": p_wait}  # Lq = lam * Wq (Little's law)


def main():
    sim, exact = simulate(200_000), erlang_c()
    print(f"M/M/{C}: lam={LAM}/min, mu={MU}/min per desk, utilisation {LAM / (C * MU):.0%}")
    print(f"{'metric':8} {'simulated':>10} {'Erlang C':>10}")
    for key in ("Wq", "Lq", "util", "P_wait"):
        print(f"{key:8} {sim[key]:10.3f} {exact[key]:10.3f}")
    print("desks needed so that P(wait) < 20%:")
    for c in range(3, 7):
        print(f"  c={c}: P(wait)={erlang_c(c)['P_wait']:.3f}  Wq={erlang_c(c)['Wq']:.3f} min")


if __name__ == "__main__":
    main()
