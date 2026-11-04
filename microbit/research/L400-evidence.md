# L400 research evidence — BBC micro:bit (simulator only)

Date: 2026-10-28. Same method as L100–L300: implementation questions per lesson → web_search / web_fetch →
screen → score (implementable / current / authoritative / open / transferable / depth, 0–2 each, keep ≥ 8) →
cross-check facts against ≥ 2 sources where possible, one official. Every number in the L400 concept notes
comes from code that ran: `research/concept_examples_l400.py` (output `concept_examples_l400.out.txt`).
Reused from earlier levels (already scored there): MicroPython radio/machine docs, RFC 6298, CRC RevEng,
paho-mqtt/Mosquitto pages, Ollama OpenAI compatibility.

## Screened out / leads only
| Candidate | Reason | Score |
|---|---|---|
| Vendor IoT device-twin / device-management pages (cloud providers) | Product pages; the idea is kept as a one-line equivalent only | 5 |
| Blog posts on "LLM guardrails for IoT" | No runnable code, no primary evidence | 4 |
| RFC 4303 §3.4.3 full text | Only the table of contents and §2.2 were retrieved (page truncated); the window details in the lab are our own design, the RFC is cited for the anti-replay service and the counter rule | — |
| The LPC1768 guide itself | Not present in the workspace; its capstone pattern ("deterministic code decides, the AI explains") is taken from PLATFORM-AGENT-SPEC.md | — |

---

## Lesson 17 — Edge-to-cloud architecture
**Questions:** What does the radio do when its receive queue is full? Can micro:bit MicroPython use BLE for
user data? What does MQTT QoS 1 promise? How do we record and guard a decision?

| Source | Score | Why |
|---|---|---|
| MicroPython docs: Radio | 2/2/2/2/2/2 = 12 | "If the queue is full, new messages are ignored"; queue default 3; length up to 251 (254 − 3) |
| MicroPython docs: Bluetooth | 2/2/2/2/1/1 = 10 | V2: "Currently the only implemented feature is BLE flashing" → option C not measurable |
| OASIS MQTT 5.0 | 2/2/2/2/2/1 = 11 | QoS 0/1/2 definitions ("at least once … duplicates can occur"); topic filters |
| Nygard, Documenting Architecture Decisions | 2/1/2/2/2/1 = 10 | ADR sections: Title, Context, Decision, Status, Consequences |
| Python docs: sqlite3 | 2/2/2/2/2/1 = 11 | `?` placeholders against SQL injection; `:memory:` |

**Key facts:** queue overflow drops new frames (radio docs) → reproduced in the stub (`Endpoint.dropped`).
Measured: lock-step 6 boards 160/180; fixed 180/180, p95 153 ms; 24 boards queue-only 151/480 vs jitter-only 480/480.
The 32-byte default length overflowed after ~1,000 s in lab 20's run (seq ≥ 1000, t ≥ 1,000,000 ms).

## Lesson 18 — Device fleet management
**Questions:** How does a board identify itself? Where can it persist last-good config? What is a canary
rollout and when do you halt it?

| Source | Score | Why |
|---|---|---|
| MicroPython docs: machine (`unique_id()`) | 2/2/2/2/1/1 = 10 | "Returns a byte string with a unique identifier of a board" |
| MicroPython docs: file system | 2/2/2/2/1/1 = 10 | ~30 kB, `open()`/`write()`, data lost on re-flash |
| Google SRE Workbook ch. 16, Canarying Releases | 2/2/2/2/2/2 = 12 | "partial and time-limited deployment … and its evaluation"; roll back when the canary is bad; one canary at a time |

**Key facts:** one-phase push: 12,086 unacked device-ticks, 5 devices deaf; staged two-phase: 0 and 1.
False rollbacks appear with a single A report or a 300 ms probation at 30 % loss (tryIt).

## Lesson 19 — Securing constrained devices
**Questions:** Which hash/MAC modules does micro:bit MicroPython ship? Which MAC fits short frames and pure
Python? How do counters stop replays without losing reordered frames?

| Source | Score | Why |
|---|---|---|
| micro:bit MicroPython docs index (module list) | 2/2/2/2/1/1 = 10 | Lists no hashlib, hmac or cryptolib module (absence checked by reading the index) |
| Aumasson & Bernstein 2012, SipHash paper | 2/2/2/2/2/2 = 12 | SipHash-2-4 as PRF and MAC; 128-bit key, 64-bit tag; 2^(s−64) blind forgery; 14 ops per SipRound |
| veorq/SipHash (reference code + vectors.h) | 2/2/2/2/2/1 = 11 | CC0/MIT/Apache-2.0; vectors 0,1,2,15,63 used in test_main; README: usable as a MAC |
| RFC 4303 (IPsec ESP) | 2/1/2/2/2/1 = 10 | Anti-replay service; per-SA counter increments and must not cycle |
| Python docs: hmac.compare_digest | 2/2/2/2/2/1 = 11 | Constant-time comparison for tags |

**Key facts:** SipHash-2-4(key 00..0f, msg 00..0e) = a129ca6149be45e5 (paper/vectors.h; our code matches).
CRC-16 over key + msg = CRC continued from crc16(key): a 16-bit state, recovered in 65,536 trials (attacks.py).
Attack results: CRC 20/20 forged; toy 19/20 forged and 18 genuine lost; SipHash 0/0, 160/160 genuine.
Not found: any statement of MicroPython big-integer speed on the nRF52833 → pending-ci measurement.

## Lesson 20 — Digital twin
**Questions:** What counts as a digital twin? How do you detect small persistent shifts with few false alarms?

| Source | Score | Why |
|---|---|---|
| NIST IR 8356 (final, Feb 2025) | 2/2/2/2/1/1 = 10 | Definition: electronic representation of real-world entities and their state transitions |
| NIST/SEMATECH e-Handbook 6.3.2.3 CUSUM | 2/2/2/2/2/2 = 12 | Tabular S_hi/S_lo; k = half the shift, h ≈ 4–5 rule of thumb; better than Shewhart for shifts ≤ 2σ |

**Key facts:** 2σ per window: 13 false alarms / 80 per 1,000; 3σ: 3 / 12; CUSUM K = 0.75, H = 5: 2 / 0.
K = 0.5 gave up to 7 per 1,000 on a 4 % link (skewed binomial) → K = 0.75 chosen on evidence.

## Lesson 21 — Local AI at the edge gateway
**Questions:** How do we connect to a local model? How do we prove a model cannot change alarms?

| Source | Score | Why |
|---|---|---|
| Ollama OpenAI compatibility (reused) | 2/2/1/2/2/1 = 10 | Local endpoint `/v1/chat/completions` |
| Python docs: hmac (reused from lesson 19) | 11 | Constant-time comparison; the frozen record uses Python's standard hashlib.sha256 |

**Key facts (measured):** model decides 195/200 changed; model may act 17/200 and the injection cleared TEMP_HIGH;
explain-only 0/200, 17 published. The proof is a test (digest equality), not a prompt.

## Capstone
| Source | Score | Why |
|---|---|---|
| Prometheus exposition formats | 2/2/2/2/2/1 = 11 | Text format `# HELP`/`# TYPE`/`name{labels} value`; Prometheus 3 requires a valid Content-Type |
| Catalog entries: Apache Superset, Grafana OSS, Prometheus | (catalog) | CSV upload; Grafana has no CSV source in core; Prometheus + promtool |

**Key facts:** scorecard PASS 10/10 (seed 22) and PASS (seed 23); 3,599/3,600 stored; 0 attacker readings stored.
