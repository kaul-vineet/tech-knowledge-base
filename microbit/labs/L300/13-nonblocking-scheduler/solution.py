# Lab 13 - tap counter + temperature reporter (AFTER: cooperative scheduler).
# No sleep() in the main loop. Each task has a period and a time budget; the
# loop asks running_time() which tasks are due, runs them, and measures them.
#   overrun     a task that takes longer than its budget is logged (JSON line)
#   late/missed a task that runs late is logged; missed periods are skipped,
#               not "caught up" in a burst
#   errors      an exception in a task is caught and logged; after MAX_ERRORS in
#               a row the task is disabled and the board goes to a SAFE STATE
from microbit import *

LONG_PRESS_MS = 3000
MAX_ERRORS = 3


def new_state():
    return {"taps": 0, "down_since": None, "temp": None}


def poll_button(state, now):
    down = button_a.is_pressed()
    if down and state["down_since"] is None:
        state["down_since"] = now
    elif not down and state["down_since"] is not None:
        held = now - state["down_since"]
        state["down_since"] = None
        if held >= LONG_PRESS_MS:
            state["taps"] = 0
            print("clear")
        else:
            state["taps"] += 1
            print("tap", state["taps"])


def read_sensor(state, now):
    state["temp"] = temperature()
    print('{"t":%d,"temp":%d,"taps":%d}' % (now, state["temp"], state["taps"]))


def draw(state, now):
    display.show(min(state["taps"], 9), wait=False)


def task(name, period_ms, fn, budget_ms):
    return {"name": name, "period": period_ms, "fn": fn, "budget": budget_ms,
            "due": 0, "errors": 0, "on": True}


def new_scheduler():
    return {"tasks": [task("button", 20, poll_button, 5),      # 20 ms: catches a 150 ms tap
                      task("sensor", 1000, read_sensor, 20),
                      task("display", 100, draw, 10)],
            "stats": {"runs": 0, "overruns": 0, "missed": 0, "errors": 0}, "safe": False}


def log(now, event, name, **kv):
    extra = "".join(',"%s":%d' % (k, kv[k]) for k in sorted(kv))
    print('{"t":%d,"event":"%s","task":"%s"%s}' % (now, event, name, extra))


def safe_state(sched, now, name):
    # outputs to a known-safe value, stop doing work, say why - once
    sched["safe"] = True
    pin0.write_digital(0)
    display.show(Image.NO, wait=False)
    log(now, "safe_state", name)


def run_once(sched, state):
    for t in sched["tasks"]:
        now = running_time()
        if sched["safe"] or not t["on"] or now < t["due"]:
            continue
        if now - t["due"] >= t["period"]:              # a whole period was skipped
            missed = (now - t["due"]) // t["period"]
            sched["stats"]["missed"] += missed
            log(now, "late", t["name"], missed=missed)
        start = now
        try:
            t["fn"](state, now)
            t["errors"] = 0
        except Exception:                               # contain the fault
            t["errors"] += 1
            sched["stats"]["errors"] += 1
            log(now, "error", t["name"], count=t["errors"])
            if t["errors"] >= MAX_ERRORS:
                t["on"] = False
                safe_state(sched, now, t["name"])
        took = running_time() - start
        if took > t["budget"]:
            sched["stats"]["overruns"] += 1
            log(start, "overrun", t["name"], ms=took, budget=t["budget"])
        sched["stats"]["runs"] += 1
        t["due"] += t["period"] * (1 + (running_time() - t["due"]) // t["period"])


def main():
    print("tap counter ready")
    state, sched = new_state(), new_scheduler()
    while True:                     # no sleep(): the loop only asks "what is due?"
        run_once(sched, state)


if __name__ == "__main__":
    main()
