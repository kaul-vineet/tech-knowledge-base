"""Lesson 17 failureLab + options: big-bang switch vs strangler facade with parallel run (in-process, fast).

Run: python failure_lab.py
"""
import fines_service as base
from app import HERE, load
from strangler import Facade, LegacyFines, ServiceFines, cutover_decision, replay
from traffic import requests


def wrong_fines(service_fn, traffic):
    """Big-bang: every member gets the service's answer. Count answers that differ from the legacy rule."""
    legacy = LegacyFines()
    return sum(service_fn(r["days_late"], r["member_type"]) != legacy.fine(r["days_late"], r["member_type"])
               for r in traffic)


def main():
    solution = load(HERE / "solution" / "fines_service.py", "fines_solution")
    traffic = list(requests())
    for label, module in [("base    ", base), ("solution", solution)]:
        facade = Facade(LegacyFines(), ServiceFines(fn=module.fine_for), mode="shadow")
        replay(facade, traffic)
        decision = cutover_decision(facade.shadow.stats)
        print(f"{label}: big-bang would charge {wrong_fines(module.fine_for, traffic)} of {len(traffic)} wrong; "
              f"shadow found {facade.shadow.stats['mismatches']} mismatches, members saw 0; cutover ready "
              f"{decision['ready']} {decision['reasons']}")
    kinds = sorted({(m["member_type"], m["days_late"]) for m in
                    _mismatches(base.fine_for, traffic)})[:6]
    print(f"mismatching (type, days late), first 6: {kinds}")


def _mismatches(fn, traffic):
    facade = Facade(LegacyFines(), ServiceFines(fn=fn), mode="shadow")
    replay(facade, traffic)
    return facade.shadow.mismatches


if __name__ == "__main__":
    main()
