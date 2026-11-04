# Lab L500 #25 — Foundations III: control and real-time theory (theorem checks)

Numerical checks for the theorems in `content/L500.json` (lesson 25) and the concept note
`content/concepts/L500/25-control-realtime.md`. Each `check_*` function returns `(ok, line)`; the lines are quoted verbatim
as `checkOutput` in the JSON, and `research/l500_checks.py` fails if they drift.

**What is checked:** Open vs closed loop and P/PI stability on a simulated heater driven through the stub's `pin0.write_analog` (plant parameters are ASSUMPTIONS), the Liu & Layland bound against exact RM simulation (incl. lesson 13's task set and non-preemptive blocking), CRC-16/CCITT-FALSE as GF(2) division (against lab 12's `crc16`).

**Validation status: validated-stub.** CPython 3.12.15 + numpy 2.5.3 on Linux, with `labs/sim_stub`. Nothing was
measured on a micro:bit; Mac/Windows runs are pending CI.

| File | Purpose |
|---|---|
| `foundations3.py` | The checks; `python foundations3.py` prints one line per theorem and exits 1 on any failure |
| `test_theory.py` | One unittest per check (run by `labs/run_tests.py`) |

## Run
```bash
cd labs/L500/25-control-realtime
python3 -m pip install numpy==2.5.3    # once; Windows: py -m pip install numpy==2.5.3
python3 foundations3.py                   # Windows (PowerShell): py foundations3.py
python3 -m unittest -v
```

## Expected output (observed, Python 3.12.15, numpy 2.5.3, Linux sandbox)
```
OK   T1 control (assumed plant tau 60 s, gain 20 C, Ts 1 s): a=0.98347 b=0.33057; P stable iff Kp < (1+a)/b = 6.000 (1.1x diverges, 0.9x settles); plant gain 16: open-loop error 1.000 C, P(Kp=2) error 0.1515 C (r/(1+K Kp) = 0.1515), PI error 0.0000 C after a -2 C disturbance, PI pole radii 0.9483/0.8976
OK   T2 RM bound: n(2^(1/n)-1) = 0.8284, 0.7798, 0.7568 (n=2,3,4) -> ln 2 = 0.6931; 2985 random sets under the bound all meet deadlines; tight set U=0.8284 meets, +1 ms misses; harmonic U=1 meets, (2,4),(5,10) U=1 misses; lesson 13 U=0.37 <= 0.7798, but non-preemptive blocking gives the 20 ms button task a 24 ms response
OK   T3 CRC-16/CCITT-FALSE: matches lab 12 crc16, check("123456789") = 0x29B1, register = M(x)x^16 mod G; linear over GF(2) (3000 random patterns); 64-bit message: all bursts of length 1-16 detected, length 17: 48 undetected in 48 positions (1 in 2^15 each); all 41664 3-bit errors detected (x+1 | G)
```
```
test_check_control (test_theory.TheoremChecks.test_check_control) ... ok
test_check_crc (test_theory.TheoremChecks.test_check_crc) ... ok
test_check_rm_bound (test_theory.TheoremChecks.test_check_rm_bound) ... ok

----------------------------------------------------------------------
Ran 3 tests

OK
```
