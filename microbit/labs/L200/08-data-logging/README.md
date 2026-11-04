# Lab 08-data-logging — Data logging

| File | Purpose |
|---|---|
| `main.py` | Lab program: `log` module rows + serial CSV |
| `export_csv.py` | PC tool: serial transcript -> clean RFC 4180 CSV (skips noise and mirrored rows) |
| `test_main.py` | Unit tests: serial CSV, log rows with timestamp column, full log (OSError 28), V1 fallback, export |
| `solution.py` | Build task solution: stop logging cleanly when the log is full |
| `test_build_task.py` | Build task check; `BUILD_FILE=main.py` checks your own version |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items |
| `agent_assist.py`, `test_agent_assist.py`, `agent_assist_output.txt` | Agent assist: code computes the stats of a logged CSV, a local model explains, code checks every quoted number (tests use the fake server only) |
| `../../sim_stub/` | Shared CPython stub: `microbit` (pins, i2c), `radio`, `log`, `i2c_devices` |

## Run in the simulator
1. Paste `main.py` into https://python.microbit.org/, press play, click **Show serial**.
2. Move the temperature and light sliders: a new CSV row appears every second.
3. Expand the simulator's **Data logging** module to see the rows stored with `log.add` (micro:bit
   docs: "expand the data log module to view the simulated data"); it can download them as CSV.
4. Select the serial text, copy it into `serial.txt`, then export (below).

Expected serial (from the `print` calls; checked by `harness/simulator-l200.spec.js` in CI —
**not yet observed**, status pending-ci):
```
time_ms,temp,light
<t>,25,200
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L200/08-data-logging
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_cli_fake (test_agent_assist.AgentAssist.test_cli_fake) ... ok
test_code_computes_stats (test_agent_assist.AgentAssist.test_code_computes_stats) ... ok
test_fake_agent_passes_check (test_agent_assist.AgentAssist.test_fake_agent_passes_check) ... ok
test_server_down_falls_back_to_code (test_agent_assist.AgentAssist.test_server_down_falls_back_to_code) ... ok
test_wrong_number_and_wrong_trend_are_rejected (test_agent_assist.AgentAssist.test_wrong_number_and_wrong_trend_are_rejected) ... ok
test_log_full_is_handled (test_build_task.LogFullBuildTask.test_log_full_is_handled) ... ok
test_other_oserrors_are_not_swallowed (test_build_task.LogFullBuildTask.test_other_oserrors_are_not_swallowed) ... ok
test_full_log_raises_enospc_in_main_lab (test_main.DataLoggingLab.test_full_log_raises_enospc_in_main_lab) ... ok
test_log_module_rows_have_timestamp_column (test_main.DataLoggingLab.test_log_module_rows_have_timestamp_column) ... ok
test_serial_csv (test_main.DataLoggingLab.test_serial_csv) ... ok
test_without_log_module_serial_only (test_main.DataLoggingLab.test_without_log_module_serial_only) ... ok
test_cli_writes_rfc4180_csv (test_main.ExportCsv.test_cli_writes_rfc4180_csv) ... ok
test_extract_skips_noise (test_main.ExportCsv.test_extract_skips_noise) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 15 tests in 1.718s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Build task
Handle a full log: catch `OSError` 28 from `log.add`, print `log full after N rows` once, stop logging and keep printing serial CSV.
`solution.py` is a worked solution; `test_build_task.py` is the check. To check your own edit of `main.py`:
```bash
BUILD_FILE=main.py python3 -m unittest -v test_build_task              # macOS (zsh)
$env:BUILD_FILE="main.py"; py -m unittest -v test_build_task          # Windows (PowerShell)
```
Observed with `solution.py` (Python 3.12.15):
```
test_log_full_is_handled (test_build_task.LogFullBuildTask.test_log_full_is_handled) ... ok
test_other_oserrors_are_not_swallowed (test_build_task.LogFullBuildTask.test_other_oserrors_are_not_swallowed) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.008s

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
try 1: time_ms,temp,light | Time (seconds),temp,light | 0.00,21,120 | 0,21,120 | 1.00,22,110 | 1000,22,110
try 2: kept 2 rows [['0', '21', '120'], ['1000', '22', '110']]; skipped 3 (Time (seconds),temp,light: time_ms not an integer, 0.00,21,120: time_ms not an integer, 1.00,22,110: time_ms not an integer)
```
In the simulator, the items that can be observed through serial are checked by
`harness/tryit-l200.spec.js` — pending-ci, not yet observed.

## Export the serial CSV to a file
Copy the serial panel text into `serial.txt` (any extra lines are fine), then:
```bash
cd labs/L200/08-data-logging
python3 export_csv.py serial.txt readings.csv    # Windows (PowerShell): py export_csv.py serial.txt readings.csv
```
Observed in the sandbox (Python 3.12.15) on a transcript with a "hello" line, mirrored log rows (tryIt 1)
and a half-received row:
```
kept 2 rows, skipped 5
  line 1 skipped (before header): hello from micro:bit
  line 3 skipped (time_ms not an integer): Time (seconds),temp,light
  line 4 skipped (time_ms not an integer): 0.00,21,120
  line 6 skipped (time_ms not an integer): 1.00,22,110
  line 8 skipped (wrong field count): 1000,22
```
`readings.csv` (CRLF line ends, as RFC 4180 and the `csv` module write them):
```
time_ms,temp,light
0,21,120
1000,22,110
```

## Agent assist (optional): the code computes, the model explains
`agent_assist.py` runs the lab's own `setup()`/`step()` on six fixed readings (or reads `--csv FILE`),
computes rows, duration, min/max/mean and trend per column, and asks a **local** model
(OpenAI-compatible, default `http://localhost:11434/v1` = Ollama) to summarise the raw CSV.
`check_explanation()` accepts the text only if every number in it is a CSV value or a computed stat
(within 0.05, i.e. rounding to 1 decimal) and every "rose"/"fell" claim matches the computed trend.
Otherwise the explanation is dropped and only the code stats are shown.
```bash
python3 agent_assist.py --fake              # Windows: py agent_assist.py --fake  (built-in fake server)
python3 agent_assist.py --csv readings.csv  # real local model (Ollama running, model pulled)
```
Observed with `--fake` (Python 3.12.15; also saved as `agent_assist_output.txt`):
```
csv:
  time_ms,temp,light
  0,21,120
  1000,21,118
  2000,22,110
  3000,23,90
  4000,24,60
  5000,24,41
code stats (authoritative): 6 rows over 5 s; temp 21..24 mean 22.5 (up); light 41..120 mean 89.8 (down)
agent explanation (checked): The log has 6 rows over 5 seconds. Temperature rose from 21 to 24, with a mean of 22.5. Light fell from 120 to 41, with a mean of 89.8.
check: PASS (every number matches the CSV or a computed stat; trends match)
```
Real model: not run here (no Ollama in the sandbox). **Caution:** the model never decides or acts;
the stats come from code. Never send secrets or keys to a model.
