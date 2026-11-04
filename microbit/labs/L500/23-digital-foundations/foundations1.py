"""L500 lesson 23 - Foundations I: numerical checks of the theorems (digital electronics and signals).

Each check_* function recomputes one result from content/L500.json and returns (ok, line).
The lines are quoted verbatim as `checkOutput`; research/l500_checks.py compares them.

Run:  python foundations1.py        (Windows: py foundations1.py)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(LABS, "sim_stub"))
import microbit  # noqa: E402  (CPython stub of the micro:bit API)
import labtest  # noqa: E402

SEED = 23


# ---------------------------------------------------------------- T1 two's complement
def encode(x, n):
    """Integer -> n-bit two's-complement pattern (an unsigned int)."""
    return x % (1 << n)


def decode(u, n):
    """n-bit pattern -> integer: value = -b[n-1]*2^(n-1) + sum b[i]*2^i."""
    return u - (1 << n) if u & (1 << (n - 1)) else u


def negate_bits(u, n):
    return (~u + 1) & ((1 << n) - 1)          # invert, add one, keep n bits


def check_twos_complement():
    total, ok = 0, True
    for n in (8, 12, 16):
        lo, hi = -(1 << (n - 1)), (1 << (n - 1)) - 1
        for x in range(lo, hi + 1):
            u = encode(x, n)
            ok &= decode(u, n) == x
            ok &= negate_bits(u, n) == encode(-x, n) if x != lo else negate_bits(u, n) == u
            total += 1
        a, b = 3 * hi // 4, hi // 2              # overflow: two positives wrap to a negative
        ok &= decode(encode(a + b, n), n) == a + b - (1 << n)
    lab10 = labtest.load_lab(os.path.join(LABS, "L200", "10-i2c-sensor"), "solution.py")
    ok &= all(round(lab10.decode_temp(u >> 4, (u & 0xF) << 4) / lab10.LSB_C) == decode(u, 12) for u in range(4096))
    z = microbit.accelerometer
    microbit._reset()
    rest = encode(z.get_z(), 16)               # stub at rest: z = -1024 mg
    ok &= rest == 0xFC00 and decode(0xFE0C, 16) == -500
    line = ("T1 two's complement: n=8,12,16 exhaustive round-trip + invert-and-add-one OK for %d values; "
            "-2^(n-1) negates to itself; lab 10 decode_temp == 12-bit decode for all 4096 patterns; stub z=-1024 mg -> 0x%04X; 0xFE0C -> %d" % (total, rest, decode(0xFE0C, 16)))
    return ok, line


# ---------------------------------------------------------------- T2 Ohm's law, power, battery
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


def e12_at_least(r):
    for decade in (1, 10, 100, 1000, 10000):
        for m in E12:
            if m * decade >= r - 1e-9:
                return m * decade
    raise ValueError(r)


def led_resistor(vs, vf, i_target):
    r_exact = (vs - vf) / i_target             # KVL: Vs = I*R + Vf
    r = e12_at_least(r_exact)                  # next standard value up -> current never exceeds target
    i = (vs - vf) / r
    return r_exact, r, i, i * i * r, vf * i    # R exact, R chosen, I, P_R, P_LED


def battery_life_h(mah, on_ma, sleep_ma, awake_ms, total_ms):
    avg = (awake_ms * on_ma + (total_ms - awake_ms) * sleep_ma) / total_ms
    return mah / avg


def check_ohm_power():
    r_exact, r, i, p_r, p_led = led_resistor(3.3, 2.0, 0.005)
    ok = abs(3.3 * i - (p_r + p_led)) < 1e-12           # power balance (energy conservation)
    ok &= abs(r_exact - 260.0) < 1e-9 and r == 270.0
    # lesson 14 figures: 483 wake-ups x 20 ms in one hour, 30 mA awake, floor 0.5 / 0.05 mA, 1,250 mAh
    awake = 483 * 20
    hi = battery_life_h(1250.0, 30.0, 0.5, awake, 3600000)
    lo = battery_life_h(1250.0, 30.0, 0.05, awake, 3600000)
    stretched = battery_life_h(1250.0, 30.0, 0.05, awake, 3607400)   # the pre-fix 7.4 s overshoot
    ok &= (round(hi, 1), round(lo, 1), round(stretched, 1)) == (2158.3, 9588.4, 9600.5)
    line = ("T2 Ohm/KVL/power: 3.3 V, Vf 2.0 V, 5 mA -> R %.0f ohm -> E12 %.0f ohm, I %.3f mA, P_R %.2f mW, "
            "P_LED %.2f mW, Vs*I = P_R + P_LED; battery 1250 mAh: %.1f h (0.5 mA floor), %.1f h (0.05 mA), "
            "%.1f h if the window is stretched to 3,607,400 ms" % (r_exact, r, i * 1e3, p_r * 1e3, p_led * 1e3, hi, lo, stretched))
    return ok, line


def check_against_lesson14():
    """The formula must reproduce what labs/L300/14-power-budget/budget.py prints."""
    sys.path.insert(0, os.path.join(LABS, "L300", "14-power-budget"))
    import budget  # noqa: E402
    est = budget.estimate(budget.run_design("solution.py"))
    ok = est["life_h"] == round(battery_life_h(1250.0, 30.0, 0.5, 483 * 20, 3600000), 1)
    ok &= est["life_h_range"][1] == round(battery_life_h(1250.0, 30.0, 0.05, 483 * 20, 3600000), 1)
    line = "T2b lesson 14 cross-check: budget.py life_h %s, range %s == closed-form t = Q / I_avg" % (
        est["life_h"], est["life_h_range"])
    return ok, line


# ---------------------------------------------------------------- T3 ADC quantisation error
def quantise(v, n_bits, vref):
    step = vref / (1 << n_bits)
    code = np.clip(np.round(v / step), 0, (1 << n_bits) - 1)
    return code * step, step


def check_adc_quantisation():
    rng = np.random.default_rng(SEED)
    n, vref = 10, 3.3
    v = rng.uniform(0.01, vref - 0.01, 1_000_000)          # a "busy" input spanning many steps
    q, step = quantise(v, n, vref)
    err = q - v
    var_ratio = err.var() / (step ** 2 / 12)
    t = np.arange(200_000)
    sine = vref / 2 + (vref / 2 - step / 2) * np.sin(2 * np.pi * 0.0123456 * t)   # (almost) full scale
    qs, _ = quantise(sine, n, vref)
    sqnr = 10 * np.log10(np.mean((sine - vref / 2) ** 2) / np.mean((qs - sine) ** 2))
    theory = 6.02 * n + 1.76
    ok = abs(var_ratio - 1) < 0.01 and abs(err.mean()) < step / 100 and np.abs(err).max() <= step / 2 + 1e-12
    ok &= abs(sqnr - theory) < 0.2
    line = ("T3 ADC: 10-bit, 3.3 V -> step %.4f mV, RMS error theory %.4f mV, measured var/(step^2/12) = %.4f; "
            "full-scale sine SQNR %.2f dB vs 6.02N+1.76 = %.2f dB" % (step * 1e3, step / math.sqrt(12) * 1e3, var_ratio, sqnr, theory))
    return ok, line


# ---------------------------------------------------------------- T4 PWM average and RMS
def check_pwm_average():
    microbit._reset()
    pin = microbit.pin1
    pin.set_analog_period(20)                             # 20 ms, as in lesson 9
    pin.write_analog(511)
    duty = pin.duty / 1023
    period_us = pin.get_analog_period_microseconds()
    t = np.arange(period_us)                              # 1 us resolution, one period
    v = np.where(t < duty * period_us, 3.3, 0.0)
    avg, rms = v.mean(), math.sqrt((v ** 2).mean())
    spectrum = np.fft.rfft(v) / len(v)
    h1 = 2 * abs(spectrum[1])
    h1_theory = 2 * 3.3 / math.pi * math.sin(math.pi * duty)
    ok = abs(avg - duty * 3.3) < 3.3 / period_us and abs(rms - math.sqrt(duty) * 3.3) < 1e-3
    ok &= abs(h1 - h1_theory) < 1e-3
    line = ("T4 PWM: write_analog(511), period %d us -> D = %.5f; average %.4f V (D*3.3 = %.4f), RMS %.4f V "
            "(sqrt(D)*3.3 = %.4f), first harmonic %.4f V (theory %.4f)" % (
                period_us, duty, avg, duty * 3.3, rms, math.sqrt(duty) * 3.3, h1, h1_theory))
    return ok, line


CHECKS = [check_twos_complement, check_ohm_power, check_against_lesson14, check_adc_quantisation, check_pwm_average]


def run():
    return [c() for c in CHECKS]


if __name__ == "__main__":
    results = run()
    for ok, line in results:
        print(("OK   " if ok else "FAIL ") + line)
    sys.exit(0 if all(ok for ok, _ in results) else 1)
