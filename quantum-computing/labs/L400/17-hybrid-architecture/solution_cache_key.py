"""Build-task solution for lab 17: key the transpile cache on circuit STRUCTURE + target, never on parameter values.

Run: python solution_cache_key.py
A parameterised template is compiled once for a target and optimisation level; angles are bound afterwards
(Qiskit: transpile the circuit with Parameter objects, then assign_parameters per evaluation).
"""
import json

import orchestrator as lab


def cache_key(template, params, backend, opt_level=1):
    """Same structure + same target + same compiler settings -> same compiled circuit. params are ignored."""
    return (template.name, template.n, template.edges, template.p, backend.target, opt_level)


if __name__ == "__main__":
    for mode in ("sync", "batched", "session"):
        print(json.dumps(lab.run(mode, key=cache_key)))
