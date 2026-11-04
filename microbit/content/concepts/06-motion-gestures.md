# Concept: acceleration vectors and named gestures

## Why it matters
You want a device that reacts when it is shaken or tilted: a tilt game, a "drop detected" alert, a shake-to-reset. You need to turn three numbers into a direction and catch short events like a shake without missing or repeating them.

## Mental model
Picture an **arrow inside the board** that always points the way gravity pulls. Lying flat, face up, it points straight down through the board (Z). Tilting rotates the arrow, but its length stays about 1 g. A *gesture* is the runtime naming a pattern of that arrow over time: "shake", "face down", "freefall".

```
flat:   x=0,   z=-1024 mg  → strength 1024 mg, tilt flat
right:  x=800, z=-640 mg   → strength 1024 mg, tilt right
```
(Values from `research/concept_examples.py`.)

## How it works
1. `get_values()` returns x, y and z in milli-g; the lab says `right` if x > 300 and `left` if x < −300 → see lab step 2
2. `was_gesture("shake")` is True once per shake and then cleared, so one shake prints `shake!` once → see lab step 3
3. MicroPython updates gestures only while you keep calling accelerometer methods, so the loop polls every 200 ms and logs `current_gesture()` → see lab step 4

## Common mistakes
- No polling loop, so gestures are never detected.
- Using `is_gesture("shake")` and reacting many times to one shake.
- Thresholds near 0, so hand tremor flips the direction.
