# Lab 12-reliable-radio — A reliable radio protocol

| File | Purpose |
|---|---|
| `main.py` | BEFORE: frames with sequence number + CRC-16, fire-and-forget (works on a quiet link) |
| `solution.py` | AFTER (build task): ack, retransmit with timeout + backoff, bounded retries, duplicate suppression, JSON counters |
| `link_sim.py` | Runs a lab version on two stub boards over a **seeded faulty radio** (`radio.Air(loss, dup, reorder, corrupt, seed)`) |
| `test_main.py` | Frames, CRC check value, bad frames counted, happy path delivers 20/20 |
| `test_fault.py` | The failureLab symptom, pinned: 14 of 20 delivered, the sender cannot tell |
| `test_build_task.py` | Proof: fails on `main.py`, passes on `solution.py` (`BUILD_FILE=...`) |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items (edits to `solution.py`) |
| `../../sim_stub/` | Shared CPython stub; L300 adds radio faults, a timeline, `power` |

## Run in the simulator (two boards)
Paste `solution.py` into two Python Editor tabs (or use `harness/host.html?boards=2`), press A on board 0:
board 1 prints `rx 1 <temperature>`; press B on board 0 for its JSON counters (`"acked":1`). The simulator
link is clean, so this only checks the happy path in MicroPython: `harness/simulator-l300.spec.js` —
**pending-ci, not yet observed**. The faults exist only in the stub.

## Step 1 — happy path, then the fault (stub, no board, no internet)
```bash
cd labs/L300/12-reliable-radio
python3 link_sim.py          # Windows (PowerShell): py link_sim.py
```
Observed (Python 3.12.15, Linux sandbox):
```
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
```
The JSON lines are the observability: the BEFORE sender says `"tx":20` and nothing else; only the
receiver's `"delivered":16` (with 2 duplicates among them) hints at trouble.

## Step 2 — the failureLab symptom as a test
```bash
python3 -m unittest -v test_fault
```
```
test_readings_vanish_silently (test_fault.Symptom.test_readings_vanish_silently) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.008s

OK
```

## Step 4 — build task: fails before, passes after
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task          # macOS (zsh): BEFORE
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task      # Windows (PowerShell)
python3 -m unittest -v test_build_task                              # AFTER: solution.py
```
Observed with `main.py` (summary lines):
```
test_dead_link_gives_up_and_reports (test_build_task.ReliableLink.test_dead_link_gives_up_and_reports) ... ERROR
test_faulty_link_delivers_all_exactly_once (test_build_task.ReliableLink.test_faulty_link_delivers_all_exactly_once) ... FAIL
test_other_seeds_too (test_build_task.ReliableLink.test_other_seeds_too) ... FAIL
test_retransmits_are_visible_in_the_json_line (test_build_task.ReliableLink.test_retransmits_are_visible_in_the_json_line) ... ERROR
ERROR: test_dead_link_gives_up_and_reports (test_build_task.ReliableLink.test_dead_link_gives_up_and_reports)
KeyError: 'gave_up'
ERROR: test_retransmits_are_visible_in_the_json_line (test_build_task.ReliableLink.test_retransmits_are_visible_in_the_json_line)
KeyError: 'retx'
FAIL: test_faulty_link_delivers_all_exactly_once (test_build_task.ReliableLink.test_faulty_link_delivers_all_exactly_once)
AssertionError: Lists differ: ['r1', 'r3', 'r4', 'r6', 'r5', 'r9', 'r9', 'r7', '[49 chars]r19'] != ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', '[76 chars]r20']
FAIL: test_other_seeds_too (test_build_task.ReliableLink.test_other_seeds_too)
AssertionError: Lists differ: ['r2', 'r5', 'r3', 'r7', 'r10', 'r9', 'r11',[44 chars]r20'] != ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', '[82 chars]r20']
Ran 4 tests in 0.097s
FAILED (failures=2, errors=2)
```
Observed with `solution.py`:
```
test_dead_link_gives_up_and_reports (test_build_task.ReliableLink.test_dead_link_gives_up_and_reports) ... ok
test_faulty_link_delivers_all_exactly_once (test_build_task.ReliableLink.test_faulty_link_delivers_all_exactly_once) ... ok
test_other_seeds_too (test_build_task.ReliableLink.test_other_seeds_too) ... ok
test_retransmits_are_visible_in_the_json_line (test_build_task.ReliableLink.test_retransmits_are_visible_in_the_json_line) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.294s

OK
```

## All tests in this lab
```bash
python3 -m unittest -v       # Windows (PowerShell): py -m unittest -v
```
Observed (Python 3.12.15):
```
test_dead_link_gives_up_and_reports (test_build_task.ReliableLink.test_dead_link_gives_up_and_reports) ... ok
test_faulty_link_delivers_all_exactly_once (test_build_task.ReliableLink.test_faulty_link_delivers_all_exactly_once) ... ok
test_other_seeds_too (test_build_task.ReliableLink.test_other_seeds_too) ... ok
test_retransmits_are_visible_in_the_json_line (test_build_task.ReliableLink.test_retransmits_are_visible_in_the_json_line) ... ok
test_readings_vanish_silently (test_fault.Symptom.test_readings_vanish_silently) ... ok
test_bad_frame_counted_not_delivered (test_main.Frames.test_bad_frame_counted_not_delivered) ... ok
test_crc16_check_value (test_main.Frames.test_crc16_check_value) ... ok
test_json_line_parses (test_main.Frames.test_json_line_parses) ... ok
test_one_flipped_bit_is_rejected (test_main.Frames.test_one_flipped_bit_is_rejected) ... ok
test_round_trip_and_fits_one_packet (test_main.Frames.test_round_trip_and_fits_one_packet) ... ok
test_quiet_link_delivers_everything (test_main.HappyPath.test_quiet_link_delivers_everything) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.207s

OK
```
macOS and Windows: same tests in the CI matrix — pending-ci.

## Try it
```bash
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed:
```
try 1: delivered 20/20, missing none, duplicates 19, in order False | sender retx 22 gave_up 0 | receiver gap -19
try 2: delivered 20/20, missing none, duplicates 0, in order True | sender retx 13 gave_up 4 | receiver gap 0
```
`gave_up 4` with all 20 delivered: the sender gave up on frames whose **acks** were lost.
