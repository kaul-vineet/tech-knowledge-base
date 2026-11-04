"""Reuse, don't duplicate: load modules from the source topics' labs (paths relative to this file).

microbit            labs/sim_stub (microbit, radio, labtest) and L300/14-power-budget/budget.py (FIGURES)
distributed-systems labs/L400/18-crdts-local-first/crdts.py (GCounter, LWWRegister) + helpers.size
application-arch    labs/L300/14-consumer-driven-contracts/solution/contract.py (ContractBuilder, like, verify_provider)
Every module is loaded under a unique name, so lab files that share names (solution.py, helpers.py) never clash.
The original files are never edited.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KB = HERE.parents[3]
MICROBIT = KB / "microbit" / "labs"
STUB = MICROBIT / "sim_stub"
DS = KB / "distributed-systems" / "labs"
AA = KB / "application-architecture" / "labs"

if str(STUB) not in sys.path:
    sys.path.insert(0, str(STUB))       # `import microbit`, `import radio`, `import labtest` -> the topic's stub


def load(path, name):
    """Import one file as module `name` (cached in sys.modules)."""
    if name in sys.modules:
        return sys.modules[name]
    path = Path(path)
    added = str(path.parent) not in sys.path
    if added:
        sys.path.insert(0, str(path.parent))   # its own sibling imports (e.g. crdts -> helpers)
    no_pyc, sys.dont_write_bytecode = sys.dont_write_bytecode, True   # leave other topics' folders untouched
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = no_pyc
        if added:
            sys.path.remove(str(path.parent))
    return mod


def crdts():
    return load(DS / "L400" / "18-crdts-local-first" / "crdts.py", "ds18_crdts")


def crdt_helpers():
    crdts()
    return sys.modules["helpers"]       # imported by crdts.py as `helpers`


def budget():
    return load(MICROBIT / "L300" / "14-power-budget" / "budget.py", "mb14_budget")


def contract():
    return load(AA / "L300" / "14-consumer-driven-contracts" / "solution" / "contract.py", "aa14_contract")


def radio():
    import radio as radio_stub
    return radio_stub


def labtest():
    import labtest as lt
    return lt
