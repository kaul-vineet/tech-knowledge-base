"""Same M/M/1 coffee-shop queue written with SimPy 4.1.2 (pending-ci: SimPy is not installed in the sandbox).

SimPy keeps the event list and the clock for you; each customer is a generator process.
python simpy_queue.py
"""
import random
from importlib.metadata import version

import simpy

LAM, MU = 0.8, 1.0


def customer(env, barista, rng, waits):
    arrived = env.now
    with barista.request() as req:  # join the queue for the single server
        yield req  # resumes when the barista is free
        waits.append(env.now - arrived)
        yield env.timeout(rng.expovariate(MU))  # service time; resource released on exit


def arrivals(env, barista, rng, waits, n):
    for _ in range(n):
        yield env.timeout(rng.expovariate(LAM))  # next arrival event
        env.process(customer(env, barista, rng, waits))


def simulate(n_customers, seed):
    rng = random.Random(seed)
    env = simpy.Environment()
    barista = simpy.Resource(env, capacity=1)
    waits = []
    env.process(arrivals(env, barista, rng, waits, n_customers))
    env.run()
    return waits


if __name__ == "__main__":
    waits = simulate(200_000, 1)
    print(f"SimPy {version('simpy')}: simulated mean wait = {sum(waits) / len(waits):.3f} min | M/M/1 Wq = {LAM / (MU * (MU - LAM)):.3f} min")
