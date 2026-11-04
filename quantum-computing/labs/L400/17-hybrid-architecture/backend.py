"""Backend adapter for lab 17: the interface the orchestrator codes against, plus a seeded simulator behind it.

A real provider (Qiskit primitives, a cloud QPU) would implement the same three methods:
transpile(template) -> compiled, run(compiled_circuits, shots) -> list of samples, open_session()/close_session().
Time is a FakeClock: queue waits, execution and retries advance it deterministically, so tests never sleep.
"""
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qopt import maxcut as mc  # noqa: E402


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def sleep(self, seconds):
        self.now += seconds


class TransientBackendError(RuntimeError):
    """Retryable: queue hiccup, lost connection, calibration pause."""


@dataclass(frozen=True)
class Template:
    """Circuit STRUCTURE without parameter values (what a transpiler sees)."""
    name: str
    n: int
    edges: tuple
    p: int


@dataclass(frozen=True)
class Circuit:
    template: Template
    params: tuple
    seed: int          # per-circuit seed chosen by the orchestrator: a retry reproduces the same samples


@dataclass
class Costs:            # modelled seconds (illustrative, not a vendor's numbers)
    queue_s: float = 2.0          # wait before a job starts outside a session
    per_circuit_s: float = 0.02   # execution per circuit (shots included)
    transpile_s: float = 0.5      # compile one template for the target
    session_gap_s: float = 0.1    # job start latency inside an open session
    interactive_ttl_s: float = 60.0


class SimulatorBackend:
    def __init__(self, clock, target="line-8", costs=None, fail_jobs=(), max_circuits=300):
        self.clock, self.target, self.costs = clock, target, costs or Costs()
        self.fail_jobs, self.max_circuits = set(fail_jobs), max_circuits
        self.jobs = self.attempts = self.transpiles = 0
        self.qpu_s = 0.0
        self.session = None            # [opened_at, last_job_end, jobs_in_session]

    def transpile(self, template):
        self.transpiles += 1
        self.clock.sleep(self.costs.transpile_s)
        return {"template": template, "target": self.target, "cuts": mc.cut_values(template.n, template.edges)}

    def open_session(self):
        self.session = [self.clock.now, self.clock.now, 0]

    def close_session(self):
        opened, self.session = self.session[0], None
        return self.clock.now - opened            # a session bills its whole window

    def run(self, compiled, circuits, shots):
        """One job = a list of circuits. Raises TransientBackendError on seeded attempts."""
        if len(circuits) > self.max_circuits:
            raise ValueError(f"job has {len(circuits)} circuits > max_circuits {self.max_circuits}")
        self.attempts += 1
        live = bool(self.session) and self.session[2] > 0 and self.clock.now - self.session[1] <= self.costs.interactive_ttl_s
        self.clock.sleep(self.costs.session_gap_s if live else self.costs.queue_s)   # session: skip the queue
        if self.attempts in self.fail_jobs:
            raise TransientBackendError(f"attempt {self.attempts} failed")
        self.jobs += 1
        run_s = self.costs.per_circuit_s * len(circuits)
        self.clock.sleep(run_s)
        self.qpu_s += run_s
        if self.session:
            self.session[1:] = [self.clock.now, self.session[2] + 1]
        return [self.sample(compiled, c, shots) for c in circuits]

    def sample(self, compiled, circuit, shots):
        """Ideal sampler; a noisy adapter overrides only this method (capstone)."""
        n, cuts = compiled["template"].n, compiled["cuts"]
        return mc.sample(n, cuts, circuit.params, shots, np.random.default_rng(circuit.seed))
