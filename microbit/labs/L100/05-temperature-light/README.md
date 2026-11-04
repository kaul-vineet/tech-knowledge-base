# Lab 05-temperature-light — Temperature and light

| File | Purpose |
|---|---|
| `main.py` | Lab program (flash/paste this into the simulator) |
| `test_main.py` | Unit tests: runs the lab logic against `labs/sim_stub` with injected inputs |
| `try_it.py`, `try_it.json`, `test_try_it.py` | The lesson's two `tryIt` items: code edits, a runner, and a test of the observed results |
| `agent_assist.py`, `test_agent_assist.py`, `agent_assist_output.txt` | Agent assist: a local model explains the telemetry; `classify()` decides; code checks the text (tests use the fake server only) |

## Run in the simulator
Move the temperature slider above 26 °C and the light slider below 40; watch serial and the display.

Simulator inputs used: temperature, lightLevel.

Expected serial in the simulator (from the program's `print` calls; checked automatically by
`harness/simulator.spec.js` in CI — **not yet observed**, status pending-ci):
```
temp=<t>,light=<l>,state=ok
temp=30,light=200,state=hot
temp=30,light=10,state=dark
```

## Run the logic tests locally (no board, no internet)
```bash
# macOS (zsh) and Windows (PowerShell) alike; forward slashes work in both
cd labs/L100/05-temperature-light
python3 -m unittest -v      # Windows (PowerShell): py -m unittest -v
```

### Expected output (observed in the sandbox, Python 3.12.15, Linux)
```
test_check_rejects_invented_number_and_missed_alarm (test_agent_assist.AgentAssist.test_check_rejects_invented_number_and_missed_alarm) ... ok
test_cli_fake (test_agent_assist.AgentAssist.test_cli_fake) ... ok
test_code_decides_alarms (test_agent_assist.AgentAssist.test_code_decides_alarms) ... ok
test_fake_agent_explanation_passes_check (test_agent_assist.AgentAssist.test_fake_agent_explanation_passes_check) ... ok
test_logged_state_mismatch_is_flagged (test_agent_assist.AgentAssist.test_logged_state_mismatch_is_flagged) ... ok
test_server_down_falls_back_to_code (test_agent_assist.AgentAssist.test_server_down_falls_back_to_code) ... ok
test_classify_thresholds (test_main.TempLightLab.test_classify_thresholds) ... ok
test_step_dark (test_main.TempLightLab.test_step_dark) ... ok
test_step_hot (test_main.TempLightLab.test_step_hot) ... ok
test_step_normal (test_main.TempLightLab.test_step_normal) ... ok
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 12 tests in 1.230s

OK
```
macOS and Windows: same tests in the CI matrix (`macos-latest`, `windows-latest`) — pending-ci.

## Try it (the lesson's `tryIt` items)
`try_it.json` holds the code edits; `try_it.py` applies them to `main.py` and runs
the result against the stub (`test_try_it.py` asserts the same results).
```bash
cd labs/L100/05-temperature-light
python3 try_it.py            # Windows (PowerShell): py try_it.py
```
Observed in the sandbox (Python 3.12.15):
```
try 1: temp=27,light=128,state=ok
try 2: temp=30,light=10,state=hot
```
In the simulator the same edits are checked by `harness/tryit.spec.js` — pending-ci, not yet observed.

## Agent assist (optional): the model explains, the code decides
`agent_assist.py` runs the lab's own `step()` on five fixed readings, lets `classify()`
decide every state, then asks a **local** model (OpenAI-compatible endpoint, default
`http://localhost:11434/v1` = Ollama) to explain the serial lines in plain language.
`check_explanation()` accepts the text only if every number in it comes from the telemetry,
the counts, the thresholds or the 0-255 scale, and it names every alarm state code found.
Otherwise the explanation is dropped and only the code decision is shown.

```bash
cd labs/L100/05-temperature-light
python3 agent_assist.py --fake            # Windows: py agent_assist.py --fake  (built-in fake server)
python3 agent_assist.py                   # real local model (Ollama running, model pulled)
python3 agent_assist.py --log serial.txt  # lines copied from the simulator's serial panel
```
Observed with `--fake` (Python 3.12.15, sandbox; also saved as `agent_assist_output.txt`):
```
telemetry:
  temp=21,light=128,state=ok
  temp=24,light=120,state=ok
  temp=27,light=110,state=hot
  temp=30,light=35,state=dark
  temp=22,light=200,state=ok
code decision (authoritative): 5 readings, alarms: #3 hot (temp=27, light=110), #4 dark (temp=30, light=35)
agent explanation (checked): The micro:bit sent 5 readings. Temperature started at 21 C and ended at 22 C, peaking at 30 C; this is the processor's own estimate, so it can read a little above the room. Light ranged from 35 to 200, where larger means brighter. The program itself labelled the readings: 1 hot and 1 dark; everything else was ok.
check: PASS (numbers all from telemetry; alarm states named)
```
Real model (not run here): `ollama pull qwen2.5:1.5b`, keep Ollama running, run without
`--fake`. Set `LOCAL_MODEL_URL` / `LOCAL_MODEL` for llama.cpp server or another model.
If Ollama is not running you get `agent: unavailable (URLError) -> code summary only`.

**Caution:** the model never takes actions or decides an alarm; `classify()` does. Never send
secrets or keys to a model.
