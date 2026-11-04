# Lab 05 - temperature and light: read both sensors, log to serial,
# and show a simple threshold result on the display.
from microbit import *

# named thresholds: tune them here, not deep inside the loop.
HOT_C = 26        # degrees Celsius (processor temperature, approximate)
DARK_LEVEL = 40   # light level 0..255, larger = brighter


def classify(temp_c, light):
    # classify: pure logic, easy to unit-test without any sensor.
    # Priority: dark is checked first, so it wins over hot.
    if light < DARK_LEVEL:
        return "dark"
    if temp_c >= HOT_C:   # single threshold (inclusive); hysteresis is the L200 upgrade
        return "hot"
    return "ok"


def step():
    # sample: whole degrees C from the processor; light by running LEDs in reverse.
    t = temperature()
    light = display.read_light_level()
    state = classify(t, light)
    # act: log key=value lines, then show the decision.
    print("temp={},light={},state={}".format(t, light, state))
    if state == "dark":
        display.show(Image.ASLEEP)
    elif state == "hot":
        display.show("H")
    else:
        display.show(Image.HAPPY)
    return state


def main():
    while True:
        step()
        sleep(1000)


if __name__ == "__main__":
    main()
