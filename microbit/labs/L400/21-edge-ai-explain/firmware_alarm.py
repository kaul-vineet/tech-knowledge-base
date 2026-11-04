# Lab 21 - the first deterministic alarm lives on the board itself (MicroPython).
# Like the LPC1768 guide's capstone: the device raises its own alarm from its own sensor, with no
# radio, gateway or model in the path. Hysteresis: on at 30 C, off only below 28 C (no flicker).
from microbit import *

ON_C, OFF_C = 30, 28


def check(hot, celsius):
    if not hot and celsius >= ON_C:
        return True
    if hot and celsius < OFF_C:
        return False
    return hot


def main():
    hot = False
    while True:
        hot = check(hot, temperature())
        display.show(Image.SKULL if hot else Image.HAPPY)   # visible in the room, gateway or not
        sleep(1000)


if __name__ == "__main__":
    main()
