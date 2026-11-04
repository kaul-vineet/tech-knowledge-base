# Concept: a power budget you can defend (modelled, not measured)

## Why it matters
On USB the logger from lesson 8 runs forever. On two AAA cells it is flat in under two days, and you find out in the field. A budget written before deployment tells you which design choice matters. Every number here is a labelled **estimate**; nothing was measured on a board.

## Mental model
**Average current is the area under the curve.** The board is either awake (high current, short) or asleep (tiny current, long). Battery life is capacity divided by the time-weighted average.

```
current
 30 mA ┤█        █        █          awake ACTIVE_MS per sample
       ┤█        █        █
 ~0    ┤█▁▁▁▁▁▁▁▁█▁▁▁▁▁▁▁▁█▁▁▁▁▁   Deep Sleep in between
        └──────── interval ─────► time
avg = (awake_ms × I_awake + asleep_ms × I_sleep) / total_ms ; life = mAh / avg
```

## How it works
1. **Figures carry labels.** `budget.py` keeps every input with its source: 30 mA is the micro:bit power-supply page's worst-case on-board budget (UPPER BOUND); the unpublished board sleep floor is assumed 0.05–0.5 mA (BOARD SLEEP FLOOR); 1.5 µA is the nRF52833 alone (CHIP ONLY, a bound); 20 ms awake per wake-up is an ASSUMPTION; 1,250 mAh is the Energizer E92 rating at 25 mA → see lab step 2
2. **`sleep()` is not a low-power mode.** It keeps the board in On mode, so the model counts all of it as awake → see lab step 3
3. **Duty cycle decides.** `power.deep_sleep(ms=...)` turns on-board components off between samples; the model charges `ACTIVE_MS` per wake-up and the sleep floor otherwise → see lab step 4
4. **Sampling rate is the biggest lever.** Deep sleep at a fixed 100 ms is still awake 20% of the time → see lab step 6
5. **Adaptive sampling.** `next_interval()` resets to 100 ms when the reading changes and doubles to 8 s while steady, so you pay for detail only during events → see lab step 4
6. **The brief is two numbers.** Life ≥ 720 h and detection delay ≤ 10 s; `report()` prints both as one JSON line → see lab step 5

Worked example (from `research/concept_examples_l300.py`, one simulated hour): the 100 ms always-on logger takes 36,000 samples at 30 mA → 1,250 / 30 = 41.7 h. Deep sleep at a fixed 100 ms: 20% awake → 6.4 mA → 195 h. Adaptive: 483 wake-ups, 0.27% awake → 0.579 mA → **about 2,160 h on the board estimate** (2,158–9,588 h across the assumed floor), worst detection delay 4.7 s. The chip-only floor's 15,245 h is a bound, not a board figure. Even the optimistic chip-only awake current (3.3 mA CPU + 4.6 mA radio receive = 7.9 mA) gives the always-on design only 158 h.

## Failure modes
- **The sleep floor is unknown.** At 0.5 mA it is 86% of the adaptive average. Measure before you promise a lifetime.
- **Results beyond the cell.** The model ignores alkaline self-discharge and temperature; months-long figures are optimistic.
- **Events shorter than the interval.** A 1.5 s spike between two samples 8 s apart is never logged.
- **Noise defeats adaptation.** A reading that flickers by 1 °C resets the interval every time; add hysteresis.

## Common mistakes
- Using the chip's datasheet sleep current as the board's current.
- Quoting a result without its labelled inputs, so nobody can check it.
- Optimising the active burst while the sampling interval decides the total.
