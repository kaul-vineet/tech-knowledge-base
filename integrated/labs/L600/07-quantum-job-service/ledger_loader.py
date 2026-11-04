"""Pick the ledger (BUILD_TARGET switch, as in the L200-L400 labs).

  default                  -> solution/ledger.py (reference)
  BUILD_TARGET=mine        -> my_ledger.py next to this file (your build task)
  fault 'lease-expiry'     -> ledger.py (the shipped, unfixed ledger)
"""
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ledger_class(fault=None):
    if fault == "lease-expiry":
        return _load(HERE / "ledger.py", "ledger_shipped").Ledger
    if os.environ.get("BUILD_TARGET") == "mine":
        return _load(HERE / "my_ledger.py", "my_ledger").Ledger
    return _load(HERE / "solution" / "ledger.py", "ledger_solution").Ledger
