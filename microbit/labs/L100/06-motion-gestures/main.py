# Lab 06 - motion: read the accelerometer (milli-g), turn X into a tilt
# direction, react to gestures, and log everything to serial.
from microbit import *

TILT_MG = 300     # |x| above this counts as a left/right tilt


def tilt(x):
    # axis threshold: X axis in milli-g -> direction (pure logic).
    if x > TILT_MG:
        return "right"
    if x < -TILT_MG:
        return "left"
    return "flat"


def step():
    # gravity vector: about 1000 mg in total when still, split across x, y, z.
    x, y, z = accelerometer.get_values()
    gesture = accelerometer.current_gesture()   # polling keeps gesture detection running
    direction = tilt(x)
    print("x={},y={},z={},tilt={},gesture={}".format(x, y, z, direction, gesture))
    if accelerometer.was_gesture("shake"):      # one-shot event: True once per shake, then cleared
        print("shake!")
        display.show(Image.SURPRISED)
    elif direction == "right":
        display.show(Image.ARROW_E)
    elif direction == "left":
        display.show(Image.ARROW_W)
    else:
        display.clear()
    return direction


def main():
    while True:
        step()
        sleep(200)


if __name__ == "__main__":
    main()
