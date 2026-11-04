"""L500 lesson 24 - Foundations II: numerical checks (sampling and signal processing).

Sensor data comes from the CPython stub (labs/sim_stub): values are injected with the stub's test
helpers and read back through the real API (display.read_light_level, accelerometer.get_z), so
they carry the same integer quantisation as the board. The traces are SYNTHETIC (seeded), not
measurements.

Run:  python foundations2.py        (Windows: py foundations2.py)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(LABS, "sim_stub"))
import microbit  # noqa: E402

SEED = 24


# ---------------------------------------------------------------- stub sensor traces
def stub_light_trace(values):
    """Inject each value into the stub light sensor and read it back (0..255 integers)."""
    microbit._reset()
    out = []
    for v in values:
        microbit.display.inject_light_level(int(min(255, max(0, round(v)))))
        out.append(microbit.display.read_light_level())
    return np.array(out, dtype=float)


def stub_accel_z(values):
    microbit._reset()
    out = []
    for v in values:
        microbit.accelerometer.inject_axes(z=round(v))
        out.append(microbit.accelerometer.get_z())
    return np.array(out, dtype=float)


def apparent_frequency(f, fs):
    """Frequency a sampled sinusoid appears at: distance to the nearest multiple of fs."""
    return abs(f - round(f / fs) * fs)


# ---------------------------------------------------------------- T1 sampling theorem + aliasing
def sinc_reconstruct(samples, fs, t):
    n = np.arange(len(samples))
    return np.array([np.sum(samples * np.sinc(fs * ti - n)) for ti in t])


def check_sampling_theorem():
    # (a) reconstruction: a signal band-limited to W = 4 Hz, sampled at fs = 10 Hz > 2W
    fs, n = 10.0, 2000
    def x(t):
        return np.sin(2 * np.pi * 1.3 * t) + 0.5 * np.cos(2 * np.pi * 3.7 * t + 0.4)
    samples = x(np.arange(n) / fs)
    t_mid = (np.arange(900, 1100) + 0.5) / fs          # half-way between samples, far from the ends
    err = np.max(np.abs(sinc_reconstruct(samples, fs, t_mid) - x(t_mid)))
    # (b) aliasing: 100 Hz lamp flicker sampled at 30 Hz is indistinguishable from 10 Hz
    k = np.arange(300)
    flicker = np.cos(2 * np.pi * 100 * k / 30)
    alias = np.cos(2 * np.pi * 10 * k / 30)
    same = np.max(np.abs(flicker - alias))
    light = stub_light_trace(128 + 100 * flicker)       # through the stub's 0..255 light sensor
    spec = np.abs(np.fft.rfft(light - light.mean()))
    peak_hz = np.argmax(spec) * 30 / len(light)
    ok = err < 0.02 and same < 1e-9 and peak_hz == 10.0 and apparent_frequency(100, 30) == 10
    line = ("T1 sampling: W=4 Hz, fs=10 Hz, sinc reconstruction max error %.4f mid-record; "
            "100 Hz sampled at 30 Hz equals 10 Hz to %.1e; stub light FFT peak at %.1f Hz "
            "(predicted |f - round(f/fs)fs| = %g Hz)" % (err, same, peak_hz, apparent_frequency(100, 30)))
    return ok, line


# ---------------------------------------------------------------- T2 moving average
def moving_average(x, n):
    return np.convolve(x, np.ones(n) / n, mode="valid")


def ma_response(n, w):
    w = np.asarray(w, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        mag = np.abs(np.sin(n * w / 2) / (n * np.sin(w / 2)))
    return np.where(np.isclose(w, 0), 1.0, mag)


def check_moving_average():
    n = 16
    w = np.linspace(0.001, np.pi, 500)
    direct = np.abs(np.array([np.sum(np.exp(-1j * wi * np.arange(n))) / n for wi in w]))
    resp_err = np.max(np.abs(direct - ma_response(n, w)))
    rng = np.random.default_rng(SEED)
    z = stub_accel_z(-1024 + rng.normal(0, 40, 20000))   # board at rest, 40 mg noise
    ratio = z.std() / moving_average(z, n).std()
    # first null of a 3-point average at fs = 30 Hz is 10 Hz: it removes the aliased flicker
    k = np.arange(300)
    light = stub_light_trace(128 + 100 * np.cos(2 * np.pi * 100 * k / 30))
    before = light.std()
    after = moving_average(light, 3).std()
    ok = resp_err < 1e-12 and abs(ratio - math.sqrt(n)) < 0.15 and after < 0.02 * before
    line = ("T2 moving average: N=16 closed-form |H| matches direct sum to %.1e; stub accel z noise std ratio "
            "%.2f (sqrt(N) = %.2f); N=3 at 30 Hz nulls 10 Hz: aliased flicker std %.1f -> %.2f" % (
                resp_err, ratio, math.sqrt(n), before, after))
    return ok, line


# ---------------------------------------------------------------- T3 exponential filter
def ema(x, alpha, y0=0.0):
    y, out = y0, []
    for v in x:
        y = y + alpha * (v - y)
        out.append(y)
    return np.array(out)


def check_ema():
    alpha, ts = 0.2, 0.1
    step = ema(np.ones(40), alpha)
    formula = 1 - (1 - alpha) ** (np.arange(40) + 1)
    step_err = np.max(np.abs(step - formula))
    tau = -ts / math.log(1 - alpha)
    rng = np.random.default_rng(SEED)
    noise = rng.normal(0, 8, 50000)
    light = stub_light_trace(120 + noise)
    filtered = ema(light, alpha, y0=120.0)[100:]
    var_ratio = filtered.var() / light.var()
    theory = alpha / (2 - alpha)
    w3 = math.acos((1 + (1 - alpha) ** 2 - 2 * alpha ** 2) / (2 * (1 - alpha)))
    ok = step_err < 1e-12 and abs(var_ratio - theory) < 0.01
    line = ("T3 EMA: alpha=0.2, Ts=0.1 s -> step error vs 1-(1-a)^(n+1) %.1e, tau %.3f s (Ts/alpha = %.3f s), "
            "-3 dB at %.4f Hz; stub light noise variance ratio %.4f (alpha/(2-alpha) = %.4f, same as N=%d MA)" % (
                step_err, tau, ts / alpha, w3 / (2 * math.pi * ts), var_ratio, theory, round((2 - alpha) / alpha)))
    return ok, line


CHECKS = [check_sampling_theorem, check_moving_average, check_ema]


def run():
    return [c() for c in CHECKS]


if __name__ == "__main__":
    results = run()
    for ok, line in results:
        print(("OK   " if ok else "FAIL ") + line)
    sys.exit(0 if all(ok for ok, _ in results) else 1)
