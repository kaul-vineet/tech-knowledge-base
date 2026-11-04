"""Lesson 12 failureLab: kill the projector at a seeded event, restart it, compare the view with the events.

Run: python failure_lab.py   (base projector.py first, then solution/projector.py)
"""
import importlib.util
import pathlib
import random

import projector as base
from app import workload
from write_model import EventStore, LoanCommands, LoanRuleViolation

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seeded_history(seed=12):
    store = EventStore()
    commands = LoanCommands(store)
    for action, member, book in workload(seed):
        try:
            getattr(commands, action)(member, book)
        except LoanRuleViolation:
            pass
    return store


def crash_and_restart(module, seed=12):
    store = seeded_history(seed)
    last = store.read_after(0)[-1][0]
    crash_seq = random.Random(seed).randint(1, last)  # fault: seeded, so every run dies at the same event
    first = module.Projector(store, log=lambda record: None, crash_at_seq=crash_seq)
    try:
        first.run_once()
    except module.SimulatedCrash as exc:
        crashed = str(exc)
    restarted = module.Projector(store, read_db=first.db, log=lambda record: None)  # new process, same read DB
    restarted.run_once()
    return store, restarted, crashed, last


def main():
    for label, module in [("base     projector.py", base),
                          ("solution projector.py", load(HERE / "solution" / "projector.py", "projector_solution"))]:
        store, projector, crashed, last = crash_and_restart(module)
        problems = module.drift(store, projector.db, module.Projector)
        print(f"{label}: {crashed}; restarted at position {projector.position()} of {last}; "
              f"drift: {len(problems)} row(s)")
        for problem in problems:
            print(f"    {problem}")
        if problems:
            projector.rebuild()
            print(f"    recovery: rebuild() -> drift {module.drift(store, projector.db, module.Projector)}")


if __name__ == "__main__":
    main()
