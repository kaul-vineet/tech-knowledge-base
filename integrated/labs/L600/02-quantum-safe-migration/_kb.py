"""Reuse the source topics' labs by import - never copy, never edit them.

Folders are APPENDED to sys.path, so this lab's own modules always win a name clash. Each entry says what is reused.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KB = HERE.parents[3]
REUSED = {
    "quantum-computing/labs/_shared": "qsim.statevector - numpy statevector simulator (Qiskit bit order)",
    "quantum-computing/labs/L500/25-algorithms-and-complexity": "theorems - order(), split(), qft_ops(), "
                                                               "inverse_ops(), order_finding_distribution()",
    "quantum-computing/labs/L400/19-resource-estimation": "estimate_lab.rsa_logical - Gidney-Ekera formulas",
    "quantum-computing/labs/L400/21-post-quantum-migration": "solution_scanner.scan_python - AST crypto inventory",
    "cryptography/labs/L400/18-post-quantum": "pq_hybrid + solution_strict - X25519MLKEM768, no silent fallback",
    "cryptography/labs/L400/17-crypto-agility": "agility_lint.scan_source - no hard-coded algorithms",
    "application-architecture/labs/L400/20-evolutionary-migrations": "flags.Flags + gate_flags - owned, expiring flags",
}
sys.dont_write_bytecode = True        # never write __pycache__ into the other topics' lab folders
for folder in REUSED:
    path = str(KB / folder)
    if path not in sys.path:
        sys.path.append(path)


def load_file(path, alias):
    """Import a module from a file under a unique name (used for service variants that share a file name)."""
    spec = importlib.util.spec_from_file_location(alias, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
