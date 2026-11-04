"""Build-task solution for lab 20: noise-aware layout. Run: python solution_layout.py

Try every placement of the 5 logical qubits on the 8 physical ones (8P5 = 6720), route each with the
most-reliable-path rule, cancel CX pairs, and keep the highest expected fidelity (ESP) whose depth fits the
budget - the idea behind Qiskit's VF2PostLayout and level-3 noise-adaptive layout, done by brute force.
"""
import itertools
import json

import compile_lab as lab
import device as D


def choose_layout(dev, budget=lab.DEPTH_BUDGET):
    best = None
    for layout in itertools.permutations(range(dev["n"]), lab.NQ):
        _, _, m = lab.compile_circuit(dev, list(layout), weighted=True, optimise=True)
        score = (m["depth"] <= budget, m["esp"], -m["depth"])
        if best is None or score > best[0]:
            best = (score, list(layout))
    return best[1]


if __name__ == "__main__":
    for label, dev in (("calibrated", D.make_device()), ("drifted (1,2) = 15%", D.make_device(drift=D.DRIFT))):
        layout = choose_layout(dev)
        _, final, m = lab.compile_circuit(dev, layout, weighted=True, optimise=True)
        print(json.dumps({"device": label, "option": "C noise-aware layout + reliable routing + cancel", "layout": layout,
                          **m, "within_depth_budget": m["depth"] <= lab.DEPTH_BUDGET}))
