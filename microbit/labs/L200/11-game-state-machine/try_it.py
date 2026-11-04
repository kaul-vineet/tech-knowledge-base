"""Try it (lab 11): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, serial  # noqa: E402
import microbit  # noqa: E402


def play(mod, actions):
    game = mod.new_game()
    with serial() as out:
        for act in actions:
            if act == "a":
                microbit.button_a.click()
            elif act == "shake":
                microbit.accelerometer.inject_gesture("shake")
            else:
                microbit.sleep(act)
            mod.step(game)
    return " | ".join(out.getvalue().splitlines()) or "(nothing)"


def try_1():
    # Delete the ("play", "shake") row; start with A, then shake during play.
    mod = load_variant(HERE, "no-shake-abort")
    return play(mod, ["a", "shake", 100])


def try_2():
    # STEP_MS = 150 instead of 300; press A 600 ms after the start (a hit with 300).
    mod = load_variant(HERE, "step-150")
    return play(mod, ["a", 600, "a"])


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
