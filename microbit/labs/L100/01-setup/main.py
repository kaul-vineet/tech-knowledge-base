# Lab 01 - first program: show an image and print to serial.
# Runs unchanged in the micro:bit Python Editor simulator and on a V1/V2 board.
from microbit import *   # stub tests swap in labs/sim_stub: same API, fake hardware


def hello():
    # Runs once at start-up.
    display.show(Image.HAPPY)
    print("hello from micro:bit")   # serial: print() text goes to the serial panel


def step(count):
    # One loop iteration: print a counter so you can watch the serial panel.
    count += 1
    print("tick", count)
    return count


def main():
    hello()
    count = 0
    while True:
        count = step(count)
        sleep(1000)  # milliseconds; in the stub only a virtual clock advances


# main.py runs as __main__ on the board/simulator (flash = copy + restart);
# unit tests import it under another name, so the endless loop does not start.
if __name__ == "__main__":
    main()
