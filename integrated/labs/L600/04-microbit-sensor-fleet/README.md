# L600 #04 An offline-first micro:bit sensor fleet

Combines **microbit** (stub boards, radio, sensors, battery model) + **distributed-systems** (delta-state CRDT,
gossip) + **application-architecture** (versioned API, consumer-driven contracts). Everything runs on the
microbit topic's CPython stub with simulated time - status **validated-stub** for the device parts.

## Run (from this folder)
| | macOS (zsh) | Windows (PowerShell) |
|---|---|---|
| scorecard | `python3 run_project.py` | `py run_project.py` |
| failure lab | `python3 run_project.py --inject wallclock-lww` | `py run_project.py --inject wallclock-lww` |
| other faults | `--inject oversize-frame`, `--inject schema-drift` | same |
| tests | `python3 -m unittest discover -s tests -t .` | `py -m unittest discover -s tests -t .` |
| before the fix | `FLEET_STORE=lww python3 -m unittest tests.test_failure_lab` | `$env:FLEET_STORE="lww"; py -m unittest tests.test_failure_lab` |
| build task (yours) | `BUILD_TARGET=mine python3 -m unittest tests.test_build_task -v` | `$env:BUILD_TARGET="mine"; py -m unittest tests.test_build_task -v` |
| try it | `python3 try_it/sync_interval.py`, `python3 try_it/partition_capacity.py` | `py try_it\sync_interval.py`, `py try_it\partition_capacity.py` |

No packages beyond the Python 3.12 standard library. CPU time is a few seconds per run; on network storage,
loading 20 stub boards can take 30-60 s of wall time.

## Files
| File | Purpose |
|---|---|
| `run_project.py` | scorecard: 4 milestones, 5 seams, 3 fitness functions as JSON lines; `--inject` |
| `firmware/node.py` | board program: flash log, dots, delta frames, selective acks, radio off between syncs |
| `gateway.py` | frame decoder (schema byte, whole records only), acks, `FleetAir` (gateways answer, radio partition) |
| `store.py` | `ReadingStore` (dot-keyed delta-state CRDT) and `WallClockLWWStore` (failure lab) |
| `fleet_sim.py` | the seeded scenario: loss, partitions, reboot, clock skew, gossip, battery model |
| `laws.py` | merge-law property test (reuses distributed-systems L400 #18 `shrink`) |
| `api.py`, `contracts.py` | /v1 + /v2 API on 127.0.0.1; consumer contracts (application-architecture L300 #14) |
| `_kb.py` | imports the reused labs in place (never copied, never edited) |
| `decisions/` | ADRs 0001-0004 (Nygard format) |
| `architecture.mmd` | Mermaid diagram |
| `solution/node_251.py` | build-task solution (251-byte frames) |
| `contracts/` | contract files written by the consumer side |

## Expected output (observed, seed 4)
```
{"kind": "milestone", "check": "M1 offline-first devices", "value": {"sampled": 14400, "dropped": 0, "peak_log": 190}, "threshold": "14400 sampled, 0 dropped, peak <= 400", "pass": true}
{"kind": "milestone", "check": "M2 delta sync over a lossy radio", "value": {"reached_gateway": 14400, "tries": 2835, "frames": 9752, "logs_empty": true}, "threshold": "every reading at a gateway; logs empty", "pass": true}
{"kind": "milestone", "check": "M3 CRDT merge + gossip", "value": {"laws": "300/300", "replicas_equal": true, "wrong_values": 0}, "threshold": "laws all pass; 5 replicas equal", "pass": true}
{"kind": "milestone", "check": "M4 versioned API + contracts", "value": {"contract_problems": 0, "v1_deprecation": "@1798761600", "api_rows": 14400}, "threshold": "0 problems; v1 deprecated; API rows == stored", "pass": true}
{"kind": "seam", "check": "S1 radio length <-> CRDT delta size", "value": {"max_frame_bytes": 30, "rejected": {"g1": 0, "g2": 0}, "full_state_frames_per_device": 224}, "threshold": "frames <= 32 B, 0 rejected", "pass": true}
{"kind": "seam", "check": "S2 device clock <-> identity/order", "value": {"wall_key_repeats": 1421, "lost": 0}, "threshold": "repeats exist, 0 lost", "pass": true}
{"kind": "seam", "check": "S3 battery <-> sync interval", "value": {"firmware_active_ms": 20, "model_active_ms": 20, "life_h_min": 2419.7}, "threshold": "same ACTIVE_MS; life >= 2000 h", "pass": true}
{"kind": "seam", "check": "S4 firmware schema <-> backend contract", "value": {"schema1_rows": 2880, "rec_len_equal": true}, "threshold": "2880 schema-1 rows; layouts equal", "pass": true}
{"kind": "seam", "check": "S5 CRDT state <-> API paging", "value": {"api_rows": 14400, "stored": 14400}, "threshold": "paged rows == stored", "pass": true}
{"kind": "fitness", "check": "F1 zero lost readings (30% loss + partitions)", "value": {"lost": 0, "sampled": 14400}, "threshold": "lost == 0", "pass": true}
{"kind": "fitness", "check": "F2 convergence within N gossip rounds", "value": {"end_of_run": 1, "experiment_max": 3, "experiment_mean": 2.27}, "threshold": "<= 4 rounds", "pass": true}
{"kind": "fitness", "check": "F3 battery life at the chosen sync interval", "value": {"sync_every_min": 10, "life_h_min": 2419.7}, "threshold": ">= 2000 h", "pass": true}
{"scorecard": "PASS", "passed": 12, "total": 12, "seed": 4, "inject": null, "dashboard": ["d01 #1 20 C", "d01 1.1 20 C light 100", "d17 1.1 20 C light n/a (fw 1)"]}
```
Exit code 0.

Failure lab (`--inject wallclock-lww`), observed:
```
{"kind": "seam", "check": "S2 device clock <-> identity/order", "value": {"wall_key_repeats": 1421, "lost": 1421}, "threshold": "repeats exist, 0 lost", "pass": false}
{"kind": "fitness", "check": "F1 zero lost readings (30% loss + partitions)", "value": {"lost": 1421, "sampled": 14400}, "threshold": "lost == 0", "pass": false}
{"scorecard": "FAIL", "passed": 9, "total": 12, "seed": 4, "inject": "wallclock-lww", "dashboard": ["d01 #1 20 C", "d01 1.1 20 C light 100", "d17 1.1 20 C light n/a (fw 1)"]}
```
Exit code 1. M4 (contracts) still passes and the replicas still converge - on the wrong data.
Other faults: `--inject oversize-frame` -> `"passed": 4, "total": 12` (14,082 lost, frames truncated to 32 B and
rejected); `--inject schema-drift` -> `"passed": 5, "total": 12` (2,880 schema-1 readings never acked, 7 contract problems).

Tests: `python -m unittest discover -s tests -t .` -> `Ran 29 tests ... OK` (about 4-5 min here, almost all
of it loading stub boards from network storage). `FLEET_STORE=lww` -> `AssertionError: 1421 != 0 : lost 1421
readings with store=lww`, FAILED (failures=1). `BUILD_TARGET=mine` on the shipped 32-byte firmware -> FAILED (failures=2).

Try it 1 (`try_it/sync_interval.py`), observed:
```
{"sync_every_min": 1, "life_h_min": 2212.4, "tries": 21816, "frames": 39841, "p95_to_gateway_s": 2280, "lost": 0, "dropped_flash_full": 0, "peak_log": 181}
{"sync_every_min": 10, "life_h_min": 2419.7, "tries": 2835, "frames": 9752, "p95_to_gateway_s": 4020, "lost": 0, "dropped_flash_full": 0, "peak_log": 190}
{"sync_every_min": 60, "life_h_min": 2445.1, "tries": 871, "frames": 6750, "p95_to_gateway_s": 14940, "lost": 0, "dropped_flash_full": 0, "peak_log": 305}
```
Try it 2 (`try_it/partition_capacity.py`), observed:
```
{"partition_h": 3.0, "selective_ack": true, "peak_log": 190, "dropped_flash_full": 0, "lost": 0, "logs_empty": true, "replicas_equal": true}
{"partition_h": 8.0, "selective_ack": true, "peak_log": 400, "dropped_flash_full": 451, "lost": 450, "logs_empty": true, "replicas_equal": true}
{"partition_h": 8.0, "selective_ack": false, "peak_log": 400, "dropped_flash_full": 1039, "lost": 2330, "logs_empty": false, "replicas_equal": true}
```

## Simulator vs real
Stub boards (no MicroPython VM, no airtime, collisions or range); per-delivery loss independent of frame length;
the flash log is a dict (a file on a board); battery figures are the microbit L300 #14 MODEL (30 mA awake,
0.5 mA assumed sleep floor, 1,250 mAh), not measurements. pendingCi: the firmware in the micro:bit V2 simulator.
