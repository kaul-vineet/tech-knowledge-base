# ADR 0019: SipHash-2-4 tags with per-device keys and counters; the gateway is the trust boundary

## Status
Accepted (2026-10-28) for the classroom threat model. Proposed, not accepted, for anything with a
safety or privacy impact: those need a hardware-backed stack (see Consequences).

## Context
micro:bit radio frames are broadcast and anyone in range with another micro:bit can record and send
them. The L300 frames carry a CRC-16, which detects noise only. micro:bit MicroPython documents no
hashlib/hmac/cryptolib module, so any MAC on the board must be written in Python. Threat model:
a curious student with a second micro:bit who replays or forges readings (a fake 45 C reading raises
a false TEMP_HIGH). Constraints: frames fit the radio (length up to 251 bytes; we configure 64);
no forged or replayed frame may pass the gateway; reordering by the radio must not drop genuine frames.
The lab measured (`attacks.py`, seed 19, 3 devices x 60 frames, loss 10 %, dup 5 %, reorder 10 %):

* CRC only (`verifier.py`): 20/20 forgeries and 18/20 replays accepted.
* Toy keyed checksum (CRC-16 over key + message) with the replay window: the attacker recovered the
  16-bit CRC state from 2 recorded frames by trying 65,536 values; 19/20 forgeries accepted, and the
  forged counters pushed the window ahead so 18 genuine frames were rejected (140 of 158 intact).
* SipHash-2-4 (64-bit tag, 128-bit per-device key) + 64-counter window (`solution.py`): 0 forgeries,
  0 replays, 160 of 160 intact genuine frames accepted. Cost: 10 SipRounds (140 64-bit operations) and
  17 extra bytes per frame in hex; time on the board is not measured yet.

## Decision
We will tag every radio frame with SipHash-2-4 under a per-device random 128-bit key, include a
per-device counter that is persisted in blocks of 100 (one flash write per 100 frames), and verify at
the gateway in the order format -> known device -> MAC (constant-time compare) -> replay window, so only
authenticated frames move the window. The gateway strips the tag and is the only component that trusts
radio data; the toy keyed checksum may only be used, labelled NOT cryptographically secure, to keep a
neighbouring class's boards out. `test_fitness.py` keeps it true over 5 seeds.

## Consequences
* No confidentiality: readings are still readable on the air (add encryption only with a vetted cipher).
* Keys sit in the device's flash file system, which anyone with the board and a USB cable can read:
  physical access defeats this design. Key provisioning and rotation are manual.
* A 64-bit tag allows blind forgery with probability 2^-64 per try; the window size trades reordering
  tolerance against state per device. MicroPython speed of 64-bit arithmetic is unmeasured (pendingCi).
