"""Simulated quantum backends: same interface, different noise, latency, failure rate and capacity.

Noise model = the quantum topic's L300 #12 model (depolarising after each gate, amplitude damping, readout flips),
run on its density-matrix simulator; every published calibration gets a version number (drift -> version + 1).
Values are illustrative, not any vendor's device. Time is modelled (seconds on a fake clock), never slept.
"""
import random
import zlib
from dataclasses import dataclass, field

import numpy as np

from _kb import dm, noise, q17
from canon import gate_counts, to_sv

TransientBackendError = q17.TransientBackendError


@dataclass
class Backend:
    name: str
    cal: dict                      # current calibration: p1, p2, damp, p01, p10 (L300 #12 keys)
    latency_s: float               # modelled execution time of one chunk
    slots: int                     # bulkhead: concurrent chunks this backend may run
    fail_rate: float = 0.0         # transient rejections at job start
    slow_rate: float = 0.0         # share of chunks that run slow_factor x longer
    slow_factor: float = 1.0
    seed: int = 0
    version: int = 1
    history: dict = field(default_factory=dict)
    outages: list = field(default_factory=list)   # [(start, end)]: every start fails (seeded fault)
    slow_starts: tuple = ()                        # seeded fault: these start numbers (1, 2, ...) run slow_factor x longer

    def __post_init__(self):
        self.history[self.version] = dict(self.cal)
        self.rng, self._exact, self.starts = random.Random(f"{self.name}-{self.seed}"), {}, 0

    def recalibrate(self, cal):
        self.version += 1
        self.cal = self.history[self.version] = dict(cal)

    def estimated_fidelity(self, n, ops):
        """Cheap product estimate used by the scheduler (an ESP-style score, not the true fidelity)."""
        c = self.cal
        n1, n2 = gate_counts(ops)
        f = (1 - c["p1"]) ** n1 * (1 - c["p2"]) ** n2 * (1 - c["damp"]) ** (n1 + 2 * n2)
        return f * (1 - (c["p01"] + c["p10"]) / 2) ** n

    def expected_latency(self):
        return self.latency_s * (1 + self.slow_rate * (self.slow_factor - 1)) / (1 - self.fail_rate)

    def start(self, now):
        """Admission of one chunk: raises TransientBackendError (retryable) or returns its run time."""
        if self.rng.random() < self.fail_rate or any(a <= now < b for a, b in self.outages):
            raise TransientBackendError(f"{self.name}: job rejected at t={now:.1f}")
        self.starts += 1
        slow = self.starts in self.slow_starts or self.rng.random() < self.slow_rate
        return self.latency_s * (self.slow_factor if slow else 1.0)

    def exact_probs(self, n, ops, version):
        key = (n, ops, version)
        if key not in self._exact:
            c = self.history[version]
            rho = dm.run(n, noise.noisy_steps(to_sv(ops), c))
            self._exact[key] = dm.readout_matrix(c["p01"], c["p10"], n) @ dm.probabilities(rho)
        return self._exact[key]

    def execute(self, n, ops, version, shots, seed, chunk):
        """Same (circuit, backend, version, seed, chunk) -> same counts: a re-executed attempt reproduces its samples;
        different circuits or backends never share a random stream (their errors stay independent)."""
        rng = np.random.default_rng([seed, chunk, version, zlib.crc32(repr(ops).encode()), zlib.crc32(self.name.encode())])
        return dm.sample(self.exact_probs(n, ops, version), shots, rng)

    def readout(self, n, version):
        c = self.history[version]
        return dm.readout_matrix(c["p01"], c["p10"], n)


def fleet(seed=7):
    return [
        Backend("fast-noisy", {"p1": 0.004, "p2": 0.04, "damp": 0.01, "p01": 0.03, "p10": 0.05},
                latency_s=1.0, slots=4, fail_rate=0.02, seed=seed),
        Backend("slow-clean", {"p1": 0.0005, "p2": 0.005, "damp": 0.002, "p01": 0.01, "p10": 0.015},
                latency_s=3.0, slots=2, fail_rate=0.02, slow_rate=0.15, slow_factor=5.0, seed=seed),
        Backend("flaky-mid", {"p1": 0.002, "p2": 0.02, "damp": 0.005, "p01": 0.02, "p10": 0.03},
                latency_s=1.5, slots=3, fail_rate=0.25, seed=seed),
    ]
