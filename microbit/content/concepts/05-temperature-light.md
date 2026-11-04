# Concept: sample, classify, act — thresholds on noisy sensors

## Why it matters
A night-light should switch on when it gets dark; a fan warning should appear when it gets hot. Raw numbers are not decisions: you need thresholds, and they must not flicker when a reading sits on the edge.

## Mental model
A **thermostat**: it reads a number, compares it with a set point and switches state. Every pass of the loop does the same three things.

```
sample: temperature(), read_light_level()
   ─► classify(temp, light): dark? → hot? → ok
   ─► act: show an image, print key=value to serial
```

## How it works
1. **Sample**: `temperature()` returns whole °C from a sensor inside the processor (an approximation of air temperature); `display.read_light_level()` returns 0–255, larger = brighter → see lab step 2
2. **Classify** in a pure function with a fixed priority: dark is checked first, so `classify(30, 39)` is `dark`; the hot check is inclusive, so `classify(26, 128)` is `hot` → see lab step 3
3. **Named thresholds** (`HOT_C`, `DARK_LEVEL`) are the knobs. One threshold flickers on noisy data: readings `[25, 26, 25, 26, 27, 26, 25, 24]` change state **4** times at 26, but only **2** times with hysteresis (on at ≥27, off at ≤25) (computed by `research/concept_examples.py`) → see lab step 4

## Common mistakes
- Treating `temperature()` as room temperature on a busy processor.
- Two overlapping conditions without a clear priority.
- Thresholds hard-coded deep in the loop instead of named constants.
