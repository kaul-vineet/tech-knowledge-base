"""Drive lab 13 on the stub with seeded button taps on a timeline (CPython only).

taps(seed): 8 quick taps (150 ms each, >= 600 ms apart) in the first 10 s.
run_blocking(): calls main.py's loop_once() (which sleeps 1 s) until the time is up.
run_scheduler(): calls run_once() in a busy loop; the stub clock moves 1 ms per pass
(on the board the loop spins as fast as MicroPython runs).
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

TAP_MS = 150


def taps(seed=13, n=8, start=200, gap=600, hold=TAP_MS):
    rng, t, out = random.Random(seed), start, []
    for _ in range(n):
        t += rng.randrange(gap, gap + 500)
        out.append((t, hold))
    return out


def schedule(presses):
    for t, hold in presses:
        microbit._at(t, microbit.button_a.press)
        microbit._at(t + hold, microbit.button_a.release)


def run_blocking(presses, until_ms=10000, filename="main.py", source=None):
    lab = load_lab(HERE, filename) if source is None else _exec(source)
    schedule(presses)
    state = lab.new_state()
    with serial() as out:
        while microbit.running_time() < until_ms:
            lab.loop_once(state)
    return state, out.getvalue()


def run_scheduler(presses, until_ms=10000, filename="solution.py", source=None, setup=None):
    lab = load_lab(HERE, filename) if source is None else _exec(source)
    schedule(presses)
    state, sched = lab.new_state(), lab.new_scheduler()
    if setup:
        setup(lab, sched)
    with serial() as out:
        while microbit.running_time() < until_ms:
            lab.run_once(sched, state)
            microbit._advance(1)
    return state, sched, out.getvalue()


def run_any(presses, until_ms=10000, filename="solution.py"):
    """Counted taps for either design (blocking loop_once or scheduler run_once)."""
    probe = load_lab(HERE, filename)
    if hasattr(probe, "run_once"):
        return run_scheduler(presses, until_ms, filename)[0]["taps"]
    return run_blocking(presses, until_ms, filename)[0]["taps"]


def _exec(source):
    import types
    microbit._reset()
    mod = types.ModuleType("lab13_variant")
    exec(compile(source, os.path.join(HERE, "solution.py"), "exec"), mod.__dict__)
    return mod


def tap_lines(text):
    return [l for l in text.splitlines() if l.startswith("tap ")]


if __name__ == "__main__":
    p = taps()
    print("taps at (ms):", [t for t, _ in p])
    state, out = run_blocking(p)
    print("main.py     (sleep 1000): counted %d of %d" % (state["taps"], len(p)))
    state, sched, out = run_scheduler(p)
    print("solution.py (scheduler) : counted %d of %d; stats %s" % (state["taps"], len(p), sched["stats"]))
