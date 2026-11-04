# Lab 10-i2c-sensor — An external sensor over I2C

| File | Purpose |
|---|---|
| `main.py` | Lab program: TMP102 register read, decode, error handling |
| `test_main.py` | Unit tests against a SIMULATED TMP102 (`labs/sim_stub/i2c_devices.py`): datasheet decode examples, bus transactions, negative values, missing device |
| `solution.py` | Build task solution: encode and write the T_HIGH register, read it back |
| `test_build_task.py` | Build task check; `BUILD_FILE=main.py` checks your own version |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items |
| `../../sim_stub/` | Shared CPython stub: `microbit` (pins, i2c), `radio`, `log`, `i2c_devices` |

## Run in the simulator
**The browser simulator cannot attach I2C devices.** The temperature sensor in the tests is a
Python model of the TI TMP102 register map, clearly labelled SIMULATED in `labs/sim_stub/i2c_devices.py`.

1. Paste `main.py`, press play, open serial.
2. Expected: `scan: [...]`, then an error line every second instead of a crash. With nothing on
   the bus the V2 firmware raises `OSError` 19 (`ENODEV`), so on a board with no sensor attached:
```
scan: []
i2c: no device at 0x48 (errno 19)
```
What the simulator's I2C returns was not verified (its HAL source could not be fetched):
`harness/simulator-l200.spec.js` accepts either the error line or a `temp_c=` line and records which —
pending-ci.
3. Real board (optional): TMP102 breakout SCL to pin 19, SDA to pin 20, 3V, GND, ADD0 to GND.

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L200/10-i2c-sensor
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_encode_matches_datasheet (test_build_task.THighBuildTask.test_encode_matches_datasheet) ... ok
test_negative_limit (test_build_task.THighBuildTask.test_negative_limit) ... ok
test_write_and_read_back (test_build_task.THighBuildTask.test_write_and_read_back) ... ok
test_config_register_power_up_value (test_main.I2CSensorLab.test_config_register_power_up_value) ... ok
test_decode_datasheet_examples (test_main.I2CSensorLab.test_decode_datasheet_examples) ... ok
test_missing_device_is_reported_not_crashing (test_main.I2CSensorLab.test_missing_device_is_reported_not_crashing) ... ok
test_negative_temperature (test_main.I2CSensorLab.test_negative_temperature) ... ok
test_scan_lists_attached_addresses (test_main.I2CSensorLab.test_scan_lists_attached_addresses) ... ok
test_step_reads_pointer_then_two_bytes (test_main.I2CSensorLab.test_step_reads_pointer_then_two_bytes) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.062s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Build task
Write `encode_temp(c)` and `set_high_limit(c)`: write pointer 0x03 plus two data bytes (T_HIGH), then read it back.
`solution.py` is a worked solution; `test_build_task.py` is the check. To check your own edit of `main.py`:
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task              # macOS (zsh)
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task          # Windows (PowerShell)
```
Observed with `solution.py` (Python 3.12.15):
```
test_encode_matches_datasheet (test_build_task.THighBuildTask.test_encode_matches_datasheet) ... ok
test_negative_limit (test_build_task.THighBuildTask.test_negative_limit) ... ok
test_write_and_read_back (test_build_task.THighBuildTask.test_write_and_read_back) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.016s

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
try 1: i2c: no device at 0x49 (errno 19)
try 2: temp_c=231.00
```
In the simulator, the items that can be observed through serial are checked by
`harness/tryit-l200.spec.js` — pending-ci, not yet observed.
