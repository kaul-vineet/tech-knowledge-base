"""Stub of the micro:bit V2 MicroPython `power` module (L300 lab 14).

API per https://microbit-micropython.readthedocs.io/en/v2-docs/power.html
(cross-checked with https://python.microbit.org/v/3/api/power):
  deep_sleep(ms=None, wake_on=None, run_every=True)  sleep, then resume where it left off
  off()                                              lowest power; wakes only by reset/USB, restarts
Stub behaviour (no real power saving, no current measurement):
  * deep_sleep moves the stub clock forward like sleep() and records
    ("deep_sleep", start_ms, slept_ms) in `log`; a button in wake_on that is
    pressed (timeline event) ends the sleep early.
  * ms=None needs wake_on in the stub (the real board would wait for reset/USB).
  * off() records ("off", t) and raises PowerOff, because the real call never returns.
  * run_every callbacks are not modelled.
"""
import microbit

log = []


class PowerOff(Exception):
    """Raised by the stub's off(): on the board the program would stop here."""


def _reset():
    del log[:]


def deep_sleep(ms=None, wake_on=None, run_every=True):
    if ms is None and wake_on is None:
        raise ValueError("stub: deep_sleep needs ms or wake_on")
    buttons = wake_on if isinstance(wake_on, (tuple, list)) else ([wake_on] if wake_on else [])
    for b in buttons:
        b._was = False
    start = microbit.running_time()
    target = start + int(ms) if ms is not None else start + 10 ** 9

    def woken():
        return any(getattr(b, "_was", False) for b in buttons)

    end = microbit._advance_to(target, stop=woken if buttons else None)
    log.append(("deep_sleep", start, end - start))


def off():
    log.append(("off", microbit.running_time()))
    raise PowerOff()
