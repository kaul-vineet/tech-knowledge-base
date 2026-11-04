# Concept: authenticating radio frames on a board with no crypto library

## Why it matters
micro:bit radio is a broadcast. Any other micro:bit on the same channel and group can record frames
and send its own. The L300 frames carry a CRC-16, and a CRC detects noise, not people: anyone can
compute it. One forged "45 C" frame raises a false TEMP_HIGH. A replayed frame from yesterday looks
like today's reading. The gateway feeds the broker, the store, the alarms and the local model, so
whatever it lets through becomes truth.

## Mental model
**A sealed, numbered note.** Each board signs its note with a secret stamp only it and the gateway
share (the MAC). It also writes a number that never repeats (the counter). The gateway is the
**trust boundary**. It checks the stamp, then checks it has not seen that number, and passes on only
notes that pass both checks.

```
board: body = dev:ctr:payload   tag = SipHash-2-4(key_dev, body)   frame = body:tag
gateway: known dev? -> tag == SipHash(key_dev, body)? (constant-time) -> ctr fresh in 64-wide window?
          no -> reject + JSON log        yes -> slide window, publish (only now)
```

## Design space
First check what the platform offers. The micro:bit MicroPython documentation lists no hashlib, hmac
or cryptolib module, so a MAC on the board must be written in Python. The honest options:
- **CRC only.** Integrity against noise; no authentication.
- **A tiny keyed checksum.** CRC-16 over key + message. It is linear, so the 128-bit key collapses into a
  16-bit CRC state. One recorded frame reveals that state after at most 65,536 trials. Use it only
  against accidents (a neighbouring class on the same group), and label it **NOT cryptographically secure**.
- **SipHash-2-4.** The authors designed this keyed PRF as a MAC for short inputs: a 128-bit key, a
  64-bit tag, and only add, rotate and XOR. It runs in pure Python, and the lab checks it against the
  reference test vectors. Its MicroPython speed is not measured yet.
- **Authenticate at the gateway only.** That is what every option above does on the receiving side.
  The board cannot verify, but the gateway can, and it is the trust boundary.
- **Replay protection.** A per-device counter that never repeats, persisted in blocks (one flash write
  per 100 frames), plus a sliding window at the gateway like IPsec ESP's anti-replay window. Reordering
  inside the window is accepted; duplicates and old frames are rejected.

## How to decide
The threat model is a student with a second board who records, replays and forges. The constraints:
0 forged or replayed frames accepted, every intact genuine frame accepted despite reordering, and a
frame that fits the radio length. The lab ran the same seeded attack (`attacks.py`: 3 boards × 60
frames, 10 % loss, 5 % duplication, 10 % reordering; Eve replays 20 frames and forges 20):

| Option | Forged accepted | Replays accepted | Genuine accepted / intact |
|---|---|---|---|
| CRC only | 20/20 | 18/20 | 158/158 |
| Toy keyed checksum + window | 19/20 | 0 | 140/158 |
| SipHash-2-4 + window | 0 | 0 | 160/160 |

The toy option is worse than it looks. Its forged counters moved the window ahead, so 18 genuine frames
were then rejected: forgery became denial of service. The order of checks matters for the same reason.
Move the replay check before the MAC check (tryIt) and SipHash still stops every forgery, but genuine
acceptance drops to 143/160. The cost of SipHash is 10 SipRounds (140 64-bit operations) and 17 more
bytes per frame in hex, so the radio length becomes 64.

## Failure modes at scale
- **Physical access.** Keys sit in the board's file system, and USB access reads them. The signal is
  forged frames that pass the MAC from one device; the fix is a new key for that device only.
- **Counter resets.** A board without persisted counters restarts at 1 and is rejected as a replay.
  The signal is a burst of `replay` rejects right after boot.
- **CPU per frame.** Unknown in MicroPython: big integers on a 32-bit core. Measure in the simulator
  before raising the sample rate.

## Common mistakes
- Calling a keyed checksum "secure" because it has a key.
- Comparing tags with `==` instead of `hmac.compare_digest`.
- Letting unauthenticated frames change state: counters, windows or the relay's dedupe.
