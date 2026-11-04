"""Reuse, don't duplicate: load modules from other topics' labs by file location (never edited, never copied).

Several labs ship modules with the same name (`helpers`, `solution_strict`, `registry` ...). load() evicts a cached
module of that name if it came from a DIFFERENT lab folder, imports the wanted one with its folder first on sys.path,
and caches it under a private alias, so `load("raft", "helpers")` and `load("idem", "helpers")` never clash."""
import importlib
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[4]  # kb/integrated/labs/L600/<this lab>/_kb.py -> kb/
LABS = {
    "pq": "cryptography/labs/L400/18-post-quantum",                     # hybrid X25519MLKEM768, strict client
    "agility": "cryptography/labs/L400/17-crypto-agility",              # algorithm registry, canonical AAD
    "group": "cryptography/labs/L400/20-group-e2ee",                    # epoch-secret KDF
    "misuse": "cryptography/labs/L300/15-testable-misuse",              # offline nonce-reuse scan
    "prob": "cryptography/labs/L500/24-probability",                    # birthday bounds
    "raft": "distributed-systems/labs/L300/12-raft-replicated-log",     # Raft node + simulated network
    "idem": "distributed-systems/labs/L100/05-idempotency-keys",        # Idempotency-Key format
    "outbox": "application-architecture/labs/L200/09-event-driven-integration",  # outbox schema + relay
    "contract": "application-architecture/labs/L300/14-consumer-driven-contracts",  # like() matchers
}


def lab_dir(lab: str) -> Path:
    return KB / LABS[lab]


def load(lab: str, module: str):
    alias = f"_kb_{lab}_{module}"
    if alias in sys.modules:
        return sys.modules[alias]
    folder = lab_dir(lab).resolve()
    for stem in (p.stem for p in folder.glob("*.py")):
        cached = sys.modules.get(stem)
        if cached is not None and Path(getattr(cached, "__file__", "") or ".").resolve().parent != folder:
            del sys.modules[stem]  # same name, other lab: evict (modules that imported it keep their reference)
    sys.path.insert(0, str(folder))
    saved, sys.dont_write_bytecode = sys.dont_write_bytecode, True  # never write __pycache__ into another topic
    try:
        mod = importlib.import_module(module)
    finally:
        sys.path.remove(str(folder))
        sys.dont_write_bytecode = saved
    sys.modules[alias] = mod
    return mod
