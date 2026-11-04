# Concept: Foundations I — digital electronics and signals

## Why it matters
Every earlier lesson quietly relied on four facts: a sensor register holds a signed number (lessons 6, 10), a resistor sets an LED's current and the battery pays for it (lessons 9, 14), an analog reading is a rounded voltage (lesson 9), and PWM "makes" an in-between voltage (lesson 9). This lesson proves each fact, states its assumptions, and checks it numerically in `labs/L500/23-digital-foundations/foundations1.py`.

## Definitions
- **n-bit two's complement.** A pattern $b_{n-1}\dots b_0$ means $v = -b_{n-1}2^{n-1} + \sum_{i<n-1} b_i 2^i$. Range: $-2^{n-1}$ to $2^{n-1}-1$.
- **Ohm's law and KVL.** Across a resistor $V = IR$. Kirchhoff's voltage law: around a closed loop the voltage rises equal the drops. Power into a component is $P = VI$; for a resistor $P = I^2R$.
- **Charge capacity.** A cell rated $Q$ mAh delivers a constant current $I$ for about $Q/I$ hours (rated at a stated discharge current; real capacity falls at higher current and lower temperature).
- **Uniform quantiser.** An ideal N-bit ADC with reference $V_{ref}$ has step $\Delta = V_{ref}/2^N$ and outputs the nearest level. Quantisation error $e = Q(v) - v$.
- **PWM.** A rectangular wave of period $T$ that is high ($V_H$) for $DT$ and low (0 V) otherwise; $D \in [0,1]$ is the duty cycle.

## Key results
**T1 — two's complement negation.** For an n-bit pattern $u$ of value $x$, "invert all bits, add one" gives the pattern of $-x$ (mod $2^n$). *Proof:* $u + \bar u = 2^n - 1$ (every bit position sums to 1), so $\bar u + 1 = 2^n - u \equiv -u \pmod{2^n}$. Addition and subtraction are the same circuit as for unsigned numbers, because both are arithmetic mod $2^n$. The one exception is $-2^{n-1}$: its negation $2^{n-1}$ is out of range and the pattern maps to itself.

**T2 — the LED resistor and the battery bill.** With supply $V_s$, LED forward voltage $V_f$ and target current $I$, KVL gives $V_s = IR + V_f$, so $R = (V_s - V_f)/I$. Power splits as $V_sI = I^2R + V_fI$. A duty-cycled load drawing $I_{on}$ for time $t_{on}$ and $I_{off}$ otherwise in a window $T_w$ has time-average $\bar I = (t_{on}I_{on} + (T_w - t_{on})I_{off})/T_w$, and life $\approx Q/\bar I$. The average must be taken over exactly the window you mean: lesson 14's model once averaged over 3,607,400 ms instead of one hour (its last 8 s sleep ran past the hour), which printed 9,600.5 h instead of the 9,588.4 h its own inputs give.

**T3 — quantisation noise $\Delta^2/12$.** If the input is "busy" (it crosses many steps, so the position inside a step is uniformly distributed), $e$ is uniform on $[-\Delta/2, \Delta/2]$: mean $0$, variance $\int_{-\Delta/2}^{\Delta/2} e^2\,de/\Delta = \Delta^2/12$, RMS $\Delta/\sqrt{12}$. For a full-scale sine (amplitude $2^N\Delta/2$, power $2^{2N}\Delta^2/8$) the signal-to-quantisation-noise ratio is $\frac{2^{2N}\Delta^2/8}{\Delta^2/12} = 1.5\cdot 2^{2N}$, i.e. $6.02N + 1.76$ dB.

**T4 — PWM average and RMS.** $\bar v = \frac1T\int_0^T v\,dt = \frac{1}{T}V_H DT = DV_H$; $v_{rms} = \sqrt{\frac1T\int v^2} = \sqrt D\,V_H$. The Fourier series has a DC term $DV_H$ and harmonics at $k/T$ with amplitude $\frac{2V_H}{k\pi}|\sin(k\pi D)|$; a low-pass filter whose cut-off is far below $1/T$ keeps the DC term, which is why "PWM = analog voltage" is true only after filtering (or for a slow load such as a heater, a motor, or the eye).

## Intuition
Two's complement is a clock face: $2^n$ positions, and "negative" just means "count backwards from zero". The battery is a bucket emptied at the *average* rate, so a tiny sleep current that flows 99.7 % of the time can dominate a large awake current. Quantisation is a rounding error you cannot see sample by sample but can predict on average. PWM is time-sharing of a voltage; anything slower than the period only feels the average.

## Worked example (numbers from `foundations1.py`)
- Stub accelerometer at rest: $z = -1024$ mg → 16-bit pattern `0xFC00`; pattern `0xFE0C` decodes to −500.
- LED: 3.3 V supply, assumed red LED $V_f = 2.0$ V, target 5 mA → $R = 260\ \Omega$ → next E12 value 270 Ω → $I = 4.815$ mA, $P_R = 6.26$ mW, $P_{LED} = 9.63$ mW, and $V_sI = P_R + P_{LED}$.
- Lesson 14: 483 wake-ups × 20 ms at 30 mA in 3,600,000 ms, floor 0.05 mA → $\bar I = 0.13037$ mA → 9,588.4 h; floor 0.5 mA → 2,158.3 h. The check also runs `budget.py` and gets the same figures.
- ADC: 10 bits, 3.3 V → $\Delta = 3.2227$ mV, RMS error 0.9303 mV; measured variance ratio 1.0006; full-scale sine SQNR 61.89 dB vs 61.96 dB predicted.
- PWM: `write_analog(511)` with a 20 ms period → $D = 511/1023 = 0.49951$ → average 1.6484 V, RMS 2.3323 V, first harmonic 2.1008 V.

## Common misconceptions
- *"The MSB is just a minus sign."* That is sign-magnitude; it has two zeros and needs different adder logic.
- *"Choose the nearest E12 resistor."* Choose the next value **up**, or the current exceeds the target.
- *"mAh ratings are exact."* They are rated at one discharge current; label the figure and its conditions.
- *"Quantisation error is always $\Delta^2/12$."* Only for busy inputs. A constant input has a fixed, deterministic error; that is why dither exists.
- *"PWM at 50 % gives the LED 1.65 V."* The LED sees 3.3 V (or 0 V) at any instant; only the average light or heat follows $D$.
- *"Averaging is window-free."* An average needs a stated window. Averaging over a window you did not intend changes the answer, as lesson 14's 9,601 h did.

## Where it is used
Lesson 6 (accelerometer values), 9 (PWM, `read_analog`), 10 (signed sensor registers over I²C), 14 (power budget). Validation: the checks run on the CPython stub and numpy; nothing here was measured on a board (validated-stub).
