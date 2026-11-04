# Lab L500 #23 — Foundations I: digital electronics and signals (theorem checks)

Numerical checks for the theorems in `content/L500.json` (lesson 23) and the concept note
`content/concepts/L500/23-digital-foundations.md`. Each `check_*` function returns `(ok, line)`; the lines are quoted verbatim
as `checkOutput` in the JSON, and `research/l500_checks.py` fails if they drift.

**What is checked:** Two's complement (also against lab 10's `decode_temp`), Ohm/KVL/power and battery life (also against lab 14's `budget.py`), ADC quantisation noise, PWM average/RMS/harmonics (via the stub's `pin1.write_analog`).

**Validation status: validated-stub.** CPython 3.12.15 + numpy 2.5.3 on Linux, with `labs/sim_stub`. Nothing was
measured on a micro:bit; Mac/Windows runs are pending CI.

| File | Purpose |
|---|---|
| `foundations1.py` | The checks; `python foundations1.py` prints one line per theorem and exits 1 on any failure |
| `test_theory.py` | One unittest per check (run by `labs/run_tests.py`) |

## Run
```bash
cd labs/L500/23-digital-foundations
python3 -m pip install numpy==2.5.3    # once; Windows: py -m pip install numpy==2.5.3
python3 foundations1.py                   # Windows (PowerShell): py foundations1.py
python3 -m unittest -v
```

## Expected output (observed, Python 3.12.15, numpy 2.5.3, Linux sandbox)
```
OK   T1 two's complement: n=8,12,16 exhaustive round-trip + invert-and-add-one OK for 69888 values; -2^(n-1) negates to itself; lab 10 decode_temp == 12-bit decode for all 4096 patterns; stub z=-1024 mg -> 0xFC00; 0xFE0C -> -500
OK   T2 Ohm/KVL/power: 3.3 V, Vf 2.0 V, 5 mA -> R 260 ohm -> E12 270 ohm, I 4.815 mA, P_R 6.26 mW, P_LED 9.63 mW, Vs*I = P_R + P_LED; battery 1250 mAh: 2158.3 h (0.5 mA floor), 9588.4 h (0.05 mA), 9600.5 h if the window is stretched to 3,607,400 ms
OK   T2b lesson 14 cross-check: budget.py life_h 2158.3, range [2158.3, 9588.4] == closed-form t = Q / I_avg
OK   T3 ADC: 10-bit, 3.3 V -> step 3.2227 mV, RMS error theory 0.9303 mV, measured var/(step^2/12) = 1.0006; full-scale sine SQNR 61.89 dB vs 6.02N+1.76 = 61.96 dB
OK   T4 PWM: write_analog(511), period 20000 us -> D = 0.49951; average 1.6485 V (D*3.3 = 1.6484), RMS 2.3324 V (sqrt(D)*3.3 = 2.3323), first harmonic 2.1008 V (theory 2.1008)
```
```
test_check_adc_quantisation (test_theory.TheoremChecks.test_check_adc_quantisation) ... ok
test_check_against_lesson14 (test_theory.TheoremChecks.test_check_against_lesson14) ... ok
test_check_ohm_power (test_theory.TheoremChecks.test_check_ohm_power) ... ok
test_check_pwm_average (test_theory.TheoremChecks.test_check_pwm_average) ... ok
test_check_twos_complement (test_theory.TheoremChecks.test_check_twos_complement) ... ok

----------------------------------------------------------------------
Ran 5 tests

OK
```
