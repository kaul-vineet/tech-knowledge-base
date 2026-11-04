# Lab 04-sound — Sound

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |

## Run in the simulator
Make sure the simulator sound is not muted. You hear a 'hello' sound and a beep. Press A (tune), B (speaker off/on), touch the logo (sweep effect).

Simulator inputs used: buttonA, buttonB, pinLogo.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
sound ready
tune played
speaker off
speaker on
effect played
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/04-sound
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15)
```
test_button_a_plays_tune (test_main.SoundLab.test_button_a_plays_tune) ... ok
test_button_b_toggles_speaker (test_main.SoundLab.test_button_b_toggles_speaker) ... ok
test_logo_plays_effect (test_main.SoundLab.test_logo_plays_effect) ... ok
test_start_plays_hello_and_pitch (test_main.SoundLab.test_start_plays_hello_and_pitch) ... ok
test_tune_after_speaker_off_is_logged_as_speaker_off (test_main.SoundLab.test_tune_after_speaker_off_is_logged_as_speaker_off) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.070s

OK
```

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/04-sound
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: variant 16 ticks = 2000 ms (original 20 ticks = 2500 ms)
try 2: serial='speaker off\ntune played\n', music.play calls=1, speaker_on during play=False
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.
