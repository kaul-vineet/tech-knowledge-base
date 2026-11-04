## Why it matters
You merge three services' logs to debug an order. Sorted by timestamp, the warehouse "received the order" 70 ms *before* the shop "sent" it. The warehouse clock is just slow: across machines, wall-clock order can put effects before causes.

## Mental model
Every node keeps a tally counter instead of trusting its wall clock. Messages carry the sender's count; on receipt you jump past it, so a reply never carries a smaller number than its cause.

```
A: 1 Buy ─ 2 send m1 ─────────────────────────── 8 recv m3
B:            3 recv m1 ─ 4 ─ 5 send m2              ↑
C:                             6 recv m2 ─ 7 send m3
```

## How it works
1. **Three rules:** local event → `clock += 1`; send → `clock += 1` and attach it; receive → `clock = max(clock, msg_ts) + 1`. → see lab step 3
2. **The guarantee runs one way.** If a happened-before b, then L(a) < L(b); the reverse does not hold. Equal values mean concurrent events: A's receive and C's audit log both have L=8. → see lab step 4
3. **Total order:** sort by `(L, node id)`. With B 80 ms slow, wall-clock order shows 2 violations; `(L, node)` order 0. → see lab step 1

## Common mistakes
- Forgetting `max()` on receive: a receive then gets a smaller stamp than its send (tryIt 1).
- Reading "L(a) < L(b)" as "a caused b".
- Ordering causally related events by different machines' wall clocks.
