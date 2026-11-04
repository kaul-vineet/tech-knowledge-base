# Midterm exam — micro:bit physical computing (week 7)

**Covers:** L100 #1–6, L200 #7–11, L300 #12–15, L500 #23–24. **Time:** 90 minutes. **Total:** 70 marks.
Closed book; one A4 formula sheet; a calculator is allowed. Show working: an answer without reasoning earns at most half marks.
Every numeric model answer below is recomputed by `research/l500_checks.py` (section "exams").

---

### Q1 — Derivation (10 marks)
Lesson 10's temperature sensor returns a 12-bit two's-complement value, left-justified in two bytes: the MSB holds bits 11..4, the top four bits of the LSB hold bits 3..0, and one step is 0.0625 °C.
(a) The bytes are MSB = 0xE7, LSB = 0x00. Decode the temperature. (4)
(b) Prove that subtracting 4096 from the raw value when bit 11 is set gives the correct signed value. (4)
(c) What is the coldest temperature the format can represent? (2)

**Model answer.** (a) raw = (0xE7 << 4) | (0x00 >> 4) = 0xE70 = 3696; bit 11 is set, so value = 3696 − 4096 = −400 steps; −400 × 0.0625 = **−25.0 °C**. (b) In 12-bit two's complement v = −b11·2^11 + Σ_{i<11} b_i 2^i = raw − b11·2^12, so when b11 = 1 the value is raw − 4096 (lesson 23, theorem 1). (c) −2048 × 0.0625 = **−128.0 °C** (a format limit, not the sensor's rated range).
*Marking:* (a) 2 for raw, 2 for value; (b) 4 for the identity with justification; (c) 2.

### Q2 — Short explanation (8 marks)
Lesson 14's "before" logger uses `sleep(100)` between samples. Explain why its battery life is the same as a program that never sleeps, and what change the lesson makes instead. Name one figure in the power model that is an assumption, not a published value.

**Model answer.** `sleep()` waits in On mode: display, sensors and interface chip stay powered, so the model charges the full awake current (30 mA upper bound) all the time → 1,250/30 = 41.7 h. The fix is `power.deep_sleep(ms=...)` between samples plus adaptive sampling (100 ms → 8 s while steady). Assumptions: the board's Deep Sleep floor (0.05–0.5 mA) and the 20 ms awake time per wake-up.
*Marking:* 3 mechanism, 3 fix, 2 assumption.

### Q3 — Prediction (10 marks)
A logger samples the accelerometer at 10 Hz on a table next to a fan that vibrates at 12 Hz.
(a) At what frequency does the vibration appear in the log? (3)
(b) A student applies a 5-point moving average. Predict what happens to the vibration and why. (4)
(c) Is this a reliable fix? (3)

**Model answer.** (a) |12 − round(12/10)·10| = **2 Hz**. (b) A 5-point MA at 10 Hz has zeros at k·10/5 = 2, 4 Hz, so the 2 Hz alias is removed (lesson 24, theorem 2). (c) No: it depends on the fan speed staying exactly at 12 Hz; at 13 Hz the alias moves to 3 Hz and passes. Sample above 24 Hz (with an anti-alias filter) or mechanically isolate the board.
*Marking:* 3 / 4 / 3.

### Q4 — Calculation (12 marks)
A sensor node is awake at 25 mA for 15 ms every 5 s and sleeps at an assumed 0.3 mA floor. It runs on 2 × AAA rated 1,250 mAh.
(a) Compute the average current and the battery life. (6)
(b) Which input dominates the average, and what would you measure first? (3)
(c) State two reasons the real life will be shorter. (3)

**Model answer.** (a) D = 15/5000 = 0.003; I_avg = 0.003 × 25 + 0.997 × 0.3 = **0.3741 mA**; life = 1,250/0.3741 = **3,341.4 h** (about 139 days). (b) The sleep floor: 0.2991 of the 0.3741 mA (80 %); measure the board's sleep current. (c) Capacity falls at low temperature and with self-discharge; the awake current or time may be higher than assumed (radio, display, retries).
*Marking:* (a) 3 + 3; (b) 3; (c) 3.

### Q5 — Design critique (12 marks)
A team ports lesson 12's reliable radio to a noisy hall but sets a fixed 50 ms retransmit timeout, `MAX_TRIES = 20`, and removes duplicate suppression "because acks make it reliable". Critique the design and propose fixes.

**Model answer.** (1) Without dedupe, a lost **ack** causes a retransmission the receiver delivers twice — retransmission turns loss into duplication; restore the `expected` sequence check and re-ack old frames. (2) A fixed short timeout retransmits while the ack is still in flight, raising `retx` and channel load in exactly the busy conditions; use exponential backoff (lesson 12 doubles to 800 ms) and ideally jitter. (3) 20 tries holds the queue hostage behind one dead frame; bound retries, count `gave_up`, and check the receiver's `gap` before calling data lost. (4) Observability: keep the JSON counters. CRC-16 still drops damaged frames; it is not an authenticity check.
*Marking:* 3 per issue with fix (max 12).

### Q6 — Derivation (10 marks)
(a) Derive the white-noise variance ratio of the exponential filter y[n] = y[n−1] + α(x[n] − y[n−1]). (6)
(b) Which α matches a 4-point moving average, and what is the resulting standard-deviation ratio? (4)

**Model answer.** (a) h[n] = α(1−α)^n, so Var(y)/σ² = Σ h² = α²/(1 − (1−α)²) = α/(2 − α) (lesson 24, theorem 3). (b) α = 2/(N+1) = **0.4**; ratio α/(2−α) = 0.4/1.6 = 0.25, standard deviation ratio **0.5**.
*Marking:* 6 / 2 + 2.

### Q7 — Prediction (8 marks)
`pin2.write_analog(767)` with a 20 ms period drives an LED through a resistor from a 3.3 V pin. (a) Predict the average output voltage. (b) A multimeter on DC shows about that value; an oscilloscope shows something else. What, and why does the LED look about 75 % bright rather than "at that voltage"?

**Model answer.** (a) D = 767/1023 = 0.7498 → 0.7498 × 3.3 = **2.474 V**. (b) The scope shows a 50 Hz square wave between 0 and 3.3 V, high for 15.0 ms of every 20 ms; the meter averages it. The LED is fully on or off at any instant; the eye integrates the duty (lesson 23, theorem 4).
*Marking:* 3 / 5.
