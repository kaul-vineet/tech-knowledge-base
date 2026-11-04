# Concept: a reliable link on top of a lossy radio

## Why it matters
Lesson 7's protocol works on a quiet desk. In a busy room packets are lost, duplicated, reordered or damaged, and nothing tells the sender. A logger that silently drops readings is worse than one that crashes: you trust the gaps.

## Mental model
**Registered post.** Every letter has a number and a seal (checksum). The receiver signs for each one (ack). If no signature comes back in time, the sender posts a copy (retransmit), waiting longer each time (backoff). The receiver files each number once and only signs again for copies.

```
A: D:7:r7:CRC ──X (lost)
A: (100 ms, no ack) D:7:r7:CRC ───────► B: deliver r7, expected=8
A: ◄─────────────────────────────────── B: A:7:CRC
A: (late copy of D:7 arrives) ─────────► B: 7 < 8 → duplicate: ack again, do not deliver
```

## How it works
1. **Sequence number and checksum on every frame.** `encode()` appends CRC-16/CCITT-FALSE over `kind:seq:payload`; `decode()` returns `None` for a wrong CRC, so one flipped bit is a counted rejection, not a wrong reading → see lab step 3
2. **Silence is the failure.** Fire-and-forget increments `tx` and moves on; only the receiver could notice the hole, and it does not → see lab step 2
3. **Ack and retransmit (stop-and-wait ARQ).** One frame in flight; `pump()` resends it after the deadline, doubling the timeout up to 800 ms → see lab step 4
4. **Bounded retries.** After `MAX_TRIES` the sender gives up, counts `gave_up` and moves on, so one dead frame cannot block the queue forever → see lab step 4
5. **Duplicate suppression.** The receiver keeps `expected`; anything older is re-acked (the first ack may have been lost) but never delivered twice. Retransmission alone turns loss into duplicates → see lab step 6
6. **Counters as a JSON line.** `jline()` prints `tx`, `retx`, `acked`, `gave_up`, `dup`, `gap`: what you read when the link misbehaves → see lab step 5

Worked example (from `research/concept_examples_l300.py`): 20 readings, 20% loss, 10% duplication, 10% reordering, 5% corruption, seed 12. Fire-and-forget delivers 14 of 20 (6 missing, 2 duplicates, out of order) while the sender reports `tx 20`. With ARQ all 20 arrive once, in order, for 42 transmissions (22 retransmits); the receiver suppresses 19 duplicates. With loss alone, a data+ack round trip succeeds with probability 0.8 × 0.8 = 0.64, and 8 failed tries in a row happen with probability 2.8e-4.

## Failure modes
- **Lost ack, not lost data.** The sender retransmits a frame the receiver already has; without dedupe the reading appears twice. Notice it as `dup` rising.
- **Giving up is not the same as lost.** With `MAX_TRIES = 2` the sender gave up 4 times, yet all 20 arrived: only the acks were lost. Report `gave_up`, but check the receiver's `gap` before you call data missing.
- **Timeout too short.** Copies leave while the ack is still travelling: `retx` is high on a quiet link.
- **Sender restart.** A reset board restarts at sequence 1 and looks old; real protocols add a boot id.

## Common mistakes
- Retransmitting without duplicate suppression, which turns "lost" into "twice".
- Acking only new frames: if the first ack is lost, the sender retries until it gives up.
- Accepting any ack, so a late ack confirms the wrong frame.
