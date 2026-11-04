"""Computes every number used in the worked examples of content/concepts/L300/*.md.

Run from the domain root:  python research/concept_examples_l300.py
Output is saved in research/concept_examples_l300.out.txt (the notes quote it).
Uses the L300 lab files and labs/sim_stub, so the numbers match the labs.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L300 = os.path.join(ROOT, "labs", "L300")
sys.path.insert(0, os.path.join(ROOT, "labs", "sim_stub"))


def lab_path(name):
    path = os.path.join(L300, name)
    for mod in ("link_sim", "tap_sim", "budget", "serial_link", "solution", "gateway", "host_sim",
                "race_model", "solution_model"):
        sys.modules.pop(mod, None)
    sys.path.insert(0, path)
    return path


print("== 12 reliable radio: 20 readings, loss 0.2 dup 0.1 reorder 0.1 corrupt 0.05 seed 12")
lab_path("12-reliable-radio")
import link_sim  # noqa: E402
before = link_sim.run("main.py", faults=link_sim.FAULTS)
after = link_sim.run("solution.py", faults=link_sim.FAULTS)
print("before:", link_sim.summary(before), "| air", before["faults"])
print("after: ", link_sim.summary(after), "| sender", json.loads(after["json"][0]))
print("receiver dup suppressed:", after["b"]["dup"])
p_round = 0.8 * 0.8
print("loss only: P(data and ack both arrive) = %.2f, expected tries %.2f, P(8 tries all fail) = %.1e"
      % (p_round, 1 / p_round, (1 - p_round) ** 8))
print("give-up time: sum of timeouts 100+200+400+800*5 =", 100 + 200 + 400 + 800 * 5, "ms")
sys.path.pop(0)

print("\n== 13 scheduler: 8 quick taps (150 ms), blocking sleep(1000) vs 20 ms button task")
lab_path("13-nonblocking-scheduler")
import tap_sim  # noqa: E402
presses = tap_sim.taps()
print("taps at:", [t for t, _ in presses])
print("chance a 150 ms tap covers one 1000 ms sample: %.0f%%" % (100 * 150 / 1000))
print("blocking loop counted:", tap_sim.run_blocking(presses)[0]["taps"], "of 8")
state, sched, _ = tap_sim.run_scheduler(presses)
print("scheduler counted:", state["taps"], "of 8; stats", sched["stats"])
sys.path.pop(0)

print("\n== 14 power budget (MODEL, estimates)")
lab_path("14-power-budget")
import budget  # noqa: E402
print("figures:", budget.FIGURES)
for name in ("main.py", "solution.py"):
    print(budget.report(name))
for floor, label in ((0.5, "board floor 0.5 mA (conservative, assumed)"),
                     (0.05, "board floor 0.05 mA (assumed)"), (0.0015, "chip-only 1.5 uA (bound)")):
    print("fixed 100 ms + deep sleep, %s: 0.2 x 30 + 0.8 x %s -> %.4f mA -> %.1f h" % (
        label, floor, 0.2 * 30 + 0.8 * floor, 1250 / (0.2 * 30 + 0.8 * floor)))
print("chip-only awake 3.328 + 4.6 = %.1f mA -> %.1f h" % (3.328 + 4.6, 1250 / 7.9))
sys.path.pop(0)

print("\n== 15 serial gateway: 200 frames, drop 2% flip 2% cut 1% seed 15")
lab_path("15-serial-gateway")
import serial_link  # noqa: E402
import solution  # noqa: E402
import gateway  # noqa: E402
chunks, stats = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)
print("faults injected:", stats, "| bytes", sum(map(len, chunks)), "in", len(chunks), "chunks")
try:
    gateway.run(serial_link.as_text_lines(chunks), gateway.JsonLinesPublisher(io.StringIO()))
except ValueError as exc:
    print("naive gateway: ValueError on the first line:", exc)
m = solution.run(chunks, gateway.JsonLinesPublisher(io.StringIO()))
print("hardened:", m, "| damaged %.1f%%" % (100.0 * (m["bad_crc"] + m["bad_len"]) / (m["frames_ok"] + m["bad_crc"] + m["bad_len"])))
print("frame for 1,20,100:", "$008" + "1,20,100" + "*%04X" % solution.crc16(b"1,20,100"))
print("random corruption passing a 16-bit CRC: 1 in", 2 ** 16)
sys.path.pop(0)

print("\n== 16 interrupt race (host model)")
lab_path("16-interrupt-race")
import host_sim  # noqa: E402
import race_model  # noqa: E402
import solution_model  # noqa: E402
print("window: 2000 cycles at 64 MHz = %.2f us; timer period 100 us -> %.0f%% of takes overlap" % (
    2000 / 64, 100 * (2000 / 64) / 100))
for name, mod in (("racy", race_model), ("fixed", solution_model)):
    w = host_sim.schedule(mod.take, {"window"})
    s = host_sim.soak(mod.take)
    print("%s: IRQ in window -> lost %d | soak 1000 takes p=0.3 seed 16: isr %d consumed %d pending %d lost %d (%.0f%%)"
          % (name, w.lost(), s.isr_total, s.consumed, s.pending, s.lost(), 100.0 * s.lost() / s.isr_total))
