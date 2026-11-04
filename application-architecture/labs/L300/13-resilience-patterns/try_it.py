"""Try it (lesson 13): a timeout longer than the hang, and a breaker without a bulkhead. Run: python try_it.py"""
import importlib.util
import pathlib

from deps import Catalogue
from failure_lab import run_waves, summary

HERE = pathlib.Path(__file__).resolve().parent


def fresh_base():
    spec = importlib.util.spec_from_file_location("loans_service_copy", HERE / "loans_service.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def try_1_long_timeout():
    module = fresh_base()
    module.TIMEOUT_S = 2.0  # longer than the 1 s hang
    records = run_waves(module, Catalogue(mode="slow", hang_s=1.0))
    slow = sorted(r["ms"] for r in records)
    print(f"[1] timeout 2.0 s: {sum(r['ok'] for r in records)}/{len(records)} ok, "
          f"{sum(r['degraded'] for r in records)} degraded, fastest {slow[0]:.0f} ms, slowest {slow[-1]:.0f} ms")


def try_2_breaker_alone():
    transitions = []
    records = run_waves(fresh_base(), Catalogue(mode="slow"),
                        log=lambda r: transitions.append(r["to"]) if r["evt"] == "breaker" else None)
    print(f"[2] breaker went {' -> '.join(['closed'] + transitions)}; still {summary(records)}")


if __name__ == "__main__":
    try_1_long_timeout()
    try_2_breaker_alone()
