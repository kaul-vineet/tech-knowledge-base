# L300 research evidence — BBC micro:bit (simulator only)

Date: 2026-10-28. Method as L100/L200: questions per lesson → web_search/web_fetch → screen → score
(implementable / current / authoritative / open / transferable / depth, 0–2 each, keep ≥ 8) → cross-check each API
or figure against ≥ 2 sources where possible, one official. Numbers in the concept notes come from
`research/concept_examples_l300.py` (output in `concept_examples_l300.out.txt`), which runs the L300 lab files.

## Screened out / used only as leads
| Candidate | Reason | Score |
|---|---|---|
| DeepWiki "Nordic NRF52840" (renode) and "Power Management" (codal-microbit-v2) | Auto-generated summaries. Used only as a lead for Renode's full nRF52840 peripheral list (rtc1, clock, uart0 IRQ 2, timer1 IRQ 9) because the GitHub page of `nrf52840.repl` rendered only part of the file | 6 |
| yunuskurt.com "Low-power firmware" blog | Background on duty cycles; no micro:bit figures | 6 |
| winget.tech / wingetly.io (Rustlang.Rustup) | Third-party winget indexes; Microsoft Learn's Rust page (official) used instead | 5 |
| support.microbit.org "Power Consumption" (Lancaster report) | V1-era measurements, attachments not readable as text; no V2 board figures | 5 |
| codal-microbit-v2 issues #30/#389 (sleep current) | Discuss display GPIO leakage in sleep, give no current values | 6 |
| raw.githubusercontent.com nrf52840.repl, winget-pkgs Rustup folder, docs.rs embassy-nrf Uarte page | Could not be fetched (empty responses / refused) — KNOWN-GAPS 68, 70 | — |

---

## Lesson 12 — A reliable radio protocol
**Questions**
1. Which checksum can MicroPython compute cheaply, and how do we check our implementation?
2. What is the standard rule for retransmission timeouts and backoff?
3. What do the radio APIs guarantee (queue, length, ValueError) that the protocol must handle?

**Kept**
| Source | Score | Why |
|---|---|---|
| CRC RevEng catalogue, 16-bit | 2/2/2/2/2/1 = 11 | CRC-16/IBM-3740 alias CCITT-FALSE: poly 0x1021, init 0xFFFF, no reflection, check 0x29B1 |
| RFC 6298 | 2/2/2/2/2/0 = 10 | On expiry retransmit and set RTO ← RTO × 2; an upper bound may cap the doubling |
| MicroPython docs: Radio (reused) | 12 | 32-byte default length, queue 3, `send(str)` header, `receive()` ValueError |
| MicroPython docs: microbit module (reused) | 11 | `running_time()` for deadlines |

**Key facts**
* CRC-16/IBM-3740: `width=16 poly=0x1021 init=0xffff refin=false refout=false xorout=0x0000 check=0x29b1`; alias
  CRC-16/CCITT-FALSE — https://reveng.sourceforge.io/crc-catalogue/16.htm. Cross-check: Python's
  `binascii.crc_hqx(data, 0xFFFF)` gives the same values (test_main.py), and the harness JS copy gives 0x29B1 and 0x1DA1.
* "The host MUST set RTO <- RTO * 2 ("back off the timer"). The maximum value ... may be used to provide an upper
  bound to this doubling" — https://www.rfc-editor.org/rfc/rfc6298 (section 5.5). The lab uses 100 → 800 ms.
* Sender cannot distinguish a lost frame from a lost ack (observed: tryIt 2, 4 give-ups, 0 missing).

## Lesson 13 — Non-blocking firmware structure
**Questions**
1. Exactly what do `is_pressed`, `was_pressed`, `get_presses`, `sleep` and `running_time` do?
2. Does MicroPython V2 offer a scheduler of its own?

**Kept**
| Source | Score | Why |
|---|---|---|
| MicroPython docs: microbit module (reused) | 11 | `sleep(n)` waits n ms; `running_time()` ms since start; `run_every` (an exception deschedules the callback) |
| MicroPython docs: Buttons (reused from L100) | 11 | `is_pressed` = now; `was_pressed` = since last call; `get_presses` = count |
| Simulator README (reused) | 11 | `set_value` for buttonA used by the harness clicks |

**Key facts**
* `run_every(callback, days, h, min, s, ms)`; "When an exception is thrown inside the callback function it deschedules
  the function" — https://microbit-micropython.readthedocs.io/en/v2-docs/microbit.html (the lab's scheduler instead
  counts errors and goes to a safe state, so the behaviour is explicit).

## Lesson 14 — Power budgeting (modelled, not measured)
**Questions**
1. What low-power modes does MicroPython V2 expose, and what do they switch off?
2. Which published current figures exist for the board and for the nRF52833?
3. What capacity does a 2 x AAA pack have at a few tens of mA?

**Kept**
| Source | Score | Why |
|---|---|---|
| MicroPython docs: Power Management V2 | 12 | `power.deep_sleep(ms=None, wake_on=None, run_every=True)`, `power.off()`; Deep Sleep uses more than Off; battery: interface MCU sleeps too |
| Python Editor API: power | 8 | Second official source for the same API |
| tech.microbit.org Power supply | 10 | "allow a worst case budget of 30mA for when all on-board peripherals are in use"; V2 regulator 300 mA |
| Power Management Specification 1.0.3 | 10 | On / Deep Sleep / Off; in Deep Sleep the target turns on-board components off and radio data is dropped; nRF52833 System ON vs System OFF |
| nRF52833 PS key features | 11 | 52 µA/MHz CoreMark from flash, 1.5 µA System ON + RTC, 0.6 µA System OFF, 4.9 mA TX 0 dBm, 4.6 mA RX |
| Energizer E92 datasheet, manufacturer copy https://data.energizer.com/pdfs/e92.pdf (form EBC-1103-M, read 2026-10-28) | 9 | Alkaline Zn/MnO2, 1.5 V, LR03; "Milliamp-Hours Capacity, Continuous discharge to 0.8 volts at 21°C" as a chart (no printed mAh value in the text layer) |
| (one-line equivalent) Older revision EBC-1103I via a distributor copy (farnell.com) | 6 | The printed figure the model uses: "1,250 mAh (to 0.8 volts) (Rated capacity at 25 mA continuous drain.)" — not re-read on the manufacturer site (KNOWN-GAPS 63) |

**Key facts and labels**
* 30 mA → UPPER BOUND (budget, not a measurement). 1.5 µA → CHIP ONLY. 3.3 mA CPU = 52 µA/MHz × 64 MHz → CHIP ONLY.
  20 ms per wake-up → ASSUMPTION. No official micro:bit V2 **board** Deep Sleep current was found (KNOWN-GAPS 63);
  the Power Management Specification 1.0.3 lists what is off in Deep Sleep but gives no currents. Update pass (R3-19):
  the model now uses an assumed BOARD SLEEP FLOOR of 0.5 mA (conservative, headline) to 0.05 mA; 1.5 µA is kept only
  as `chip_only_bound_h`.
* Model results (one simulated hour): always-on 41.7 h; Deep Sleep at fixed 100 ms 195.3 h (board floor 0.5 mA;
  208.3 h on the chip floor); adaptive **2,158.3 h board estimate (range 2,158.3–9,588.4 h)**, chip-only bound
  15,244.7 h (483 wake-ups, averaged over exactly 3,600,000 ms; before the 2026-10-30 fix the final 8 s sleep
  overshot the hour and gave 2,158.9 / 9,600.5 / 15,275.4 h); chip-only always-on 158.2 h.

## Lesson 15 — A serial gateway to the PC
**Questions**
1. Current paho-mqtt version and its 2.x API change?
2. Current Mosquitto version and install commands on macOS and Windows?
3. pyserial version for the optional real-board path?

**Kept**
| Source | Score | Why |
|---|---|---|
| paho-mqtt on PyPI | 2/2/2/2/2/1 = 11 | 2.1.0 (2024-04-29); `mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)`; `loop_start()`; QoS 1 `on_publish` after PUBACK; `wait_for_publish()`; EPL-2.0 OR BSD-3-Clause |
| mosquitto.org download | 10 | 2.1.2; `brew install mosquitto`; Windows x64 installer; Ubuntu/Debian packages |
| Homebrew formula mosquitto | 9 | 2.1.2 bottle for Apple Silicon; `brew services start mosquitto` |
| winget-pkgs EclipseFoundation.Mosquitto | 9 | Manifest folder lists 2.1.2 (newest) |
| pyserial on PyPI | 9 | 3.5 (2020-11-22), BSD |
| CRC RevEng (reused) | 11 | Same CRC as lesson 12 |

**Key facts**
* "Callbacks API is versioned ... CallbackAPIVersion.VERSION1 ... deprecated and will be removed in paho-mqtt version
  3.0" — https://pypi.org/project/paho-mqtt/. Pin: `pip install paho-mqtt==2.1.0`.

## Lesson 16 — Close-sibling low-level code (Rust/Embassy, Renode)
**Questions**
1. Does Renode model the nRF52833? If not, how close is its nRF52840 model (addresses, IRQs, memory, UART mode)?
2. Which register offsets/values start TIMER1 periodically and drive UART0 on the nRF52833? Which pins does the
   micro:bit V2 use for the target UART?
3. Current Embassy crate versions and the `#[interrupt]` pattern for a user ISR?
4. How are Rust and Renode installed on macOS arm64 and Windows?

**Kept**
| Source | Score | Why |
|---|---|---|
| Renode platforms/cpus listing | 11 | Only `nrf52840.repl`; no nRF52833 platform |
| Renode nrf52840.repl (partial) + NRF52840.robot | 9 / 11 | `timer1: Timers.NRF52840_Timer @ sysbus 0x40009000`; robot tests override `uart0: easyDMA: false` for UART |
| Renode issue #1014 | 8 | Stock repl sets easyDMA true; legacy UART firmware hangs (Renode 1.17.0) |
| Renode releases | 11 | 1.17.0 (2026-09-07): linux-portable.tar.gz, osx-arm64-portable.dmg, setup.exe, windows-portable.zip |
| nRF52833 PS TIMER / UART / Memory | 12 / 12 / 12 | TIMER1 0x40009000, offsets 0x000/0x00C/0x140/0x200/0x304/0x504/0x508/0x510/0x540; UART0 0x40002000, ENABLE=4, PSEL.TXD 0x50C, TXD 0x51C, EVENTS_TXDRDY 0x11C, BAUDRATE 0x524 (115200 = 0x01D7E000); 512 kB flash, 128 kB RAM; TIMER1 ID 9, UARTE0 ID 2 |
| tech.microbit.org schematic V2 pinmap | 10 | P0.06 UART_INT_RX (= target TX), P1.08 UART_INT_TX (= target RX) |
| embassy-nrf docs.rs + Embassy examples (Cargo.toml, multiprio.rs) | 10 / 10 | embassy-nrf 0.11.0, `time-driver-rtc1`; executor 0.10.0 `platform-cortex-m`; `use embassy_nrf::interrupt; #[interrupt] unsafe fn ...`; `InterruptExt::set_priority(Priority::P6)` |
| rustup.rs, Homebrew rustup, Microsoft Learn Rust setup | 9 / 9 / 9 | `brew install rustup` (keg-only, 1.29.2); Windows `winget install Rustlang.Rustup` + MSVC build tools |

**Honesty check ("is the sibling honest?")** Same Cortex-M4F core family; TIMER1 at 0x40009000 and UART0 at
0x40002000 on both (nRF52833 PS instantiation table vs Renode repl/DeepWiki lead); IRQ numbers equal the peripheral
IDs on both. Differences stated in the lab README: memory size, extra 840 peripherals, no micro:bit board devices,
virtual timing, legacy-UART override. The lab claims only "builds for the nRF52833 and runs on Renode's nRF52840
model", never "tested on a micro:bit".

## Cross-topic checks
* distributed-systems L200 #8 "At-least-once messaging: ack, visibility timeout, redelivery, dead letters" and L100 #4
  "Retries with exponential backoff, jitter and a retry budget" (titles read from its L100/L200 JSON) → lesson 12 `seeAlso`.
* application-architecture L200 #9 "Event-driven integration: outbox, bus and AsyncAPI" → lesson 15 `seeAlso`.
* simulation L200 #7 "Input modelling: fit service times and check the fit" → lesson 14 `seeAlso`.
