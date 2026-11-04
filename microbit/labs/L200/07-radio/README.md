# Lab 07-radio — Radio between two boards

| File | Purpose |
|---|---|
| `main.py` | Lab program; flash the same file on both boards |
| `test_main.py` | Unit tests: message format on one stub board, delivery between TWO stub boards (shared radio air) |
| `solution.py` | Build task solution: acknowledge every message |
| `test_build_task.py` | Build task check (two stub boards); `BUILD_FILE=main.py` checks your own version |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |
| `../../sim_stub/` | Shared CPython stub: `microbit` (pins, i2c), `radio`, `log`, `i2c_devices` |

## Run in the simulator
1. Open https://python.microbit.org/, paste `main.py`, press play, click **Show serial**.
2. Expand the simulator's **Radio** module (it acts as the "other micro:bit").
3. Press **A**: the radio module shows the message sent by the code; serial shows `tx btn 1 A`.
4. Type `btn:5:B` in the radio module and send it: serial shows `rx btn 5 B`. Type `hello`: `rx bad 1`.

Two real simulators talking to each other: `harness/simulator-l200.spec.js` opens two simulator
iframes in one page (`host.html?boards=2`) and forwards each board's `radio_output` bytes to the other
board as `radio_input` (the README's embedding messages). Expected serial (from the `print` calls;
**not yet observed**, status pending-ci):
```
board 0: radio group 7 / tx btn 1 A          board 1: radio group 7 / rx btn 1 A
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L200/07-radio
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_duplicate_is_acked_but_not_shown_twice (test_build_task.AckBuildTask.test_duplicate_is_acked_but_not_shown_twice) ... ok
test_sender_sees_ack (test_build_task.AckBuildTask.test_sender_sees_ack) ... ok
test_decode_rejects_garbage (test_main.MessageFormat.test_decode_rejects_garbage) ... ok
test_duplicates_are_dropped (test_main.MessageFormat.test_duplicates_are_dropped) ... ok
test_encode_decode_round_trip (test_main.MessageFormat.test_encode_decode_round_trip) ... ok
test_raw_bytes_and_bad_text_are_counted_not_crashing (test_main.MessageFormat.test_raw_bytes_and_bad_text_are_counted_not_crashing) ... ok
test_send_adds_string_header (test_main.MessageFormat.test_send_adds_string_header) ... ok
test_button_on_a_shows_on_b (test_main.TwoBoards.test_button_on_a_shows_on_b) ... ok
test_different_group_hears_nothing (test_main.TwoBoards.test_different_group_hears_nothing) ... ok
test_queue_of_3_drops_the_4th (test_main.TwoBoards.test_queue_of_3_drops_the_4th) ... ok
test_temperature_from_b_reaches_a (test_main.TwoBoards.test_temperature_from_b_reaches_a) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.422s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Build task
Add acknowledgements: every received `btn`/`tmp` message is answered with `ack:<seq>:`; the sender prints `acked <seq>`.
`solution.py` is a worked solution; `test_build_task.py` is the check. To check your own edit of `main.py`:
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task              # macOS (zsh)
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task          # Windows (PowerShell)
```
Observed with `solution.py` (Python 3.12.15):
```
test_duplicate_is_acked_but_not_shown_twice (test_build_task.AckBuildTask.test_duplicate_is_acked_but_not_shown_twice) ... ok
test_sender_sees_ack (test_build_task.AckBuildTask.test_sender_sees_ack) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.076s

OK
```
(`main.py` as shipped fails this check on purpose: the feature is not there yet.)

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs the result on
the stub (`test_try_it.py` asserts the same results).
```bash
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: tx btn 1 A
try 2: tx btn 1 A*40 | rx btn 1 A*23 | bytes on air: 32
```
In the simulator, the items that can be observed through serial are checked by
`harness/tryit-l200.spec.js` — pending-ci, not yet observed. Try 2's 23-character cut follows the V1
`modradio.cpp` rule; V2 behaviour is unverified until that test runs (KNOWN-GAPS #41, review F26).
