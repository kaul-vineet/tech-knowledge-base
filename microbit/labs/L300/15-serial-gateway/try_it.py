"""Try it (lab 15): seeded noisy link (2% drop, 2% flip, 1% cut, seed 15).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import io
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import variant_source  # noqa: E402
from gateway import JsonLinesPublisher  # noqa: E402
import serial_link  # noqa: E402
import solution  # noqa: E402


def truth(seq):
    i = seq - 1
    return 20 + i // 50, 100 + i % 10


def wrong_values(pub):
    rows = [m["payload"] for m in pub.sent if m["topic"].endswith("/telemetry")]
    bad = [r for r in rows if (r["temp"], r["light"]) != truth(r["seq"])]
    return len(rows), len(bad)


def try_1():
    # Remove the CRC check, and flip a bit in 10% of frames instead of 2%.
    mod = types.ModuleType("gw_no_crc")
    mod.__file__ = os.path.join(HERE, "solution.py")
    exec(compile(variant_source(HERE, "no-crc-check"), mod.__file__, "exec"), mod.__dict__)
    chunks, _ = serial_link.noisy(serial_link.device_bytes(), **dict(serial_link.FAULTS, flip=0.1))
    out = []
    for name, gw in (("no CRC", mod), ("with CRC", solution)):
        pub = JsonLinesPublisher(io.StringIO())
        m = gw.run(chunks, pub)
        n, bad = wrong_values(pub)
        out.append("%s: forwarded %d, %d WRONG, bad_crc %d, bad_payload %d" % (
            name, n, bad, m["bad_crc"], m["bad_payload"]))
    return " | ".join(out)


def try_2():
    # Same bytes, fed one byte at a time (a slow serial port).
    chunks, _ = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)
    pub = JsonLinesPublisher(io.StringIO())
    m = solution.run([bytes([b]) for b in b"".join(chunks)], pub)
    n, bad = wrong_values(pub)
    return "forwarded %d readings, %d wrong; metrics %s" % (n, bad, m)


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
