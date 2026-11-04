"""Lab 20 - error-aware compilation: layout, routing and optimisation on a fake 8-qubit ladder device.

Run:  python compile_lab.py      (pure Python + numpy; prints JSON lines)
Circuit: lesson 14's 5-node QAOA p=1 (a triangle, so it never fits a ladder without SWAPs).
Options compared by expected fidelity ESP = product of (1 - error) over every gate and measurement
(Nishio et al. 2020's estimated success probability), CX count and depth; noisy_check.py confirms that ESP
tracks the simulated output fidelity. The FAULT: choose_layout() is trivial and blind to today's drifted edge.
Qiskit path (same error map in a Target, optimization_level 0-3): python compile_qiskit.py   (CI)
"""
import itertools
import json

import device as D

GRAPH = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]
GAMMA, BETA, NQ = 0.6283, 0.3927, 5
DEPTH_BUDGET = 22                      # the fitness threshold (logical depth 17 + room for one SWAP)


def logical_ops():
    ops = [("h", (q,), None) for q in range(NQ)]
    for a, b in GRAPH:
        ops += [("cx", (a, b), None), ("rz", (b,), -GAMMA), ("cx", (a, b), None)]   # RZZ(-gamma) per edge
    return ops + [("rx", (q,), 2 * BETA) for q in range(NQ)]


def route(ops, layout, dev, weighted):
    """Insert SWAPs (3 CX each) along the shortest - or most reliable - path until both qubits are adjacent."""
    _, nxt = D.all_pairs(dev, weighted)
    phys, out = dict(enumerate(layout)), []
    for name, qs, arg in ops:
        if name == "cx":
            a, b = phys[qs[0]], phys[qs[1]]
            hops = D.path(nxt, a, b)
            for u, v in zip(hops, hops[1:-1]):                           # move a next to b
                out += [("cx", (u, v), None), ("cx", (v, u), None), ("cx", (u, v), None)]
                inv = {p: l for l, p in phys.items()}
                lu, lv = inv.get(u), inv.get(v)
                phys[lu] = v
                if lv is not None:
                    phys[lv] = u
            out.append(("cx", (phys[qs[0]], phys[qs[1]]), None))
        else:
            out.append((name, tuple(phys[q] for q in qs), arg))
    return out, [phys[q] for q in range(len(layout))]


def cancel(ops):
    """Optimisation: drop back-to-back identical CX pairs (CX.CX = I) on the same qubits."""
    out = []
    for op in ops:
        if op[0] == "cx" and out:
            last = next((i for i in range(len(out) - 1, -1, -1) if set(out[i][1]) & set(op[1])), None)
            if last is not None and out[last] == op:
                out.pop(last)
                continue
        out.append(op)
    return out


def metrics(ops, final, dev):
    esp, level = 1.0, [0] * dev["n"]
    for name, qs, _ in ops:
        esp *= 1 - (D.cx_error(dev, *qs) if name == "cx" else dev["sq"][qs[0]] if name in ("h", "rx") else 0.0)
        start = max(level[q] for q in qs) + 1
        for q in qs:
            level[q] = start
    for q in final:
        esp *= 1 - dev["ro"][q]                                          # readout of the measured qubits
    return {"esp": round(esp, 4), "cx": sum(o[0] == "cx" for o in ops), "depth": max(level)}


def choose_layout(dev):
    """NAIVE: logical qubit i -> physical qubit i, whatever today's calibration says."""
    return list(range(NQ))


def compile_circuit(dev, layout, weighted=False, optimise=False):
    ops, final = route(logical_ops(), layout, dev, weighted)
    ops = cancel(ops) if optimise else ops
    return ops, final, metrics(ops, final, dev)


def dense_layout(dev):
    """Degree-based: map the busiest logical qubits to the best-connected physical ones (no error data)."""
    deg = {q: sum(q in e for e in D.EDGES) for q in range(dev["n"])}
    ldeg = sorted(range(NQ), key=lambda q: -sum(q in e for e in GRAPH))
    phys = sorted(range(1, 7), key=lambda q: -deg[q]) + [0, 7]
    layout = [0] * NQ
    for lq, pq in zip(ldeg, phys):
        layout[lq] = pq
    return layout


if __name__ == "__main__":
    for label, dev in (("calibrated", D.make_device()), ("drifted (1,2) = 15%", D.make_device(drift=D.DRIFT))):
        for option, layout, weighted, opt in (("A trivial + hop routing", choose_layout(dev), False, False),
                                              ("B dense + hop routing + cancel", dense_layout(dev), False, True)):
            _, final, m = compile_circuit(dev, layout, weighted, opt)
            print(json.dumps({"device": label, "option": option, "layout": layout, **m,
                              "within_depth_budget": m["depth"] <= DEPTH_BUDGET}))
    print("logical circuit:", metrics(logical_ops(), range(NQ), {"n": NQ, "cx": {e: 0 for e in itertools.combinations(range(NQ), 2)},
                                                                    "sq": [0] * NQ, "ro": [0] * NQ}))
