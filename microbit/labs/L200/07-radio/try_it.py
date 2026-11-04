"""Try it (lab 07): run two code changes on two stub boards and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_boards  # noqa: E402
from tryit import serial, variant_source  # noqa: E402


def press_a_and_poll(boards):
    a, b = boards
    sa, sb = a.lab.new_state(), b.lab.new_state()
    a.mb.button_a.click()
    with serial() as out:
        a.lab.step(sa)
        b.lab.step(sb)
    return out.getvalue().strip().replace("\n", " | ")


def try_1():
    # Board B runs the variant GROUP = 8; board A keeps GROUP = 7. Press A on board A.
    boards = load_boards(HERE, sources={"B": variant_source(HERE, "group-8")})
    return press_a_and_poll(boards)


def try_2():
    # Both boards send a 40-character value ("A" * 40) with the default length=32.
    src = variant_source(HERE, "long-value")
    boards = load_boards(HERE, sources={"A": src, "B": src})
    line = press_a_and_poll(boards)
    sent = boards[0].radio.sent[-1]
    return "%s | bytes on air: %d" % (line.replace("A" * 40, "A*40").replace("A" * 23, "A*23"), len(sent))


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
