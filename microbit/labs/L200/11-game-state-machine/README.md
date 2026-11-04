# Lab 11-game-state-machine — A game as a state machine

| File | Purpose |
|---|---|
| `main.py` | Lab program: catch-the-dot game with a transition table |
| `test_main.py` | Unit tests: the whole state x event table, a full timed round, shake, timeout boundary |
| `solution.py` | Build task solution: pause/resume with B; paused time is not counted |
| `test_build_task.py` | Build task check; `BUILD_FILE=main.py` checks your own version |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items |
| `../../sim_stub/` | Shared CPython stub: `microbit` (pins, i2c), `radio`, `log`, `i2c_devices` |

## Run in the simulator
1. Paste `main.py`, press play, open serial: `game ready: A or shake to start`.
2. Press **A**: `idle -> play (a)`; the dot runs along the middle row. Press A when it is in the
   centre: `hit 1`; elsewhere: `miss 1`.
3. After 6 s: `play -> over (timeout)` and `score N`. Press A: `over -> idle (a)`.
4. Choose **shake** in the accelerometer module and send it: `idle -> play (shake)`; shaking again
   during play aborts to idle.

Expected lines are from the `print` calls; checked by `harness/simulator-l200.spec.js` —
**not yet observed**, pending-ci.

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L200/11-game-state-machine
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_paused_time_is_not_counted (test_build_task.PauseBuildTask.test_paused_time_is_not_counted) ... ok
test_table_has_pause_and_resume (test_build_task.PauseBuildTask.test_table_has_pause_and_resume) ... ok
test_not_over_one_ms_early (test_main.GameRun.test_not_over_one_ms_early) ... ok
test_round_with_hit_and_miss (test_main.GameRun.test_round_with_hit_and_miss) ... ok
test_shake_starts_and_aborts (test_main.GameRun.test_shake_starts_and_aborts) ... ok
test_every_state_event_pair (test_main.TransitionTable.test_every_state_event_pair) ... ok
test_every_target_is_a_known_state (test_main.TransitionTable.test_every_target_is_a_known_state) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.016s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Build task
Add pause: B in `play` goes to `paused`, B in `paused` resumes; paused time must not count toward `ROUND_MS`.
`solution.py` is a worked solution; `test_build_task.py` is the check. To check your own edit of `main.py`:
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task              # macOS (zsh)
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task          # Windows (PowerShell)
```
Observed with `solution.py` (Python 3.12.15):
```
test_paused_time_is_not_counted (test_build_task.PauseBuildTask.test_paused_time_is_not_counted) ... ok
test_table_has_pause_and_resume (test_build_task.PauseBuildTask.test_table_has_pause_and_resume) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.004s

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
try 1: idle -> play (a)
try 2: idle -> play (a) | miss 0
```
In the simulator, the items that can be observed through serial are checked by
`harness/tryit-l200.spec.js` — pending-ci, not yet observed.
