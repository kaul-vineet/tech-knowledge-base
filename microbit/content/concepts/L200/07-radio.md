# Concept: broadcast messages with a small text protocol

## Why it matters
Two boards can share a score, a sensor reading or a "go" signal without wires. The radio gives you broadcast packets and nothing else: no connection, no delivery guarantee, no message format. You add those yourself, in a few lines.

## Mental model
A **walkie-talkie channel**: everyone tuned to the same group hears every message; nobody confirms they heard it. Your program agrees a tiny language on top.

```
board A                          air (group 7)                board B
send("btn:1:A") ─► 01 00 01 "btn:1:A" (10 bytes) ─► queue (3) ─► receive() ─► decode() ─► "rx btn 1 A"
```

## How it works
1. **Same group, same everything.** `radio.config(group=7)` must match on both boards (channel, address and data rate too); a different group simply hears nothing → see lab step 4
2. **Text needs a header.** `radio.send(str)` adds bytes `01 00 01`; `receive()` strips them and raises `ValueError` for anything else, so the lab catches it and counts "bad" → see lab step 2
3. **Format = kind, sequence, value.** `decode()` rejects wrong field counts, unknown kinds and non-numeric sequence numbers; the sequence number drops duplicates → see lab step 3
4. **Packets are small and queues are short.** Default `length=32` bytes and `queue=3`. A receiver that does not poll loses the fourth message; a long message is cut, not split → see lab step 5

Worked example (from `research/concept_examples_l200.py`): `btn:1:A` is 10 bytes on air. A 40-character value asks for 49 bytes; `length=32` keeps 32, so only 23 of the 40 characters arrive. Four sends to a board that never polls: 3 queued, 1 dropped.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Short events or readings between nearby boards | You need guaranteed delivery without adding acks |
| One sender, many listeners (broadcast) | Messages are larger than 251 bytes |
| Classroom or bench prototypes | Data must be private: anyone on the group can listen |

## Common mistakes
- Different groups (or forgetting `config`) on the two boards, then debugging the code.
- Calling `receive()` without catching `ValueError` from non-text packets.
- Polling slowly (long `sleep` or blocking `scroll`) so the 3-message queue overflows.
