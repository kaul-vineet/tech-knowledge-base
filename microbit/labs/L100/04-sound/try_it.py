"""Try it (lab 04): run a code change and a prediction against the stub.

Tune length is computed from the lab's TUNE list with the documented rules
(NOTE[octave][:ticks], octave/ticks carry over, 4 ticks/beat at 120 bpm);
the stub itself makes no sound and has no timing.
Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402

import re  # noqa: E402

NOTE = re.compile(r"^([a-gr])(#|b)?(\d)?(?::(\d+))?$")


def tune_ticks(notes, ticks=4):
    # Default ticks is 4; each note's ":n" sets it for this and later notes.
    total = 0
    for n in notes:
        m = NOTE.match(n.lower())
        if not m:
            raise ValueError(n)
        if m.group(4):
            ticks = int(m.group(4))
        total += ticks
    return total


def tune_ms(notes, ticks_per_beat=4, bpm=120):
    return tune_ticks(notes) * 60000 / bpm / ticks_per_beat


def try_1():
    # Change the last note "c5:6" to "c5" (no ticks).
    from labtest import load_lab
    changed = load_variant(HERE, "last-note-no-ticks").TUNE
    original = load_lab(HERE).TUNE
    return "variant %d ticks = %d ms (original %d ticks = %d ms)" % (
        tune_ticks(changed), tune_ms(changed), tune_ticks(original), tune_ms(original))


def try_2():
    # No code change: press B (speaker off), then A. Is the tune still played?
    import music
    from labtest import load_lab
    mod = load_lab(HERE)
    with serial() as out:
        microbit.button_b.click()
        mod.step()
        microbit.button_a.click()
        mod.step()
    plays = [e for e in microbit.sound_log if e[0] == "music" and e[1][0] == "play"]
    return "serial=%r, music.play calls=%d, speaker_on during play=%s" % (
        out.getvalue(), len(plays), plays[-1][2] if plays else None)


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

