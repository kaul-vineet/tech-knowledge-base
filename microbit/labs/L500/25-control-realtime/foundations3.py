"""L500 lesson 25 - Foundations III: numerical checks (control, real-time scheduling, CRC over GF(2)).

* Control: a first-order thermal plant (a heater or a warm LED driven by PWM duty u in [0, 1]).
  The controller writes its duty to the stub's pin0.write_analog(); the plant reads pin0.duty back.
  PLANT PARAMETERS ARE ILLUSTRATIVE ASSUMPTIONS (tau = 60 s, gain 20 C at full duty), not measured.
* Scheduling: exact simulation of preemptive rate-monotonic scheduling from a critical instant.
* CRC: CRC-16/CCITT-FALSE, the checksum used in labs/L300/12-reliable-radio.

Run:  python foundations3.py        (Windows: py foundations3.py)
"""
import itertools
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(LABS, "sim_stub"))
import microbit  # noqa: E402
import labtest  # noqa: E402

SEED = 25

# ---------------------------------------------------------------- T1 discrete control of a heater
TS, TAU, GAIN, AMBIENT = 1.0, 60.0, 20.0, 20.0      # s, s, C at full duty, C  (ASSUMPTIONS)
A = math.exp(-TS / TAU)
B = GAIN * (1 - A)


def simulate(controller, steps=600, r=5.0, gain=GAIN, disturbance=None, saturate=True):
    """x = temperature above ambient. x[k+1] = a x[k] + b' u[k] (+ disturbance). Returns x trace."""
    microbit._reset()
    b_true = gain * (1 - A)
    x, state, xs = 0.0, {}, []
    for k in range(steps):
        u = controller(r - x, state)
        if saturate:
            u = min(1.0, max(0.0, u))
            microbit.pin0.write_analog(int(round(u * 1023)))     # the "heater" PWM output
            u = microbit.pin0.duty / 1023                        # the plant sees the quantised duty
        d = disturbance(k) if disturbance else 0.0
        x = A * x + b_true * u + (1 - A) * d
        xs.append(x)
    return np.array(xs)


def open_loop(u0):
    return lambda e, s: u0


def p_ctrl(kp):
    return lambda e, s: kp * e


def pi_ctrl(kp, ki):
    def c(e, s):
        s["i"] = s.get("i", 0.0) + e * TS
        return kp * e + ki * s["i"]
    return c


def check_control():
    r = 5.0
    kp_max = (1 + A) / B                                  # stability boundary of the P loop
    # open loop is exact only if the model is exact: plant gain 16 instead of 20 -> error stays
    ol = simulate(open_loop(r / GAIN), gain=16.0, saturate=False)[-1]
    p = simulate(p_ctrl(2.0), gain=16.0, saturate=False)[-1]
    p_theory = r / (1 + 16.0 * 2.0)
    pi = simulate(pi_ctrl(0.5, 0.02), gain=16.0, disturbance=lambda k: -2.0 if k >= 300 else 0.0)
    # PI closed-loop poles: state (x, integral)
    kp, ki = 0.5, 0.02
    b16 = 16.0 * (1 - A)
    m = np.array([[A - b16 * (kp + ki * TS), b16 * ki], [-TS, 1.0]])
    poles = np.abs(np.linalg.eigvals(m))
    unstable = simulate(p_ctrl(kp_max * 1.1), steps=200, saturate=False)
    stable = simulate(p_ctrl(kp_max * 0.9), steps=2000, saturate=False)
    ok = abs((r - ol) - 1.0) < 1e-3 and abs((r - p) - p_theory) < 1e-6
    ok &= abs(r - pi[-1]) < 1e-2 and poles.max() < 1
    ok &= abs(unstable[-1]) > 1e6 and abs(stable[-1] - r * GAIN * kp_max * 0.9 / (1 + GAIN * kp_max * 0.9)) < 1e-6
    line = ("T1 control (assumed plant tau 60 s, gain 20 C, Ts 1 s): a=%.5f b=%.5f; P stable iff Kp < (1+a)/b = %.3f "
            "(1.1x diverges, 0.9x settles); plant gain 16: open-loop error %.3f C, P(Kp=2) error %.4f C "
            "(r/(1+K Kp) = %.4f), PI error %.4f C after a -2 C disturbance, PI pole radii %.4f/%.4f" % (
                A, B, kp_max, r - ol, r - p, p_theory, r - pi[-1], poles.max(), poles.min()))
    return ok, line


# ---------------------------------------------------------------- T2 rate-monotonic bound
def ll_bound(n):
    return n * (2 ** (1 / n) - 1)


def rm_first_jobs_meet_deadlines(tasks):
    """Exact for synchronous release (critical instant, L&L Theorem 1): simulate preemptive RM
    in integer time until the largest period; check every task's first job finishes by its period."""
    order = sorted(range(len(tasks)), key=lambda i: tasks[i][1])        # shorter period = higher priority
    horizon = max(t for _, t in tasks)
    remaining = {i: tasks[i][0] for i in order}
    done = {}
    for now in range(horizon):
        for i in order:
            c, t = tasks[i]
            if now > 0 and now % t == 0:
                if remaining[i] > 0 and i not in done:
                    return False                                         # previous job unfinished
                remaining[i] = c
        for i in order:
            if remaining[i] > 0:
                remaining[i] -= 1
                if remaining[i] == 0 and i not in done:
                    done[i] = now + 1
                break
    return all(i in done and done[i] <= tasks[i][1] for i in order)


def nonpreemptive_worst_response(high, low):
    """Cooperative scheduler (lesson 13): the high-priority job is released 1 ms after a low-priority
    job started; it waits for the low job to finish (blocking), then runs."""
    (c_hi, _), (c_lo, _) = high, low
    return (c_lo - 1) + c_hi


def check_rm_bound():
    rng = random.Random(SEED)
    tested = 0
    for _ in range(3000):
        n = rng.randint(2, 4)
        periods = [rng.randint(5, 200) for _ in range(n)]
        u_target = rng.uniform(0.3, ll_bound(n))
        shares = [rng.random() for _ in range(n)]
        tasks = [(max(1, int(u_target * s / sum(shares) * t)), t) for s, t in zip(shares, periods)]
        if sum(c / t for c, t in tasks) <= ll_bound(n):
            tested += 1
            if not rm_first_jobs_meet_deadlines(tasks):
                return False, "T2 counterexample %r" % (tasks,)
    tight = [(41, 100), (59, 141)]                         # C1 = T2 - T1, C2 = 2T1 - T2 (worst case, r = 1.41)
    tight_over = [(41, 100), (60, 141)]
    harmonic = [(1, 2), (2, 4)]                            # U = 1, schedulable: the bound is only sufficient
    full = [(2, 4), (5, 10)]                               # U = 1, not harmonic: misses
    lesson13 = [(5, 20), (20, 1000), (10, 100)]            # (budget ms, period ms) from lab 13 solution.py
    u13 = sum(c / t for c, t in lesson13)
    blocking = nonpreemptive_worst_response((5, 20), (20, 1000))
    ok = rm_first_jobs_meet_deadlines(tight) and not rm_first_jobs_meet_deadlines(tight_over)
    ok &= rm_first_jobs_meet_deadlines(harmonic) and not rm_first_jobs_meet_deadlines(full)
    ok &= rm_first_jobs_meet_deadlines(lesson13) and abs(ll_bound(1000) - math.log(2)) < 1e-3
    ok &= blocking > 20
    line = ("T2 RM bound: n(2^(1/n)-1) = %.4f, %.4f, %.4f (n=2,3,4) -> ln 2 = %.4f; %d random sets under the bound "
            "all meet deadlines; tight set U=%.4f meets, +1 ms misses; harmonic U=1 meets, (2,4),(5,10) U=1 misses; "
            "lesson 13 U=%.2f <= %.4f, but non-preemptive blocking gives the 20 ms button task a %d ms response" % (
                ll_bound(2), ll_bound(3), ll_bound(4), math.log(2), tested,
                sum(c / t for c, t in tight), u13, ll_bound(3), blocking))
    return ok, line


# ---------------------------------------------------------------- T3 CRC over GF(2)
POLY = 0x1021                     # x^16 + x^12 + x^5 + 1  (implicit x^16)
G_FULL = (1 << 16) | POLY


def crc16_bytes(data, init=0xFFFF):
    crc = init
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ POLY) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def poly_mod(a, g=G_FULL):
    dg = g.bit_length() - 1
    while a and a.bit_length() - 1 >= dg:
        a ^= g << (a.bit_length() - 1 - dg)
    return a


def bits_to_bytes(bits):
    return bytes(int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8))


def flip(msg, positions):
    b = bytearray(msg)
    for p in positions:
        b[p // 8] ^= 0x80 >> (p % 8)
    return bytes(b)


def check_crc():
    lab12 = labtest.load_lab(os.path.join(LABS, "L300", "12-reliable-radio"), "solution.py")
    same_as_lab = all(lab12.crc16(s) == crc16_bytes(s.encode("latin-1")) for s in ("123456789", "D:7:r7", "A:12:"))
    check_value = crc16_bytes(b"123456789")
    # raw register with init 0 = M(x) x^16 mod G  (polynomial division over GF(2))
    msg = bytes(random.Random(SEED).getrandbits(8) for _ in range(8))
    m_int = int.from_bytes(msg, "big")
    division_ok = crc16_bytes(msg, init=0) == poly_mod(m_int << 16)
    nbits = len(msg) * 8
    base = crc16_bytes(msg)
    syn = [crc16_bytes(flip(msg, [j])) ^ base for j in range(nbits)]            # single-bit syndromes
    rng = random.Random(SEED + 1)
    linear = all(crc16_bytes(flip(msg, ps)) ^ base == np.bitwise_xor.reduce([syn[p] for p in ps])
                 for ps in (rng.sample(range(nbits), rng.randint(2, 9)) for _ in range(3000)))
    syn = np.array(syn, dtype=np.int64)
    undetected = {}
    for length in range(1, 18):                     # every burst of length <= 17 at every position
        missed = 0
        for start in range(nbits - length + 1):
            end = start + length - 1
            sub = np.zeros(1, dtype=np.int64)
            for j in range(start + 1, end):          # all subsets of the inner bits (XOR-closed set)
                sub = np.concatenate([sub, sub ^ syn[j]])
            edge = syn[start] ^ (syn[end] if end != start else 0)
            missed += int(np.count_nonzero((sub ^ edge) == 0))
        undetected[length] = missed
    positions17 = nbits - 17 + 1
    odd_ok = all(crc16_bytes(flip(msg, ps)) != base for ps in itertools.combinations(range(nbits), 3))
    ok = same_as_lab and check_value == 0x29B1 and division_ok and linear and odd_ok
    ok &= all(undetected[length] == 0 for length in range(1, 17)) and undetected[17] == positions17
    line = ("T3 CRC-16/CCITT-FALSE: matches lab 12 crc16, check(\"123456789\") = 0x%04X, register = M(x)x^16 mod G; "
            "linear over GF(2) (3000 random patterns); 64-bit message: all bursts of length 1-16 detected, "
            "length 17: %d undetected in %d positions (1 in 2^15 each); all %d 3-bit errors detected (x+1 | G)" % (
                check_value, undetected[17], positions17, math.comb(nbits, 3)))
    return ok, line


CHECKS = [check_control, check_rm_bound, check_crc]


def run():
    return [c() for c in CHECKS]


if __name__ == "__main__":
    results = run()
    for ok, line in results:
        print(("OK   " if ok else "FAIL ") + line)
    sys.exit(0 if all(ok for ok, _ in results) else 1)
