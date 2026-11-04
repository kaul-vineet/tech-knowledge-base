# 1. Publish PSF-matched difference alerts through a classifying broker with per-night association

## Status
Accepted (2026-10-29)

## Context
A survey field is imaged twice per night (exposures a and b, 20 minutes apart) for 8 nights against a deep reference. Seeing (PSF σ 1.5–2.1 px) and transparency (×0.75–1.0) change every night. Followers want a small stream of real events (here: a supernova from night 3, the known variable V1, an asteroid). Constraints:
- at most 6 alerts per night;
- at least 80 % real;
- the supernova alerted every night;
- a known variable never sold as a transient;
- every packet schema-valid;
- classification by code only (a local model may explain, never decide).

`alerts.py` (solution) measured three options on the seeded nights:
- A, firehose (every 5σ residual is an alert): 9.8 alerts/night, 46.2 % real.
- B, broker classifies (bogus / known_variable / moving / transient) and drops bogus: 4.2 per night, 88.2 % real.
- C, B plus one alert per object per night, with history (prv_candidates): 3.5 per night, 85.7 % real.

The shipped naive difference (new − reference) gave 58.2 alerts per night at 4.5 % real under option C, because every star left a residual.

## Decision
Use option C on PSF- and flux-matched differences. The reference is blurred to the night's seeing with one Gaussian kernel (Alard & Lupton 1998, simplified), then fitted with new = a·ref + b. Packets follow `schema.py` (ZTF/Rubin-style field names; Avro on the wire, see `alert_avro.py`). The broker's rules (sharpness, sign, known-variable cross-match within 1.5 px, motion between exposures a and b) decide the class. `agent_assist.py` may explain an alert, but its text is published only if it names code's class and every number in it is one of the facts.

## Consequences
- The volume falls by a factor of 17 (58.2 → 3.5 per night) and the real fraction rises from 4.5 % to 85.7 %.
- C trades a little purity against B (85.7 % vs 88.2 %). Deduplication by a 2 px objectId grid merges exposure b into a's object, but an asteroid moves 4 px, so it gets a new objectId every exposure (18 "moving" alerts).
- The broker depends on the known-variable catalogue. tryIt 2: without it, V1 becomes 2 transient alerts. Monitor cross-match availability.
- A single Gaussian kernel assumes round, constant PSFs. Field-varying or elongated PSFs need a spatially varying kernel (full Alard–Lupton) or ZOGY (scaling limit).
- Fitness function: `test_fitness.py` checks ≤ 6/night, ≥ 0.8 real, 0 schema errors, the supernova on nights 3–7, V1 always known_variable, and ≥ 80 % of asteroid detections moving.
