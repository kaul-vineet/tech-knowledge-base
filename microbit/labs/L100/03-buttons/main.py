# Lab 03 - buttons: is_pressed (held now?) vs was_pressed (pressed since
# last check?) vs get_presses (how many presses since last check?).
from microbit import *


def step(count):
    # counted edges: get_presses() returns every press of A since the last
    # call (even several during one sleep), then resets to 0.
    count_before = count
    count += button_a.get_presses()
    # edge flag: was_pressed() is a single yes/no since last time, cleared on read.
    if button_b.was_pressed():
        count = 0
    if count != count_before:
        print("count", count)
        display.show(count % 10, wait=False)   # last digit, non-blocking
    # level: is_pressed() is true only while the button is held down right now.
    if button_a.is_pressed() and button_b.is_pressed():
        print("both held")
    return count


def main():
    print("A = +1, B = reset")
    count = 0
    while True:
        count = step(count)
        sleep(100)    # polling interval: presses between polls wait in the runtime


if __name__ == "__main__":
    main()
