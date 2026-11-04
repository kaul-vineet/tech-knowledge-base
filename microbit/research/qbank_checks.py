"""Question-bank checks for the micro:bit topic (content/qbank/L100-L500.json).

* Every `calculation` question: recomputes the answer with code (lab code where it exists:
  lab 04 TUNE, lab 09 duty_for, lab 10 decode_temp, lab 11 dot_x, lab 12 crc16 and timeouts,
  lab 14 next_interval, lab 19 siphash24/seal; L500: labs/L500 foundations modules) and asserts the keyed option is that value and
  no other option is.
* Every `code-reading` / `debugging` snippet whose answer is its output: EXECUTES the snippet
  against labs/sim_stub (CPython stub of the microbit API) with the stated inputs injected,
  and asserts the observed output (or exception name) is in the keyed option and in no other.
* Every other Python snippet is at least compiled; Rust snippets are skipped.

Run:  python research/qbank_checks.py     (Windows: py research\\qbank_checks.py)   -> prints OK, exit 0
"""
import contextlib
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC = os.path.dirname(HERE)
LABS = os.path.join(TOPIC, "labs")
STUB = os.path.join(LABS, "sim_stub")
sys.path.insert(0, STUB)

import microbit  # noqa: E402  (the stub)
import labtest  # noqa: E402


def lab(rel, filename="main.py"):
    return labtest.load_lab(os.path.join(LABS, rel), filename)


def lab_module(rel, filename):
    """Import a plain (non-microbit) lab module by path."""
    import importlib.util
    path = os.path.join(LABS, rel, filename)
    spec = importlib.util.spec_from_file_location("qb_" + filename.replace(".", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ calculations
def _ms_per_tick():
    import music
    music._reset()
    ticks, bpm = music.get_tempo()
    return 60000 / bpm / ticks


def _tune_ms(tune, ms_per_tick):
    total, ticks = 0, 4                      # default ticks per note = 4; ":n" carries over
    for note in tune:
        if ":" in note:
            ticks = int(note.split(":")[1])
        total += ticks
    return total * ms_per_tick


def _taps_seen(taps, period_ms, tap_ms=150):
    samples = range(0, 9000, period_ms)
    return sum(any(s <= t < s + tap_ms for t in samples) for s in taps)


def _life_h(wakeups, active_ms, total_ms, on_ma, sleep_ma, mah):
    awake = wakeups * active_ms if wakeups else total_ms
    avg = (awake * on_ma + (total_ms - awake) * sleep_ma) / total_ms
    return mah / avg


def _siphash_rounds(body):
    fa = lab_module("L400/19-radio-auth", "frame_auth.py")
    count = [0]
    orig = fa._round

    def counting(*v):
        count[0] += 1
        return orig(*v)
    fa._round = counting
    fa.siphash24(bytes(range(16)), body.encode())
    return count[0]


def c_L100_008():
    i = 17
    return "({}, {})".format(i % 5, i // 5)


def c_L100_021():
    return "{:.0f} ms".format(6 * _ms_per_tick())


def c_L100_022():
    import music
    music.set_tempo(bpm=90)
    ticks, bpm = music.get_tempo()
    ms = 2 * 60000 / bpm / ticks
    music._reset()
    return "{:.0f} ms".format(ms)


def c_L100_023():
    return "{:.2f} Hz".format(261.63 * 2 ** (4 / 12))


def c_L100_024():
    tune = lab("L100/04-sound").TUNE
    return "{:g} s".format(_tune_ms(tune, _ms_per_tick()) / 1000)


def c_L100_034():
    offset = 23 - 27
    return "{} °C".format(25 + offset)


def c_L100_038():
    microbit._reset()
    microbit.accelerometer.inject_axes(480, -360, 800)
    return "{} mg".format(microbit.accelerometer.get_strength())


def c_L200_005():
    import radio
    radio._reset()
    radio.send("x" * 40)
    return "{} characters".format(len(radio.sent[-1]) - len(radio.STRING_HEADER))


def c_L200_018():
    return str(lab("L200/09-pins-pwm").duty_for(3))


def c_L200_019():
    return "{:.2f} V".format(767 / 1023 * 3.3)


def c_L200_020():
    return "{:.0f} Hz".format(1000 / 5)


def c_L200_028():
    return "{} °C".format(lab("L200/10-i2c-sensor").decode_temp(0x15, 0x80))


def c_L200_029():
    return "{} °C".format(lab("L200/10-i2c-sensor").decode_temp(0xFF, 0x00))


def c_L200_030():
    m = lab("L200/10-i2c-sensor")
    raw = int(30.5 / m.LSB_C)
    msb, lsb = raw >> 4, (raw & 0xF) << 4
    assert m.decode_temp(msb, lsb) == 30.5
    return "0x{:02X} 0x{:02X}".format(msb, lsb)


def c_L200_038():
    m = lab("L200/11-game-state-machine")
    return "column {}".format(m.dot_x({"started": 1000}, 3700))


def c_L300_003():
    s = lab("L300/12-reliable-radio", "solution.py")
    total = sum(min(s.TIMEOUT_MS * 2 ** i, s.MAX_TIMEOUT_MS) for i in range(s.MAX_TRIES))
    return "{:g} s".format(total / 1000)


def c_L300_004():
    p_fail = 1 - 0.8 * 0.8
    return "{:.2f} %".format(100 * p_fail ** 8)


def c_L300_012():
    taps = [932, 1680, 2630, 3695, 4645, 5655, 6689, 7744]
    assert _taps_seen(taps, 1000) == 1            # the lesson's figure for sleep(1000)
    return "{} of 8".format(_taps_seen(taps, 300))


def c_L300_019():
    s = lab("L300/13-nonblocking-scheduler", "solution.py")
    per_s = sum(1000 // t["period"] for t in s.new_scheduler()["tasks"])
    return str(10 * per_s)


def c_L300_020():
    return "{:.1f} h".format(_life_h(0, 20, 3600000, 30.0, 0.5, 1250.0))


def c_L300_022():
    life = _life_h(483, 20, 3600000, 30.0, 0.5, 1250.0)
    return "about {:,.0f} h".format(round(life, -1))


def c_L300_030():
    return "{:g} %".format((6 + 3) / 200 * 100)


def c_L300_039():
    tick_hz = 16e6 / 2 ** 5
    return "{:.0f} µs".format(100 / tick_hz * 1e6)


def c_L300_041():
    lost = 1316 - 1000 - 0
    return "{} lost ({:.0f} %)".format(lost, 100 * lost / 1316)


def c_L400_002():
    return "{:.1f} %".format(100 * 151 / 480)


def c_L400_003():
    return "{} bytes".format(12 * 64)


def c_L400_004():
    return "{:.2f} ms".format(24 * 10 / 115200 * 1000)


def c_L400_013():
    return "{:.2f} %".format(100 * 0.3 ** 6)


def c_L400_018():
    rounds = _siphash_rounds("x" * 24)
    return "{} SipRounds, {} operations".format(rounds, rounds * 14)


def c_L400_019():
    fa = lab_module("L400/19-radio-auth", "frame_auth.py")
    frame = fa.seal("n1", 1234, "21,140,0", bytes(range(16)))
    return "{} bytes".format(len(frame) + 3)


def c_L400_028():
    return "{:.2f} °C".format(1 / math.sqrt(12))


def c_L400_041():
    return "{:.2f} %".format(100 * 3599 / 3600)


# ------------------------------------------------------------------ L500 calculations (lessons 23-27)
def _f1():
    return lab_module("L500/23-digital-foundations", "foundations1.py")


def _f2():
    return lab_module("L500/24-sampling-filters", "foundations2.py")


def _f3():
    return lab_module("L500/25-control-realtime", "foundations3.py")


def c_L500_004():
    return "%d ohm" % _f1().e12_at_least((3.3 - 2.0) / 0.010)


def c_L500_008():
    return "%.2f V" % (255 / 1023 * 3.3)


def c_L500_011():
    return "%g Hz" % _f2().apparent_frequency(100, 30)


def c_L500_014():
    return str(math.ceil((40 / 10) ** 2))


def c_L500_017():
    return "%g" % (2 / (9 + 1))


def c_L500_020():
    return "%.2f C" % (4 / (1 + 20 * 1.5))


def c_L500_024():
    return "%.3f" % _f3().ll_bound(2)


def c_L500_031():
    return str(math.ceil(39 * 7 * 24 / 41.7))


def c_L500_038():
    return "%g Mbit/s" % (2e6 * math.log2(1 + 15) / 1e6)


CALC = {"mb-" + k[2:].replace("_", "-"): v for k, v in globals().items() if k.startswith("c_L")}


# ------------------------------------------------------------------ snippets
# id -> (setup code run first in the same namespace, module __name__, mode)
# mode "exact": normalised output == keyed option; "contains": observed exception name or
# output appears in the keyed option and in no other option.
RUN = {
    "mb-L100-003": ("", "lab_01", "exact"),
    "mb-L100-009": ("", "__main__", "exact"),
    "mb-L100-010": ("", "__main__", "contains"),
    "mb-L100-011": ("", "__main__", "exact"),
    "mb-L100-015": ("button_a.click(3)", "__main__", "exact"),
    "mb-L100-018": ("button_a.click(2); button_b.click()", "__main__", "exact"),
    "mb-L100-028": ("", "__main__", "exact"),
    "mb-L100-031": ("", "__main__", "exact"),
    "mb-L100-032": ("import microbit as _m; _m._inject_temperature(24); display.inject_light_level(200)",
                    "__main__", "exact"),
    "mb-L100-039": ("", "__main__", "exact"),
    "mb-L100-040": ("accelerometer.inject_gesture('shake'); accelerometer.inject_gesture('face up')",
                    "__main__", "exact"),
    "mb-L200-003": ("", "__main__", "exact"),
    "mb-L200-004": ("import radio as _r; _r._inject(b'\\x02hello')", "__main__", "exact"),
    "mb-L200-006": ("", "__main__", "exact"),
    "mb-L200-012": ("", "__main__", "exact"),
    "mb-L200-013": ("", "__main__", "exact"),
    "mb-L200-017": ("import log as _l; _l._set_capacity(200)", "__main__", "contains"),
    "mb-L200-022": ("", "__main__", "exact"),
    "mb-L200-023": ("", "__main__", "contains"),
    "mb-L200-032": ("", "__main__", "exact"),
    "mb-L200-034": ("", "__main__", "exact"),
    "mb-L200-037": ("", "__main__", "exact"),
    "mb-L200-042": ("", "__main__", "exact"),
    "mb-L300-001": ("", "__main__", "exact"),
    "mb-L300-007": ("", "__main__", "exact"),
    "mb-L300-014": ("", "__main__", "exact"),
    "mb-L300-026": ("", "__main__", "exact"),
    "mb-L300-029": ("", "__main__", "exact"),
    "mb-L300-033": ("", "__main__", "exact"),
    "mb-L300-034": ("", "__main__", "contains"),
    "mb-L300-043": ("", "__main__", "exact"),
    "mb-L400-008": ("", "__main__", "exact"),
    "mb-L400-012": ("", "__main__", "exact"),
    "mb-L400-020": ("", "__main__", "exact"),
    "mb-L400-024": ("", "__main__", "exact"),
    "mb-L400-027": ("", "__main__", "exact"),
    "mb-L400-036": ("", "__main__", "exact"),
    "mb-L400-037": ("", "__main__", "exact"),
    # L500 (lessons 23-27): plain-Python snippets, executed the same way
    "mb-L500-002": ("", "__main__", "contains"),
    "mb-L500-003": ("", "__main__", "exact"),
    "mb-L500-006": ("", "__main__", "exact"),
    "mb-L500-012": ("", "__main__", "exact"),
    "mb-L500-013": ("", "__main__", "exact"),
    "mb-L500-016": ("", "__main__", "exact"),
    "mb-L500-021": ("", "__main__", "exact"),
    "mb-L500-022": ("", "__main__", "exact"),
    "mb-L500-026": ("", "__main__", "exact"),
    "mb-L500-042": ("", "__main__", "exact"),
}


def is_python(code):
    return not any(tok in code for tok in ("fn ", "let ", "unsafe ", "#[", "::"))


def run_snippet(qid, code):
    """Execute a snippet on a freshly reset stub; return the observed text."""
    setup, name, mode = RUN[qid]
    microbit._reset()
    for mod in ("radio", "log", "power", "music"):
        __import__(mod)._reset()
    ns = {"__name__": name}
    exec("from microbit import *", ns)
    exec(setup, ns)
    buf = io.StringIO()
    error = None
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, qid, "exec"), ns)
        except Exception as e:  # noqa: BLE001 - the exception IS the answer for some questions
            error = type(e).__name__
    lines = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip()]
    out = " / ".join(lines)
    return (error or out) if mode == "contains" else (out + (" / " + error if error else ""))


def load_bank():
    bank = []
    for lv in ("L100", "L200", "L300", "L400", "L500"):
        with open(os.path.join(TOPIC, "content", "qbank", lv + ".json"), encoding="utf-8") as f:
            bank += json.load(f)
    return bank


def main():
    errors, n_calc, n_run, n_compiled = [], 0, 0, 0
    bank = load_bank()
    ids = {q["id"] for q in bank}
    for key in list(CALC) + list(RUN):
        if key not in ids:
            errors.append("%s: check defined but question missing" % key)
    for q in bank:
        qid, opts, ans = q["id"], q["options"], q["answer"]
        if q["type"] == "calculation":
            if qid not in CALC:
                errors.append("%s: calculation without a recompute function" % qid)
                continue
            want = CALC[qid]()
            n_calc += 1
            if opts[ans] != want:
                errors.append("%s: keyed %r but code computes %r" % (qid, opts[ans], want))
            if sum(o == want for o in opts) != 1:
                errors.append("%s: computed value %r is not exactly one option" % (qid, want))
        code = q.get("code")
        if not code:
            if qid in RUN:
                errors.append("%s: RUN entry but no code" % qid)
            continue
        if not is_python(code):
            continue
        try:
            compile(code, qid, "exec")
            n_compiled += 1
        except SyntaxError as e:
            errors.append("%s: snippet does not compile: %s" % (qid, e))
            continue
        if len(code.rstrip("\n").splitlines()) > 15:
            errors.append("%s: snippet longer than 15 lines" % qid)
        if qid in RUN:
            observed = run_snippet(qid, code)
            n_run += 1
            mode = RUN[qid][2]
            hits = [i for i, o in enumerate(opts) if (o == observed if mode == "exact" else observed in o)]
            if hits != [ans]:
                errors.append("%s: observed %r matches options %s, keyed %d" % (qid, observed, hits, ans))
        elif q["type"] == "code-reading":
            errors.append("%s: code-reading snippet not executed (add a RUN entry)" % qid)
    for e in errors:
        print("ERROR", e)
    print("calculations recomputed: %d; snippets executed on sim_stub: %d; Python snippets compiled: %d"
          % (n_calc, n_run, n_compiled))
    if errors:
        print("FAILED")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
