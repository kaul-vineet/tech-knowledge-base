# L500 evidence — micro:bit theory companion (lessons 23-27) and assessment pack

Retrieved 2026-10-30 with web_search / web_fetch. Scores: implementable, current, authoritative, open, transferable,
right depth (0-2 each). Numbers in the lessons come from `labs/L500/*/foundations*.py` (real output, quoted as
`checkOutput`) and are re-verified by `research/l500_checks.py`.

## Lesson 23 — Foundations I: digital electronics and signals
**Questions.** 1. What exactly do the labs assume about signed registers, LED current, ADC steps and PWM? 2. Can every
figure be re-derived from definitions and checked against the stub and the lab code? 3. Why does lesson 14 print
9,600.5 h when its inputs give about 9,588 h?
**Sources.** Kept: MicroPython pin docs (write_analog 0-1023, read_analog; reused from L200), micro:bit power-supply page
(30 mA budget; reused from L300). The derivations are standard (definitions, KVL, uniform distribution, Fourier series)
and are proved in the lesson rather than cited. Dropped: vendor application notes on LED resistors (product-specific).
**Key facts.** Lab 10 decodes a 12-bit two's-complement value (`decode_temp`), so the check compares it with the generic
decoder for all 4,096 patterns. Lab 14: `budget.run_design()` looped `while running_time() < run_ms`; the last 8 s
Deep Sleep started at 3,599,400 ms, so the clock ended at 3,607,400 ms and the average was taken over that. Inputs over
exactly one hour give 0.13037 mA and 9,588.4 h; over 3,607,400 ms, 9,600.5 h. Fixed by clipping to `run_ms`; regression
test added; all downstream figures updated (KNOWN-GAPS 96).

## Lesson 24 — Foundations II: sampling and signal processing
**Questions.** 1. What is the precise statement of the sampling theorem and where is it first stated in this form?
2. What does aliasing look like on micro:bit light data? 3. What are the exact noise and lag trade-offs of MA vs EMA?
**Sources.** Kept: Shannon 1949, Proc. IRE 37(1):10-21 (IEEE Xplore 1697831; Theorem 1 text seen in the 1998 reprint's
search extract: "If a function f(t) contains no frequencies higher than W cps, it is completely determined by giving its
ordinates at a series of points spaced 1/2W seconds apart") — score 10 (closed access lowers "open"). Dropped: Wikipedia
(secondary), blog derivations (no primary evidence).
**Key facts.** Mains flicker at 100 Hz is illustrative (twice 50 Hz), not measured. Traces are seeded synthetic data
through the stub's `inject_light_level`/`inject_axes` and read back through the real API names.

## Lesson 25 — Foundations III: control and real-time theory
**Questions.** 1. When is a P loop on a first-order plant stable, and what error remains? 2. What exactly do Liu & Layland
prove, under which assumptions, and does lesson 13 meet them? 3. Which errors does lesson 12's CRC-16 provably catch?
**Sources.** Kept: Liu & Layland 1973, J. ACM 20(1):46-61, DOI 10.1145/321738.321743 (dblp record; abstract read in
search extracts: fixed-priority bound "as low as 70 percent", deadline-driven scheduling reaches full utilisation) —
score 10. CRC RevEng catalogue (reused: CCITT-FALSE parameters and check 0x29B1). Dropped: textbook-style lecture
notes (licence unclear; the proofs are given in full or sketched in the lesson).
**Key facts.** Lesson 13 tasks (budget/period): button 5/20, sensor 20/1000, display 10/100 ms → U = 0.37. The scheduler
is cooperative, so the RM preemption assumption is violated: worst button response 24 ms. The heater plant is an
assumption (tau 60 s, gain 20 C); it is driven through the stub's `pin0.write_analog`.

## Lesson 26 — Ethics: classroom data, children's privacy, e-waste, accessibility
**Questions.** 1. Which professional-code principles and which children's-data rules apply to a classroom sensor network
(UK and India, policy level)? 2. What is the scale of e-waste and what do our firmware choices change? 3. What
accessibility barriers does the micro:bit itself present, and what does its maker recommend?
**Sources (kept, score).** ACM Code 2018 (11): 1.1 sustainability text and 1.2 "consequences of data aggregation" read.
IEEE Code 7.8 (11): item 1 incl. "sustainable development practices" and "protect the privacy of others". ICO
Children's code standards page (11): 15 standards listed incl. 8 Data minimisation and 14 Connected toys and devices;
page notes review after the Data (Use and Access) Act 2025; transitional page: issued 12 Aug 2020, conform by 2 Sep 2021.
DPDP Act 2023 Gazette copy on meity.gov.in (11) and its s.9 text (verbatim in several readers; consistent): verifiable
parental consent; no detrimental processing; no tracking/behavioural monitoring/targeted ads at children; exemptions as
prescribed. PIB 14 Nov 2025 (9): Rules notified, 18-month phased timeline, verifiable consent with limited exemptions
(healthcare, education, real-time safety). UN CRC GC No. 25 (10). Global E-waste Monitor 2024 (11): 62 Mt (2022),
22.3 % documented collected/recycled, 82 Mt projected 2030. WEEE Directive 2012/19/EU (10). micro:bit hardware
accessibility statement and visual-impairment guide (11): barrier groups; Bluetooth pairing and compass calibration need
sight; Python Editor keyboard and screen-reader support. WCAG 2.2 (12): Recommendation 5 Oct 2023.
**Dropped.** DPDP commentary sites (secondary; used only to find the official text and the commencement phases).

## Lesson 27 — Reading seminar
**Questions.** 1. Are the two papers' bibliographic records and URLs correct? 2. Can we summarise them without
reproducing text? 3. Which assumption in each is most relevant to the labs?
**Sources.** Shannon 1949 (IEEE Xplore 1697831; DOI listed by Scilit and INSPIRE; 1998 reprint 659497). Liu & Layland
1973 (dblp; DOI 10.1145/321738.321743). DOI landing pages could not be fetched by the tool (KNOWN-GAPS 99). Course-hosted
PDFs exist (e.g. university course pages) but carry no licence statement and are not linked.

## Assessment pack
ABET EAC 2025-2026 Criterion 3 outcomes 1-7 and CAC 2025-2026 outcomes 1-5 (+ CS 6) read on abet.org; CS2023's 17
knowledge areas read on csed.acm.org. The 14-week plan is this topic's proposal (no week plan exists in `kb/`).
