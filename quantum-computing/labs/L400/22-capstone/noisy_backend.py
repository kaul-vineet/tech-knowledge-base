"""Capstone backend adapter: lesson 17's SimulatorBackend + lesson 20's compiler + a noise model.

transpile(): routes the template onto the fake ladder (lesson 20) and records layout, CX, depth and the gate
fidelity F = product of (1 - error) over all gates. sample(): white-noise model F * ideal + (1 - F) * uniform,
then per-qubit readout flips of the measured physical qubits. test_milestones checks the white-noise model
against lesson 20's full density-matrix simulation.
"""
import numpy as np

from reuse import l17_backend, l20_compile, l20_device

mc = l17_backend.mc


def qaoa_ops(template, gamma=0.6, beta=0.4):
    ops = [("h", (q,), None) for q in range(template.n)]
    for a, b in template.edges:
        ops += [("cx", (a, b), None), ("rz", (b,), -gamma), ("cx", (a, b), None)]
    return ops + [("rx", (q,), 2 * beta) for q in range(template.n)]


def gate_fidelity(ops, dev):
    f = 1.0
    for name, qs, _ in ops:
        f *= 1 - (l20_device.cx_error(dev, *qs) if name == "cx" else dev["sq"][qs[0]] if name in ("h", "rx") else 0.0)
    return f


def readout(probs, ro):
    """Apply independent readout flips; ro[q] = flip probability of logical bit q."""
    out = probs.copy()
    for q, r in enumerate(ro):
        v = out.reshape(-1, 2, 2 ** q)
        v[:] = (1 - r) * v + r * v[:, ::-1, :]
    return out


def best_layout(template, dev, candidates=200, seed=0, budget=None):
    """Noise-aware layout by sampling placements (lesson 20 searched all 6720; 8! = 40320 is too many here)."""
    rng = np.random.default_rng(seed)
    pool = [list(range(template.n))] + [list(rng.permutation(dev["n"])[:template.n]) for _ in range(candidates)]
    best = None
    for layout in pool:
        ops, final = l20_compile.route(qaoa_ops(template), [int(q) for q in layout], dev, weighted=True)
        ops = l20_compile.cancel(ops)
        m = l20_compile.metrics(ops, final, dev)
        score = (budget is None or m["depth"] <= budget, m["esp"], -m["depth"])
        if best is None or score > best[0]:
            best = (score, [int(q) for q in layout], ops, final, m)
    return best[1:]


def probabilities(compiled, params):
    """White-noise gate model (fidelity F) followed by readout flips on the measured physical qubits."""
    n, cuts, f = compiled["template"].n, compiled["cuts"], compiled["fidelity"]
    ideal = np.abs(mc.qaoa_state(n, cuts, params)) ** 2
    return readout(f * ideal + (1 - f) / 2 ** n, compiled["ro"])


class NoisyBackend(l17_backend.SimulatorBackend):
    def __init__(self, clock, dev, depth_budget=None, **kw):
        super().__init__(clock, target=f"ladder-8:{sorted(dev['cx'].items())}", **kw)
        self.dev, self.depth_budget = dev, depth_budget

    def transpile(self, template):
        compiled = super().transpile(template)
        layout, ops, final, m = best_layout(template, self.dev, budget=self.depth_budget)
        compiled.update(layout=layout, final=final, metrics=m, fidelity=gate_fidelity(ops, self.dev),
                        ro=[self.dev["ro"][p] for p in final])
        return compiled

    def sample(self, compiled, circuit, shots):
        p = probabilities(compiled, circuit.params)
        return np.random.default_rng(circuit.seed).choice(len(p), size=shots, p=p / p.sum())


def white_noise_check():
    """TVD between this module's white-noise model and lesson 20's density-matrix simulation (drifted device,
    lesson 20's circuit and noise-aware layout). Also returns the ideal-vs-density TVD for scale."""
    from reuse import l20_noisy
    dev = l20_device.make_device(drift=l20_device.DRIFT)
    ops, final = l20_compile.route(l20_compile.logical_ops(), [5, 1, 6, 2, 3], dev, weighted=True)
    ops = l20_compile.cancel(ops)
    full, ideal = l20_noisy.distribution(ops, final, dev), l20_noisy.ideal()
    f = gate_fidelity(ops, dev)
    model = readout(f * ideal + (1 - f) / len(ideal), [dev["ro"][p] for p in final])
    return {"tvd_model": round(float(0.5 * np.abs(model - full).sum()), 4),
            "tvd_ideal": round(float(0.5 * np.abs(ideal - full).sum()), 4)}
