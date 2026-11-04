# 04 on the Mac mini — the firmware in the real MicroPython simulator, and a week-long soak of hundreds of boards

The lab runs `firmware/node.py` on the microbit topic's CPython stub (status `validated-stub`). On the Mac mini you
can run the same firmware in the official **MicroPython micro:bit V2 simulator** (WebAssembly, MIT) on two bridged
boards — a node and a minimal gateway — and leave a **7-simulated-day soak** of 100–500 stub boards running overnight.

Simulator choice, from what `kb/microbit` already supports: the topic's Playwright harness (`microbit/harness/`:
`host.html`, `serve.js`, `sim-helpers.js`, radio bridge between iframes) drives the official simulator. Renode appears
in the topic only for the Rust interrupt-race lab (L300 #16), not for MicroPython, so it is not used here.

| File | What it does |
|---|---|
| `make_sim_programs.py` | writes `sim_out/`: `node_sim.py` (firmware unchanged except `main()`: 30 samples 200 ms apart, final sync, one `stats ...` serial line), `node_sim_wait500.py` (ACK_WAIT_MS 500), `node_sim_oversize.py` (the oversize-frame fault), `gateway_sim.py` (a minimal device-side gateway for the simulator only). `--here` runs them on the CPython stub: what the browser must match |
| `sim/` | Playwright project (`@playwright/test` 1.64.1, as the topic's harness) that reuses the topic's harness files by path: 3 tests on two simulator boards |
| `soak.py` | `fleet_sim.run()` unchanged with `N_DEV` = site size, for `--days` simulated days; sites of ≤ 255 boards in parallel processes; memory per board-hour → largest site per RAM size |
| `ci.sh` | medium-size Mac runs for `.github/workflows/mac-mini.yml`: programs + stub check, the simulator tests (skipped with a message without `npx`), a 50-board × 1-day soak |
| `tests/test_mac_mini.py` | 6 tests (programs on the stub, the 1-byte device id, a short site run) |

## Run
```bash
# macOS (zsh), from integrated/labs/L600/04-microbit-sensor-fleet, inside the lab venv
python mac_mini/make_sim_programs.py --here                   # writes sim_out/ and checks it on the stub
cd mac_mini/sim && npm install && npx playwright install chromium && npx playwright test && cd ../..   # needs internet
caffeinate -i python mac_mini/soak.py --boards 250 --days 7 --out ~/kb-runs/04-soak.jsonl     # overnight, one site
caffeinate -i python mac_mini/soak.py --boards 500 --days 7 --out ~/kb-runs/04-soak500.jsonl  # two sites in parallel
python -m unittest discover -s mac_mini/tests -t mac_mini/tests
```
Node 24 and Playwright: as `microbit/harness/README.md` (`brew install node@24`; Playwright supports macOS 14+).

## Real output here (Linux sandbox, 2026-11-02 — CPython stub, NOT MicroPython and NOT the simulator)
```
$ python mac_mini/make_sim_programs.py --here
{"stub_run": {"program": "node_sim.py", "sampled": 30, "frames": 12, "tries": 3, "acked": 30, "left": 0, "maxframe": 30, "max_bytes_on_air": 30, "expect": "acked=30 left=0, frames <= 32 B"}}
{"stub_run": {"program": "node_sim_wait500.py", "sampled": 30, "frames": 12, "tries": 3, "acked": 30, "left": 0, "maxframe": 30, "max_bytes_on_air": 30, ...}}
{"stub_run": {"program": "node_sim_oversize.py", "sampled": 30, "frames": 10, "tries": 10, "acked": 30, "left": 0, "maxframe": 102, "max_bytes_on_air": 32, "expect": "maxframe > 32, truncated to 32 B on air"}}
$ python mac_mini/soak.py --here
{"experiment": "04 fleet soak", "boards": 20, "hours": 12, "device_id_max_per_radio_group": 255, "sites": 1, ...}
{"site": 1, "boards": 20, "hours": 12, "seed": 4, "sampled": 14400, "stored_b1": 14400, "lost": 0, "wrong_values": 0, "logs_empty": true, "replicas_equal": true, "convergence_rounds": 1, "drain_min": 2, "dropped_flash_full": 0, "peak_log": 190, "frames": 9752, "tries": 2835, "p95_to_gateway_s": 4020, "gossip_bytes": 445419, "life_h_min": 2419.7, "conflicts": 0, "wall_s": 11.9, "pass": true, ...}
{"memory": "peak RSS per board-hour (whole process, includes start-up)", ..., "reliable": false, "seq_wrap_days": 45.5, ...}
```
Two limits the soak script proves by code: the frame header carries the device id in one byte (`frames()` raises for
device 256), so 500 boards are two radio groups ("sites"); and the 16-bit `seq` per boot wraps after 45.5 days of
one-a-minute sampling without a reboot — a soak longer than that must show duplicate dots.

## Experiments (what you should see on the Mac and how to read it)
1. **Firmware in MicroPython.** Test 1 (500 ms ack wait) should pass: 30 readings sampled, every frame ≤ 32 B, all 30
   acked, flash log empty — the firmware's bytes/bit-shifting/dict code runs unchanged in MicroPython 2.x. Test 2 runs
   the shipped 50 ms window and only records `acked`: below 30 means the postMessage bridge between two iframes is
   slower than 50 ms (a property of the browser setup, not of a real radio — real timing needs two boards). Test 3
   records how many bytes the simulator puts on air for an 84–102-byte frame with `length=32`: 32 confirms the stub's
   truncation rule (from MicroPython's modradio source), anything larger means the stub is wrong and the failure lab's
   explanation must change. Passing test 1 is the first observed MicroPython run of this firmware (today it is `validated-stub` only).
2. **A week, 250 boards.** Expect `lost` 0, `wrong_values` 0, `logs_empty` and `replicas_equal` true, `dropped_flash_full`
   0 and `life_h_min` far above 168 h (~2,400 h from the L300 #14 battery model). Watch `p95_to_gateway_s`, `drain_min`
   and `gossip_bytes`: with 12× more devices on the same two gateways the drain after the outage window gets longer; a
   `drain_min` that hits the 240-minute cap (`logs_empty: false`) is the sign that ADR 0003's 10-minute sync interval
   or the gateway count must change for that fleet size.
3. **500 boards = 2 sites.** Expect the same per-site results and a peak memory per process that fits the
   `max_boards_per_site_for_7_days_by_ram_GB` line (reliable only from the Mac run, not from the 20-board sandbox run).

## Overnight
`soak.py --boards 500 --days 7`: two 250-board sites × 10,080 simulated minutes each, in parallel processes. The
stub's radio delivers every frame to every endpoint (O(boards²) per minute), so expect hours, not minutes. It reveals
week-scale effects the 12-hour lab run cannot: log growth at the gateways and replicas, gossip volume per day, and
whether every device still drains after a week of 30 % loss.

Sources and verification notes: `integrated/research/mac-mini-evidence.md`, section 04.
