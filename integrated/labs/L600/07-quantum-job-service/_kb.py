"""Reuse, don't copy: load the source topics' lab modules from their own folders (paths relative to this file).

Every module is loaded by file path under a unique name, so lab files that share a name (helpers.py,
backend.py) cannot clash. Nothing here edits the original labs.
"""
import importlib.util
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[4]
QSHARED = KB / "quantum-computing" / "labs" / "_shared"
if str(QSHARED) not in sys.path:
    sys.path.insert(0, str(QSHARED))          # qsim / qopt: the quantum topic's numpy simulators


def load(relpath, name):
    if name in sys.modules:
        return sys.modules[name]
    path = KB / relpath
    folder = str(path.parent)
    sys.path.insert(0, folder)                # sibling imports (e.g. election.py -> helpers.py)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(folder)
    return mod


from qsim import density as dm  # noqa: E402
from qsim import statevector as sv  # noqa: E402

qasm = load("quantum-computing/labs/L100/05-openqasm-portability/crosscheck_qasm_numpy.py", "q05_qasm_reader")
noise = load("quantum-computing/labs/L300/12-noise-models/noise_lab.py", "q12_noise_lab")
mitigation = load("quantum-computing/labs/L300/13-error-mitigation/mitigation_lab.py", "q13_mitigation_lab")
q17 = load("quantum-computing/labs/L400/17-hybrid-architecture/backend.py", "q17_backend")
election = load("distributed-systems/labs/L200/07-leader-election-leases/election.py", "ds07_election")
resilience = load("application-architecture/labs/L300/13-resilience-patterns/resilience.py", "aa13_resilience")
slo = load("application-architecture/labs/L300/15-slo-error-budgets/slo.py", "aa15_slo")
capacity = load("application-architecture/labs/L400/21-capacity-planning/capacity.py", "aa21_capacity")
