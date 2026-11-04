# L200 research evidence — BBC micro:bit (simulator only)

Date: 2026-10-28. Method as L100: questions per lesson → web_search/web_fetch → screen → score
(implementable / current / authoritative / open / transferable / depth, 0–2 each, keep ≥ 8) →
cross-check each API against ≥ 2 sources, one official. Numbers in the concept notes come from
`research/concept_examples_l200.py` (output in `concept_examples_l200.out.txt`).

## Screened out / used only as leads
| Candidate | Reason | Score |
|---|---|---|
| DeepWiki python-editor-v3 "Simulator" + "Simulator Modules" pages | Auto-generated summary. Used only as a lead for `log_output`/`log_delete` messages and "digital and analog input" in the Pins module; neither is in the simulator README, so neither is relied on (KNOWN-GAPS 40, 42) | 6 |
| pc-microbit-extension / pc-microbit-micropython (readthedocs) | Third-party course notes that restate the log docs | 7 |
| MakeCode datalogger reference | Different language/runtime; one equivalents line only | 7 |
| GitHub source of the simulator (`src/board/*.ts`, `microbithal_js.c`), `python-editor-v3/src/device/simulator.ts`, `micropython-microbit-v2/.../modlog.c`, `.../modradio.c` | Could not be fetched (empty responses) — see KNOWN-GAPS 41 | — |

---

## Lesson 7 — Radio between two boards
**Questions**
1. What do `config`, `send`, `receive`, `receive_bytes`, `receive_full` do and what are the defaults?
2. What happens to long messages, a full queue and non-text packets?
3. How do two simulator instances exchange radio packets?

**Kept**
| Source | Score | Why |
|---|---|---|
| MicroPython docs: Radio (v2-docs) | 2/2/2/2/2/2 = 12 | API, defaults, header bytes, ValueError, queue rules |
| Simulator README (radio_output / radio_input) | 2/2/2/2/1/2 = 11 | The documented embedding messages the bridge uses |
| bbcmicrobit/micropython `modradio.cpp` | 2/1/2/2/1/2 = 10 | Truncation to `length`, "radio is not enabled" (V1 port; V2 assumed equal) |
| micro:bit Python Editor reference: Radio | 1/2/2/1/1/1 = 8 | Second official source: groups 0–255, power 0–7, poll in a loop |
| micropython-microbit-v2 releases | 1/2/2/2/1/1 = 9 | "Importing the radio module now turns on the radio automatically" (v2.1.0-beta.1) |

**Key facts**
* `length` default 32, up to 251; `queue` default 3, full queue drops new messages; `channel` 0–83 default 7; `power` 0–7 default 6; `group` 0–255 default 0; `send(str)` = `send_bytes` with `b'\x01\x00\x01'` prepended; `receive()` checks those 3 bytes and raises `ValueError` if conversion fails — https://microbit-micropython.readthedocs.io/en/v2-docs/radio.html
* Cross-check: groups 0–255 and power 0–7 — https://python.microbit.org/v/3/reference/radio
* `radio_output` data is bytes, strings prefixed 0x01 0x00 0x01; `radio_input` "is assumed to be sent to the currently configured radio group" — https://github.com/microbit-foundation/micropython-microbit-v2-simulator
* Sender truncates to `max_len` (configured length); receiver also truncates; `ensure_enabled()` raises `ValueError("radio is not enabled")` — https://github.com/bbcmicrobit/micropython/blob/master/source/microbit/modradio.cpp
* Demo page state shows `radio {"enabled":false,"group":0}` — https://python-simulator.usermbit.org/v/0.1/demo.html

## Lesson 8 — Data logging
**Questions**
1. Exact `log` API: `set_labels`, `add`, timestamps, `set_mirroring`, `delete`, full-log behaviour?
2. What CSV does the runtime produce (timestamp heading, decimals, line ends)?
3. Does the simulator support `log`, and what is the fallback/export path?

**Kept**
| Source | Score | Why |
|---|---|---|
| MicroPython docs: Data Logging V2 | 2/2/2/2/2/2 = 12 | Full API incl. `OSError` 28 |
| micro:bit user guide: Data logging | 1/2/2/1/2/2 = 10 | "Simulated logging … expand the data log module"; time restarts at reset; full vs fast delete |
| Python Editor reference: Data logging | 1/2/2/1/1/1 = 8 | Second official API source, `run_every` example |
| codal-microbit-v2 `MicroBitLog.cpp` | 2/2/2/2/1/2 = 11 | "Time (seconds)" heading, two decimals, comma rows, CRLF on mirror |
| MicroPython docs: microbit module (`run_every`) | 2/2/2/2/1/2 = 11 | An exception in the callback deschedules it |
| MicroPython docs: file system | 2/2/2/2/1/1 = 10 | File fallback: ~30k, modes r/w only (no append), flat |
| RFC 4180 | 1/2/2/2/2/1 = 10 | CSV rules used by `export_csv.py` |
| micropython-microbit-v2 releases | 1/2/2/2/1/1 = 9 | `log` and `run_every` added in v2.1.0-beta.1 (simulator lib is 2.1.1) |

**Key facts**
* `set_labels(*labels, timestamp=log.SECONDS)`; units MILLISECONDS…DAYS or None; new labels add a header row; missing labels → empty field; full → `OSError` 28 ENOSPC; mirroring off by default — https://microbit-micropython.readthedocs.io/en/v2-docs/log.html (cross-check https://python.microbit.org/v/3/reference/data-logging)
* `timeStampHeading = "Time (" + units + ")"`; non-ms units get `"." + 2 digits`; rows joined with ","; mirror sends row + `"\r\n"`; empty rows not written — https://github.com/lancaster-university/codal-microbit-v2/blob/master/source/MicroBitLog.cpp
* "Run the simulator and expand the data log module to view the simulated data" — https://microbit.org/get-started/user-guide/data-logging/
* File system: `open(name, 'w')` overwrites; no append mode listed; ~30k — https://microbit-micropython.readthedocs.io/en/v2-docs/filesystem.html

## Lesson 9 — Pins and PWM
**Questions**
1. Which pins read/write digital, analog, PWM, touch, and what are the value ranges?
2. Default touch modes and pulls?
3. What pin input does the simulator support?

**Kept**: Pins docs (12), Python Editor reference: Pins (8), simulator README (11), demo page (10).

**Key facts**
* `write_analog` 0–1023 (511 = 50 % ≈ 1.65 V); `set_analog_period` min 1 ms, `set_analog_period_microseconds` min 256 µs; `read_analog` 0–1023; edge pins resistive touch by default, logo capacitive; default pulls NO_PULL / PULL_DOWN / PULL_UP for analog / digital / touch reads; V2 display columns on pins 3, 4, 6, 7, 10 — https://microbit-micropython.readthedocs.io/en/v2-docs/pin.html
* Cross-check: pins 0–2 digital 0/1, analog 0–1023, resistive by default, capacitive option on V2 — https://python.microbit.org/v/3/reference/pins
* "Buttons and pins (touch state) have 0 and 1 values. In future, analog values will be supported for pins." — simulator README

## Lesson 10 — I2C sensor
**Questions**
1. `i2c.read/write/scan` signatures, addressing, pins?
2. What error does a missing device raise on V2?
3. A real, documented register map to model?

**Kept**: I2C docs (12), `microbit_i2c.c` source (10: 2/2/2/2/1/1), TI TMP102 datasheet (11: 2/2/2/1/2/2; licence: TI terms, facts only).

**Key facts**
* 7-bit addressing; `read(addr, n, repeat=False)`, `write(addr, buf, repeat=False)`; `scan()`; SCL pin 19, SDA pin 20; V2 has separate I²C lines for motion sensors — https://microbit-micropython.readthedocs.io/en/v2-docs/i2c.html
* read/write error → `mp_raise_OSError(MP_ENODEV)` ("Assume an error means there is no I2C device with addr"); scan covers 0x08–0x77 — https://github.com/microbit-foundation/micropython-microbit-v2/blob/master/src/codal_port/microbit_i2c.c
* TMP102: address 1001000 (0x48) with ADD0 to GND; pointer 00 temp (RO), 01 config, 10 T_LOW, 11 T_HIGH; 12-bit left-justified, 0.0625 °C/LSB, two's complement; 25 °C = 0x190, −25 °C = 0xE70; config power-up 0x60A0; T_HIGH 80 °C, T_LOW 75 °C — https://www.ti.com/lit/ds/symlink/tmp102.pdf

## Lesson 11 — Game state machine
**Questions**
1. A clear, citable definition of a finite state machine and table/enum implementation?
2. Timing: `running_time()` semantics; edge-style inputs (`was_pressed`, `was_gesture`)?

**Kept**: Game Programming Patterns "State" (10: 2/2/1/2/2/1; free web edition), microbit module docs (12), Buttons docs (12), Accelerometer docs (12) — the last three already verified in L100.

**Key facts**
* FSM: fixed set of states, one at a time, inputs/events, transitions; unmatched input ignored; enum + switch is the simplest implementation; concurrent machines when two things vary — https://gameprogrammingpatterns.com/state.html
* `running_time()` returns ms since the board started — https://microbit-micropython.readthedocs.io/en/v2-docs/microbit.html

## Agent assist (lesson 8)
Reuses the L100 sources (Ollama OpenAI compatibility, client/fake server). The vendored fake server got
one more marker rule, `[[MICROBIT-CSV]]`, documented in its header (PLATFORM-AGENT-SPEC B.2).
