"""Same 3-desk clinic reception with SimPy 4.1.2 (pending-ci: SimPy is not installed in the sandbox).

simpy.Resource(env, capacity=c) is the c desks plus their shared FIFO line; SimPy keeps the event list.
python simpy_mmc.py
"""
import random
from importlib.metadata import version

import simpy

from mmc_queue import LAM, MU, C, erlang_c


def patient(env, desks, rng, waits, busy_time):
    arrived = env.now
    with desks.request() as req:  # join the line; released automatically when the block ends
        yield req
        waits.append(env.now - arrived)
        service = rng.expovariate(MU)
        busy_time.append(service)
        yield env.timeout(service)


def arrivals(env, desks, rng, waits, busy_time, n):
    for _ in range(n):
        yield env.timeout(rng.expovariate(LAM))
        env.process(patient(env, desks, rng, waits, busy_time))


def simulate(n_customers, c=C, seed=1):
    rng = random.Random(seed)
    env = simpy.Environment()
    desks = simpy.Resource(env, capacity=c)
    waits, busy_time = [], []
    env.process(arrivals(env, desks, rng, waits, busy_time, n_customers))
    env.run()
    return {"Wq": sum(waits) / len(waits), "util": sum(busy_time) / (c * env.now),
            "P_wait": sum(w > 0 for w in waits) / len(waits)}


if __name__ == "__main__":
    sim, exact = simulate(200_000), erlang_c()
    print(f"SimPy {version('simpy')}: " + " | ".join(f"{k} {sim[k]:.3f} (Erlang C {exact[k]:.3f})" for k in sim))
