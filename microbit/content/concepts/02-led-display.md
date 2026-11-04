# Concept: a display is a buffer of brightness numbers

## Why it matters
You want a status indicator: a tick when a reading is fine, a dim pattern while waiting, a scrolling value. With only 25 LEDs you think in pixels and brightness levels, and you need to know which calls block your program.

## Mental model
The display is a **5×5 grid of numbers 0–9**, the *display buffer*. Your code edits the grid; a driver keeps scanning it onto the LEDs row by row, fast enough to look steady (multiplexing).

```
"00900:09590:95159:09590:00900" ─parse─► 5×5 buffer ─driver scans rows─► LEDs
```

## How it works
1. Brightness is per pixel, from 0 (off) to 9 (brightest); `level_image(n)` fills all 25 pixels with `n`, and the loop ramps 0 → 9 and wraps → see lab step 2
2. `Image("...")` reads digits row by row and `:` ends a row. The lab's `DIAMOND` lights **13 of 25** LEDs with a brightness sum of **93**; pixel `(x=2, y=1)` is **5**, stored at flat index `y*5 + x = 7` (computed by `research/concept_examples.py`) → see lab step 3
3. `show()` replaces the whole buffer, built-in images such as `Image.HEART` are read-only (`copy()` first), and `scroll()` blocks until the text has passed unless `wait=False` → see lab step 4

## Common mistakes
- Editing a built-in image instead of a `copy()` of it.
- Using brightness 0–255 (the C++/MakeCode range); MicroPython takes 0–9.
- Forgetting that `scroll()` blocks, so button presses wait.
