"""Lab 17 - hybrid quantum-classical architecture: orchestrator + job queue + backend adapter.

Run:  python orchestrator.py      (numpy simulator behind the adapter; modelled time on a FakeClock)
Workload: multi-start SPSA on QAOA p=1 for an 8-node 3-regular graph (4 starts x 2 circuits per iteration).
Compares three execution designs - sync loop, batched jobs, session + batches - by modelled wall time,
billed seconds, jobs, circuits and transpiles. Prints one JSON line per design.
SDK path (Qiskit StatevectorSampler, one PUB list per iteration): python sampler_qiskit.py   (CI)
"""
import json
import time

import numpy as np

from backend import Circuit, FakeClock, SimulatorBackend, Template, TransientBackendError, mc

GRAPH = mc.regular_graph(8, 3, seed=7)
TEMPLATE = Template("qaoa-maxcut", 8, tuple(GRAPH), 1)
DEFAULT_MODE = "batched"          # the decision recorded in docs/adr/0001-batched-jobs.md
WORKLOAD = {"starts": 4, "iters": 30, "shots": 512, "seed": 2026, "classical_s": 0.05}


def cache_key(template, params, backend, opt_level=1):
    """NAIVE: the bound parameter values are part of the key, so every new angle misses the cache."""
    return (template, tuple(np.round(params, 12)), backend.target, opt_level)


class Orchestrator:
    def __init__(self, backend, clock, mode=DEFAULT_MODE, key=cache_key, max_attempts=4, backoff_s=1.0):
        self.backend, self.clock, self.mode, self.key = backend, clock, mode, key
        self.max_attempts, self.backoff_s = max_attempts, backoff_s
        self.cache, self.hits, self.retries = {}, 0, 0

    def compiled(self, circuit):
        k = self.key(circuit.template, circuit.params, self.backend)
        if k in self.cache:
            self.hits += 1                                     # transpile cache: compile once per structure
        else:
            self.cache[k] = self.backend.transpile(circuit.template)
        return self.cache[k]

    def submit(self, circuits, shots):
        """One job with retries: exponential backoff on the fake clock; same seeds -> same samples (idempotent)."""
        compiled = [self.compiled(c) for c in circuits][0]
        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.backend.run(compiled, circuits, shots)
            except TransientBackendError:
                if attempt == self.max_attempts:
                    raise
                self.retries += 1
                self.clock.sleep(self.backoff_s * 2 ** (attempt - 1))

    def evaluate(self, circuits, shots):
        """Job-queue policy: 'sync' = one job per circuit; 'batched'/'session' = one job per optimizer step."""
        if self.mode == "sync":
            samples = [s for c in circuits for s in self.submit([c], shots)]
        else:
            samples = self.submit(circuits, shots)
        t = circuits[0].template
        cuts = mc.cut_values(t.n, t.edges)
        return [float(cuts[s].mean()) for s in samples]


def spsa_multistart(orch, w=WORKLOAD, a=0.2, c=0.15, template=TEMPLATE):
    """Classical side: SPSA ascent on <C> from several seeded starts; the orchestrator hides execution."""
    rng = np.random.default_rng(w["seed"])
    x = rng.uniform(0.1, 1.5, size=(w["starts"], 2))
    for k in range(w["iters"]):
        ak, ck = a / (k + 1 + 3) ** 0.602, c / (k + 1) ** 0.101          # Spall's gain exponents
        delta = rng.choice([-1.0, 1.0], size=x.shape)
        circuits = [Circuit(template, tuple(x[i] + sgn * ck * delta[i]), seed=w["seed"] + 1000 * k + 2 * i + (sgn > 0))
                    for i in range(w["starts"]) for sgn in (+1, -1)]
        values = orch.evaluate(circuits, w["shots"])
        for i in range(w["starts"]):
            x[i] += ak * (values[2 * i] - values[2 * i + 1]) / (2 * ck) * delta[i]
        orch.clock.sleep(w["classical_s"])                                  # classical update time
    return x


def run(mode, key=cache_key, fail_jobs=(), w=WORKLOAD):
    clock = FakeClock()
    backend = SimulatorBackend(clock, fail_jobs=fail_jobs)
    orch = Orchestrator(backend, clock, mode, key)
    t0 = time.perf_counter()
    if mode == "session":
        backend.open_session()
    x = spsa_multistart(orch, w)
    billed = backend.close_session() if mode == "session" else backend.qpu_s
    cuts = mc.cut_values(TEMPLATE.n, TEMPLATE.edges)
    best = max(mc.expectation(TEMPLATE.n, cuts, xi) for xi in x) / cuts.max()
    return {"mode": mode, "wall_s": round(clock.now, 2), "billed_s": round(billed, 2), "jobs": backend.jobs,
            "circuits": w["iters"] * 2 * w["starts"], "transpiles": backend.transpiles, "cache_hits": orch.hits,
            "retries": orch.retries, "best_ratio": round(best, 4), "local_cpu_s": round(time.perf_counter() - t0, 2)}


if __name__ == "__main__":
    for mode in ("sync", "batched", "session"):
        print(json.dumps(run(mode)))
    print(json.dumps({**run("batched", fail_jobs=(3, 4, 17)), "note": "seeded transient failures on attempts 3, 4, 17"}))
