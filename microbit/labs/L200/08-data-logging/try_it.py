"""Try it (lab 08): turn on log mirroring, then export the mixed serial transcript.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
sys.path.insert(0, HERE)
from tryit import load_variant, serial  # noqa: E402
import export_csv  # noqa: E402
import microbit  # noqa: E402


def mirrored_transcript():
    # Variant mirroring-on: log.set_mirroring(True) after set_labels; two samples 1 s apart.
    mod = load_variant(HERE, "mirroring-on")
    with serial() as out:
        mod.setup()
        state = mod.new_state()
        for temp_c, light in ((21, 120), (22, 110)):
            microbit._inject_temperature(temp_c)
            microbit.display.inject_light_level(light)
            mod.step(state)
            microbit.sleep(mod.INTERVAL_MS)
    return out.getvalue()


def try_1():
    return " | ".join(mirrored_transcript().splitlines())


def try_2():
    # Export the transcript from try 1 with export_csv.extract().
    header, rows, skipped = export_csv.extract(mirrored_transcript().splitlines())
    reasons = ", ".join("%s: %s" % (text, why) for _, text, why in skipped)
    return "kept %d rows %s; skipped %d (%s)" % (len(rows), rows, len(skipped), reasons)


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
