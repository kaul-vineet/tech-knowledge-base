# L600 #04 An offline-first micro:bit sensor fleet — evidence

Checked 2026-10-30. Primary sources only (official docs, specs/RFCs, papers, maintained OSS). Every number in the
lesson and the question bank is recomputed by `integrated/research/checks_04.py` (prints OK, exit 0); the run
values come from `integrated/labs/L600/04-microbit-sensor-fleet` (seed 4, CPython 3.12, Linux).

## Research questions
1. What may a micro:bit radio message carry, and what happens to a longer one or to a full queue?
2. What clock does a micro:bit have after a reset, and can it identify a reading?
3. Which CRDT shape lets replicas sync small deltas over lossy links and still converge?
4. How does a time-series store treat two points with the same key and timestamp?
5. How should an HTTP API announce that a version is deprecated and when it goes away?
6. What does sync cost in battery, using the microbit topic's own model?

## Sources kept (score /12: implementable, current, authoritative, open, transferable, right depth)
| # | Source | URL | Score | Used for | Verified how |
|---|---|---|---|---|---|
| 1 | MicroPython for micro:bit V2 docs: Radio | https://microbit-micropython.readthedocs.io/en/v2-docs/radio.html | 12 | length default 32, "up to 251 bytes long (254 - 3 bytes for S0, LENGTH and S1 preamble)"; queue default 3; "If the queue is full, new messages are ignored"; radio.off() saves power | fetched 2026-10-30; matches the microbit topic's stub (`_DEFAULTS`, `_RANGES`) and L200 evidence (sender truncates, modradio.cpp) |
| 2 | MicroPython docs: microbit module | https://microbit-micropython.readthedocs.io/en/v2-docs/microbit.html | 12 | `running_time()`: "milliseconds since the board was switched on or restarted" -> wall time built on it steps back after a reboot | fetched 2026-10-30 |
| 3 | MicroPython docs: Power Management V2 | https://microbit-micropython.readthedocs.io/en/v2-docs/power.html | 12 | Deep Sleep wake sources are pins, buttons, UART, timer (no radio) -> devices must start the sync | fetched 2026-10-30 |
| 4 | micro:bit tech site: Power supply | https://tech.microbit.org/hardware/power-supply/ | 11 | 30 mA worst-case on-board budget (BOARD_ON_MA in the reused budget.py) | fetched 2026-10-30 |
| 5 | Energizer E92 datasheet | https://data.energizer.com/pdfs/e92.pdf | 10 | 1,250 mAh (BATTERY_MAH in budget.py) | reused from microbit L300 #14 evidence, not re-fetched |
| 6 | Almeida, Shoker, Baquero: Delta State Replicated Data Types (arXiv 1603.01529; JPDC 111, 2018) | https://arxiv.org/abs/1603.01529 | 11 | delta mutators, anti-entropy over unreliable channels; causal context = version vector + dot cloud | abstract fetched 2026-10-30 |
| 7 | Shapiro et al.: A comprehensive study of CRDTs (INRIA RR-7506, 2011) | https://perso.lip6.fr/Marc.Shapiro/papers/2011/Comprehensive-CRDTs-RR7506-2011-01.pdf | 11 | merge = join (commutative, associative, idempotent); G-Counter/version vector | reused from distributed-systems L400 #18 |
| 8 | Demers et al.: Epidemic algorithms for replicated database maintenance (PODC 1987) | https://www.cis.upenn.edu/~bcpierce/courses/dd/papers/demers-epidemic.pdf | 10 | anti-entropy: "every site regularly chooses another site at random and by exchanging database contents with it resolves any differences"; push-pull | search result + PDF text 2026-10-30 |
| 9 | Kulkarni et al.: Logical Physical Clocks (OPODIS 2014; UB tech report 2014-04) | https://cse.buffalo.edu/tech-reports/2014-04.pdf | 10 | HLC option in ADR 0001; physical time "may cause the timestamps to go backwards" | abstract and intro fetched 2026-10-30 |
| 10 | InfluxDB OSS v2 docs: Handle duplicate data points | https://docs.influxdata.com/influxdb/v2/write-data/best-practices/duplicate-points/ | 9 | same measurement + tag set + timestamp -> "InfluxDB uses the field value of the new point" (the failure lab's LWW-by-timestamp behaviour) | fetched 2026-10-30; used as an `inRealSystems` example only |
| 11 | RFC 9745: The Deprecation HTTP Response Header Field | https://www.rfc-editor.org/rfc/rfc9745.html | 12 | `Deprecation: @<unix seconds>` (Structured Field Date); Sunset must not be earlier | fetched 2026-10-30 |
| 12 | RFC 8594: The Sunset HTTP Header Field | https://www.rfc-editor.org/rfc/rfc8594.html | 12 | Sunset uses an HTTP-date | reused from application-architecture L400 #20 |
| 13 | Ian Robinson: Consumer-Driven Contracts (martinfowler.com) and Pact docs | https://martinfowler.com/articles/consumerDrivenContracts.html | 10 | consumer contracts verified by the provider | reused from application-architecture L300 #14 |
| 14 | Michael Nygard: Documenting Architecture Decisions | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | 10 | ADR format (Title, Status, Context, Decision, Consequences) | reused from microbit/app-arch capstones |

Dropped: blog posts on "IoT time-series design" (secondary, no runnable code); vendor IoT-platform pages (marketing);
`ustruct` docs page for micro:bit (fetch returned nothing) -> the firmware packs bytes with shifts instead of struct.

## What was verified by running code here
- `python run_project.py` -> 12/12 PASS, exit 0 (seed 4). `--inject wallclock-lww` -> FAIL 9/12 (1,421 lost),
  `--inject oversize-frame` -> FAIL 4/12 (14,082 lost), `--inject schema-drift` -> FAIL 5/12 (2,880 lost). Exit 1 each.
- `python -m unittest discover -s tests -t .` -> all tests OK (see the lab README for the count and timing);
  `FLEET_STORE=lww` makes `test_failure_lab.test_no_reading_lost_under_clock_skew` fail; `BUILD_TARGET=mine`
  makes `test_build_task` fail on the shipped 32-byte firmware.
- Simulated time throughout (the stub clock); no wall-clock assertions, so nothing is timing-flaky.

## Assumptions (labelled in code)
- ACK_WAIT_MS = 50 ms radio-on window per attempt; no airtime, collision or range model in the stub.
- Board Deep Sleep floor 0.5 mA (budget.py's conservative assumption) dominates every battery figure.
- Loss is per delivery and independent of frame length in the stub; real packet loss grows with length.
- Flash persistence is a dict passed by the harness; on a board it would be a file written with open().

## Not verified here (pendingCi)
- The firmware in the official micro:bit V2 simulator (micropython-microbit-v2-simulator) or on boards.
- Real radio loss vs frame length, real flash wear from appending a record per minute.
