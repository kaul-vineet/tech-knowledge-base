"""Power budget MODEL for lab 14 (PC side). ESTIMATES, NOT MEASUREMENTS.

Runs a logger design (main.py or solution.py) on the stub for one simulated hour
with a fixed temperature trace, counts how long the board is awake vs in Deep
Sleep, and turns that into average current and battery life using the figures
below. Every figure has a source and a label; change them and re-run.

Run:  python budget.py            (Windows: py budget.py)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab  # noqa: E402
import microbit  # noqa: E402
import power  # noqa: E402

FIGURES = {
    # Board awake (On mode). UPPER BOUND: tech.microbit.org power-supply page,
    # "allow a worst case budget of 30mA for when all on-board peripherals are in use".
    "BOARD_ON_MA": 30.0,
    # Deep Sleep floor of the whole BOARD (interface MCU, regulator, sensors powered down,
    # pull-ups). BOARD SLEEP FLOOR, ASSUMPTION: no published figure; the model brackets it
    # at 0.05-0.5 mA and leads with the conservative end. Replace it with a measurement.
    "SLEEP_MA": 0.5,
    "SLEEP_MA_LOW": 0.05,
    # CHIP ONLY: nRF52833 PS "1.5 uA at 3 V in System ON mode, no RAM retention, wake on
    # RTC". A floor the board cannot beat - never quote it as the board's battery life.
    "CHIP_SLEEP_MA": 0.0015,
    # Awake time per Deep Sleep wake-up (read + log + back to sleep). ASSUMPTION: not
    # published, not measured here; measure it on a board before trusting the result.
    "ACTIVE_MS": 20,
    # 2 x AAA alkaline in series: Energizer E92 datasheet, 1,250 mAh rated at 25 mA to 0.8 V
    # (older revision EBC-1103I; the current manufacturer sheet gives capacity as a chart).
    "BATTERY_MAH": 1250.0,
}
REQUIRED_HOURS = 720           # the brief: one month on one set of batteries
MAX_DETECT_MS = 10000          # ...and notice a 1 C change within 10 s
HOUR_MS = 3600 * 1000
# temperature trace (C) for one hour: (from_ms, value). Same on every run.
TRACE = [(0, 20), (600000, 21), (610000, 22), (620000, 23), (630000, 24), (2400000, 20)]


def schedule_trace(trace):
    for t, value in trace:
        microbit._at(t, lambda v=value: microbit._inject_temperature(v))


def load_design(filename, source=None):
    if source is None:
        return load_lab(HERE, filename)
    import types
    microbit._reset()
    mod = types.ModuleType("lab14_variant")
    exec(compile(source, os.path.join(HERE, filename), "exec"), mod.__dict__)
    return mod


def run_design(filename, trace=TRACE, run_ms=HOUR_MS, source=None):
    lab = load_design(filename, source)
    schedule_trace(trace)
    state, samples = lab.new_state(), []
    while microbit.running_time() < run_ms:
        now = microbit.running_time()
        lab.loop_once(state)                  # the design's own loop body
        samples.append((now, state["last"]))
    slept = sum(ms for kind, _, ms in power.log if kind == "deep_sleep")
    # The last sleep can run past the window (e.g. an 8 s sleep started at 3,599,400 ms).
    # Clip to the window so the averages use exactly run_ms; that tail belongs to the next hour.
    overshoot = microbit.running_time() - run_ms
    return {"total_ms": run_ms, "slept_ms": slept - max(overshoot, 0),
            "wakeups": len(power.log), "samples": samples}


def detect_delays(samples, trace=TRACE):
    """ms from each trace change until a sample first shows the new value."""
    out = []
    for t, value in trace[1:]:
        seen = [s for s, v in samples if s >= t and v == value]
        out.append(seen[0] - t if seen else None)
    return out


def life_h(run, fig, sleep_ma):
    if run["wakeups"]:     # deep-sleep design: awake ACTIVE_MS per wake-up, asleep otherwise
        awake = min(run["wakeups"] * fig["ACTIVE_MS"], run["total_ms"])
    else:                  # never sleeps: awake the whole time
        awake = run["total_ms"]
    avg_ma = (awake * fig["BOARD_ON_MA"] + (run["total_ms"] - awake) * sleep_ma) / run["total_ms"]
    return awake, avg_ma, round(fig["BATTERY_MAH"] / avg_ma, 1)


def estimate(run, fig=FIGURES):
    # headline = BOARD estimate at the conservative sleep floor; the chip figure is only a bound
    awake, avg_ma, life = life_h(run, fig, fig["SLEEP_MA"])
    return {"awake_pct": round(100.0 * awake / run["total_ms"], 2), "avg_ma": round(avg_ma, 4),
            "life_h": life, "life_h_range": [life, life_h(run, fig, fig["SLEEP_MA_LOW"])[2]],
            "chip_only_bound_h": life_h(run, fig, fig["CHIP_SLEEP_MA"])[2]}


def report(filename, fig=FIGURES, trace=TRACE, source=None):
    run = run_design(filename, trace, source=source)
    est = estimate(run, fig)
    delays = detect_delays(run["samples"], trace)
    ok = est["life_h"] >= REQUIRED_HOURS and all(d is not None and d <= MAX_DETECT_MS for d in delays)
    line = dict(design=filename, samples=len(run["samples"]), wakeups=run["wakeups"],
                max_delay_ms=max(d for d in delays if d is not None), meets_brief=ok, **est)
    return json.dumps(line)             # observability: one JSON line per design


if __name__ == "__main__":
    print("figures (estimates, see sources in the code):", FIGURES)
    print("life_h = BOARD estimate at the conservative sleep floor; range = 0.5-0.05 mA floor;"
          " chip_only_bound_h is NOT a board figure")
    for name in ("main.py", "solution.py"):
        print(report(name))
