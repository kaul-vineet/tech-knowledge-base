# Lab 15-serial-gateway — A serial gateway to the PC

| File | Purpose |
|---|---|
| `main.py` | Device (MicroPython): prints framed readings `$LLL<seq>,<temp>,<light>*CCCC` every 500 ms |
| `gateway.py` | BEFORE (PC): reads text lines, forwards MQTT-style JSON lines; no length/CRC check |
| `solution.py` | AFTER (build task): byte framer (length + CRC-16 + resync by one byte), payload range check, metrics JSON lines; `--demo`, `--file`, `--serial`, `--mqtt` |
| `serial_link.py` | Seeded serial faults (boot garbage, dropped byte, flipped bit, line cut short, random chunking); `python serial_link.py` writes `samples/` |
| `mqtt_bridge.py` | Publisher for a real broker: paho-mqtt 2.1.0, `CallbackAPIVersion.VERSION2`, QoS 1 (pending-ci) |
| `agent_assist.py` | A local model explains the gateway counters; **code decides the alarms** |
| `test_main.py`, `test_fault.py`, `test_build_task.py`, `test_try_it.py`, `test_agent_assist.py` | Stub/fake-server tests |
| `test_mqtt_ci.py` | Through Mosquitto with paho-mqtt — skipped here, runs in CI job `gateway-mqtt` (pending-ci) |
| `samples/clean.txt`, `samples/noisy.bin` | Transcripts written by `serial_link.py` |

## Step 1 — the device frames
In the Python Editor, paste `main.py` and open serial: one frame per 500 ms, e.g.
`$0081,20,127*0B24` at 20 °C and light 127 (the stub's values). `harness/simulator-l300.spec.js`
recomputes the length and the CRC of every frame the real MicroPython prints — **pending-ci**.

## Steps 2-3 — happy path, then the fault
```bash
cd labs/L300/15-serial-gateway
python3 serial_link.py                         # writes samples/ (Windows: py serial_link.py)
python3 gateway.py --file samples/clean.txt    # clean transcript: works
python3 gateway.py --file samples/noisy.bin    # noisy link: crashes on line 1
```
Observed (Python 3.12.15, Linux sandbox):
```
wrote samples/clean.txt (4092 bytes) and samples/noisy.bin (4099 bytes); faults {'dropped': 3, 'flipped': 5, 'cut': 2}
```
```
{"payload": {"light": 100, "seq": 1, "temp": 20}, "qos": 1, "topic": "microbit/mb1/telemetry"}
...
{"payload": {"light": 109, "seq": 200, "temp": 23}, "qos": 1, "topic": "microbit/mb1/telemetry"}
200 messages
```
```
Traceback (most recent call last):
  File "labs/L300/15-serial-gateway/gateway.py", line 55, in <module>
    main()
  File "labs/L300/15-serial-gateway/gateway.py", line 51, in main
    run(f, JsonLinesPublisher())
  File "labs/L300/15-serial-gateway/gateway.py", line 42, in run
    publisher.publish(TOPIC.format(device=device), parse_line(line))
                                                   ^^^^^^^^^^^^^^^^
  File "labs/L300/15-serial-gateway/gateway.py", line 34, in parse_line
    seq, temp, light = payload.split(",")
    ^^^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 3, got 1)
```
And as a test (it also shows a flipped digit forwarded as a real value):
```
test_a_flipped_digit_is_forwarded_as_truth (test_fault.Symptom.test_a_flipped_digit_is_forwarded_as_truth) ... ok
test_boot_garbage_crashes_it (test_fault.Symptom.test_boot_garbage_crashes_it) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.053s

OK
```

## Step 4 — build task: fails before, passes after
```bash
BUILD_FILE=gateway.py python3 -m unittest -v test_build_task          # macOS (zsh): BEFORE
$env:BUILD_FILE="gateway.py"; py -m unittest -v test_build_task      # Windows (PowerShell)
python3 -m unittest -v test_build_task                                 # AFTER: solution.py
```
Observed with `gateway.py` (summary lines):
```
test_chunk_size_does_not_matter (test_build_task.Hardened.test_chunk_size_does_not_matter) ... ERROR
test_garbage_only_input_is_survived (test_build_task.Hardened.test_garbage_only_input_is_survived) ... ERROR
test_metrics_line_explains_the_losses (test_build_task.Hardened.test_metrics_line_explains_the_losses) ... ERROR
test_noisy_link_no_crash_no_wrong_value (test_build_task.Hardened.test_noisy_link_no_crash_no_wrong_value) ... ERROR
ERROR: test_chunk_size_does_not_matter (test_build_task.Hardened.test_chunk_size_does_not_matter)
ValueError: not enough values to unpack (expected 3, got 1)
ERROR: test_garbage_only_input_is_survived (test_build_task.Hardened.test_garbage_only_input_is_survived)
ValueError: not enough values to unpack (expected 3, got 1)
ERROR: test_metrics_line_explains_the_losses (test_build_task.Hardened.test_metrics_line_explains_the_losses)
ValueError: not enough values to unpack (expected 3, got 1)
ERROR: test_noisy_link_no_crash_no_wrong_value (test_build_task.Hardened.test_noisy_link_no_crash_no_wrong_value)
ValueError: not enough values to unpack (expected 3, got 1)
Ran 4 tests in 0.107s
FAILED (errors=4)
```
Observed with `solution.py`:
```
test_chunk_size_does_not_matter (test_build_task.Hardened.test_chunk_size_does_not_matter) ... ok
test_garbage_only_input_is_survived (test_build_task.Hardened.test_garbage_only_input_is_survived) ... ok
test_metrics_line_explains_the_losses (test_build_task.Hardened.test_metrics_line_explains_the_losses) ... ok
test_noisy_link_no_crash_no_wrong_value (test_build_task.Hardened.test_noisy_link_no_crash_no_wrong_value) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.174s

OK
```
`test_chunk_size_does_not_matter` caught a real bug while this lab was written: the first framer
returned a batch of frames per chunk, so the periodic metrics line depended on chunk size. `feed()` is
now a generator.

## Step 5 — observability and agent assist
```bash
python3 solution.py --demo | python3 -c "import sys;[print(l,end='') for l in sys.stdin if 'metrics' in l]"
python3 agent_assist.py --fake                 # Windows: py agent_assist.py --fake
```
Observed:
```
{"payload": {"bad_crc": 3, "bad_len": 2, "bad_payload": 0, "frames_ok": 50, "resyncs": 5, "skipped_bytes": 98}, "qos": 1, "topic": "microbit/gateway/metrics"}
{"payload": {"bad_crc": 3, "bad_len": 3, "bad_payload": 0, "frames_ok": 100, "resyncs": 6, "skipped_bytes": 114}, "qos": 1, "topic": "microbit/gateway/metrics"}
{"payload": {"bad_crc": 3, "bad_len": 5, "bad_payload": 0, "frames_ok": 150, "resyncs": 8, "skipped_bytes": 167}, "qos": 1, "topic": "microbit/gateway/metrics"}
{"payload": {"bad_crc": 3, "bad_len": 6, "bad_payload": 0, "frames_ok": 190, "resyncs": 9, "skipped_bytes": 184}, "qos": 1, "topic": "microbit/gateway/metrics"}
```
```
metrics: {"bad_crc": 3, "bad_len": 6, "bad_payload": 0, "frames_ok": 190, "resyncs": 9, "skipped_bytes": 184}
alarms (decided by code): LINK_NOISY=4.5, SEQ_GAP=9
agent explanation (checked): The gateway accepted 190 of 199 frames. 3 frames failed the CRC check and 6 had the wrong length, so 4.5% of frames were damaged on the serial link, which looks like noise or a loose cable rather than a sensor fault. It resynchronised 9 times and kept running. 9 readings are missing from the sequence. Alarms raised by the gateway code: LINK_NOISY, SEQ_GAP.
check: PASS (numbers from the metrics; alarm names match the code's alarms)
```
Alarms come only from `decide_alarms()` (damaged frames above 2% → `LINK_NOISY`, a gap in the
sequence → `SEQ_GAP`, a reading at or above 30 °C → `TEMP_HIGH`). The explanation is shown only if
every number comes from the counters and it names exactly the raised alarms. Real model: same setup
as lab 05 (Ollama, `qwen2.5:1.5b`, `LOCAL_MODEL_URL` / `LOCAL_MODEL`) — not run here.

## Step 6 — to a real broker (optional, pending-ci)
Install Mosquitto and paho-mqtt 2.1.0, start the broker on `127.0.0.1:1883`, then:
```bash
# macOS (zsh)
brew install mosquitto && brew services start mosquitto
python3 -m pip install paho-mqtt==2.1.0
mosquitto_sub -h 127.0.0.1 -t 'microbit/#' -v &        # watch
python3 solution.py --demo --mqtt 127.0.0.1:1883
```
```powershell
# Windows (PowerShell)
winget install -e --id EclipseFoundation.Mosquitto
py -m pip install paho-mqtt==2.1.0
& "C:\Program Files\mosquitto\mosquitto.exe" -p 1883     # in a second window
py solution.py --demo --mqtt 127.0.0.1:1883
```
`MQTT_BROKER=127.0.0.1:1883 python3 -m unittest -v test_mqtt_ci` checks it end to end. Not run in the
sandbox (no broker, no paho-mqtt): CI job `gateway-mqtt`. A real board: `python3 -m pip install
pyserial==3.5`, then `python3 solution.py --serial /dev/tty.usbmodem...` (macOS) or `--serial COM3`
(Windows) — not run (simulator-only track).

## All tests in this lab
```bash
python3 -m unittest -v
```
```
test_cli_fake (test_agent_assist.AgentAssist.test_cli_fake) ... ok
test_code_decides_alarms (test_agent_assist.AgentAssist.test_code_decides_alarms) ... ok
test_fake_agent_passes_check (test_agent_assist.AgentAssist.test_fake_agent_passes_check) ... ok
test_invented_alarm_and_number_are_rejected (test_agent_assist.AgentAssist.test_invented_alarm_and_number_are_rejected) ... ok
test_server_down_alarms_still_stand (test_agent_assist.AgentAssist.test_server_down_alarms_still_stand) ... ok
test_chunk_size_does_not_matter (test_build_task.Hardened.test_chunk_size_does_not_matter) ... ok
test_garbage_only_input_is_survived (test_build_task.Hardened.test_garbage_only_input_is_survived) ... ok
test_metrics_line_explains_the_losses (test_build_task.Hardened.test_metrics_line_explains_the_losses) ... ok
test_noisy_link_no_crash_no_wrong_value (test_build_task.Hardened.test_noisy_link_no_crash_no_wrong_value) ... ok
test_a_flipped_digit_is_forwarded_as_truth (test_fault.Symptom.test_a_flipped_digit_is_forwarded_as_truth) ... ok
test_boot_garbage_crashes_it (test_fault.Symptom.test_boot_garbage_crashes_it) ... ok
test_frame_format (test_main.Device.test_frame_format) ... ok
test_step_prints_one_frame (test_main.Device.test_step_prints_one_frame) ... ok
test_clean_transcript_is_forwarded (test_main.NaiveGatewayHappyPath.test_clean_transcript_is_forwarded) ... ok
test_readings_and_metrics_arrive (test_mqtt_ci.ThroughBroker.test_readings_and_metrics_arrive) ... skipped 'needs MQTT_BROKER and paho-mqtt (CI job gateway-mqtt)'
test_try_1 (test_try_it.TryIt.test_try_1) ... ok
test_try_2 (test_try_it.TryIt.test_try_2) ... ok

----------------------------------------------------------------------
Ran 17 tests in 1.604s

OK (skipped=1)
```

## Step 7 — try it
```bash
python3 try_it.py
```
```
try 1: no CRC: forwarded 181, 2 WRONG, bad_crc 0, bad_payload 9 | with CRC: forwarded 179, 0 WRONG, bad_crc 13, bad_payload 0
try 2: forwarded 190 readings, 0 wrong; metrics {'frames_ok': 190, 'bad_len': 6, 'bad_crc': 3, 'bad_payload': 0, 'resyncs': 9, 'skipped_bytes': 184}
```
