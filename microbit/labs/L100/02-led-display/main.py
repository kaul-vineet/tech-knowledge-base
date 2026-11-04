# Lab 02 - the 5x5 LED display: scroll text, built-in and custom images,
# per-pixel brightness (0 = off .. 9 = brightest).
from microbit import *

# Custom image: one string per row, digits are brightness, ":" ends a row.
# display buffer: these 25 numbers are what the driver scans onto the LEDs.
DIAMOND = Image("00900:"
                "09590:"
                "95159:"
                "09590:"
                "00900")


def intro():
    display.scroll("Hi")          # blocking call: returns only after the text has scrolled past
    display.show(Image.HEART)     # built-in image (read-only: copy() before editing)
    sleep(500)
    display.show(DIAMOND)         # show() replaces the whole buffer
    sleep(500)
    print("intro done")


def level_image(level):
    # Whole display at one brightness level.
    img = Image()                 # blank 5x5
    img.fill(level)               # per-pixel brightness 0-9 (not 0-255 as in MakeCode)
    return img


def step(level):
    # One loop iteration: show the next brightness level and log it.
    display.show(level_image(level))
    print("brightness", level)
    return (level + 1) % 10       # 0..9 then wrap


def main():
    intro()
    level = 0
    while True:
        level = step(level)
        sleep(200)


if __name__ == "__main__":
    main()
