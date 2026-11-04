"""Helpers shared by the lab unit tests (CPython only).

load_lab(): one board. load_boards(): several boards sharing a radio "air" (L200 lab 07;
L300 lab 12 passes a seeded faulty Air).
"""
import contextlib
import importlib.util
import io
import os
import sys
import types

STUB_DIR = os.path.dirname(os.path.abspath(__file__))
if STUB_DIR not in sys.path:
    sys.path.insert(0, STUB_DIR)

import microbit  # noqa: E402  (the stub)


def load_lab(lab_dir, filename="main.py"):
    """Reset the stub and import a lab's main.py as a fresh module.

    The module name is not "__main__", so the lab's `while True` loop
    (guarded by `if __name__ == "__main__":`) does not start.
    """
    microbit._reset()
    path = os.path.join(lab_dir, filename)
    name = "lab_" + os.path.basename(os.path.abspath(lab_dir)).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def serial():
    """Capture print() output, like the simulator's serial panel."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        yield buf


class Board:
    """One stub micro:bit with its own `microbit` module copy and radio endpoint."""

    def __init__(self, name, mb, radio_ep, lab):
        self.name, self.mb, self.radio, self.lab = name, mb, radio_ep, lab


def load_boards(lab_dir, names=("A", "B"), filename="main.py", sources=None, air=None):
    """Load the same lab on several independent stub boards sharing one radio Air.

    Each board gets a fresh copy of the microbit stub (own buttons, display,
    clock, sensors) and its own radio.Endpoint; the lab module binds to them
    because they sit in sys.modules while main.py is imported.
    sources: optional {board name: program text} to run edited code on one board.
    air: optional radio.Air(loss=..., dup=..., reorder=..., corrupt=..., seed=...) (L300 faults).
    """
    import radio as radio_stub
    air = air if air is not None else radio_stub.Air()
    boards = []
    saved = {k: sys.modules.get(k) for k in ("microbit", "radio")}
    try:
        for name in names:
            spec = importlib.util.spec_from_file_location(
                "microbit_board_" + name, os.path.join(STUB_DIR, "microbit", "__init__.py"))
            mb = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mb)
            ep = radio_stub.Endpoint(air, name, mb.running_time)
            sys.modules["microbit"], sys.modules["radio"] = mb, ep
            path = os.path.join(lab_dir, filename)
            if sources and name in sources:
                lab = types.ModuleType("lab_board_" + name)
                lab.__file__ = path
                exec(compile(sources[name], path, "exec"), lab.__dict__)
            else:
                lspec = importlib.util.spec_from_file_location("lab_board_" + name, path)
                lab = importlib.util.module_from_spec(lspec)
                lspec.loader.exec_module(lab)
            boards.append(Board(name, mb, ep, lab))
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return boards
