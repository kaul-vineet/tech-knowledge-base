"""buildTask solution (lesson 8): a waiting-room limit. Arrivals that find max_queue people already in line leave
(blocked / balking). max_queue=None keeps the unlimited line; max_queue=0 is the Erlang B "lost calls" system.

python solution/mmc_capacity.py
"""
import heapq
import itertools
import random
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mmc_queue import LAM, MU, C  # noqa: E402


def simulate(n_customers, c=C, lam=LAM, mu=MU, seed=1, max_queue=None):
    rng = random.Random(seed)
    events, seq = [], itertools.count()
    heapq.heappush(events, (rng.expovariate(lam), next(seq), "arrive", 0))
    busy, line, waits, blocked = 0, deque(), [], 0
    area_line = area_busy = last = 0.0
    while events:
        t, _, kind, cust = heapq.heappop(events)
        area_line += len(line) * (t - last)
        area_busy += busy * (t - last)
        last = t
        if kind == "arrive":
            if cust + 1 < n_customers:
                heapq.heappush(events, (t + rng.expovariate(lam), next(seq), "arrive", cust + 1))
            if busy < c:
                busy += 1
                waits.append(0.0)
                heapq.heappush(events, (t + rng.expovariate(mu), next(seq), "depart", cust))
            elif max_queue is not None and len(line) >= max_queue:
                blocked += 1  # NEW: waiting room full -> the arrival leaves and is counted
            else:
                line.append(t)
        elif line:
            waits.append(t - line.popleft())
            heapq.heappush(events, (t + rng.expovariate(mu), next(seq), "depart", None))
        else:
            busy -= 1
    return {"Wq": sum(waits) / len(waits), "Lq": area_line / last, "util": area_busy / (c * last),
            "P_wait": sum(w > 0 for w in waits) / len(waits), "blocked": blocked / n_customers}


def erlang_b(c=C, lam=LAM, mu=MU):
    b = 1.0
    for k in range(1, c + 1):  # stable recursion: B(k) = a B(k-1) / (k + a B(k-1))
        b = (lam / mu) * b / (k + (lam / mu) * b)
    return b


if __name__ == "__main__":
    for q in (None, 5, 0):
        r = simulate(200_000, max_queue=q)
        print(f"max_queue={q}: blocked {r['blocked']:.3f}  Wq {r['Wq']:.3f} min  util {r['util']:.3f}")
    print(f"Erlang B (max_queue=0): {erlang_b():.3f}")
