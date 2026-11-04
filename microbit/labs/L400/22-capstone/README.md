# Lab 22-capstone — Classroom environmental monitor network

Six simulated boards (temperature, light, motion), reliable radio, an authenticating gateway, MQTT, storage, dashboard
exports, a fleet rollout, a digital-twin drift check and local-model explanations — built from labs 12-21 and run end
to end with seeded faults. Deterministic core decides; the AI only explains. Validation: **validated-stub**.
Architecture: `architecture.mmd`. Decisions: `adr/` (0022-0024) and the lab ADRs 0017-0021.

| File | Purpose |
|---|---|
| `firmware_patches.json`, `build_firmware.py` | Generates `build/classroom_node.py` from lab 19 `frame_auth.py` + lab 17 `solution.py` + 4 patches (each must match once) |
| `pipeline.py` | Scenario (seed 22, 600 s), `Gateway` (lab 15 framer via lab 17 `edge_sim`, lab 19 verifier, MiniBroker, SQLite), `Eve` (replays + forgeries) |
| `run_capstone.py` | Milestones M1-M6, writes `out/dashboard.csv` + `out/metrics.txt`, prints the scorecard as JSON lines |
| `test_milestones.py` | One test class per milestone on one seeded run |
| `test_fitness.py` | Whole scorecard on seed 23 |
| `test_mqtt_ci.py` | CI only: rows to Mosquitto with paho-mqtt (lab 15's `MqttPublisher`) — pending-ci |

## Run
```bash
cd labs/L400/22-capstone
python3 build_firmware.py
python3 run_capstone.py        # Windows: py run_capstone.py   (about 1 minute)
```
Observed:
```
wrote build/classroom_node.py 255 lines
```
```
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
```

## Tests
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
Ran 9 tests in <time>
OK (skipped=1)
```

## Dashboard (manual, pending)
* Apache Superset: Settings > Data > Upload CSV -> `out/dashboard.csv` (allow uploads on the database); chart temp per dev over `t_sensor`.
* Prometheus + Grafana: `out/metrics.txt` is in the Prometheus text exposition format. Serve it on 127.0.0.1
  (`python3 -m http.server 9101 --bind 127.0.0.1 -d out`; `.txt` is sent as `text/plain`, which Prometheus 3 needs),
  scrape `http://127.0.0.1:9101/metrics.txt` (`metrics_path: /metrics.txt`), add Prometheus as a Grafana data source;
  `sum(classroom_readings_total)` must equal the stored rows (3,599).
