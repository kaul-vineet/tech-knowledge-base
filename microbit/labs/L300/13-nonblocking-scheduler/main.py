# Lab 13 - tap counter + temperature reporter (BEFORE: a blocking loop).
# A press shorter than 3 s counts; holding A for 3 s or more clears the count.
# The loop polls the button, reads the sensor, then sleep()s for 1 s. It works
# when you press deliberately (hold ~1.5 s), but a quick 150 ms tap that starts
# and ends during the sleep is never seen: is_pressed() only looks at "now".
from microbit import *

SENSOR_MS = 1000           # one temperature line per second
LONG_PRESS_MS = 3000       # hold this long to clear the count


def new_state():
    return {"taps": 0, "down_since": None, "temp": None}


def poll_button(state, now):
    # edge detection on is_pressed(): we need the press DURATION, so polling
    # (not was_pressed) - and polling only works if it runs often enough
    down = button_a.is_pressed()
    if down and state["down_since"] is None:
        state["down_since"] = now                     # press started
    elif not down and state["down_since"] is not None:
        held = now - state["down_since"]
        state["down_since"] = None                    # press ended
        if held >= LONG_PRESS_MS:
            state["taps"] = 0
            print("clear")
        else:
            state["taps"] += 1
            print("tap", state["taps"])


def read_sensor(state, now):
    state["temp"] = temperature()
    print('{"t":%d,"temp":%d,"taps":%d}' % (now, state["temp"], state["taps"]))


def loop_once(state):
    now = running_time()
    poll_button(state, now)
    read_sensor(state, now)
    display.show(min(state["taps"], 9), wait=False)
    sleep(SENSOR_MS)       # BLOCKING: nothing else runs for 1 s


def main():
    print("tap counter ready")
    state = new_state()
    while True:
        loop_once(state)


if __name__ == "__main__":
    main()
