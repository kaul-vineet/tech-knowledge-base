# BBC micro:bit — L100 + L200 + L300 + L400 + capstone + L500 theory (simulator only)

**Status: not yet run on macOS or Windows; CI matrix pending.**

Start here. This domain teaches the basics of programming a BBC micro:bit
in **MicroPython** without a physical board. Everything runs in the
**MicroPython micro:bit V2 simulator** in the micro:bit Python Editor
(open source, MIT, WebAssembly).

| Item | Pinned version / location |
|---|---|
| Simulator | `micropython-microbit-v2-simulator`, embed URL `https://python-simulator.usermbit.org/v/0.1/simulator.html` (repo `main` checked 2026-10-28) |
| MicroPython in the simulator | micro:bit MicroPython 2.1.1 (repo `lib` folder commit message; see KNOWN-GAPS) |
| Editor | micro:bit Python Editor v3, https://python.microbit.org/ |
| API reference | https://microbit-micropython.readthedocs.io/en/v2-docs/ |
| Local tests | Python 3.12 stdlib + `labs/sim_stub` (no installs); macOS `python3.12`, Windows `py -3.12` |
| Hosts | Apple-silicon Mac mini (macOS 14+) and Windows 11 PC; no micro:bit board needed (`HARDWARE.md`) |
| Simulator tests (CI) | Node 24, `@playwright/test` 1.64.1, Chromium |
| L300 optional (pending-ci) | Mosquitto 2.1.2 + paho-mqtt 2.1.0 (lesson 15); Rust stable + `thumbv7em-none-eabihf`, Embassy (embassy-nrf 0.11.0), Renode 1.17.0 (lesson 16) |
| L400 + capstone | Python 3.12 stdlib only (SQLite, hmac); optional, pending: Mosquitto + paho-mqtt (capstone), Ollama (lesson 21), Superset / Prometheus / Grafana (capstone dashboards) |
| L500 theory checks | Python 3.12 + numpy 2.5.3 (`pip install numpy==2.5.3`; the only third-party package in the topic) + `labs/sim_stub` |

**Validation key** (field `validation` in each lesson):
* `validated-stub` — the lab's unit tests and tryIt scripts ran and passed, but only against `labs/sim_stub`
  (a CPython imitation of the `microbit` API written for this KB) on Linux. Not MicroPython, not the simulator,
  not a board. All 22 lessons (L100–L400 and the capstone) have this status (review F02). L300 #16 is the exception in kind: what ran
  locally is a Python host model of the Rust logic plus static checks of the Rust sources; the Rust build,
  `cargo test` and the Renode run are listed in its `validation.pendingCi`.
* `validation.pendingCi` — the files and variants that have **not** run yet: the Playwright simulator tests,
  the macOS/Windows matrix, and any real-model or real-board variant.
* `pending-ci` — written against the documented API but not run at all (not used in this topic).

**Learning tools:** open-source tools that complement the labs (Python Editor, MakeCode, standalone simulator,
Orange/Superset for logged CSVs, Renode for lesson 16, JupyterLab/SimPy/Ollama/Prometheus/Grafana at L400) are listed in `documentation/LEARNING-TOOLS.md`. Each mapped lesson has a
`learningTools` field with a concrete exercise (column "Tools" below).

## Lesson map (L100 = "Run it": copy, run, observe)

| # | Lesson | Lab | Main APIs | Validation | Tools |
|---|---|---|---|---|---|
| 1 | Set up your environment | `labs/L100/01-setup` | editor, simulator, serial/REPL, sensor controls, local tests | validated-stub (logic); simulator run pending-ci | — |
| 2 | The LED display | `labs/L100/02-led-display` | `display.scroll/show`, `Image`, pixel brightness 0–9 | validated-stub; simulator pending-ci | — |
| 3 | Buttons | `labs/L100/03-buttons` | `is_pressed`, `was_pressed`, `get_presses` | validated-stub; simulator pending-ci | — |
| 4 | Sound | `labs/L100/04-sound` | `music.play/pitch`, `audio.play(Sound…)`, `audio.SoundEffect`, `speaker.on/off`, `pin_logo` | validated-stub; simulator pending-ci | — |
| 5 | Sensing temperature and light | `labs/L100/05-temperature-light` | `temperature()`, `display.read_light_level()` (+ agent assist) | validated-stub (agent assist: fake model server); simulator pending-ci | Python Editor |
| 6 | Motion and gestures | `labs/L100/06-motion-gestures` | `accelerometer.get_values`, `current_gesture`, `was_gesture` | validated-stub; simulator pending-ci | Python Editor, MakeCode |

## Lesson map (L200 = "Build it": change and combine, then prove it with tests)

| # | Lesson | Lab | Main APIs | Build task | Validation | Tools |
|---|---|---|---|---|---|---|
| 7 | Radio between two boards | `labs/L200/07-radio` | `radio.config(group)`, `send`/`receive`, message format `kind:seq:value` | acks | validated-stub (two stub boards); two bridged simulators pending-ci | MakeCode, standalone simulator |
| 8 | Data logging | `labs/L200/08-data-logging` | `log.set_labels/add` (timestamps), serial CSV, `export_csv.py` (+ agent assist) | handle a full log (`OSError` 28) | validated-stub (agent assist: fake server); simulator pending-ci | Python Editor, Orange (Superset) |
| 9 | Pins and PWM on the edge connector | `labs/L200/09-pins-pwm` | `write_digital`, `write_analog`, `set_analog_period`, `is_touched`, `pin_logo` | potentiometer via `read_analog` (stub only) | validated-stub; simulator pending-ci | — |
| 10 | An external sensor over I2C | `labs/L200/10-i2c-sensor` | `i2c.write/read/scan`, TMP102 register map, `OSError` 19 | write the T_HIGH register | validated-stub against a **simulated** TMP102; simulator pending-ci | — |
| 11 | A game as a state machine | `labs/L200/11-game-state-machine` | transition table, `was_pressed`, `was_gesture`, `running_time()` | pause/resume | validated-stub; simulator pending-ci | MakeCode |

## Lesson map (L300 = "Harden it": a fault breaks it, you make it robust, a test proves it)

| # | Lesson | Lab | Fault injected (seeded) → fix | Build task proof | Validation | Tools |
|---|---|---|---|---|---|---|
| 12 | A reliable radio protocol | `labs/L300/12-reliable-radio` | 20% loss + dup/reorder/corrupt: 14/20 delivered silently → ack, retransmit + backoff, dedupe, CRC-16 | `main.py` fails, `solution.py` passes (20/20 once, in order) | validated-stub; two simulators pending-ci | standalone simulator, MakeCode |
| 13 | Non-blocking firmware structure | `labs/L300/13-nonblocking-scheduler` | 150 ms taps during `sleep(1000)`: 1/8 counted → cooperative scheduler, overrun/late/error JSON lines, safe state | 8/8 taps | validated-stub; simulator pending-ci | Python Editor, MakeCode |
| 14 | Power budgeting (modelled, not measured) | `labs/L300/14-power-budget` | 100 ms logging, board On: 41.7 h on 2 x AAA (model) → adaptive sampling + `power.deep_sleep` | ≈2,158 h board estimate (assumed 0.5 mA floor; range 2,158–9,588 h) ≥ 720 h, delay ≤ 10 s (model) | validated-stub (estimates only) | Orange, Python Editor |
| 15 | A serial gateway to the PC | `labs/L300/15-serial-gateway` | boot garbage, dropped/flipped bytes, cut lines: gateway crashes → framing (length + CRC) + resync; MQTT-style JSON (+ agent assist) | 190/200 forwarded, 0 wrong | validated-stub; Mosquitto + paho-mqtt pending-ci | Orange, Superset |
| 16 | Close-sibling low-level code: a timer interrupt race in Rust | `labs/L300/16-interrupt-race` | IRQ between read and write: ticks lost (host model) → critical section | 0 lost in every interleaving | validated-stub (host model + static checks); Rust build, `cargo test`, Renode (nRF52840 model) pending-ci | Renode |

## Lesson map (L400 = "Design it": constraints, options measured, decision recorded, fitness test)

| # | Lesson | Lab | Design question → options (measured on the seeded stub) → decision | Fitness function | Validation | Tools |
|---|---|---|---|---|---|---|
| 17 | Edge-to-cloud architecture: from sensor boards to a dashboard | `labs/L400/17-edge-to-cloud` | Path to broker/store/dashboard: direct serial 180/180 (6 cables) · relay as written 160/180, p95 9.6 s · relay desynchronised 180/180, p95 153 ms · BLE not available in MicroPython → ADR 0017 | 5 seeds: ≥ 99 %, p95 ≤ 2 s | validated-stub | Superset, standalone simulator |
| 18 | Device fleet management: versioned config over the radio | `labs/L400/18-fleet-config` | Config updates: one-phase 12,086 unacked ticks, 5 boards deaf · two-phase push-all 0 / 4 exposed · two-phase staged 0 / 1 exposed → ADR 0018 | 0 unacked ticks; blast radius ≤ 1 | validated-stub | standalone simulator, Python Editor |
| 19 | Securing constrained devices: authenticated radio frames | `labs/L400/19-radio-auth` | No hashlib on micro:bit: CRC 20/20 forgeries in · keyed CRC (NOT secure) 19/20 · SipHash-2-4 + replay window 0, genuine 160/160 → ADR 0019 | 5 seeds: 0 forged, 0 replays | validated-stub | Python Editor |
| 20 | A digital twin of the sensor network | `labs/L400/20-digital-twin` | Drift check: \|z\| > 2 80 false alarms per 1,000 · \|z\| > 3 12 · CUSUM 0, drifts found in 8-9 windows → ADR 0020 | ≤ 5 per 1,000; drift ≤ 10 windows | validated-stub | JupyterLab, SimPy |
| 21 | Local AI at the edge gateway: it explains, code decides | `labs/L400/21-edge-ai-explain` | Who may change alarms: model decides 195/200 changed · model may act 17/200 + injection clears TEMP_HIGH · explain-only 0/200 → ADR 0021 (+ agent assist) | 600 adversarial replies: digest unchanged | validated-stub (fake model server) | Ollama |
| 22 | Capstone: classroom environmental monitor network | `labs/L400/22-capstone` | Labs 12-21 composed: 6 boards, attacker, rollout, twin, alarms, local agent, exports; scorecard PASS 10/10 (seeds 22 and 23); ADRs 0022-0024 | whole scorecard on seed 23 | validated-stub | Superset, Prometheus, Grafana |

Each L400 lab (17-21) has the shipped BEFORE file (the lesson `code`), `solution.py`, `test_fault.py` (symptom),
`test_build_task.py` (`BUILD_TARGET=mine` runs the BEFORE file and fails; `BUILD_FILE=<file>` also works),
`test_fitness.py`, an ADR in `adr/` (Nygard format) and a README with real output. Lessons carry `designBrief`,
`options` (with measured evidence), `decisionRecord`, `fitnessFunction` and `scalingLimits`. Shared helpers:
`labs/L400/_edge/` (per-link loss `LinkAir`, MQTT-style `MiniBroker`, SQLite store, CSV/Prometheus exports, `reuse()`
to import earlier labs). The capstone builds its board program from labs 17 and 19 (`build_firmware.py`) and prints a
JSON-lines scorecard (`run_capstone.py`). Concept notes: `content/concepts/L400/` (17-21: 718-735 words; capstone 545).

## Lesson map (L500 = "Theory & rigour": derive it, prove it, check it in code, read the sources)
| # | Lesson | Lab / material | Theorems (each checked in code) and assessed work | Status |
|---|---|---|---|---|
| 23 | Foundations I: digital electronics and signals | `labs/L500/23-digital-foundations` | Two's complement; Ohm/KVL, power and window-averaged battery life (= lab 14's figures); ADC noise Δ²/12 and 6.02N+1.76 dB; PWM average/RMS · 8 problems | validated-stub |
| 24 | Foundations II: sampling and signal processing | `labs/L500/24-sampling-filters` | Sampling theorem + aliasing (100 Hz at 30 Hz → 10 Hz on stub light data); moving average response and √N; EMA step, τ, α/(2−α) · 8 problems | validated-stub |
| 25 | Foundations III: control and real-time theory | `labs/L500/25-control-realtime` | P/PI stability and steady-state error on a simulated heater (assumed plant); Liu & Layland RM bound vs exact simulation (lesson 13: U = 0.37, but 24 ms non-preemptive response); CRC as GF(2) division, all bursts ≤ 16 detected · 8 problems | validated-stub |
| 26 | Ethics: classroom data, children's privacy, e-waste and accessibility | concept note + case study | ACM/IEEE codes, ICO Children's code, DPDP Act 2023 s.9 (policy level), Global E-waste Monitor 2024, micro:bit accessibility · case analysis + 6 problems | validated-stub (no code) |
| 27 | Reading seminar: Shannon (1949) and Liu & Layland (1973) | concept note + readings | 2 papers, 5 guiding questions each, 2 critical responses · 6 problems | validated-stub (no code) |

Each L500 lesson in `content/L500.json` carries `learningObjectives` (Bloom: derive/prove/explain/evaluate/critique),
`theorems` (statement, proof, `check` = the function that verifies it, `checkOutput` = its real output), a `problemSet`
with full solutions and a `rubric`; lesson 26 adds `caseStudy`, lesson 27 `readings`. Concept notes:
`content/concepts/L500/` (23-25: 913-1,138 words; 26: 824; 27: 549). Course assessment pack: `content/assessment/`
(syllabus with a 14-week plan, weights and CS2023/ABET mapping; midterm; final; 15-item concept inventory;
capstone oral defence; ADR peer review; team roles and pair programming). Question bank: `content/qbank/L500.json` (45).
Checks: `python research/l500_checks.py` (every theorem check, `checkOutput` freshness, 74 problem-set values and
23 exam values recomputed), `python research/check_l500_qbank.py`, `python research/qbank_checks.py`.

Each L300 lab has `main.py` (or `gateway.py`, `race_model.py`) = BEFORE, `solution.py` = AFTER, `test_fault.py`
(the symptom, pinned), `test_build_task.py` (fails with `BUILD_FILE=<before>`, passes on the solution) and a
README with the real output of both. Lessons carry `failureLab`, `tradeOffs` and a 5-7 item `codeWalkthrough`.
`buildTask.solution` is always one real path; lesson 16's Rust fix is `firmware/src/bin/fixed.rs` and its Python mirror
(the one that runs locally) is in `buildTask.solutionMirror`.
Observability: labs 12, 13, 14 and 15 print JSON lines (link counters, scheduler events, budget report,
gateway metrics). Concept notes: `content/concepts/L300/` (450-550 words). The stub gained a seeded faulty radio
(`radio.Air(loss, dup, reorder, corrupt, seed)`), an input timeline (`microbit._at`, `_advance`) and `power`.
Lesson 16 is not MicroPython: Rust + Embassy for the nRF52833, run in Renode on the nRF52840 model — a
**close sibling**, not the micro:bit; its README lists what differs from real V2 hardware.

Each L200 lab adds `solution.py` + `test_build_task.py` (the lesson's `buildTask`), and each lesson has a
`codeWalkthrough`. Concept notes: `content/concepts/L200/` (320–400 words, with a Trade-offs table).
No new packages: the stub in `labs/sim_stub/` gained `radio`, `log`, full pins, `i2c` and a clearly
labelled **simulated** I2C device model (`i2c_devices.py`); `labtest.load_boards()` runs two boards.

Lesson content (steps, expected results, troubleshooting, sources) is in
`content/L100.json`, `content/L200.json`, `content/L300.json`, `content/L400.json` and `content/L500.json`.

**Concepts first:** read `documentation/CONCEPTS-PRIMER.md` once, then each lesson's
concept note in `content/concepts/` (`01-setup.md` … `06-motion-gestures.md`) before
its lab. Hands-on leads: each note is short (200–250 words: Why it matters, Mental model,
How it works with 3 points that each point to a lab step, Common mistakes). Each lesson
object links its note via `conceptNote`/`conceptSummary` and carries the rest:
`inRealSystems`, `useWhen`, `checkYourself` (shown with the checkpoint), `tryIt`
(2 code changes with prediction and observed result) and `next` (L200 topic).
The lab code names each concept in a comment where it happens.
Worked-example numbers come from `research/concept_examples.py`.

**Concept share** (REBALANCE-SPEC script: concept-note words vs lesson-object words, measured 2026-10-28 after
L400): L100 concept 1,487 / hands-on 7,077 = 17.4% (target 20–25%); L200 1,937 / 6,410 = 23.2% (target 25–30%);
L300 2,787 / 11,501 = 19.5% (target 30–35%); L400 + capstone 4,203 / 16,055 = 20.7% (target 35–40%). Notes are at full length (L300 527–550,
L400 718–735 and the capstone 545 words by `wc -w`); they were not padded and labs were not cut (KNOWN-GAPS 38, 50, 71, 92).

## How to run the labs

**In the simulator (the real thing):** open https://python.microbit.org/,
replace the code with a lab's `main.py`, press the simulator's play button,
click *Show serial*. Use the controls under the simulator for buttons,
temperature, light, accelerometer and gestures.

**Logic tests on your PC (no board, no internet)** — Mac mini (zsh) or Windows (PowerShell);
see `documentation/HARDWARE.md`, lesson 1 step 6 and `../shared/WORKSTATION-SETUP.md` for installing Python 3.12:
```bash
python3 labs/run_tests.py          # all labs + local-agent helper; Windows: py labs\run_tests.py
cd labs/L100/03-buttons
python3 -m unittest -v             # one lab (incl. tryIt checks); Windows: py -m unittest -v
python3 try_it.py                  # print the lesson's tryIt results; Windows: py try_it.py
cd ../../L200/07-radio
python3 -m unittest -v test_build_task   # L200 build-task check (solution.py); BUILD_FILE=main.py checks yours
cd ../../L300/12-reliable-radio
python3 link_sim.py                      # L300: BEFORE vs AFTER on the seeded faulty radio
python3 -m unittest -v test_fault        # the failureLab symptom
BUILD_FILE=main.py python3 -m unittest test_build_task   # must FAIL (Windows: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
```
L300 optional parts (pending-ci, see each lab README): lab 15 to a real broker (`brew install mosquitto` /
`winget install -e --id EclipseFoundation.Mosquitto`, `pip install paho-mqtt==2.1.0`); lab 16 Rust
(`brew install rustup` / `winget install -e --id Rustlang.Rustup`, `rustup target add thumbv7em-none-eabihf`)
and Renode 1.17.0 (GitHub release assets for macOS arm64, Windows, Linux).

L400 (stub, about 1 minute per lab): `cd labs/L400/17-edge-to-cloud && python3 options.py` (each lab has its measuring
script: `fleet_sim.py`, `attacks.py`, `drift_eval.py`, `options.py`), `BUILD_TARGET=mine python3 -m unittest test_build_task`
must FAIL (Windows: `$env:BUILD_TARGET="mine"; py -m unittest test_build_task`), `python3 -m unittest -v test_fitness`;
capstone: `cd labs/L400/22-capstone && python3 run_capstone.py` prints the scorecard.

L500 (needs numpy 2.5.3): `cd labs/L500/23-digital-foundations && python3 foundations1.py` (24: `foundations2.py`,
25: `foundations3.py`) prints one OK line per theorem; from the topic root `python3 research/l500_checks.py`,
`python3 research/check_l500_qbank.py` and `python3 research/qbank_checks.py` must print OK
(Windows: `py -m pip install numpy==2.5.3`, then `py research\l500_checks.py`).

**Agent assist (lessons 5, 8, 15 and 21 + capstone, optional):** lab 21's `solution.py` lets a local model explain
a classroom incident from a frozen alarm record; it has no write path, `check_reply()` checks its words and a SHA-256
digest proves the alarms did not change (a device label carrying "clear TEMP_HIGH" is rejected). lab 15's `agent_assist.py` lets a local model explain
the serial gateway's counters while `decide_alarms()` raises every alarm (`LINK_NOISY`, `SEQ_GAP`,
`TEMP_HIGH`) and code checks the explanation's numbers and alarm names. lab 08's `agent_assist.py` lets a local model
summarise a logged CSV while code computes the statistics and rejects any quoted number or trend the
data does not support. Lesson 5: `labs/L100/05-temperature-light/agent_assist.py`
lets a local model (Ollama/llama.cpp, OpenAI-compatible, `LOCAL_MODEL_URL`) explain the
serial telemetry; `classify()` decides every alarm and code checks the explanation
(the LLM explains, never decides). `--fake` uses the deterministic fake server in
`labs/_shared/local_agent/` (vendored shared helper; tests never call a real model).
Each lab keeps its logic in functions (`step()`, `classify()`, …) and starts
its `while True` loop only under `if __name__ == "__main__":`, so tests can
import it and call one iteration with injected inputs.

**Labs in the real simulator, automatically (CI):** `harness/` contains a
Playwright test that embeds the simulator iframe, flashes each `main.py`,
sets buttons/sensors with `postMessage` (to the exact simulator origin), and
asserts on serial output; `tryit.spec.js` does the same for the tryIt edits. L200 adds
`simulator-l200.spec.js` / `tryit-l200.spec.js`; lab 07 opens two simulators and `host.html`
forwards `radio_output` from one to the other as `radio_input`. See
`harness/README.md`. It runs in `.github/workflows/labs.yml` (job
`simulator`); it needs internet, so it was not run while writing this KB.
CI runs both jobs on `ubuntu-latest`, `macos-latest` (arm64) and `windows-latest`; L400 adds the capstone scorecard,
`BUILD_TARGET=mine` fail-before checks, `harness/simulator-l400.spec.js` and the capstone's broker test; L300 adds `gateway-mqtt`
(Mosquitto + paho-mqtt, same matrix), `rust-firmware` (cargo test + build, same matrix) and `renode` (Linux only).

**Hardware:** no micro:bit board is needed; see `documentation/HARDWARE.md` for what runs on
the Mac mini vs the Windows PC. Each lesson has `platforms` (`expected` until CI runs).

## Folder layout
```
documentation/   README (this), CONCEPTS-PRIMER, VERIFIED-RESOURCES, KNOWN-GAPS, HARDWARE, LEARNING-TOOLS
research/        L100-…L500-evidence.md, concept_examples(_l200|_l300|_l400).py (+ .out.txt), qbank_checks.py,
                 l500_checks.py, check_l500_qbank.py
content/         L100.json … L500.json, concepts/NN-*.md, concepts/L200/ … concepts/L500/, qbank/L100-L500.json,
                 assessment/ (syllabus, midterm, final, concept-inventory.json, capstone-oral-defence, peer-review-adr, team-roles)
labs/L100/NN-*/  main.py + test_main.py + README.md + try_it.py/.json + test_try_it.py
labs/L200/NN-*/  same + solution.py + test_build_task.py (08: export_csv.py, agent_assist.py)
labs/L300/NN-*/  BEFORE + solution.py + test_fault.py + test_build_task.py (+ drivers: link_sim, tap_sim,
                 budget, serial_link, host_sim); 16: firmware/ (Rust), logic/ (Rust), renode/
labs/L400/NN-*/  BEFORE + solution.py + test_fault / test_build_task / test_fitness + adr/ (+ options, sims);
                 22-capstone: build_firmware.py, pipeline.py, run_capstone.py, architecture.mmd, adr/
labs/L400/_edge/ shared L400 helpers (LinkAir, MiniBroker, SQLite store + exports, reuse)
labs/L500/NN-*/  foundationsN.py (theorem checks) + test_theory.py + README.md (23, 24, 25)
labs/sim_stub/   CPython stub: microbit/ (pins, i2c, input timeline), radio.py (seeded faults), power.py, log.py, i2c_devices.py (SIMULATED),
                 music.py, audio.py, labtest.py (load_lab, load_boards), tryit.py
labs/_shared/local_agent/  vendored client.py + fake_model_server.py (agent assist)
labs/run_tests.py
harness/         Playwright simulator tests (pending-ci; L300: simulator-l300.spec.js; L400: simulator-l400.spec.js)
.github/workflows/labs.yml
```

## Equivalents
* MakeCode for micro:bit has its own browser simulator (blocks / JavaScript /
  MakeCode Python). MicroPython code from these labs does **not** run there; it is used as a
  "see it in blocks" learning tool in lessons 6, 7 and 11 (`LEARNING-TOOLS.md`).
* With a physical board, the same `main.py` files flash from the Python
  Editor; V2-only lines (speaker, logo, SoundEffect) fail on a V1.
