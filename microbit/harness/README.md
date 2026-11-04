# Simulator harness (Playwright) — status: pending-ci

Runs each L100 and L200 lab (and the L300 device programs) inside the **MicroPython micro:bit V2 simulator** (the one
in the micro:bit Python Editor) and checks what it prints to serial.
It needs internet, so it runs in GitHub Actions (`.github/workflows/labs.yml`,
job `simulator`). It has **not** been run in the authoring sandbox (no network).

## Design

```
Playwright (Chromium)
  └─ http://127.0.0.1:4173/  host.html   (served by serve.js on loopback only, no deps)
       └─ <iframe src="https://python-simulator.usermbit.org/v/0.1/simulator.html">
            ⇅ window.postMessage (targetOrigin = exact simulator origin, never "*")
```

| Step | Message (parent → iframe) | What the test waits for (iframe → parent) |
|---|---|---|
| boot | — | `{kind:"ready", state}` → `window.sim.ready` |
| mute | `{kind:"mute"}` | — |
| run lab | `{kind:"flash", filesystem:{"main.py": Uint8Array}}` | `serial_output` text |
| press A/B, touch logo | `{kind:"set_value", id:"buttonA"/"buttonB"/"pinLogo", value:1}` then `0` | `serial_output` |
| sensors | `{kind:"set_value", id:"temperature"/"lightLevel"/"accelerometerX", value:n}` | `serial_output` |
| gesture | `{kind:"set_value", id:"gesture", value:"shake"}` then `"none"` | `serial_output` |

* Sensor ids come from the simulator's own demo page (`/v/0.1/demo.html`):
  `buttonA buttonB pinLogo pin0 pin1 pin2 accelerometerX/Y/Z gesture
  compassX/Y/Z compassHeading lightLevel soundLevel temperature`.
* `host.html` answers `request_flash` by re-sending the last program, as the
  README requires.
* `host.html` posts only to the simulator's exact origin (`new URL(simUrl).origin`,
  default `https://python-simulator.usermbit.org`) and ignores messages whose
  `origin` differs, as MDN recommends for `postMessage`.
* `tryit.spec.js` flashes each lab with its tryIt edits applied (read from the
  lab's `try_it.json`, the same file `try_it.py` uses) and checks serial output.
* All serial text is accumulated in `window.sim.serial`; `waitForSerial()`
  polls it with a RegExp and prints the full transcript on timeout.

## L200 additions
* **Two boards** (lab 07): `host.html?boards=2` creates two simulator iframes (`window.sims[0]`,
  `window.sims[1]`; `window.sim` is board 0). Every helper in `sim-helpers.js` takes an optional board index.
* **Radio bridge**: each `radio_output` (bytes, string messages start `0x01 0x00 0x01`) is posted to the
  other board as `radio_input` — both message kinds are in the simulator README. The README says
  `radio_input` "is assumed to be sent to the currently configured radio group", so the **bridge filters
  by group itself**, using `state.radio.group` (the `radio` key seen on `demo.html`). If a board reports
  no group, the packet is forwarded.
* `log_output` / `log_delete` are **not** in the simulator README (seen only in a secondary summary of
  the Python Editor); `host.html` records them in `sim.logOutput` and the lab 08 test only attaches what it
  saw as an annotation — no test requires them.
* `simulator-l200.spec.js` (5 lab tests) and `tryit-l200.spec.js` (7 tryIt tests).
* `host-bridge.check.js` runs `host.html`'s script in Node with fake iframes (no browser, no network) and
  checks the bridge, the group filter and the origin checks. **Run in the sandbox: OK** (`npm run check`).
* Lab 10 (I2C): the simulator cannot attach I2C devices; the test accepts the "no device" line or a
  `temp_c=` line and records which one appeared.

## L300 additions
* `simulator-l300.spec.js` (5 tests) runs the L300 **device** programs: lab 12 `solution.py` on two bridged boards
  (a reading crosses and is acked; the frame's CRC-16 is recomputed in JS), lab 13 `solution.py` (three 150 ms
  clicks → `tap 3`) and `main.py` (count only recorded), lab 14 `solution.py` (`power` + `log` in the simulator:
  any error recorded), lab 15 `main.py` (every printed frame's length and CRC checked).
* The L300 **faults** (radio loss, tap timeline, battery model, serial noise) exist only in the CPython stub; there
  is no `tryit-l300.spec.js` because every L300 tryIt depends on them. Lab 16 (Rust/Renode) is not a simulator lab.
* `sim-helpers.js` also looks in `labs/L300`; `playwright.config.js` matches `-l300` spec files.

## Run (machine with internet)

```bash
cd harness
npm install --save-exact          # installs @playwright/test 1.64.1
npx playwright install chromium
npx playwright test               # L100: 6 lab + 9 tryIt; L200: 5 lab + 7 tryIt; L300: 5 device tests
SIM_URL=https://python-simulator.usermbit.org/staging/simulator.html npx playwright test  # other build (macOS zsh)
```
Windows (PowerShell): the same `npm`/`npx` commands, one per line; for another build:
```powershell
$env:SIM_URL = "https://python-simulator.usermbit.org/staging/simulator.html"; npx playwright test
```
Install Node 24 first: macOS `brew install node@24` (keg-only: add `$(brew --prefix node@24)/bin`
to PATH); Windows `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0` (pinned: the LTS id moves to
Node 26 once 26 becomes LTS; see `../../shared/WORKSTATION-SETUP.md`). Playwright supports macOS 14+ and
Windows 11+. CI runs this harness on `ubuntu-latest`, `macos-latest` and `windows-latest`
(`--with-deps` only on Linux).

Offline checks run in the sandbox: `npm run check` (`node --check` on all JS files plus
`node host-bridge.check.js`) and, for L100, a fetch of `serve.js` (GET / → 200, other → 404).

## Known risks
* The embedding API and URLs are "not yet stable" (simulator README); a URL or
  message change breaks this harness, not the labs.
* Timing: button clicks hold 150 ms; the labs poll every 20–200 ms.
* Two simulators in one page double the WASM download and CPU; the default 120 s timeout is kept.
* Whether `set_value` for `temperature` accepts 30 depends on the simulator's
  range for that sensor (not documented in the README).
