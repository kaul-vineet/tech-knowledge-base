"""Computes every number used in the worked examples of content/concepts/L200/*.md.

Run from the domain root:  python research/concept_examples_l200.py
Output is saved in research/concept_examples_l200.out.txt (the notes quote it).
Uses the L200 lab files and labs/sim_stub, so the numbers match the labs.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "labs", "sim_stub"))
from labtest import load_boards, load_lab, serial  # noqa: E402
from i2c_devices import TMP102  # noqa: E402
import microbit  # noqa: E402

LABS = os.path.join(ROOT, "labs", "L200")


def lab(name):
    return load_lab(os.path.join(LABS, name))


print("== 07 radio: bytes on air, truncation, queue")
m = lab("07-radio")
msg = m.encode("btn", 1, "A")
print("message:", msg, "-> bytes on air:", len(b"\x01\x00\x01" + msg.encode()))
long_msg = m.encode("btn", 1, "A" * 40)
print("40-char value: requested", 3 + len(long_msg), "bytes, length=32 keeps", 32, "->",
      32 - 3 - len("btn:1:"), "of 40 characters")
a, b = load_boards(os.path.join(LABS, "07-radio"))
sa = a.lab.new_state()
for _ in range(4):
    a.mb.button_a.click()
    with serial():
        a.lab.step(sa)
print("4 sends, receiver never polls, queue=3 -> queued", len(b.radio._queue), "dropped", b.radio.dropped)

print("\n== 08 data logging: rows, timestamps, sizes")
m = lab("08-data-logging")
import log  # noqa: E402
with serial() as out:
    m.setup()
    st = m.new_state()
    for t, l in ((21, 120), (22, 110), (23, 100)):
        microbit._inject_temperature(t)
        microbit.display.inject_light_level(l)
        m.step(st)
        microbit.sleep(m.INTERVAL_MS)
print("serial CSV:", out.getvalue().splitlines())
print("log rows:  ", log.rows)
row = "1000,22,110"
print("serial row", repr(row), "=", len(row) + 2, "bytes with CRLF; rows per hour at 1 s:", 3600)

print("\n== 09 pins: duty, average voltage, timing")
m = lab("09-pins-pwm")
for level in range(5):
    d = m.duty_for(level)
    print("level", level, "duty", d, "-> %.0f %% duty, average %.2f V, on-time %.2f ms of %d ms"
          % (100 * d / 1023, 3.3 * d / 1023, m.PERIOD_MS * d / 1023, m.PERIOD_MS))
print("period", m.PERIOD_MS, "ms ->", 1000 // m.PERIOD_MS, "Hz")

print("\n== 10 i2c: one read transaction, decode, sign")
m = lab("10-i2c-sensor")
microbit.i2c._attach(0x48, TMP102(21.5))
with serial():
    t = m.step()
print("transactions:", microbit.i2c.transactions, "->", t, "C")
raw = (0x15 << 4) | (0x80 >> 4)
print("raw = (0x15 << 4) | (0x80 >> 4) =", hex(raw), "=", raw, "x 0.0625 =", raw * 0.0625)
raw = (0xE7 << 4) | 0
print("-25 C bytes E7 00: raw", hex(raw), "=", raw, "-> signed", raw - 4096, "x 0.0625 =",
      (raw - 4096) * 0.0625, "; without sign handling", raw * 0.0625)

print("\n== 11 game: table size and a timeline")
m = lab("11-game-state-machine")
states, events = ("idle", "play", "over"), ("a", "shake", "timeout")
pairs = [(s, e) for s in states for e in events]
print("pairs", len(pairs), "table rows", len(m.TRANSITIONS),
      "ignored", sum(1 for p in pairs if p not in m.TRANSITIONS))
for t in (0, 600, 900, 5999, 6000):
    print("t=%d ms dot_x=%d" % (t, m.dot_x({"started": 0}, t)))
