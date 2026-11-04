# Lab 14 - temperature logger (BEFORE: fixed fast sampling, board always on).
# Logs temperature every 100 ms and shows it on the display. Works fine on USB
# power. On 2 x AAA the MODEL in budget.py says it is flat in under 2 days:
# sleep() keeps the board in On mode (display, sensors, interface MCU awake).
from microbit import *
import log

INTERVAL_MS = 100              # 10 samples per second, always
log.set_labels("temp", timestamp=log.MILLISECONDS)


def new_state():
    return {"samples": 0, "last": None}


def sample(state):
    t = temperature()
    log.add(temp=t)                         # one CSV row per sample
    display.show(t, wait=False)             # display on = current drawn all the time
    state["samples"] += 1
    state["last"] = t
    return t


def loop_once(state):
    sample(state)
    sleep(INTERVAL_MS)                      # On mode: the board does not power down
    return INTERVAL_MS


def main():
    state = new_state()
    while True:
        loop_once(state)


if __name__ == "__main__":
    main()
