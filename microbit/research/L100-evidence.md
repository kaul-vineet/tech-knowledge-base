# L100 research evidence — BBC micro:bit (simulator only)

Date: 2026-10-28. Method: questions per lesson → web_search/web_fetch → screen → score (0–2 × 6 criteria, keep ≥ 8) → cross-check each API against ≥ 2 sources (one official).
Score order: implementable / current / authoritative / open / transferable / depth.

## Screened out (all lessons)
| Candidate | Reason | Score |
|---|---|---|
| regentelectronics.com "Micro bit V2: Enhanced Features" | Vendor blog / shop marketing | 4 |
| robocraze.com "Microbit vs Microbit V2" | Vendor blog, no code | 4 |
| microbit-micropython.readthedocs.io/en/latest (1.1.1 docs) | V1-era docs; v2-docs used instead | 7 |
| docs.micropython.org | Generic MicroPython, no micro:bit `microbit` module | 6 |
| deepwiki.com python-editor-v3 simulator pages | Auto-generated secondary summary; used only as a lead, facts re-checked on demo.html/README | 6 |
| microbit.org sensory-toy project | Useful example (was_gesture + audio.play) but duplicate of docs; not needed | 7 |

---

## Lesson 1 — Set up your environment
**Questions**
1. How do I run MicroPython for micro:bit without a board, and which simulator version is used?
2. Where do serial output and the REPL appear, and how are sensors controlled?
3. What differs between V1 and V2 for code that runs in the simulator?

**Kept**
| Source | Score | Why |
|---|---|---|
| Simulator repo README | 2/2/2/2/1/2 = 11 | Official; licence, embed URL, message API, REPL included |
| Python Editor guide (support) | 2/1/2/1/1/2 = 9 | Official how-to: play button, sensor controls, serial Ctrl+C/Ctrl+D |
| New Python Editor page | 1/1/2/1/1/2 = 8 | Official list of simulated features + V1/V2 note (tone partly promotional; facts only) |
| Details of micro:bit V2 | 1/1/2/1/2/2 = 9 | Official V2 feature list |
| MicroPython docs: REPL | 1/2/2/2/1/1 = 9 | REPL concept, 115200 baud (board-oriented) |

**Key facts (with source)**
* Simulator is MIT, embeds as iframe; "The embedding API and URLs are not yet stable"; embed URL `.../v/0.1/simulator.html`; it "provides a simulated micro:bit (including REPL)"; the iframe itself has no serial terminal or sensor UI — https://github.com/microbit-foundation/micropython-microbit-v2-simulator
* Editor simulator: "Tap the play symbol to run the current code and use the controls to simulate different conditions"; serial console: Ctrl+C / Ctrl+D interrupt and restart — https://support.microbit.org/support/solutions/articles/19000135210-python-editor-guide
* Simulated features: "buttons, gestures, light levels, temperature, compass, sound, radio, serial pins and data logging"; "The simulator shows a micro:bit V2 … some code may work on the simulator but not on your physical micro:bit" (V1) — https://microbit.org/new-microbit-python-editor/ (cross-checked: same V1/V2 text in the editor guide)
* Editor needs internet to load, then tolerates unstable connection — same two pages.
* V2 adds speaker, MEMS microphone, touch logo — https://support.microbit.org/support/solutions/articles/19000119052-details-of-micro-bit-v2 ; https://makecode.microbit.org/device/v2
* Simulator repo `lib` last commit: "micro:bit MicroPython 2.1.1" — repo page (inference, see KNOWN-GAPS #4).

## Lesson 2 — The LED display
**Questions**
1. Current API for scroll/show and their blocking behaviour?
2. How to define a custom image and set brightness?
3. Is there a global brightness call in MicroPython?

**Kept**: Display docs (12), Image docs (12), MakeCode set-brightness (9, equivalent only).

**Key facts**
* `display.show(image, delay=400, *, wait=True, loop=False, clear=False)`; `display.scroll(text, delay=150, *, wait=True, loop=False, monospace=False)`; `set_pixel` value 0–9 — https://microbit-micropython.readthedocs.io/en/v2-docs/display.html
* `Image("90009:09090:…")`, ':' ends a row; `fill(value)` 0–9; built-ins read-only (`set_pixel`/`fill` raise) — https://microbit-micropython.readthedocs.io/en/v2-docs/image.html
* Cross-check: both pages agree on the 0–9 brightness range. Display docs list no global brightness function.
* MakeCode `led.setBrightness(0–255)`; "The brightness is not supported in the simulator" — https://makecode.microbit.org/reference/led/set-brightness

## Lesson 3 — Buttons
**Questions**
1. Exact semantics of is_pressed / was_pressed / get_presses?
2. How are button presses injected in the simulator (UI and API)?

**Kept**: Buttons docs (12), Pins docs (10: buttons on pins 5/11, pin_logo), Simulator demo page (10).

**Key facts**
* `is_pressed()` — currently held; `was_pressed()` — pressed since start or last call, clears the state; `get_presses()` — running total, reset to zero — https://microbit-micropython.readthedocs.io/en/v2-docs/button.html
* Simulator ids `buttonA`, `buttonB`, `pinLogo`, `pin0..2`; "Buttons and pins (touch state) have 0 and 1 values" — https://python-simulator.usermbit.org/v/0.1/demo.html + simulator README.
* Pins 5 and 11 have pull-ups for buttons A/B — https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html

## Lesson 4 — Sound
**Questions**
1. Current music API (notation, play, pitch)?
2. Which audio APIs are V2-only (Sound, SoundEffect, speaker) and their parameters?
3. Does the simulator's MicroPython include SoundEffect?

**Kept**: Music docs (12), Audio docs (12), Speaker docs (11), Pins docs (10), micropython-microbit-v2 releases (11).

**Key facts**
* Note format `NOTE[octave][:duration]`, octave/duration carry over, default tick 125 ms at 120 bpm; `music.play(music, pin=pin0, wait=True, loop=False)`; `music.pitch(frequency, duration=-1, pin=pin0, wait=True)`; default output pin 0 + V2 speaker — https://microbit-micropython.readthedocs.io/en/v2-docs/music.html
* `audio.play(Sound.HELLO)` built-in sounds (V2): GIGGLE, HAPPY, HELLO, MYSTERIOUS, SAD, SLIDE, SOARING, SPRING, TWINKLE, YAWN; `audio.SoundEffect(freq_start=500, freq_end=2500, duration=500, vol_start=255, vol_end=0, waveform=WAVEFORM_SQUARE, fx=FX_NONE, shape=SHAPE_LOG)`; constants accessed as `audio.SoundEffect.WAVEFORM_TRIANGLE`; ranges 0–9999 / 0–255 — https://microbit-micropython.readthedocs.io/en/v2-docs/audio.html
* `speaker.off()` "does not disable sound output to an edge connector pin"; `speaker.is_on()` — https://microbit-micropython.readthedocs.io/en/v2-docs/speaker.html
* `pin_logo` is V2, touch-sensitive, `is_touched()` — https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html
* SoundEffect added in v2.1.0-beta.1; out-of-range values raise from v2.1.0; parameter renamed `wave`→`waveform` in beta.2 — https://github.com/microbit-foundation/micropython-microbit-v2/releases (so 2.1.1 in the simulator includes it).
* Cross-check speaker/sound V2: https://makecode.microbit.org/device/v2 (built-in speaker, sound expressions are v2-only).

## Lesson 5 — Sensing temperature and light
**Questions**
1. Return types/ranges of temperature() and read_light_level()?
2. Can both be set in the simulator, under which ids?

**Kept**: microbit module docs (12), Display docs (12), Sensors page (9), Editor guide (9).

**Key facts**
* `microbit.temperature()` → integer °C — https://microbit-micropython.readthedocs.io/en/v2-docs/microbit.html
* `display.read_light_level()` → 0–255, larger = more light, LEDs in reverse-bias — https://microbit-micropython.readthedocs.io/en/v2-docs/display.html
* Temperature sensor is inside the processor, approximates air temperature — https://microbit.org/get-started/features/sensors/
* Simulator ids `temperature`, `lightLevel` (range 0–255) — demo.html + simulator README; editor guide: "temperature sensor, light sensor … simulate the conditions".

## Lesson 6 — Motion and gestures
**Questions**
1. Units and calls for accelerometer axes?
2. Gesture names, current_gesture vs was_gesture, polling requirement?
3. Simulator ids for axes and gestures?

**Kept**: Accelerometer docs (12), Gestures tutorial (11), Simulator demo page (10).

**Key facts**
* Default range ±2000 mg; `get_x/get_y/get_z`, `get_values()` (x, y, z); gestures: up, down, left, right, face up, face down, freefall, 3g, 6g, 8g, shake; `was_gesture(name)` = since last call; "Gestures are not updated in the background … constant calls" — https://microbit-micropython.readthedocs.io/en/v2-docs/accelerometer.html
* Cross-check: same gesture list and `current_gesture()`/`was_gesture("shake")` usage — https://microbit-micropython.readthedocs.io/en/v2-docs/tutorials/gestures.html
* Simulator ids `accelerometerX/Y/Z`, `gesture` — https://python-simulator.usermbit.org/v/0.1/demo.html; `set_value` value may be number or string (python-editor-v3 behaviour, seen via DeepWiki summary; lead only).

## Harness (Playwright)
* Message protocol (flash, set_value, serial_output, request_flash, mute, stop, reset, radio_input/output) — simulator README.
* python-editor-v3 uses Playwright 1.64.1 — https://github.com/microbit-foundation/python-editor-v3 (commit "Update playwright to v1.64.1"). That it embeds `/v/0.1/simulator.html` comes from a DeepWiki summary of its `Simulator.tsx` (lead only; matches the README embed URL).
* Playwright 1.64 current — https://playwright.dev/docs/release-notes

---

## Concepts layer (added 2026-10-28)

Method as above. Worked-example numbers come from `research/concept_examples.py` (output saved in `research/concept_examples.out.txt`), which imports the lab files and `labs/sim_stub`; no number was computed by hand. Word counts measured with `wc -w`: primer 805; notes 579–627 (before the rebalance). After REBALANCE-SPEC: primer 543, notes 238–245; the lab 01 byte count became 895 after concept comments were added to `main.py` (re-run of `concept_examples.py`).

**Questions**
1. Setup: how do editor, simulator iframe, serial and stub connect; what is WebAssembly/postMessage?
2. Display: how are 25 LEDs driven and why is brightness a buffer value?
3. Buttons: level vs edge, bounce, how other platforms expose edges?
4. Sound: how note names map to Hz and ticks to ms?
5. Temperature/light: how to make threshold decisions stable?
6. Motion: what the three axes mean physically; how gestures relate to events?

**Screened out**
| Candidate | Reason | Score |
|---|---|---|
| microbit-sam.github.io/microbit-docs (display) | Unofficial mirror of the Lancaster runtime docs; used the lancaster-university.github.io original | 6 |
| lancaster-university.github.io/microbit-docs/ubit/buttons/ | Fetch returned no content | — |
| Lancaster DAL docs as V2 authority | Written for the V1 runtime; kept only for general mechanics (multiplexing, gesture events), V2 specifics taken from MicroPython v2-docs | (kept at 9 with caveat) |

**Kept (new)**: tech.microbit.org/hardware (8), Lancaster display (9) and accelerometer (9) docs, codal-microbit-v2 (9), MakeCode LED screen (9), MDN postMessage (11), webassembly.org (9), MicroPython machine.Pin (11), Arduino Debounce (9), Wikipedia scientific pitch notation (9), Home Assistant Threshold (9), MDN DeviceMotionEvent (10). Scores: implementable/current/authoritative/open/transferable/depth.

**Key facts with cross-checks**
* Single-board computer with application processor + separate USB interface processor — https://tech.microbit.org/hardware/ (cross-check: V2 hardware spec on https://support.microbit.org/support/solutions/articles/19000119052-details-of-micro-bit-v2).
* CODAL is used by MakeCode and the Foundation Python editors; MIT — https://github.com/lancaster-university/codal-microbit-v2 (cross-check: micropython-microbit-v2 release notes list CODAL updates).
* WebAssembly is a portable, sandboxed binary format — https://webassembly.org/ ; simulator is MicroPython compiled with Emscripten — simulator README.
* postMessage = controlled cross-origin messaging between windows/iframes; targetOrigin `*` discouraged when the target is known — https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage (harness uses `*`; see KNOWN-GAPS).
* 25 LEDs on 12 GPIO pins (3 rows × 9 columns) via multiplexing; refresh every 18 ms (55 Hz); readLightLevel returns 0 on first call; greyscale up to 256 levels — https://lancaster-university.github.io/microbit-docs/ubit/display/ (cross-check: MakeCode screen page says display pins are shared with light sensing; MicroPython display docs: reverse-bias light sensing, 0–255).
* (x, y) coordinates 0–4, display buffer overwritten by show — https://makecode.microbit.org/device/screen (cross-check: MicroPython display/image docs).
* Level vs edge: MicroPython `Pin.irq` with IRQ_FALLING / IRQ_RISING — https://docs.micropython.org/en/latest/library/machine.Pin.html (cross-check: micro:bit Buttons docs semantics).
* Bounce causes spurious transitions; debounce by checking twice within a short time — https://www.arduino.cc/en/Tutorial/BuiltInExamples/Debounce.
* C4 = MIDI 60 = 261.6256 Hz, A4 = 440 Hz (MIDI 69), A5 = 880 Hz — https://en.wikipedia.org/wiki/Scientific_pitch_notation (cross-check: music docs "middle C is c4, concert A (440) is a4"; script output 261.63 Hz).
* Hysteresis = distance past the threshold before state changes — https://www.home-assistant.io/integrations/threshold/.
* Accelerometer milli-g on 3 axes, gesture events incl. SHAKE/FREEFALL, uses I²C, smartphone orientation and airbag examples — https://lancaster-university.github.io/microbit-docs/ubit/accelerometer/ (cross-check: MicroPython accelerometer docs).
* Browser DeviceMotionEvent acceleration in m/s² — https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent.

## Platforms (Mac mini + Windows) and agent assist (added 2026-10-28, PLATFORM-AGENT-SPEC)

Questions: (1) Which install commands give Python 3.12, Node 24 and Ollama on Apple-silicon macOS and Windows 11, with verified package ids? (2) Does Playwright (harness) run on both? (3) Which browsers run the editor/simulator? (4) Does a local OpenAI-compatible endpoint exist at localhost:11434/v1?

Kept (scores in VERIFIED-RESOURCES): Homebrew formula pages (python@3.12, node@24, ollama), winget-pkgs manifests (OpenJS.NodeJS.LTS, Ollama.Ollama), Python docs (Windows install manager, venv), Playwright install page, GitHub runners reference, micro:bit browser requirements, Ollama OpenAI-compat/GPU/Windows/macOS docs, qwen2.5:1.5b model card.
Dropped: winget `Python.Python.3.12` (exists in winget-pkgs, latest manifest seen 3.12.10; python.org now recommends the Python install manager, so it is not the main path); `docs.ollama.com/windows` (fetch returned no content; GitHub `docs/windows.mdx` used instead); MakeCode browser pages (about MakeCode, not the Python Editor).

Key facts:
* `brew install python@3.12` installs `python3.12`; unversioned `python3` symlinks are only in `libexec/bin` — https://formulae.brew.sh/formula/python@3.12. Hence the setup step calls `python3.12`.
* `node@24` is keg-only (not on PATH by default) — https://formulae.brew.sh/formula/node@24.
* Python install manager via `winget install 9NQ7512CXL7T -e --accept-package-agreements`; `py install <tag>`; `py -V:3.12` (the `V:` may be omitted for tags starting with 3) — https://docs.python.org/3/using/windows.html (cross-check: venv docs list `.venv\Scripts\Activate.ps1` and `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`).
* winget id `OpenJS.NodeJS.LTS` ships 24.x (x64 + arm64 MSI) — winget-pkgs manifests; Node 24 also in Playwright's supported list (22/24/26).
* Playwright supports Windows 11+, macOS 14+, Debian/Ubuntu — https://playwright.dev/docs/intro.
* micro:bit editors: Chrome/Edge 126+ recommended on Windows and Apple devices; Firefox 128+ and Safari 17+ do not support WebUSB — https://support.microbit.org/... (cross-check: Python Editor page says "no micro:bit needed" via simulator; MakeCode pages list Safari/Firefox as compatible for MakeCode only).
* `macos-latest` = arm64 (M1, 3 vCPU, 7 GB) and `windows-latest` = x64 — GitHub runners reference.
* Ollama serves an OpenAI-compatible `/v1/chat/completions` at `http://localhost:11434/v1/` — https://docs.ollama.com/api/openai-compatibility (cross-check: Ollama windows.mdx "API will be served on http://localhost:11434").
* Ollama: Metal on Apple silicon; Windows 10 22H2+, NVIDIA driver 551.61+, AMD ROCm v7 or Vulkan; >= 4 GB for the Windows install; macOS 14+ — Ollama docs gpu.mdx / windows.mdx / macos.mdx. Winget `Ollama.Ollama` installer is x64 only (manifest).
* `qwen2.5:1.5b` = 986 MB (Q4_K_M), Apache-2.0 — Ollama library page.

## Update pass (2026-10-28, review F04/F05)
* Windows Python now follows the shared canonical path `winget install -e --id Python.Python.3.12` (winget-pkgs folder
  `manifests/p/Python/Python/3/12`, latest 3.12.10, fetched 2026-10-28) so that every topic uses one recipe
  (`shared/WORKSTATION-SETUP.md`); the Python install manager remains a valid alternative per docs.python.org.
* Windows Node pinned to `OpenJS.NodeJS.LTS --version 24.19.0` (winget-pkgs; review F04).
* Ollama winget manifests fetched 2026-10-28: latest 0.34.2, behind Ollama 0.40.x → Windows uses OllamaSetup.exe.
