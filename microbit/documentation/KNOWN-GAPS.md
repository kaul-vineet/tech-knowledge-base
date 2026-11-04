# Known gaps — micro:bit L100 + L200 + L300 + L400

## Not run / not observed
1. **The simulator was never run while writing this KB** (sandbox has no internet). Every "expected serial in the simulator" block is derived from the lab's `print` calls, not observed. `harness/simulator.spec.js` checks them in CI → status **pending-ci**.
2. **`if __name__ == "__main__":` on the simulator/board.** The labs rely on `main.py` running as `__main__` in MicroPython. No micro:bit doc page states this explicitly. If it is false, the labs print nothing and the CI harness fails on every lab; fix by replacing the guard with a plain `main()` call and making tests import functions only.
3. Lab "validated-stub" (was "validated-local" before review F02) means: logic passed `unittest` against `labs/sim_stub` in CPython 3.12.15. The stub is not MicroPython and not the simulator.

## Simulator facts not fully verified
4. **MicroPython version inside the simulator**: inferred as 2.1.1 from the repo's `lib` folder commit message ("micro:bit MicroPython 2.1.1"); no build artefact was inspected. The only pinned identifier is the embed path `/v/0.1/`; no release tag number was confirmed.
5. **Embedding API stability**: the README says the embedding API and URLs are not yet stable. Message names in the harness (`flash`, `set_value`, `serial_output`, `request_flash`, `mute`, `ready`, `state_change`) are from the README and the python-editor-v3 behaviour; a change breaks the harness, not the labs.
6. **Sensor ranges**: lightLevel 0–255 (README). Temperature slider range, accelerometer slider range (±1024 per a secondary DeepWiki page) and gesture reset to `"none"` after ~500 ms (DeepWiki) are **not** from primary sources. The harness uses temperature 30, X = 800 and resets gesture to `"none"`.
7. **Sound in the simulator**: the Python Editor page lists "sound" among simulated features, but whether `speaker.off()` is audible/modelled and how `audio.SoundEffect` renders were not verified.
8. **REPL in the simulator**: the simulator README says it includes a REPL and the editor guide documents Ctrl+C / Ctrl+D in the serial console (written for a WebUSB-connected board). Behaviour in the simulator's serial panel was not observed.
9. Could not fetch: `raw.githubusercontent.com/.../src/demo.html`, GitHub `tree/main/src/board`, `blob/main/src/board/state.ts`, and the simulator DeepWiki page (empty responses). Sensor ids were taken from the live `demo.html` page instead.

## Stub limitations (by design)
10. Built-in image bitmaps in `sim_stub` are illustrative (tests compare to the same objects, not to device bitmaps).
11. `SoundEffect` constant values in the stub: only the defaults (WAVEFORM_SQUARE=3, FX_NONE=0, SHAPE_LOG=18, from the docs' `repr()` example) are sourced; others are placeholders.
12. Built-in `music` tunes in the stub are placeholder note lists.
13. No font rendering, scrolling timing, button bounce, gesture recognition, audio, or `wait=` blocking.

## Content decisions / dropped items
14. **Display brightness**: MicroPython for micro:bit has no global brightness function in the Display docs; the lesson uses per-pixel 0–9. MakeCode's `led.setBrightness` is listed as an equivalent only (its docs: not supported in the MakeCode simulator).
15. Microphone/sound level, compass, radio, data logging: simulated but out of L100 scope.
16. MakeCode simulator: listed as an equivalent and as a learning tool (lessons 6, 7, 11; `LEARNING-TOOLS.md`); labs are MicroPython and were not tried there.
17. Real-hardware quirks (e.g. light-level warm-up, temperature offset from processor heat) are not covered beyond a short troubleshooting note.

## CI / tooling
18. GitHub Actions versions (`actions/checkout@v4`, `setup-python@v5`, `setup-node@v4`, `upload-artifact@v4`) were not re-checked against their latest majors.
19. `.github/workflows/labs.yml` sits inside this domain folder. GitHub only runs workflows from the repository root; copy it there and set `KB_DIR`.
20. `@playwright/test` is pinned to 1.64.1 (seen in python-editor-v3's recent commit; release notes show 1.64 as current). No lock file is committed because npm was unavailable offline.
21. Licences: readthedocs page licence assumed from the MIT-licensed project; support.microbit.org and makecode.microbit.org pages state no licence.

## Concepts layer
22. **L300–L400 concept map is a proposal** (L200 is now built; L100 `next` fields point at the built L200 lessons). No agreed curriculum file for this domain was found in the kb folder; the map in `CONCEPTS-PRIMER.md` is a suggestion and the "Next:" lines in each note follow it.
23. **V1-era runtime docs.** Multiplexing figures (12 pins, 3×9), the 18 ms / 55 Hz refresh and "first light reading is 0" come from the Lancaster micro:bit runtime (DAL) docs, written for V1. V2 uses CODAL; equivalent V2 figures were not found.
24. Worked examples run against the stub (`research/concept_examples.py`): they check the lab arithmetic and logic, not simulator or hardware behaviour. Angles in note 06 use atan2(x, −z), a simple illustration, not the runtime's pitch/roll algorithm.
25. ~~The harness posts messages with targetOrigin `*`.~~ Fixed: `harness/host.html` now posts to the exact simulator origin (`new URL(simUrl).origin`, by default `https://python-simulator.usermbit.org`) and ignores messages from any other origin. Not yet exercised in CI.
26. Licences of MDN, Wikipedia, Home Assistant, Lancaster docs and tech.microbit.org pages were not re-checked on the pages themselves.
27. The Lancaster buttons doc page returned no content; debounce facts rely on the Arduino tutorial instead.

## Rebalance (hands-on first, REBALANCE-SPEC)
28. **tryIt items are validated on the stub only.** All 12 were run (`try_it.py`, asserted by `test_try_it.py`); 9 are also checked in the simulator by `harness/tryit.spec.js` → **pending-ci**, not observed. No simulator check: 01 item 2 (removing the `__main__` guard only matters for PC test imports), 02 item 1 (LED pixels are not visible to the serial-based harness) and 04 item 1 (timing).
29. **04 tryIt 1 (tune length)** is computed by `try_it.py` from the lab's `TUNE` with the documented note rules (`NOTE[octave][:ticks]`, carry-over, 125 ms ticks); the stub has no timing and the harness does not assert simulator timing.
30. **06 tryIt 2 (`is_gesture`)**: the stub keeps "shake" as the current gesture until another is injected; whether the simulator keeps it current until `"none"` is sent (DeepWiki says it resets after ~500 ms) is unverified, so the harness only requires two `shake!` lines.
31. **03 tryIt in the simulator** depends on click timing (60 ms holds vs a 3 s poll); a click straddling a poll could count 2. The harness therefore only asserts `count 1` appears and `count 3` does not.
32. Concept share is measured with the REBALANCE-SPEC script: **46% before, 20% after** (20.5%: concept 1487 / hands-on 5770 words), at the low edge of the 20–25% target. Notes are 238–245 words by `wc -w` (245–249 by the script's `split()`, which also counts arrows), so at L100 the share cannot rise much further without growing notes past the 250-word cap.

## Platforms and agent assist (PLATFORM-AGENT-SPEC)
33. **Mac and Windows were not run.** All local runs are on Linux (CPython 3.12.15). Every lesson has `platforms: {mac: expected, windows: expected}`; the CI matrix (`ubuntu-latest`, `macos-latest` arm64, `windows-latest`) runs the stub tests, agent-assist demo and Playwright harness — pending-ci.
34. **Setup-step commands not executed**: `brew`, `winget`, `pbcopy`, `Set-Clipboard`, `Start-Process`, `open -a "Google Chrome"` were checked against docs/manifests only. The macOS REPL shortcut (Control+C, not Cmd+C) is expected terminal behaviour, not observed in the simulator.
35. **Browsers**: micro:bit recommends Chrome/Edge; Safari 17+ and Firefox 128+ are named as lacking WebUSB only. Simulator use in Safari/Firefox was not tested; the harness uses Chromium only.
36. **Agent assist used the fake server only.** No real model (Ollama/llama.cpp) was run; `realModelNote` is guidance. The fake reply is a fixed template from the vendored `fake_model_server.py` (one rule added, documented in its header). The number check rejects any number not in the telemetry/counts/thresholds/0-255, so a real model that computes an average is rejected even if correct — deliberate at L100.
37. **RAM for the local model** was not measured; HARDWARE.md gives only the documented model size (986 MB) and Ollama's 4 GB install space on Windows. Winget `Ollama.Ollama` lists an x64 installer only (Windows on Arm not covered).
38. **Concept share fell to 18.0%** (concept 1487 / hands-on 6767) after adding mac/windows step fields, platforms, and agentAssist — below the 20-25% L100 target. Notes were not padded (cap 250 words).
39. Pre-existing wrong counts fixed: lessons 2-4 `testCases` said 8/9/9 tests; observed 6/7/7.

## L200 (Build it)
40. **Simulator data logging not observed.** The micro:bit user guide says the simulator's data log module shows simulated data. The iframe messages `log_output` / `log_delete` are NOT in the simulator README; they were seen only in a secondary DeepWiki summary of the Python Editor. `host.html` records them, the lab 08 test only annotates what it saw. The exact CSV the simulator produces (timestamp heading, decimals, mirroring format) is unverified; the stub follows CODAL `MicroBitLog.cpp`, which is the device runtime.
41. **Could not fetch** (empty responses): simulator sources (`src/board/*.ts`, `src/microbithal_js.c`), `python-editor-v3/src/device/simulator.ts`, `micropython-microbit-v2/src/codal_port/modlog.c` and `modradio.c`. Radio truncation and "radio is not enabled" come from the V1 `modradio.cpp`; the V2 port is assumed to behave the same.
42. **Analog pin input in the simulator**: the README says pins take touch values 0/1 and "In future, analog values will be supported"; a DeepWiki page says the Pins module offers analog input. Conflict unresolved → the lab 09 build task (`read_analog`) is checked on the stub only. Pin outputs (`write_digital`/`write_analog`) are not visible to the harness; only serial is checked. Whether `read_digital()` on pins 0–2 follows the simulator's touch control was not verified (the lab uses `is_touched()`).
43. **I2C**: the browser simulator cannot attach I2C devices. The TMP102 in `labs/sim_stub/i2c_devices.py` is a SIMULATED Python model (TI register map); it ignores conversion time, shutdown/one-shot, extended mode and ALERT. What the simulator's `i2c.read/write/scan` return with nothing attached is unknown; the harness accepts the error line or a `temp_c=` line and records which. The stub's NACK for a bad pointer byte (OSError 19) is a stub choice.
44. **Radio stub values**: `RATE_1MBIT/RATE_2MBIT` numbers, RSSI (−45) and timestamps (`running_time()*1000`) are placeholders; no range, collisions or timing. In the simulator pair, group filtering is done by `host.html` from `state.radio.group` (shape seen on demo.html only); if the state carries no group, packets are forwarded regardless.
45. **Log stub**: time-unit constant values and the log capacity are stub-only (`_set_capacity`); the real MY_DATA size is not modelled.
46. **Two-board simulator tests never run** (no internet). Two WASM simulators in one page may need more than the 120 s timeout on slow runners.
47. **Python Editor UI steps not observed**: lab 07 steps 1–2 (Radio module chat) and lab 08 step 2 (Data logging module) follow the docs; the chat's exact message bytes were not inspected.
48. **Float formatting**: `"{:.2f}"` in labs 10 is assumed to print the same in MicroPython (single-precision floats on the device) as in CPython; test values are exact binary fractions (21.5, −10.25, 30.5) to avoid rounding differences.
49. **Duplicate filter trade-off** (lab 07): a sender that restarts at sequence 1 is ignored until it passes the receiver's last number — documented in the code walkthrough, not solved at L200.
50. **Concept share L200 = 25.0%** (concept 1937 / hands-on 5810 by the REBALANCE script; notes 358–389 words by `wc -w`), exactly at the low edge of 25–30%. Hands-on fields were shortened to reach it; notes were not padded.
51. **No real board or real model**: the optional TMP102 wiring step and the agent assist with Ollama were not run.

## Update pass: learning tools + review fixes (2026-10-28)
52. **Learning-tool exercises not run.** All 8 `learningTools` entries (lessons 5, 6, 7, 8, 11) need a browser,
    the simulator or a desktop app; each `expected` says "Pending a manual run" and quotes the lab's printed value
    to compare with. Whether the Python Editor simulator shows the data-log table, MakeCode datalogger blocks in its
    simulator, and the standalone simulator's radio_input payload format are unverified (catalog gaps).
53. **F02 (High) — fixed in labels, not in substance.** Status is now `validated-stub` (defined in README) and every
    lesson lists `validation.pendingCi`. The labs still have not run on MicroPython or in the simulator; that needs the
    harness run in CI (root workflow is a separate job; this folder's `.github/` was not edited).
54. **F01 (High) — recorded.** README states "not yet run on macOS or Windows; CI matrix pending". `platforms` stays `expected`.
55. **F04 — fixed.** Windows Node is pinned `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0` (lesson 1 step 7,
    HARDWARE, harness README); HARDWARE says "Node 24 (Maintenance LTS)". Re-check after the Node 26 LTS promotion.
56. **F05 — fixed.** Lesson 1 now uses the canonical commands from `shared/WORKSTATION-SETUP.md` (winget
    `Python.Python.3.12` instead of the Python install manager `9NQ7512CXL7T`; `$env:PYTHONUTF8 = "1"`;
    ExecutionPolicy hint) and links to it; lesson 5's real-model note uses `brew services start ollama` / `OllamaSetup.exe`.
    Not executed on either OS (see #34).
57. **F26 — recorded, not resolved.** Lesson 7 tryIt 2 (`'A'*40` → 23 characters) is the V1 `modradio.cpp` rule; the
    `expected` now says so. Only `harness/tryit-l200.spec.js` 'long-value' in the V2 simulator can confirm it (pending-ci).
58. **F09 — recorded.** Concept share stays below target at L100 (18%, #38); not padded.
59. **F03 — no change needed** for L100 (all `next` fields name built L200 lessons); L200 `next` fields now read
    "L300 (planned): …".
60. **F08** — lesson 8 `seeAlso` points to simulation L200 #7 "Input modelling: fit service times and check the fit".
61. **F27** — `__pycache__` folders removed; no stray logs found.

## L300 (Harden it, 2026-10-28)
62. **Faults are stub-only.** Radio loss/dup/reorder/corrupt (lab 12), quick taps on a timeline (13), the temperature
    trace (14) and serial noise (15) are injected in the CPython stub with fixed seeds. The browser simulator has no
    fault injection; `harness/simulator-l300.spec.js` checks only the happy path in MicroPython — **pending-ci, never
    run**. Real-board loss rates and timing will differ from the seeded numbers.
63. **Lab 14 is a model, not a measurement.** 30 mA is the tech site's worst-case on-board *budget* (upper bound), 1.5 µA
    is the nRF52833 chip alone, 20 ms awake per wake-up is an assumption, 1,250 mAh comes from an older Energizer E92
    datasheet revision (the current one shows the figure only as a chart). The micro:bit V2 **board** Deep Sleep current
    was not found in any official source; results beyond ~1 year ignore self-discharge. Whether the simulator emulates
    `power.deep_sleep` is unverified (harness records it).
64. **Stub `power` and timeline are new stub behaviour.** `deep_sleep(ms=None)` without `wake_on` raises in the stub
    (the board waits for reset/USB); `run_every` during Deep Sleep is not modelled; button wake-up works via the timeline.
65. **Lab 13 busy loop in the simulator.** The scheduler's `while True: run_once()` never sleeps; whether the WASM
    simulator stays responsive to button input under a busy loop is not verified (harness test pending-ci).
66. **Lab 15 broker path not run.** paho-mqtt 2.1.0 and Mosquitto 2.1.2 are not installed in the sandbox;
    `mqtt_bridge.py` and `test_mqtt_ci.py` follow the PyPI README API and run only in CI job `gateway-mqtt`. The
    Windows step assumes the installer's default path `C:\Program Files\mosquitto\mosquitto.exe` (not verified).
    pyserial 3.5 (real board) not run: simulator-only track.
67. **Lab 16 Rust/Renode never built or run.** No Rust toolchain or Renode in the sandbox. Versions (embassy-executor
    0.10.0, embassy-time 0.5.1, embassy-nrf 0.11.0, cortex-m 0.7.6, cortex-m-rt 0.7, critical-section 1.1,
    panic-halt 1.0.0) come from docs.rs and the Embassy main-branch example `Cargo.toml`; crates.io pages were not
    fetched. Embassy APIs change between releases (`#[interrupt]` + `InterruptExt` usage follows the main-branch
    multiprio example). CI jobs `rust-firmware` and `renode` are the first real check.
68. **Renode is a close sibling, not the target.** No nRF52833 platform exists in Renode (only `nrf52840.repl`); the
    nRF52833 build runs on the nRF52840 model with legacy UART0 (`easyDMA: false`, renode issue #1014; Renode's own
    UARTE shell test is tagged skipped). The raw `nrf52840.repl` file could not be fetched in full (the GitHub page
    rendered only part of it); the full peripheral list came from a DeepWiki summary (lead only). Whether the racy
    build loses ticks under Renode's virtual timing is recorded, not asserted; the race is proven on the host model.
    That the Embassy RTC1 time driver and CLOCK start-up work in Renode's model is unverified.
69. **Lab 16 local test is a Python port.** `host_sim.py` mirrors `logic/src/lib.rs` line for line; the Rust host test
    (`cargo test`) is pending-ci. Static checks compare register addresses/values in the Rust source with the PS.
70. **Microsoft Learn Rust page** (winget `Rustlang.Rustup`) was seen through web_search results, not web_fetch; the
    winget-pkgs folder for Rustup could not be fetched (GitHub refused). Homebrew `rustup` and rustup.rs were fetched.
71. **Concept share L300 = 20.1%** (concept 2,775 / hands-on 11,014 by the REBALANCE script on `content/L300.json`;
    notes 527–549 words by `wc -w`), below the 30–35% target. Notes were not padded past 550 words and labs were not cut;
    L300 lesson objects carry more fields (failureLab, tradeOffs, 5–7 walkthrough items, Mac/Windows commands).
72. **No L300 tryIt runs in the simulator.** All 10 tryIt results are stub/host-model observations (the faults they
    depend on exist only there).
73. **Learning-tool exercises (L300) not run** — browser/desktop tools; each `expected` says "Pending a manual run".

## L300 update pass: review fixes + learning tools (2026-10-28)
74. **R3-19 — fixed in the model.** Lab 14's headline `life_h` is now a board-level estimate at an assumed, conservative
    BOARD SLEEP FLOOR of 0.5 mA, with `life_h_range` for 0.5–0.05 mA and the nRF52833-only figure kept apart as
    `chip_only_bound_h`. Adaptive design: ≈2,158 h (range 2,158–9,588 h; chip-only bound 15,245 h; averaged over exactly one hour — see lab README). The floor range is an
    **assumption**: no official micro:bit V2 board Deep Sleep current exists (Power Management Spec 1.0.3 gives modes,
    not currents). Replace it with a measurement before quoting any lifetime.
75. **R3-13 — fixed with a residue.** The E92 source is now Energizer's own datasheet (form EBC-1103-M). That sheet gives
    capacity as a chart only, so the 1,250 mAh at 25 mA value still comes from the older revision's printed text
    (EBC-1103I, distributor copy, kept only as a one-line equivalent in VERIFIED-RESOURCES / evidence).
76. **R3-09 — fixed.** Lesson 16 `buildTask.solution` is the single path `firmware/src/bin/fixed.rs`; the Python mirror
    is in the new field `buildTask.solutionMirror` (`solution_model.py`).
77. **R3-10 — recorded, accepted.** Lab 13's lesson `code` (`main.py`, the BEFORE file) is 54 lines, under the ~60–120
    guide. It is short on purpose (a blocking loop is the fault); the hardened `solution.py` is 104 lines. Not padded.
78. **R3-04 — fixed on this side.** `seeAlso` added: #13 → distributed-systems L300 #16 (backpressure/shedding);
    #16 → distributed-systems L300 #13 (lost update, fencing, interleaving checker). Already present: #12 →
    distributed-systems L100 #4 (retries), #15 → application-architecture L200 #9 (events). Back-links live in the
    other topics' JSON and were not edited in this pass.
79. **R3-05 / R3-06 — no change needed.** All L200 #7–11 `next` fields name real L300 lessons; every L300 build-task
    test has the `BUILD_FILE=<before>` switch and the shipped lab files are the unfixed versions.
80. **R3-14 — reported** in README (all levels): L100 17.4%, L200 23.2%, L300 19.6% (below targets; not padded).
81. **Renode learning tool (L300 #16) not run.** Its `expected` quotes the robot test's `done lost_total=0` and the
    host model's 316 of 1,316 lost; the emulator run stays pending-ci (R3-01: still no macOS/Windows run).

## L400 (Design it) + capstone (2026-10-28)
82. **Everything L400 is validated-stub.** All numbers (delivery, latency, attacks, drift, alarm digests, scorecard)
    come from CPython 3.12.15 on Linux against `labs/sim_stub`, in simulated time. The stub radio has no airtime,
    collisions or range, and stub boards spend no CPU time: lab 17's "40 boards work" is a protocol result, not a
    capacity claim. `harness/simulator-l400.spec.js` is written but has not run (no internet); macOS/Windows CI pending (R3-01).
83. **MicroPython speed of SipHash-2-4 is unknown.** It needs 64-bit arithmetic, which MicroPython does with big
    integers on the 32-bit nRF52833; whether the micro:bit build enables arbitrary-precision integers was not checked in
    the docs. The harness test records the time per tag; until then the lesson does not claim a sample-rate limit.
84. **No hashing module on micro:bit MicroPython** is an absence finding: the documented module index lists none (hashlib,
    hmac, cryptolib); the firmware build might contain undocumented modules. Not tested on a board.
85. **RFC 4303 §3.4.3 not retrieved in full.** Only §2.2 and the contents were read; the 64-counter window and the
    "MAC before window" order are this lab's design, consistent with but not quoted from the RFC.
86. **The LPC1768 guide was not available in the workspace.** Its capstone pattern ("deterministic core decides, AI only
    explains") is taken from PLATFORM-AGENT-SPEC.md; lesson 21 and the capstone follow that statement.
87. **Fake model server rule `[[MICROBIT-INCIDENT]]` is deliberately injectable** (it obeys "clear <ALARM>" in a label) to
    stand in for a manipulable model. No real model was run (Ollama pending); real small models will be rejected more
    often than 17/200, and their failure modes may differ from `fuzz.py`'s 11 kinds.
88. **Lab 20's twin models links as independent.** Coupling through the shared relay produced one alarm on a nominal
    board (n1 at 1,050 s); n6's DRIFT_LAT in the capstone has no separated cause; the false-alarm thresholds count it. The thermal model is a fixed
    first-order curve with seeded noise, not a real room.
89. **Lab 18 keeps configuration in RAM.** Persisting last-good to flash (`open()`/`write()`) is described, not exercised;
    a stub `open()` would write into the lab folder, so the lab avoids it. Config frames are not authenticated in lab 18
    (lab 19 adds a MAC; the capstone does not authenticate config frames yet - L400 candidate).
90. **Capstone firmware is generated by text patches** (`firmware_patches.json`, each must match exactly once). The
    generated `build/classroom_node.py` was parsed and run on the stub only; it has not been flashed to the simulator.
91. **Dashboards not opened.** Superset, Prometheus and Grafana exercises are manual and pending; Prometheus 3's
    Content-Type rule is why the export is `metrics.txt` (served as text/plain). Superset has no official Windows support.
92. **Concept share L400 = 20.7 %** (concept 4,203 / hands-on 16,055 words by the REBALANCE script on `content/L400.json`;
    notes 718-735 words for 17-21 and 545 for the capstone by `wc -w`), below the 35-40 % target. Notes were not padded past
    750 words and labs were not cut; L400 lesson objects carry designBrief, options, fitnessFunction, scalingLimits,
    mac/windows steps and capstone milestones/rubric.
93. **Simulation L400 digital-twin lesson did not exist** when lesson 20 was written; the cross-link points at simulation
    L100 #2 and L300 #13 instead. Add the L400 link (both ways) once that lesson exists.
94. **Learning-tool exercises (L400) not run** - browser/desktop tools; each `expected` says "Pending a manual run".
95. **L400 test runtime.** Each L400 lab's suite takes about 1 minute here (loading seven stub boards per run); the
    capstone runs its pipeline twice (seeds 22 and 23). CI timeouts were not tuned.

## L500 theory companion + lesson 14 reconciliation (2026-10-30)
96. **Lesson 14 battery figure reconciled.** The adaptive design's stated inputs (483 wake-ups x 20 ms at 30 mA in one hour,
    0.05 mA floor, 1,250 mAh) give 9,588.4 h, but the lab printed 9,600.5 h. Cause: the final 8 s Deep Sleep, started at
    3,599,400 ms, ran the stub clock to 3,607,400 ms and `budget.py` averaged over the clock, adding 7.4 s of sleep.
    Fix: `run_design()` now clips the run to `run_ms` (one hour). New figures, consistent in the lab README, `content/L300.json`
    (code, step, proof, expected results), the concept note, `research/concept_examples_l300.out.txt`, L300-evidence,
    the qbank and this file: headline 2,158.3 h (was 2,158.9), range 2,158.3-9,588.4 h (was 9,600.5), chip-only bound
    15,244.7 h (was 15,275.4), avg 0.5792 mA. main.py (41.7 h) and both tryIt results are unchanged.
    `test_main.Model.test_window_is_exactly_one_hour` pins it; L500 #23 problem 23.7 teaches it.
97. **L500 is validated against the stub only.** Every theorem check runs on CPython 3.12.15 + numpy 2.5.3 (Linux) with
    `labs/sim_stub`. Sensor traces in lesson 24 are synthetic and seeded; the lesson 25 heater is a simulated plant with
    ASSUMED parameters (tau 60 s, gain 20 C); LED Vf values are assumptions. Nothing was measured on a board.
    Mac/Windows runs (and numpy 2.5.3 wheels there) are pending the CI step added to `labs.yml`.
98. **numpy is now a dependency, for L500 only.** L100-L400 labs stay stdlib-only; `labs/run_tests.py` and
    `research/qbank_checks.py` now import numpy because they include the L500 checks.
99. **Primary-paper landing pages not fetched.** The research tool could not fetch the DOI pages
    (doi.org/10.1109/JRPROC.1949.232969, doi.org/10.1145/321738.321743) or dl.acm.org. Bibliographic data were confirmed
    from IEEE Xplore search records (1697831; reprint 659497), Scilit/INSPIRE DOI listings and dblp (JACM 20(1):46-61).
    The papers' content was read from search-result text of course-hosted copies (licence unstated; not linked); summaries
    are paraphrases. Liu & Layland's section numbering was not verified, so the lessons cite theorems, not sections.
100. **General-n RM proof is a sketch.** Lesson 25 proves the n = 2 bound in full and sketches the general case with a
    pointer to Liu & Layland (Theorems 1-5). The check covers it numerically (2,985 random sets, tight set, counterexamples).
101. **Law at policy level only.** ICO Children's code and DPDP Act statements were checked against the regulator /
    Gazette text on 2026-10-30, not by a lawyer. The ICO marks the code "under review" after the Data (Use and Access)
    Act 2025. DPDP Rules 2025 commence in phases (18 months from 13 Nov 2025 per PIB); the 13 May 2027 date for the
    children's-data rules comes from secondary sources and is flagged as "check the date" in the lesson. Whether a school's
    own sensor network is an "information society service" under the Children's code is left open deliberately.
102. **ACM Code principle texts.** Principles 1.1 and 1.2 were read in the retrieved text; the titles of 1.6, 2.9, 3.7 and
    4.1 are cited by number and title only (from the Code's structure), not quoted.
103. **14-week plan.** The pedagogy review that asked for a 14-week syllabus is not in `kb/`; the week plan in
    `content/assessment/syllabus.md` is this topic's own proposal. ABET mapping is the course team's proposal, not an
    accreditation decision.
104. **Exam and problem answers.** Every numeric answer in the L500 problem sets, midterm and final is recomputed by
    `research/l500_checks.py` (97 values); essay/proof answers are model answers, not auto-checked.
105. **No L500 simulator or hardware runs.** Lesson 23-25 checks are host-side Python; none is MicroPython for the board.

## L400 candidates (further study)
- **Authenticated configuration** in the capstone (lab 18 frames with lab 19's MAC and counters) and key rotation per device.
- **Two relays** with cross-relay dedupe (the relay is a single point of failure in ADR 0017).
- **Firmware internals and hardware-in-the-loop CI** (was the L300 #16 `next`): building MicroPython/CODAL, native modules,
  Renode/real-board runs in CI.
- **Measured MicroPython budgets**: SipHash time per tag, relay CPU per frame, RAM per queue slot (simulator, then board).
- **EWMA vs CUSUM** for the twin, and a twin that models relay coupling; re-calibration policy after maintenance.
- **Real local model evaluation**: rejection rate and failure kinds with qwen2.5:1.5b and a larger model, same `check_reply`.

## Found while writing the explanations (Nov 2026)
- **L400 #20:** the explanation's CUSUM walkthrough uses an illustrative sequence (labelled as such); the real figures come from drift_eval.py.
- **Capstone #22:** the scorecard also raises an `n6 DRIFT_LAT` alarm that the lesson text doesn't mention; all 10 criteria still pass.
