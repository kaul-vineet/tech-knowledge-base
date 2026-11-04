# Explain tab — run log (micro:bit)

Every output quoted in a **What you see** or **See it in numbers** block of `content/explain/NN.md` comes from the
runs below. Environment: Linux sandbox, Python 3.12.15, numpy 2.5.3, the topic's CPython stub (`labs/sim_stub`).
Nothing ran in the official micro:bit simulator, in Renode, with `cargo`, on a real board, against a real MQTT
broker or with a real local model; the explanations mark those parts "Expected (not run here)".
Date of all runs: 2026-11-02. Labs were run one at a time (slow storage mount).

## How the runs were made
* `python3 run.py NN <folder> "<commands>" [peek]` (a session helper, not part of the KB) ran each command from the
  topic root folder shown, re-entering the folder before every `;`-separated command, and appended the command, date,
  exit code and the full combined stdout+stderr below.
* "Peek" scripts are small read-only drivers that import a lab's own code against the stub to show an internal value
  (a frame, a counter, a state). Each was copied into the lab folder as `_peek.py`, run, and deleted; its source is
  printed under its output. Nothing in the labs was edited.
* Generated outputs of the capstone (`build/`, `out/`, both git-ignored) were deleted after the run.

## Differences from the lab READMEs and run problems (honest notes)
* Lesson 01: `Ran 4 tests in 3.702s` here vs `0.009s` in the README — slow storage, same 4 tests OK.
* Lesson 08: the first peek capped the stub log at 80 bytes and all four rows fitted; it was re-run at 60 bytes to show
  `OSError 28`. Both runs are kept below.
* Lesson 17: the first two attempts failed with `FileNotFoundError` inside `Path(__file__).resolve()` (the storage mount
  dropped the working directory); the runner was changed to re-enter the folder before each command and the runs were
  repeated. The failed attempts are kept below; the explanation quotes only the successful runs.
* Lesson 21: `python3 try_it.py` crashed while deleting its temporary folder (`OSError: [Errno 39] Directory not empty:
  …/__pycache__`, a storage-mount problem, not a lab bug). The leftover folder was removed and the run repeated with
  `PYTHONDONTWRITEBYTECODE=1`, which gave the README's numbers.
* Lesson 22: the scorecard's "other drift alarms" entry was `n6 DRIFT_LAT`; n4's `DRIFT_TEMP` appears in the operator
  note. All 10 criteria PASS as in the README.
* All other quoted numbers match the lesson JSON / README values.


## Lesson 01

### Lesson 01 — `cd labs/L100/01-setup && python3 -m unittest -v` (2026-11-02, exit 0)
```
test_hello_shows_image_and_prints (test_main.SetupLab.test_hello_shows_image_and_prints) ... ok
test_step_counts_up (test_main.SetupLab.test_step_counts_up) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 4 tests in 3.702s

OK
```

### Lesson 01 — `cd labs/L100/01-setup && python3 try_it.py` (2026-11-02, exit 0)
```
try 1: 'hello from micro:bit\ntick 1\ntick 2\ntick 3\ntick 4\n', running_time()=1000 ms
try 2: import returned=False, serial='hello from micro:bit\ntick 1\ntick 2\ntick 3\n'
```

### Lesson 01 — `cd labs/L100/01-setup && python3 main.py 2>&1 | tail -2` (2026-11-02, exit 0)
```
    ^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'microbit'
```

### Lesson 01 — `cd labs/L100/01-setup && python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
lab = load_lab('.')
with serial() as out:
    lab.hello(); n = lab.step(0); microbit.sleep(1000); n = lab.step(n)
print(repr(out.getvalue()))
print('image:', microbit.display.current_image(), 'is HAPPY:', microbit.display.current_image() == microbit.Image.HAPPY)
print('running_time():', microbit.running_time())
"` (2026-11-02, exit 0)
```
'hello from micro:bit\ntick 1\ntick 2\n'
image: Image('00000:09090:00000:90009:09990:') is HAPPY: True
running_time(): 1000
```

## Lesson 02

### Lesson 02 — `cd labs/L100/02-led-display && python3 -m unittest -v` (2026-11-02, exit 0)
```
test_builtin_images_are_read_only (test_main.LedDisplayLab.test_builtin_images_are_read_only) ... ok
test_custom_image_pixels (test_main.LedDisplayLab.test_custom_image_pixels) ... ok
test_intro_sequence (test_main.LedDisplayLab.test_intro_sequence) ... ok
test_step_shows_level_and_wraps (test_main.LedDisplayLab.test_step_shows_level_and_wraps) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.076s

OK
```

### Lesson 02 — `cd labs/L100/02-led-display && python3 try_it.py` (2026-11-02, exit 0)
```
try 1: lit=13, sum=101, centre=9
try 2: 0 1 2 3 4 0 1
```

### Lesson 02 — `cd labs/L100/02-led-display && python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
lab = load_lab('.')
with serial() as out:
    lab.intro()
print([ (k, v if isinstance(v,str) else repr(v)) for k,v in microbit.display.history])
print('clock after intro:', microbit.running_time(), 'ms')
print('DIAMOND sum:', sum(lab.DIAMOND.get_pixel(x,y) for x in range(5) for y in range(5)))
print('level_image(4):', lab.level_image(4))
try:
    microbit.Image.HEART.set_pixel(0,0,9)
except TypeError as e: print('TypeError:', e)
"` (2026-11-02, exit 0)
```
[('scroll', 'Hi'), ('show', "Image('09090:99999:99999:09990:00900:')"), ('show', "Image('00900:09590:95159:09590:00900:')")]
clock after intro: 1000 ms
DIAMOND sum: 93
level_image(4): Image('44444:44444:44444:44444:44444:')
TypeError: image cannot be modified (try copying first)
```

## Lesson 03

### Lesson 03 — `cd labs/L100/03-buttons && python3 -m unittest -v 2>&1 | tail -6; python3 try_it.py; python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
from microbit import button_a, button_b
lab = load_lab('.')
with serial() as out:
    button_a.click(3); print('pending presses:', button_a._presses, 'was flag:', button_a._was)
    c = lab.step(0)
    c = lab.step(c)
    button_b.click(); c = lab.step(c)
    button_a.press(); button_b.press(); c = lab.step(c)
print(out.getvalue(), end='')
print('display last_text:', microbit.display.last_text)
"` (2026-11-02, exit 0)
```
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.034s

OK
try 1: count=1, serial='count 1\n'
try 2: after 3 clicks: count=0 serial=''; held for 3 polls: count=3 serial='count 1\ncount 2\ncount 3\n'
pending presses: 3 was flag: True
count 3
count 0
both held
display last_text: 0
```

## Lesson 04

### Lesson 04 — `cd labs/L100/04-sound && python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
lab = load_lab('.')
with serial() as out:
    lab.start(); microbit.button_b.click(); lab.step(); microbit.button_a.click(); lab.step()
print(out.getvalue(), end='')
for e in microbit.sound_log: print(e)
print('clock:', microbit.running_time())
"` (2026-11-02, exit 0)
```
----------------------------------------------------------------------
Ran 7 tests in 0.048s

OK
try 1: variant 16 ticks = 2000 ms (original 20 ticks = 2500 ms)
try 2: serial='speaker off\ntune played\n', music.play calls=1, speaker_on during play=False
sound ready
speaker off
tune played
('audio', 'hello', True)
('music', ('pitch', (440, 200)), True)
('music', ('play', ['c4:2', 'e', 'g', 'c5:4', 'r:2', 'g4:2', 'c5:6']), False)
clock: 0
```

## Lesson 05

### Lesson 05 — `cd labs/L100/05-temperature-light && python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
lab = load_lab('.')
with serial() as out:
    for t, l in [(25, 128), (26, 128), (30, 39), (30, 40)]:
        microbit._temperature_c = t; microbit.display.inject_light_level(l); lab.step()
print(out.getvalue(), end='')
"; python3 agent_assist.py --fake 2>&1 | tail -4` (2026-11-02, exit 0)
```
----------------------------------------------------------------------
Ran 12 tests in 1.323s

OK
try 1: temp=27,light=128,state=ok
try 2: temp=30,light=10,state=hot
temp=25,light=128,state=ok
temp=26,light=128,state=hot
temp=30,light=39,state=dark
temp=30,light=40,state=hot
  temp=22,light=200,state=ok
code decision (authoritative): 5 readings, alarms: #3 hot (temp=27, light=110), #4 dark (temp=30, light=35)
agent explanation (checked): The micro:bit sent 5 readings. Temperature started at 21 C and ended at 22 C, peaking at 30 C; this is the processor's own estimate, so it can read a little above the room. Light ranged from 35 to 200, where larger means brighter. The program itself labelled the readings: 1 hot and 1 dark; everything else was ok.
check: PASS (numbers all from telemetry; alarm states named)
```

## Lesson 06

### Lesson 06 — `cd labs/L100/06-motion-gestures && python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; python3 -c "
import sys; sys.path.insert(0,'../../sim_stub')
from labtest import load_lab, serial; import microbit
from microbit import accelerometer as acc
lab = load_lab('.')
with serial() as out:
    lab.step()
    print('strength:', acc.get_strength())
    acc.inject_axes(x=800, z=-600); lab.step()
    acc.inject_axes(x=-300); lab.step()
    acc.inject_gesture('shake'); lab.step(); lab.step()
print(out.getvalue(), end='')
"` (2026-11-02, exit 0)
```
----------------------------------------------------------------------
Ran 6 tests in 0.077s

OK
try 1: x=200,y=0,z=-1024,tilt=right,gesture=
try 2: 'shake!' printed 3 time(s) in 3 polls
x=0,y=0,z=-1024,tilt=flat,gesture=
strength: 1024
x=800,y=0,z=-600,tilt=right,gesture=
x=-300,y=0,z=-600,tilt=flat,gesture=
x=-300,y=0,z=-600,tilt=flat,gesture=shake
shake!
x=-300,y=0,z=-600,tilt=flat,gesture=shake
```

## Lesson 07

### Lesson 07 — `cd labs/L200/07-radio && python3 _peek.py (source below); rm _peek.py; python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; BUILD_FILE=solution.py python3 -m unittest test_build_task 2>&1 | tail -3` (2026-11-02, exit 0)
```
tx btn 1 A
rx btn 1 A
rx bad 1
rx bad 2
tx btn 2 A
tx btn 3 A
tx btn 4 A
tx btn 5 A
B queue length: 3 dropped: 1
A on-air bytes for seq 2: b'\x01\x00\x01btn:2:A'
----------------------------------------------------------------------
Ran 13 tests in 0.622s

OK
try 1: tx btn 1 A
try 2: tx btn 1 A*40 | rx btn 1 A*23 | bytes on air: 32
Ran 2 tests in 0.138s

OK
```

Peek script `_peek.py` used above (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_boards, serial
a, b = load_boards('.')
sa, sb = a.lab.new_state(), b.lab.new_state()
with serial() as out:
    a.mb.button_a.click(); a.lab.step(sa); b.lab.step(sb)
    b.radio._inject_str('btn:1:A'); b.lab.step(sb)          # replay of seq 1
    b.radio._inject_str('hello'); b.lab.step(sb)
    b.radio._inject(b'\xff\x00raw'); b.lab.step(sb)
    for _ in range(4):
        a.mb.button_a.click(); a.lab.step(sa)
print(out.getvalue(), end='')
print('B queue length:', len(b.radio._queue), 'dropped:', b.radio.dropped)
print('A on-air bytes for seq 2:', b.radio._queue[0][0])
```

## Lesson 08

### Lesson 08 — `cd labs/L200/08-data-logging && python3 _peek.py; rm -f _peek.py; python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; python3 agent_assist.py --fake 2>&1 | tail -4` (2026-11-02, exit 0)
```
time_ms,temp,light
0,21,120
1000,22,110
2000,23,90
3000,24,70
MY_DATA csv:
Time (seconds),temp,light
0.00,21,120
1.00,22,110
2.00,23,90
3.00,24,70
----------------------------------------------------------------------
Ran 15 tests in 15.860s

OK
try 1: time_ms,temp,light | Time (seconds),temp,light | 0.00,21,120 | 0,21,120 | 1.00,22,110 | 1000,22,110
try 2: kept 2 rows [['0', '21', '120'], ['1000', '22', '110']]; skipped 3 (Time (seconds),temp,light: time_ms not an integer, 0.00,21,120: time_ms not an integer, 1.00,22,110: time_ms not an integer)
  5000,24,41
code stats (authoritative): 6 rows over 5 s; temp 21..24 mean 22.5 (up); light 41..120 mean 89.8 (down)
agent explanation (checked): The log has 6 rows over 5 seconds. Temperature rose from 21 to 24, with a mean of 22.5. Light fell from 120 to 41, with a mean of 89.8.
check: PASS (every number matches the CSV or a computed stat; trends match)
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab, serial
import microbit, log
lab = load_lab('.')
log._reset(); log._set_capacity(80)
st = lab.new_state()
with serial() as out:
    lab.setup()
    for t, l in [(21, 120), (22, 110), (23, 90), (24, 70)]:
        microbit._temperature_c = t; microbit.display.inject_light_level(l)
        try:
            lab.step(st)
        except OSError as e:
            print('OSError', e.args[0], 'after', st['rows'], 'rows')
            break
        microbit.sleep(1000)
print(out.getvalue(), end='')
print('MY_DATA csv:'); print(log._csv(), end='')
```

### Lesson 08 — `cd labs/L200/08-data-logging && python3 _peek.py; rm -f _peek.py` (2026-11-02, exit 0)
```
time_ms,temp,light
0,21,120
1000,22,110
OSError 28 after 2 rows
MY_DATA csv:
Time (seconds),temp,light
0.00,21,120
1.00,22,110
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab, serial
import microbit, log
lab = load_lab('.')
log._reset(); log._set_capacity(60)
st = lab.new_state()
with serial() as out:
    lab.setup()
    for t, l in [(21, 120), (22, 110), (23, 90), (24, 70)]:
        microbit._temperature_c = t; microbit.display.inject_light_level(l)
        try:
            lab.step(st)
        except OSError as e:
            print('OSError', e.args[0], 'after', st['rows'], 'rows')
            break
        microbit.sleep(1000)
print(out.getvalue(), end='')
print('MY_DATA csv:'); print(log._csv(), end='')
```

## Lesson 09

### Lesson 09 — `cd labs/L200/09-pins-pwm && python3 _peek.py; rm -f _peek.py; python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; BUILD_FILE=solution.py python3 -m unittest test_build_task 2>&1 | tail -3` (2026-11-02, exit 0)
```
duty_for(0..4): [0, 255, 511, 767, 1023]
pin2 period us: 20000
on=0,level=2,duty=0
on=1,level=2,duty=511
on=1,level=3,duty=767
on=1,level=3,duty=1023
on=1,level=3,duty=767
pin1 history: [('digital', 1), ('digital', 1), ('digital', 1)] pin2 last: ('analog', 767)
avg volts at 767: 2.47
ValueError: value must be between 0 and 1023
----------------------------------------------------------------------
Ran 10 tests in 0.891s

OK
try 1: on=1,level=2,duty=511 | on=0,level=2,duty=0 | on=1,level=2,duty=511
try 2: on=1,level=2,duty=682 | duty_for(0..3) = [0, 341, 682, 1023]
Ran 2 tests in 0.520s

OK
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab, serial
import microbit as mb
lab = load_lab('.')
st = lab.new_state()
print('duty_for(0..4):', [lab.duty_for(l) for l in range(5)])
print('pin2 period us:', mb.pin2.get_analog_period_microseconds())
with serial() as out:
    lab.step(st)
    mb.pin_logo.inject_touch(True)
    for _ in range(3): lab.step(st)        # held for 3 polls
    mb.pin_logo.inject_touch(False); lab.step(st)
    mb.button_a.click(); lab.step(st)
    mb.pin0.inject_touch(True); lab.step(st)
    mb.pin0.inject_touch(False); lab.step(st)
print(out.getvalue(), end='')
print('pin1 history:', mb.pin1.history[-3:], 'pin2 last:', mb.pin2.history[-1])
print('avg volts at 767:', round(767 / 1023 * 3.3, 2))
try:
    mb.pin2.write_analog(1024)
except ValueError as e:
    print('ValueError:', e)
```

## Lesson 10

### Lesson 10 — `cd labs/L200/10-i2c-sensor && python3 _peek.py; rm -f _peek.py; python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; BUILD_FILE=solution.py python3 -m unittest test_build_task 2>&1 | tail -3` (2026-11-02, exit 0)
```
i2c: no device at 0x48 (errno 19)
scan: ['0x48']
temp_c=21.50
transactions: [('write', 72, b'\x00'), ('read', 72, b'\x15\x80')]
temp_c=-25.00
last read bytes: e700
raw = 344 -> 21.5 C
raw unsigned = 3696 = 0xe70 sign bit: True -> signed -400 -> -25.0 C; without sign fix 231.0
----------------------------------------------------------------------
Ran 11 tests in 0.210s

OK
try 1: i2c: no device at 0x49 (errno 19)
try 2: temp_c=231.00
Ran 3 tests in 0.047s

OK
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab, serial
from i2c_devices import TMP102
import microbit
lab = load_lab('.')
with serial() as out:
    lab.step()                                   # nothing attached yet
    s = TMP102(celsius=21.5); microbit.i2c._attach(0x48, s)
    print('scan:', [hex(a) for a in microbit.i2c.scan()])
    microbit.i2c.transactions.clear(); lab.step()
    print('transactions:', microbit.i2c.transactions)
    s.set_temperature(-25); lab.step()
    print('last read bytes:', microbit.i2c.transactions[-1][2].hex())
print(out.getvalue(), end='')
msb, lsb = 0x15, 0x80
raw = (msb << 4) | (lsb >> 4)
print('raw =', raw, '->', raw * 0.0625, 'C')
raw = (0xE7 << 4) | (0x00 >> 4)
print('raw unsigned =', raw, '=', hex(raw), 'sign bit:', bool(raw & 0x800), '-> signed', raw - 4096, '->', (raw - 4096) * 0.0625, 'C; without sign fix', raw * 0.0625)
```

## Lesson 11

### Lesson 11 — `cd labs/L200/11-game-state-machine && python3 _peek.py; rm -f _peek.py; python3 -m unittest -v 2>&1 | tail -4; python3 try_it.py; BUILD_FILE=solution.py python3 -m unittest test_build_task 2>&1 | tail -3` (2026-11-02, exit 0)
```
idle -> play (a)
t=600 dot_x=2
hit 1
t=900 dot_x=3
miss 1
t=5999 state=play
play -> over (timeout)
score 1
t=6000 state=over
ignored pair: ('over', None)
----------------------------------------------------------------------
Ran 9 tests in 3.421s

OK
try 1: idle -> play (a)
try 2: idle -> play (a) | miss 0
Ran 2 tests in 0.009s

OK
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab, serial
import microbit as mb
lab = load_lab('.')
g = lab.new_game()
with serial() as out:
    mb.button_a.click(); lab.step(g)                 # t=0: start
    for t_target in (600, 900):
        mb.sleep(t_target - mb.running_time())
        print('t=%d dot_x=%d' % (mb.running_time(), lab.dot_x(g, mb.running_time())))
        mb.button_a.click(); lab.step(g)
    mb.sleep(5999 - mb.running_time()); lab.step(g)
    print('t=%d state=%s' % (mb.running_time(), g['state']))
    mb.sleep(1); lab.step(g)
    print('t=%d state=%s' % (mb.running_time(), g['state']))
    print('ignored pair:', lab.next_state('over', 'shake'))
print(out.getvalue(), end='')
```

## Lesson 12

### Lesson 12 — `cd labs/L300/12-reliable-radio && python3 _peek.py; rm -f _peek.py; python3 link_sim.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_FILE=main.py python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|ERROR|KeyError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
frame: D:3:23:F877 len 11
check value crc16("123456789") = 0x29B1
decode ok   : ('D', 3, '23')
decode flip : None
waits per try: [100, 200, 400, 800, 800, 800, 800, 800] total ms before give-up: 4700
main.py     quiet  delivered 20/20, missing none, duplicates 0, in order True
  air {'sent': 20, 'lost': 0, 'duplicated': 0, 'reordered': 0, 'corrupted': 0}
  A {"t":6000,"tx":20,"rx":0,"bad":0,"delivered":0}
  B {"t":6000,"tx":0,"rx":20,"bad":0,"delivered":20}
main.py     faulty delivered 14/20, missing ['r2', 'r8', 'r11', 'r13', 'r14', 'r20'], duplicates 2, in order False
  air {'sent': 20, 'lost': 5, 'duplicated': 2, 'reordered': 2, 'corrupted': 1}
  A {"t":6000,"tx":20,"rx":0,"bad":0,"delivered":0}
  B {"t":6000,"tx":0,"rx":17,"bad":1,"delivered":16}
solution.py quiet  delivered 20/20, missing none, duplicates 0, in order True
  air {'sent': 40, 'lost': 0, 'duplicated': 0, 'reordered': 0, 'corrupted': 0}
  A {"t":6000,"tx":20,"retx":0,"acked":20,"gave_up":0,"rx":20,"bad":0,"dup":0,"gap":0,"delivered":0}
  B {"t":6000,"tx":0,"retx":0,"acked":0,"gave_up":0,"rx":20,"bad":0,"dup":0,"gap":0,"delivered":20}
solution.py faulty delivered 20/20, missing none, duplicates 0, in order True
  air {'sent': 81, 'lost': 14, 'duplicated': 4, 'reordered': 9, 'corrupted': 2}
  A {"t":6000,"tx":42,"retx":22,"acked":20,"gave_up":0,"rx":31,"bad":1,"dup":0,"gap":0,"delivered":0}
  B {"t":6000,"tx":0,"retx":0,"acked":0,"gave_up":0,"rx":40,"bad":1,"dup":19,"gap":0,"delivered":20}
Ran 1 test in 0.171s

OK
ERROR: test_dead_link_gives_up_and_reports (test_build_task.ReliableLink.test_dead_link_gives_up_and_reports)
KeyError: 'gave_up'
ERROR: test_retransmits_are_visible_in_the_json_line (test_build_task.ReliableLink.test_retransmits_are_visible_in_the_json_line)
KeyError: 'retx'
FAIL: test_faulty_link_delivers_all_exactly_once (test_build_task.ReliableLink.test_faulty_link_delivers_all_exactly_once)
FAIL: test_other_seeds_too (test_build_task.ReliableLink.test_other_seeds_too)
Ran 4 tests in 1.776s
FAILED (failures=2, errors=2)
Ran 4 tests in 0.427s

OK
try 1: delivered 20/20, missing none, duplicates 19, in order False | sender retx 22 gave_up 0 | receiver gap -19
try 2: delivered 20/20, missing none, duplicates 0, in order True | sender retx 13 gave_up 4 | receiver gap 0
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab
lab = load_lab('.', 'solution.py')
f = lab.encode('D', 3, '23')
print('frame:', f, 'len', len(f))
print('check value crc16("123456789") = 0x%04X' % lab.crc16('123456789'))
print('decode ok   :', lab.decode(f))
print('decode flip :', lab.decode(f.replace(':3:', ':2:')))
t, d = lab.TIMEOUT_MS, 0
waits = []
for i in range(lab.MAX_TRIES):
    waits.append(t); d += t; t = min(t * 2, lab.MAX_TIMEOUT_MS)
print('waits per try:', waits, 'total ms before give-up:', d)
```

## Lesson 13

### Lesson 13 — `cd labs/L300/13-nonblocking-scheduler && python3 _peek.py; rm -f _peek.py; python3 tap_sim.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_FILE=main.py python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|ERROR|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
taps: [(932, 150), (1680, 150), (2630, 150), (3695, 150), (4645, 150), (5655, 150), (6689, 150), (7744, 150)]
{"t":0,"event":"error","task":"sensor","count":1}
{"t":1000,"event":"error","task":"sensor","count":2}
{"t":2000,"event":"error","task":"sensor","count":3}
{"t":2000,"event":"safe_state","task":"sensor"}
safe: True pin0: ('digital', 0) stats: {'runs': 124, 'overruns': 0, 'missed': 0, 'errors': 3}
taps at (ms): [932, 1680, 2630, 3695, 4645, 5655, 6689, 7744]
main.py     (sleep 1000): counted 1 of 8
solution.py (scheduler) : counted 8 of 8; stats {'runs': 610, 'overruns': 0, 'missed': 0, 'errors': 0}
Ran 1 test in 0.013s

OK
ERROR: test_failing_task_leads_to_safe_state (test_build_task.Scheduler.test_failing_task_leads_to_safe_state)
ERROR: test_long_press_still_clears (test_build_task.Scheduler.test_long_press_still_clears)
ERROR: test_no_overruns_on_the_happy_path (test_build_task.Scheduler.test_no_overruns_on_the_happy_path)
ERROR: test_overrun_is_logged (test_build_task.Scheduler.test_overrun_is_logged)
ERROR: test_sensor_keeps_its_period (test_build_task.Scheduler.test_sensor_keeps_its_period)
FAIL: test_every_quick_tap_counts (test_build_task.Scheduler.test_every_quick_tap_counts)
AssertionError: 1 != 8
Ran 6 tests in 0.121s
FAILED (failures=1, errors=5)
Ran 6 tests in 1.216s

OK
try 1: counted 6 of 8 | stats {'runs': 160, 'overruns': 0, 'missed': 0, 'errors': 0} | events none
try 2: counted 8 of 8 | stats {'runs': 440, 'overruns': 10, 'missed': 170, 'errors': 0} | events ['late', 'overrun']
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import tap_sim, microbit
print('taps:', tap_sim.taps())
def broken(lab, sched):
    def bad(state, now):
        raise OSError(19)
    sched["tasks"][1]["fn"] = bad
state, sched, out = tap_sim.run_scheduler(tap_sim.taps(), until_ms=3500, setup=broken)
print('\n'.join(l for l in out.splitlines() if '"event"' in l))
print('safe:', sched['safe'], 'pin0:', microbit.pin0.read_digital() if False else microbit.pin0.history[-1], 'stats:', sched['stats'])
```

## Lesson 14

### Lesson 14 — `cd labs/L300/14-power-budget && python3 _peek.py; rm -f _peek.py; python3 budget.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_FILE=main.py python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|ERROR|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
steady intervals: [200, 400, 800, 1600, 3200, 6400, 8000, 8000, 8000] -> on change: 100
awake ms: 9660 avg mA: 0.5792 life h: 2158.3
figures (estimates, see sources in the code): {'BOARD_ON_MA': 30.0, 'SLEEP_MA': 0.5, 'SLEEP_MA_LOW': 0.05, 'CHIP_SLEEP_MA': 0.0015, 'ACTIVE_MS': 20, 'BATTERY_MAH': 1250.0}
life_h = BOARD estimate at the conservative sleep floor; range = 0.5-0.05 mA floor; chip_only_bound_h is NOT a board figure
{"design": "main.py", "samples": 36000, "wakeups": 0, "max_delay_ms": 0, "meets_brief": false, "awake_pct": 100.0, "avg_ma": 30.0, "life_h": 41.7, "life_h_range": [41.7, 41.7], "chip_only_bound_h": 41.7}
{"design": "solution.py", "samples": 483, "wakeups": 483, "max_delay_ms": 4700, "meets_brief": true, "awake_pct": 0.27, "avg_ma": 0.5792, "life_h": 2158.3, "life_h_range": [2158.3, 9588.4], "chip_only_bound_h": 15244.7}
Ran 1 test in 13.803s

OK
ERROR: test_interval_backs_off_and_resets (test_build_task.Adaptive.test_interval_backs_off_and_resets)
FAIL: test_board_deep_sleeps_between_samples (test_build_task.Adaptive.test_board_deep_sleeps_between_samples)
AssertionError: 0 != 600
FAIL: test_meets_the_brief (test_build_task.Adaptive.test_meets_the_brief)
AssertionError: False is not true : {'design': 'main.py', 'samples': 36000, 'wakeups': 0, 'max_delay_ms': 0, 'meets_brief': False, 'awake_pct': 100.0, 'avg_ma': 30.0, 'life_h': 41.7, 'life_h_range': [41.7, 41.7], 'chip_only_bound_h': 41.7}
FAIL: test_tradeoff_short_spike_can_be_missed (test_build_task.Adaptive.test_tradeoff_short_spike_can_be_missed)
AssertionError: True is not false : the spike was sampled
Ran 4 tests in 2.358s
FAILED (failures=3, errors=1)
Ran 4 tests in 0.042s

OK
try 1: solution.py: avg 6.4 mA, life 195.3 h, meets brief False
try 2: main.py: avg 7.9 mA, life 158.2 h, meets brief False
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab
lab = load_lab('.', 'solution.py')
seq, i = [], lab.MIN_MS
for _ in range(9):
    i = lab.next_interval(i, False); seq.append(i)
print('steady intervals:', seq, '-> on change:', lab.next_interval(8000, True))
awake = 483 * 20; hour = 3600 * 1000
avg = (awake * 30.0 + (hour - awake) * 0.5) / hour
print('awake ms:', awake, 'avg mA: %.4f' % avg, 'life h: %.1f' % (1250 / avg))
```

## Lesson 15

### Lesson 15 — `cd labs/L300/15-serial-gateway && python3 _peek.py; rm -f _peek.py; python3 gateway.py --file samples/clean.txt | head -1; python3 gateway.py --file samples/clean.txt | wc -l; python3 gateway.py --file samples/noisy.bin 2>&1 | tail -1; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_FILE=gateway.py python3 -m unittest test_build_task 2>&1 | grep -E '^(Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 solution.py --demo 2>&1 | tail -2; python3 agent_assist.py --fake 2>&1 | tail -4; python3 try_it.py` (2026-11-02, exit 0)
```
device frame: $0081,20,100*1DA1
input bytes: b'\x00boot!!$0081,20,100*1DA1\n$0081,22,100*1DA1\n$00$0081,20,100*1DA1\n'
payloads: [b'1,20,100', b'1,20,100']
metrics: {'frames_ok': 2, 'bad_len': 1, 'bad_crc': 1, 'bad_payload': 0, 'resyncs': 2, 'skipped_bytes': 25}
{"payload": {"light": 100, "seq": 1, "temp": 20}, "qos": 1, "topic": "microbit/mb1/telemetry"}
200
ValueError: not enough values to unpack (expected 3, got 1)
Ran 2 tests in 0.059s

OK
Ran 4 tests in 0.175s
FAILED (errors=4)
Ran 4 tests in 2.088s

OK
{"payload": {"light": 109, "seq": 200, "temp": 23}, "qos": 1, "topic": "microbit/mb1/telemetry"}
{"payload": {"bad_crc": 3, "bad_len": 6, "bad_payload": 0, "frames_ok": 190, "resyncs": 9, "skipped_bytes": 184}, "qos": 1, "topic": "microbit/gateway/metrics"}
metrics: {"bad_crc": 3, "bad_len": 6, "bad_payload": 0, "frames_ok": 190, "resyncs": 9, "skipped_bytes": 184}
alarms (decided by code): LINK_NOISY=4.5, SEQ_GAP=9
agent explanation (checked): The gateway accepted 190 of 199 frames. 3 frames failed the CRC check and 6 had the wrong length, so 4.5% of frames were damaged on the serial link, which looks like noise or a loose cable rather than a sensor fault. It resynchronised 9 times and kept running. 9 readings are missing from the sequence. Alarms raised by the gateway code: LINK_NOISY, SEQ_GAP.
check: PASS (numbers from the metrics; alarm names match the code's alarms)
try 1: no CRC: forwarded 181, 2 WRONG, bad_crc 0, bad_payload 9 | with CRC: forwarded 179, 0 WRONG, bad_crc 13, bad_payload 0
try 2: forwarded 190 readings, 0 wrong; metrics {'frames_ok': 190, 'bad_len': 6, 'bad_crc': 3, 'bad_payload': 0, 'resyncs': 9, 'skipped_bytes': 184}
Exception ignored in: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
BrokenPipeError: [Errno 32] Broken pipe
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys; sys.path.insert(0, '../../sim_stub')
from labtest import load_lab
import solution
dev = load_lab('.')
f = dev.frame('1,20,100')
print('device frame:', f)
fr = solution.Framer()
noisy = b'\x00boot!!' + f.encode() + b'\n' + f.replace('20', '22').encode() + b'\n$00' + f.encode() + b'\n'
print('input bytes:', noisy)
print('payloads:', list(fr.feed(noisy)))
print('metrics:', fr.m)
```

## Lesson 16

### Lesson 16 — `cd labs/L300/16-interrupt-race && python3 _peek.py; rm -f _peek.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_FILE=race_model.py python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 -m unittest test_main 2>&1 | tail -3; python3 try_it.py; command -v cargo || echo 'cargo: not installed'; command -v renode || echo 'renode: not installed'` (2026-11-02, exit 0)
```
racy  IRQ in window: isr 1 consumed 0 pending 0 lost 1
racy  soak: irqs 1316 isr 1316 consumed 1000 pending 0 lost 316
fixed IRQ in window: isr 1 consumed 0 pending 1 lost 0
fixed soak: irqs 1316 isr 1316 consumed 1316 pending 0 lost 0
Ran 3 tests in 0.008s

OK
FAIL: test_every_interleaving (test_build_task.NoLostTicks.test_every_interleaving)
AssertionError: 1 != 0 : ('window',)
FAIL: test_other_seeds (test_build_task.NoLostTicks.test_other_seeds)
AssertionError: 280 != 0 : 1
FAIL: test_soak (test_build_task.NoLostTicks.test_soak)
AssertionError: Tuples differ: (1316, 316) != (1316, 0)
Ran 3 tests in 0.008s
FAILED (failures=3)
Ran 3 tests in 0.082s

OK
Ran 6 tests in 5.908s

OK
try 1: racy, short window: irqs 1039, isr runs 1039, consumed 1000, pending 0, lost 39
try 2: fixed, long section: irqs 1632, isr runs 1316, consumed 1316, pending 0, lost 0
cargo: not installed
renode: not installed
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import host_sim, race_model, solution_model
for name, mod in (("racy ", race_model), ("fixed", solution_model)):
    m = host_sim.schedule(mod.take, {"window"})
    print(name, "IRQ in window: isr", m.isr_total, "consumed", m.consumed, "pending", m.pending, "lost", m.lost())
    s = host_sim.soak(mod.take)
    print(name, "soak: irqs", s.irqs, "isr", s.isr_total, "consumed", s.consumed, "pending", s.pending, "lost", s.lost())
```

## Lesson 17

### Lesson 17 — `cd labs/L400/17-edge-to-cloud && python3 options.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 -m unittest test_fitness 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 1)
```
{"file": "solution.py", "sensors": 6, "sampled": 180, "stored": 180, "delivery_pct": 100.0, "p50_ms": 13, "p95_ms": 13, "max_ms": 13, "tx": 0, "retx": 0, "gave_up": 0, "relay_queue_drops": 0, "sensor_queue_drops": 0, "bad_serial": 0, "option": "A direct serial", "usb_cables": 6}
{"file": "node.py", "sensors": 6, "sampled": 180, "stored": 160, "delivery_pct": 88.9, "p50_ms": 2128, "p95_ms": 9578, "max_ms": 10568, "tx": 549, "retx": 369, "gave_up": 56, "relay_queue_drops": 149, "sensor_queue_drops": 1027, "bad_serial": 0, "option": "B radio relay (node.py)", "usb_cables": 1}
{"file": "solution.py", "sensors": 6, "sampled": 180, "stored": 180, "delivery_pct": 100.0, "p50_ms": 13, "p95_ms": 153, "max_ms": 393, "tx": 210, "retx": 30, "gave_up": 0, "relay_queue_drops": 0, "sensor_queue_drops": 0, "bad_serial": 0, "option": "B radio relay (solution.py)", "usb_cables": 1}
{"option": "C BLE", "measured": false, "why": "micro:bit MicroPython V2: only BLE flashing is implemented; no BLE API for user code"}
Ran 1 test in 0.000s

FAILED (errors=1)
Ran 1 test in 0.000s
FAILED (errors=1)
Ran 1 test in 0.000s

FAILED (errors=1)
Ran 1 test in 0.001s

FAILED (errors=1)
Traceback (most recent call last):
  File "try_it.py", line 8, in <module>
    HERE = Path(__file__).resolve().parent
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/pathlib.py", line 1240, in resolve
    s = self._flavour.realpath(self, strict=strict)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen posixpath>", line 425, in realpath
  File "<frozen posixpath>", line 412, in abspath
FileNotFoundError: [Errno 2] No such file or directory
```

### Lesson 17 — `cd labs/L400/17-edge-to-cloud && cd /mnt/workspace/working/kb/microbit/labs/L400/17-edge-to-cloud && python3 -m unittest test_fault 2>&1 | tail -3; cd /mnt/workspace/working/kb/microbit/labs/L400/17-edge-to-cloud && BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'` (2026-11-02, exit 0)
```
Ran 1 test in 1.509s

OK
FAIL: test_24_boards_still_deliver (test_build_task.Classroom.test_24_boards_still_deliver)
AssertionError: 8.8 not greater than or equal to 99.0
FAIL: test_frames_still_fit_after_a_school_day (test_build_task.Classroom.test_frames_still_fit_after_a_school_day)
AssertionError: 38 not less than or equal to 32
FAIL: test_six_boards_deliver_everything_fast (test_build_task.Classroom.test_six_boards_deliver_everything_fast)
AssertionError: 88.9 not greater than or equal to 99.0
Ran 3 tests in 16.754s
FAILED (failures=3)
```

### Lesson 17 — `cd labs/L400/17-edge-to-cloud && cd /mnt/workspace/working/kb/microbit/labs/L400/17-edge-to-cloud && python3 -m unittest test_build_task 2>&1 | tail -3; cd /mnt/workspace/working/kb/microbit/labs/L400/17-edge-to-cloud && python3 -m unittest test_fitness 2>&1 | tail -3; cd /mnt/workspace/working/kb/microbit/labs/L400/17-edge-to-cloud && python3 try_it.py` (2026-11-02, exit 0)
```
Ran 3 tests in 5.699s

OK
Ran 1 test in 13.615s

OK
try 1: delivered 480/480 (100.0%), p95 165 ms, gave_up 0, relay drops 0, sensor drops 176
try 2: delivered 151/480 (31.5%), p95 19031 ms, gave_up 216, relay drops 570, sensor drops 15787
```

## Lesson 18

### Lesson 18 — `cd labs/L400/18-fleet-config && python3 fleet_sim.py; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 -m unittest test_fitness 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
{"device": "config_agent.py", "strategy": "push-all", "unacked_ticks": 12086, "max_on_bad": 5, "deaf_device_ms": 120800, "jobs": "v2 done @310, v3 halted @23010", "final": "333332", "gw_sent": 177}
{"device": "solution.py", "strategy": "push-all", "unacked_ticks": 0, "max_on_bad": 4, "deaf_device_ms": 12000, "jobs": "v2 done @1210, v3 halted @18310", "final": "222222", "gw_sent": 99}
{"device": "solution.py", "strategy": "staged", "unacked_ticks": 0, "max_on_bad": 1, "deaf_device_ms": 3000, "jobs": "v2 done @1850, v3 halted @18610", "final": "222222", "gw_sent": 34}
Ran 1 test in 0.271s

OK
FAIL: test_bad_config_rolls_back_everywhere (test_build_task.TwoPhase.test_bad_config_rolls_back_everywhere)
AssertionError: Lists differ: [3, 3, 3, 3, 3, 2] != [2, 2, 2, 2, 2, 2]
FAIL: test_never_runs_an_unacknowledged_config (test_build_task.TwoPhase.test_never_runs_an_unacknowledged_config)
AssertionError: 12086 != 0 : push-all
Ran 2 tests in 0.999s
FAILED (failures=2)
Ran 2 tests in 1.985s

OK
Ran 1 test in 50.202s

OK
try 1: jobs: v2 halted @3310, v3 halted @18310 | final versions 111111 | unacked_ticks 0
try 2: jobs: v2 halted @8920, v3 halted @16810 | final versions 111111 | unacked_ticks 0
```

## Lesson 19

### Lesson 19 — `cd labs/L400/19-radio-auth && python3 _peek.py; rm -f _peek.py; python3 attacks.py; python3 cost.py; python3 -m unittest test_main 2>&1 | tail -3; BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 -m unittest test_fitness 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
sealed frame: n1:7:21.5:67dc8be19df0c9cc | tag bytes on air: 17
genuine           -> ('n1', 7, '21.5')
replay            -> None
forged            -> None
tampered          -> None
older, in window  -> ('n1', 5, '21.0')
unknown dev       -> None
stats: {'accepted': 2, 'rejected': 4}
log: ['{"reject": "replay", "frame": "n1:7:21.5:67dc8be19df0c9cc"}', '{"reject": "mac", "frame": "n1:8:45.0:0000000000000000"}', '{"reject": "mac", "frame": "n1:7:45.0:67dc8be19df0c9cc"}', '{"reject": "unknown_device", "frame": "n9:1:1:9e2ea7fb0c7b098c"}']
{"verifier": "verifier.py", "mode": "crc", "genuine_sent": 180, "genuine_intact": 158, "genuine_accepted": 158, "forged_accepted": 20, "replays_accepted": 18, "toy_state_recovered": false, "rejected": 7}
{"verifier": "solution.py", "mode": "toy", "genuine_sent": 180, "genuine_intact": 158, "genuine_accepted": 140, "forged_accepted": 19, "replays_accepted": 0, "toy_state_recovered": true, "rejected": 50}
{"verifier": "solution.py", "mode": "siphash", "genuine_sent": 180, "genuine_intact": 160, "genuine_accepted": 160, "forged_accepted": 0, "replays_accepted": 0, "toy_state_recovered": false, "rejected": 50}
{"mode": "crc", "tag_bytes_on_air": 5, "cpython_us_per_tag": 107.4}
{"mode": "toy", "tag_bytes_on_air": 5, "cpython_us_per_tag": 191.9}
{"mode": "siphash", "tag_bytes_on_air": 17, "cpython_us_per_tag": 152.4, "rounds": 10, "ops64": 140}
{"counter_flash_writes_per_1000_frames": 10}
Ran 4 tests in 0.039s

OK
FAIL: test_attack_scenario (test_build_task.Gateway.test_attack_scenario)
AssertionError: 0 != 160
FAIL: test_forged_frame_does_not_move_the_window (test_build_task.Gateway.test_forged_frame_does_not_move_the_window)
AssertionError: None is not true
FAIL: test_reordering_inside_the_window_is_fine_replays_are_not (test_build_task.Gateway.test_reordering_inside_the_window_is_fine_replays_are_not)
AssertionError: Lists differ: [False, False, False, False] != [True, True, True, True]
Ran 4 tests in 9.887s
FAILED (failures=3)
Ran 4 tests in 16.206s

OK
Ran 1 test in 44.512s

OK
try 1: genuine accepted 159 of 160 intact, forged accepted 0, replays accepted 0
try 2: genuine accepted 143 of 160 intact, forged accepted 0, replays accepted 0
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import frame_auth as fa, solution
key = bytes(range(16))
f = fa.seal("n1", 7, "21.5", key)
print("sealed frame:", f, "| tag bytes on air:", len(f.rpartition(":")[2]) + 1)
v = solution.Verifier({"n1": key})
forged = "n1:8:45.0:" + "0" * 16
for label, text in [("genuine", f), ("replay", f), ("forged", forged), ("tampered", f.replace("21.5", "45.0")),
                    ("older, in window", fa.seal("n1", 5, "21.0", key)), ("unknown dev", fa.seal("n9", 1, "1", key))]:
    print("%-17s -> %s" % (label, v.check(text)))
print("stats:", v.stats)
print("log:", v.log)
```

## Lesson 20

### Lesson 20 — `cd labs/L400/20-digital-twin && python3 _peek.py; rm -f _peek.py; python3 drift_eval.py; python3 -m unittest test_main 2>&1 | tail -3; python3 -m unittest test_fault 2>&1 | tail -3; BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|AssertionError|Ran|FAILED)'; python3 -m unittest test_build_task 2>&1 | tail -3; python3 -m unittest test_fitness 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 0)
```
nominal z  : [0.4, -1.1, 2.3, -0.5, 0.9, -2.1, 1.2, 0.3]
  S_hi K=.75: [0.0, 0.0, 1.55, 0.3, 0.45, 0.0, 0.45, 0.0] | |z|>2 fires at [2, 5]
shifted z  : [1.6, 1.4, 1.9, 1.2, 1.7, 1.5, 1.8, 1.3]
  S_hi K=.75: [0.85, 1.5, 2.65, 3.1, 4.05, 4.8, 5.85, 6.4] | first > H at window 6
  S_hi K=0  : [1.6, 3.0, 4.9, 6.1, 7.8, 9.3, 11.1, 12.4] | first > H at window 3
{"detected_after_windows": {"n3 DRIFT_TEMP": 7, "n5 DRIFT_LAT": 7}, "false_alarms_fixture": 13, "false_alarms_per_1000_synthetic": 80, "twin": "twin.py"}
{"detected_after_windows": {"n3 DRIFT_TEMP": 8, "n5 DRIFT_LAT": 9}, "false_alarms_fixture": 2, "false_alarms_per_1000_synthetic": 0, "twin": "solution.py"}
Ran 4 tests in 19.713s

OK
Ran 1 test in 8.805s

OK
FAIL: test_rarely_cries_wolf (test_build_task.DriftCheck.test_rarely_cries_wolf)
AssertionError: 13 not less than or equal to 2
Ran 2 tests in 3.670s
FAILED (failures=1)
Ran 2 tests in 11.586s

OK
Ran 2 tests in 3.711s

OK
try 1: {"n3 DRIFT_TEMP": 10, "n5 DRIFT_LAT": 9} | false alarms: fixture 3, synthetic 12 per 1000
try 2: {"n3 DRIFT_TEMP": 5} | false alarms: fixture 6, synthetic 74 per 1000
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
K, H = 0.75, 5.0
def run(zs, k=K):
    hi = 0.0; out = []
    for z in zs:
        hi = max(0.0, hi + z - k); out.append(round(hi, 2))
    return out
noise = [0.4, -1.1, 2.3, -0.5, 0.9, -2.1, 1.2, 0.3]
shift = [1.6, 1.4, 1.9, 1.2, 1.7, 1.5, 1.8, 1.3]
print("nominal z  :", noise)
print("  S_hi K=.75:", run(noise), "| |z|>2 fires at", [i for i, z in enumerate(noise) if abs(z) > 2])
print("shifted z  :", shift)
print("  S_hi K=.75:", run(shift), "| first > H at window", next(i for i, s in enumerate(run(shift)) if s > H))
print("  S_hi K=0  :", run(shift, 0.0), "| first > H at window", next(i for i, s in enumerate(run(shift, 0.0)) if s > H))
```

## Lesson 21

### Lesson 21 — `cd labs/L400/21-edge-ai-explain && python3 incident_assistant.py --fake 2>&1 | tail -8; python3 options.py; python3 -m unittest test_main 2>&1 | tail -3; BUILD_TARGET=mine python3 -m unittest test_build_task 2>&1 | tail -2; python3 -m unittest test_build_task 2>&1 | tail -3; python3 solution.py 2>&1 | tail -12; python3 -m unittest test_fitness 2>&1 | tail -3; python3 try_it.py` (2026-11-02, exit 1)
```
alarms shown: AUTH_REJECTS@gateway, DRIFT_LAT@n1, DRIFT_LAT@n2, DRIFT_LAT@n5, DRIFT_TEMP@n3, DRIFT_TEMP@n4
operator note: TEMP_HIGH cleared after recalibration; no action needed.
{"injected_label_temp_high_still_raised": {"A model decides": false, "B model may act": false, "C explain only": true}}
{"option": "A model decides", "alarm_sets_changed": 195, "of": 200}
{"option": "B model may act", "alarm_sets_changed": 17, "of": 200}
{"option": "C explain only", "alarm_sets_changed": 0, "of": 200}
{"option": "C explain only", "replies_published": 17, "fallback_notes": 183}
Ran 3 tests in 0.691s

OK

FAILED (failures=18, errors=53)
Ran 3 tests in 0.868s

OK
label injected: False | alarms: AUTH_REJECTS@gateway, DRIFT_LAT@n1, DRIFT_LAT@n2, DRIFT_LAT@n5, DRIFT_TEMP@n3, DRIFT_TEMP@n4, TEMP_HIGH@n4
  accepted: True 
  explanation: Alarms raised by the gateway code: AUTH_REJECTS, DRIFT_LAT, DRIFT_LAT, DRIFT_LAT, DRIFT_TEMP, DRIFT_TEMP, TEMP_HIGH. The gateway rejected 3 radio frames that failed authentication; n1's radio link needs more retransmissions than the twin predicts; n2's radio link needs more retransmissions than the twin predicts; n5's radio link needs more retransmissions than the twin predicts; n3's temperature reads higher than the twin's room model; n4's temperature reads higher than the twin's room model; the room temperature reached 31 C at n4 (limit 30 C).
  note: Check the boards named above in the room; only the gateway code can change these alarms.
label injected: True | alarms: AUTH_REJECTS@gateway, DRIFT_LAT@n1, DRIFT_LAT@n2, DRIFT_LAT@n5, DRIFT_TEMP@n3, DRIFT_TEMP@n4, TEMP_HIGH@n4
  accepted: False ['keys must be exactly explanation, operator_note']
  explanation: (rejected - not shown)
  note: Alarms raised by the gateway code: AUTH_REJECTS at gateway, DRIFT_LAT at n1, DRIFT_LAT at n2, DRIFT_LAT at n5, DRIFT_TEMP at n3, DRIFT_TEMP at n4, TEMP_HIGH at n4. Check these boards in the room.
Ran 1 test in 5.215s

OK
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/microbit/labs/L400/21-edge-ai-explain/try_it.py", line 51, in <module>
    print("try 1:", try_1())
                    ^^^^^^^
  File "/mnt/workspace/working/kb/microbit/labs/L400/21-edge-ai-explain/try_it.py", line 42, in try_1
    return run_variant("no-state-check")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/microbit/labs/L400/21-edge-ai-explain/try_it.py", line 23, in run_variant
    with tempfile.TemporaryDirectory(dir=HERE) as d:  # private copy: parallel runs cannot collide
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/tempfile.py", line 950, in __exit__
    self.cleanup()
  File "/usr/lib/python3.12/tempfile.py", line 954, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "/usr/lib/python3.12/tempfile.py", line 934, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
  File "/usr/lib/python3.12/shutil.py", line 759, in rmtree
    _rmtree_safe_fd(stack, onexc)
  File "/usr/lib/python3.12/shutil.py", line 703, in _rmtree_safe_fd
    onexc(func, path, err)
  File "/usr/lib/python3.12/shutil.py", line 662, in _rmtree_safe_fd
    os.rmdir(name, dir_fd=dirfd)
OSError: [Errno 39] Directory not empty: '/mnt/workspace/working/kb/microbit/labs/L400/21-edge-ai-explain/tmpat_o6iir/__pycache__'
```

### Lesson 21 — `cd labs/L400/21-edge-ai-explain && PYTHONDONTWRITEBYTECODE=1 python3 try_it.py` (2026-11-02, exit 0)
```
try 1: alarm sets changed 0/200, replies published 35, published notes claiming a state change 18
try 2: alarm sets changed 0/200, replies published 79, published notes claiming a state change 0
```

## Lesson 22

### Lesson 22 — `cd labs/L400/22-capstone && export PYTHONDONTWRITEBYTECODE=1 && python3 build_firmware.py && python3 run_capstone.py && wc -l out/dashboard.csv && grep -c '' out/metrics.txt && grep -m3 classroom_readings_total out/metrics.txt` (2026-11-02, exit 0)
```
wrote build/classroom_node.py 255 lines
{"milestone": "M1", "criterion": "delivery", "value": 99.97, "threshold": ">= 99.0 %", "pass": true}
{"milestone": "M1", "criterion": "p95 latency ms", "value": 324, "threshold": "<= 2000", "pass": true}
{"milestone": "M2", "criterion": "forged/replayed readings stored", "value": [0, 0], "threshold": "[0, 0]", "pass": true}
{"milestone": "M2", "criterion": "attacks seen and rejected", "value": {"mac": 9, "replay": 8}, "threshold": "mac >= 1 and replay >= 1", "pass": true}
{"milestone": "M3", "criterion": "unacked config ticks / canary blast radius", "value": [0, 1], "threshold": "[0, <= 1]", "pass": true}
{"milestone": "M4", "criterion": "n5 link drift found (window)", "value": 14, "threshold": "<= 19 (drift from window 10)", "pass": true}
{"milestone": "M4", "criterion": "other drift alarms", "value": ["n6 DRIFT_LAT"], "threshold": "<= 1 entry", "pass": true}
{"milestone": "M5", "criterion": "TEMP_HIGH n4 by gateway and firmware", "value": [true, true], "threshold": "[true, true]", "pass": true}
{"milestone": "M5", "criterion": "model cannot change alarms", "value": true, "threshold": "digest equal; injected reply rejected", "pass": true}
{"milestone": "M6", "criterion": "dashboard exports match the store", "value": [3599, 3599, 3599], "threshold": "all equal", "pass": true}
{"scorecard": "PASS", "passed": 10, "total": 10, "operator_note": "Alarms raised by the gateway code: AUTH_REJECTS at gateway, DRIFT_LAT at n5, DRIFT_LAT at n6, DRIFT_TEMP at n4, TEMP_HIG..."}
3600 out/dashboard.csv
16
# HELP classroom_readings_total Readings stored per device.
# TYPE classroom_readings_total counter
classroom_readings_total{dev="n1"} 600
```

### Lesson 22 — `cd labs/L400/22-capstone && export PYTHONDONTWRITEBYTECODE=1 && python3 -m unittest -v 2>&1 | tail -14` (2026-11-02, exit 0)
```
test_scorecard_passes_on_another_seed (test_fitness.Fitness.test_scorecard_passes_on_another_seed) ... ok
test_board_program_is_built_from_the_labs (test_milestones.M0Firmware.test_board_program_is_built_from_the_labs) ... ok
test_delivery_and_latency (test_milestones.M1Network.test_delivery_and_latency) ... ok
test_attacks_rejected (test_milestones.M2TrustedGateway.test_attacks_rejected) ... ok
test_staged_two_phase_rollout (test_milestones.M3Fleet.test_staged_two_phase_rollout) ... ok
test_drift_found (test_milestones.M4Twin.test_drift_found) ... ok
test_model_explains_code_decides (test_milestones.M5AlarmsAndAgent.test_model_explains_code_decides) ... ok
test_exports_and_scorecard (test_milestones.M6Dashboard.test_exports_and_scorecard) ... ok
test_publish_capstone_rows (test_mqtt_ci.RealBroker.test_publish_capstone_rows) ... skipped 'needs MQTT_BROKER=127.0.0.1:1883 and paho-mqtt (CI job gateway-mqtt)'

----------------------------------------------------------------------
Ran 9 tests in 40.191s

OK (skipped=1)
```

## Lesson 23

### Lesson 23 — `cd labs/L500/23-digital-foundations && PYTHONDONTWRITEBYTECODE=1 python3 foundations1.py; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest 2>&1 | tail -3` (2026-11-02, exit 0)
```
OK   T1 two's complement: n=8,12,16 exhaustive round-trip + invert-and-add-one OK for 69888 values; -2^(n-1) negates to itself; lab 10 decode_temp == 12-bit decode for all 4096 patterns; stub z=-1024 mg -> 0xFC00; 0xFE0C -> -500
OK   T2 Ohm/KVL/power: 3.3 V, Vf 2.0 V, 5 mA -> R 260 ohm -> E12 270 ohm, I 4.815 mA, P_R 6.26 mW, P_LED 9.63 mW, Vs*I = P_R + P_LED; battery 1250 mAh: 2158.3 h (0.5 mA floor), 9588.4 h (0.05 mA), 9600.5 h if the window is stretched to 3,607,400 ms
OK   T2b lesson 14 cross-check: budget.py life_h 2158.3, range [2158.3, 9588.4] == closed-form t = Q / I_avg
OK   T3 ADC: 10-bit, 3.3 V -> step 3.2227 mV, RMS error theory 0.9303 mV, measured var/(step^2/12) = 1.0006; full-scale sine SQNR 61.89 dB vs 6.02N+1.76 = 61.96 dB
OK   T4 PWM: write_analog(511), period 20000 us -> D = 0.49951; average 1.6485 V (D*3.3 = 1.6484), RMS 2.3324 V (sqrt(D)*3.3 = 2.3323), first harmonic 2.1008 V (theory 2.1008)
Ran 5 tests in 1.998s

OK
```

## Lesson 24

### Lesson 24 — `cd labs/L500/24-sampling-filters && PYTHONDONTWRITEBYTECODE=1 python3 foundations2.py; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest 2>&1 | tail -3` (2026-11-02, exit 0)
```
OK   T1 sampling: W=4 Hz, fs=10 Hz, sinc reconstruction max error 0.0002 mid-record; 100 Hz sampled at 30 Hz equals 10 Hz to 8.2e-13; stub light FFT peak at 10.0 Hz (predicted |f - round(f/fs)fs| = 10 Hz)
OK   T2 moving average: N=16 closed-form |H| matches direct sum to 5.8e-16; stub accel z noise std ratio 3.98 (sqrt(N) = 4.00); N=3 at 30 Hz nulls 10 Hz: aliased flicker std 70.7 -> 0.00
OK   T3 EMA: alpha=0.2, Ts=0.1 s -> step error vs 1-(1-a)^(n+1) 2.2e-16, tau 0.448 s (Ts/alpha = 0.500 s), -3 dB at 0.3566 Hz; stub light noise variance ratio 0.1120 (alpha/(2-alpha) = 0.1111, same as N=9 MA)
Ran 3 tests in 0.912s

OK
```

## Lesson 25

### Lesson 25 — `cd labs/L500/25-control-realtime && PYTHONDONTWRITEBYTECODE=1 python3 foundations3.py; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest 2>&1 | tail -3` (2026-11-02, exit 0)
```
OK   T1 control (assumed plant tau 60 s, gain 20 C, Ts 1 s): a=0.98347 b=0.33057; P stable iff Kp < (1+a)/b = 6.000 (1.1x diverges, 0.9x settles); plant gain 16: open-loop error 1.000 C, P(Kp=2) error 0.1515 C (r/(1+K Kp) = 0.1515), PI error 0.0000 C after a -2 C disturbance, PI pole radii 0.9483/0.8976
OK   T2 RM bound: n(2^(1/n)-1) = 0.8284, 0.7798, 0.7568 (n=2,3,4) -> ln 2 = 0.6931; 2985 random sets under the bound all meet deadlines; tight set U=0.8284 meets, +1 ms misses; harmonic U=1 meets, (2,4),(5,10) U=1 misses; lesson 13 U=0.37 <= 0.7798, but non-preemptive blocking gives the 20 ms button task a 24 ms response
OK   T3 CRC-16/CCITT-FALSE: matches lab 12 crc16, check("123456789") = 0x29B1, register = M(x)x^16 mod G; linear over GF(2) (3000 random patterns); 64-bit message: all bursts of length 1-16 detected, length 17: 48 undetected in 48 positions (1 in 2^15 each); all 41664 3-bit errors detected (x+1 | G)
Ran 3 tests in 5.027s

OK
```

## Lesson 26

### Lesson 26 — `cd research && python3 _peek.py; rm -f _peek.py; PYTHONDONTWRITEBYTECODE=1 python3 l500_checks.py 2>&1 | tail -3` (2026-11-02, exit 0)
```
6,552 h
6,552/41.7 = 157.1
158 sets = 316 cells
9,480 cells for 30 boards
6,552/2,158.3 = 3.04
4 sets = 8 cells
240 cells for 30 boards
lessons 5; theorems checked 10; problems 36; numeric values recomputed 97 (incl. midterm/final)
OK
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys
sys.dont_write_bytecode = True
import l500_checks as C
for line in C.p26_4():
    print(line)
```

## Lesson 27

### Lesson 27 — `cd research && python3 _peek.py; rm -f _peek.py` (2026-11-02, exit 0)
```
27.1: ['3.459', '3.459 Mbit/s']
27.2: ['5(2^{1/5} - 1) = 0.7435', 'ln 2 = 0.6931']
lesson 13 U = 0.37 | n=3 bound = 0.7798
```
Peek script `_peek.py` (copied into the lab folder, run, deleted):
```python
import sys
sys.dont_write_bytecode = True
import l500_checks as C
print("27.1:", C.p27_1())
print("27.2:", C.p27_2())
print("lesson 13 U =", 5/20 + 20/1000 + 10/100, "| n=3 bound =", round(C.F3.ll_bound(3), 4))
```
