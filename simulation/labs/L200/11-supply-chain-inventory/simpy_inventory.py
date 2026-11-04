"""Same (s, S) bike-shop model with SimPy 4.1.2 (pending-ci: SimPy is not installed in the sandbox).

simpy.Container holds the tubes (a bulk amount: put / get / level). Each day: deliveries at t, sales at t+0.5,
review at t+0.9. Fed the SAME streams as inventory.py, it must give the SAME cost to rounding.
python simpy_inventory.py
"""
from importlib.metadata import version

import simpy

import inventory as inv


def delivery(env, tubes, qty, day, state):
    yield env.timeout(day - env.now)  # arrives on the morning of `day`
    state["on_order"] -= qty
    yield tubes.put(qty)


def shop(env, tubes, s, S, demand, lead, state):
    yield env.timeout(0.5)
    for t, d in enumerate(demand):
        sold = min(tubes.level, int(d))
        if sold:
            yield tubes.get(sold)
        state["lost"] += int(d) - sold
        yield env.timeout(0.4)  # evening review
        position = tubes.level + state["on_order"]
        if position <= s:
            state["on_order"] += S - position
            state["orders"] += 1
            env.process(delivery(env, tubes, S - position, t + int(lead[t]), state))
        state["holding"] += inv.HOLD * tubes.level
        yield env.timeout(0.6)


def simulate(s, S, demand, lead):
    env = simpy.Environment()
    tubes = simpy.Container(env, init=S)
    state = {"on_order": 0, "orders": 0, "lost": 0, "holding": 0.0}
    env.process(shop(env, tubes, s, S, demand, lead, state))
    env.run()
    cost = state["holding"] + inv.ORDER * state["orders"] + inv.LOST * state["lost"]
    return {"cost_per_day": cost / len(demand), "orders": state["orders"], "lost": state["lost"]}


if __name__ == "__main__":
    d, lead = inv.streams(0)
    for pol in ((30, 80), (30, 90)):
        a, b = inv.simulate(*pol, d, lead), simulate(*pol, d, lead)
        print(f"SimPy {version('simpy')} s={pol[0]} S={pol[1]}: {b['cost_per_day']:.4f}/day vs numpy {a['cost_per_day']:.4f}")
