"""Computes every number used in the worked examples of content/concepts/*.md.

Run from the domain root:  python research/concept_examples.py
Output is saved in research/concept_examples.out.txt (the notes quote it).
Uses the lab files and labs/sim_stub, so the numbers match the labs.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "labs", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

LABS = os.path.join(ROOT, "labs", "L100")


def lab(name):
    return load_lab(os.path.join(LABS, name))


print("== 01 setup: what 'flash' sends and what the loop does")
src = open(os.path.join(LABS, "01-setup", "main.py"), encoding="utf-8").read()
payload = src.encode("utf-8")              # same bytes as TextEncoder().encode(code)
print("main.py bytes:", len(payload))
print("first 8 bytes (hex):", payload[:8].hex(" "))
m = lab("01-setup")
with serial() as out:
    m.hello()
    n = 0
    for _ in range(3):
        n = m.step(n)
        microbit.sleep(1000)
print("serial after hello + 3 iterations:", repr(out.getvalue()))
print("stub running_time() after 3 x sleep(1000):", microbit.running_time(), "ms")

print("\n== 02 display: image string -> 25 brightness values")
m = lab("02-led-display")
d = m.DIAMOND
rows = [[d.get_pixel(x, y) for x in range(5)] for y in range(5)]
for r in rows:
    print(" ", r)
print("pixel (x=2, y=1):", d.get_pixel(2, 1), "-> flat index y*5+x =", 1 * 5 + 2)
print("lit LEDs:", sum(v > 0 for r in rows for v in r), "of 25; brightness sum:", sum(map(sum, rows)))
print("level_image(5) top-left:", m.level_image(5).get_pixel(0, 0))
print("DAL refresh 18 ms ->", round(1000 / 18, 1), "Hz;  15 ms ->", round(1000 / 15, 1), "Hz")
print("V1 wiring: 3 row pins x 9 column pins =", 3 * 9, "positions,", 3 + 9, "GPIO pins for 25 LEDs")

print("\n== 03 buttons: three quick clicks between two polls")
lab("03-buttons")
microbit.button_a.click(times=3)
print("poll 1: is_pressed =", microbit.button_a.is_pressed(),
      "| was_pressed =", microbit.button_a.was_pressed(),
      "| get_presses =", microbit.button_a.get_presses())
print("poll 2: is_pressed =", microbit.button_a.is_pressed(),
      "| was_pressed =", microbit.button_a.was_pressed(),
      "| get_presses =", microbit.button_a.get_presses())
m = lab("03-buttons")
microbit.button_a.click(times=3)
with serial() as out:
    c = m.step(0)
print("lab step(0) after 3 clicks ->", c, repr(out.getvalue()))

print("\n== 04 sound: note strings -> ticks, ms, Hz")
m = lab("04-sound")
NAMES = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
tick_ms = 60000 / 120 / 4
octave, ticks, total = 4, 4, 0
for note in m.TUNE:
    name, _, dur = note.partition(":")
    letter, rest = name[0].lower(), name[1:]
    if rest:
        octave = int(rest)
    if dur:
        ticks = int(dur)
    total += ticks
    if letter == "r":
        print("  %-6s rest   %d ticks = %4d ms" % (note, ticks, ticks * tick_ms))
        continue
    midi = 12 * (octave + 1) + NAMES[letter]
    hz = 440 * 2 ** ((midi - 69) / 12)
    print("  %-6s %s%d midi %d  %7.2f Hz  %d ticks = %4d ms" % (note, letter.upper(), octave, midi, hz, ticks, ticks * tick_ms))
print("tick =", tick_ms, "ms; total ticks =", total, "->", total * tick_ms, "ms")
print("SWEEP:", m.SWEEP.freq_start, "->", m.SWEEP.freq_end, "Hz in", m.SWEEP.duration, "ms")

print("\n== 05 temperature/light: thresholds and hysteresis")
m = lab("05-temperature-light")
for t, l in [(21, 128), (26, 128), (30, 39), (25, 40)]:
    print("  classify(%d, %d) = %s" % (t, l, m.classify(t, l)))
readings = [25, 26, 25, 26, 27, 26, 25, 24]
plain = ["hot" if r >= m.HOT_C else "ok" for r in readings]
hyst, state = [], "ok"
for r in readings:                       # on at >= 27, off at <= 25
    if state == "ok" and r >= m.HOT_C + 1:
        state = "hot"
    elif state == "hot" and r <= m.HOT_C - 1:
        state = "ok"
    hyst.append(state)


def changes(states):
    return sum(a != b for a, b in zip(states, states[1:]))


print("readings:", readings)
print("plain threshold 26 :", plain, "changes =", changes(plain))
print("hysteresis 27/25   :", hyst, "changes =", changes(hyst))

print("\n== 06 motion: axes -> strength and tilt")
m = lab("06-motion-gestures")
for xyz in [(0, 0, -1024), (800, 0, -640), (-500, 0, -880)]:
    microbit.accelerometer.inject_axes(*xyz)
    s = microbit.accelerometer.get_strength()
    pitch = math.degrees(math.atan2(xyz[0], -xyz[2]))
    print("  xyz=%s strength=%d mg  tilt=%s  angle_from_flat=%.1f deg" % (xyz, s, m.tilt(xyz[0]), pitch))
m = lab("06-motion-gestures")
microbit.accelerometer.inject_gesture("shake")
with serial() as out:
    m.step()
    m.step()
print("shake then 2 polls -> 'shake!' printed", out.getvalue().count("shake!"), "time(s)")
print("lab tilt(300) ->", m.tilt(300))

print("\n== check-yourself answers")
print("02: flat index 12 -> (x, y) =", (12 % 5, 12 // 5))
microbit._reset()
microbit.button_a.click(times=5)
print("03: 5 taps during one sleep -> get_presses() =", microbit.button_a.get_presses(),
      "; second was_pressed() with no new press ->", (microbit.button_a.was_pressed(), microbit.button_a.was_pressed())[1])
print("04: 'a4:8' ->", 8 * tick_ms, "ms; A5 (midi 81) ->", round(440 * 2 ** ((81 - 69) / 12), 2), "Hz")
print("05: classify(26, 39) ->", lab("05-temperature-light").classify(26, 39))
