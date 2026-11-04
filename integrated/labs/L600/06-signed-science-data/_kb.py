"""Reuse, don't duplicate: load modules from the source topics' labs by path (never edited, never copied).
Several labs use the same module names (helpers, inputs, registry), so each load runs with the lab folder first on
sys.path and the clashing names popped from sys.modules before and restored after (the distributed capstone's loader)."""
import importlib.util
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[4]
CLASH = ("helpers", "inputs", "votable", "registry", "units", "signatures", "release", "release_sign")


def load(relpath, alias):
    path = KB / relpath
    saved_path, saved = list(sys.path), {m: sys.modules.pop(m) for m in CLASH if m in sys.modules}
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(alias, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path[:] = saved_path
        for m in CLASH:
            sys.modules.pop(m, None)
        sys.modules.update(saved)


UNITS = load("astronomy/labs/L100/04-units-magnitudes/units.py", "kb06_units")  # parallax -> pc, distance modulus
INPUTS = load("astronomy/labs/L400/21-open-data-practice/inputs.py", "kb06_inputs")  # Gaia-like rows + real credits
OPEN_DATA = load("astronomy/labs/L400/21-open-data-practice/solution/release.py", "kb06_open_data")  # licence rule
OPEN_DATA_SHIPPED = load("astronomy/labs/L400/21-open-data-practice/release.py", "kb06_open_data_shipped")  # NC bug
SIGNATURES = load("cryptography/labs/L200/07-ed25519-signatures/signatures.py", "kb06_signatures")  # RFC 8032 vector
SUPPLY = load("cryptography/labs/L300/14-supply-chain-signing/release_sign.py", "kb06_supply")  # key_id, Rejected
REGISTRY = load("cryptography/labs/L400/17-crypto-agility/registry.py", "kb06_registry")  # Ed25519 + ML-DSA-65 policy
SIM = load("distributed-systems/labs/L400/17-consistency-quorums/helpers.py", "kb06_sim")  # seeded event loop
