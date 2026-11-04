# Concept: sound as frequency over time

## Why it matters
You want a beep when a threshold is crossed, a short tune on success, and a way to stay silent in a classroom. You need to turn note names into frequencies and durations, and know where the sound comes out.

## Mental model
A tune is a **piano roll**: a list of (pitch, duration) pairs. Pitch comes from the note name (A4 = 440 Hz), duration from ticks and tempo. The sound leaves through two taps.

```
"c4:2" ─► 261.63 Hz for 2 ticks × 125 ms = 250 ms ─► tone ─┬─► pin 0 (always)
                                                           └─► V2 speaker (on/off)
```

## How it works
1. Notes are `NOTE[octave][:ticks]`, and octave and ticks carry over to later notes. At the default tempo (4 ticks per beat, 120 bpm) a tick is 125 ms, so the lab's `TUNE` is **20 ticks = 2500 ms** and `music.play()` blocks the loop that long (computed by `research/concept_examples.py`) → see lab step 2
2. `speaker.off()` closes only the V2 speaker tap; pin 0 still receives the sound → see lab step 3
3. `audio.SoundEffect` (V2 only) is one slide over time: the lab's `SWEEP` goes from **400 to 2000 Hz in 400 ms** → see lab step 5

## Common mistakes
- Forgetting that octave and ticks carry over, so later notes change length unexpectedly.
- Blocking playback hiding button presses for seconds.
- Expecting `speaker.off()` to silence pin 0.
