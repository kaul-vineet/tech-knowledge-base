# Lab 14 - temperature logger (AFTER: adaptive sampling + deep sleep).
# Sample fast only while the temperature is changing; when it is steady, double
# the interval up to MAX_MS. Between samples the board goes into Deep Sleep
# (power.deep_sleep), which turns the on-board components off. Trade-off: a
# change is noticed up to MAX_MS late, and a change shorter than the current
# interval can be missed entirely.
from microbit import *
import log
import power

MIN_MS = 100                   # interval while the value is moving
MAX_MS = 8000                  # longest gap: worst-case detection delay
CHANGE = 1                     # degrees C that count as "changing"
log.set_labels("temp", "interval", timestamp=log.MILLISECONDS)


def new_state():
    return {"samples": 0, "last": None, "interval": MIN_MS}


def next_interval(interval, changed):
    # adaptive sampling: reset on change, back off (x2) while steady
    return MIN_MS if changed else min(interval * 2, MAX_MS)


def sample(state):
    t = temperature()
    changed = state["last"] is None or abs(t - state["last"]) >= CHANGE
    state["interval"] = next_interval(state["interval"], changed)
    log.add(temp=t, interval=state["interval"])
    state["samples"] += 1
    state["last"] = t
    return t


def loop_once(state):
    sample(state)
    power.deep_sleep(ms=state["interval"])  # Deep Sleep: board components off
    return state["interval"]


def main():
    state = new_state()
    while True:
        loop_once(state)


if __name__ == "__main__":
    main()
