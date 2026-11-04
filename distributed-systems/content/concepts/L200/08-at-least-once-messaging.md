## Why it matters
A worker takes "charge order 42" from a queue, charges the card, then crashes before saying "done". Deleting messages on delivery would lose the order, so brokers redeliver instead — **at-least-once** — and duplicates become your problem.

## Mental model
Receiving is borrowing a library book: it is hidden from others until the due date (visibility timeout). Returning it (ack) removes it; an overdue book goes back on the shelf; one borrowed and never returned too often goes to the problem shelf (dead-letter queue).

```
send -> [queue] --receive--> hidden 3 s --ack--> deleted
           ^                     | no ack
           +---- visible again --+   3rd unacked receive -> DLQ
```

## How it works
1. **Receive hides, it does not delete**, and returns a receipt. → see lab step 1
2. **Ack deletes; silence redelivers**, possibly to another consumer, with a new receipt so a stale consumer cannot ack it. → see lab step 2
3. **A crash between effect and ack duplicates the effect**: the card was charged, the ack never came. → see lab step 3
4. **Dead-letter after N receives.** A poison message crashes every handler; after `MAX_RECEIVES` it moves aside for a human. → see lab step 4
5. **Idempotent consumers make duplicates harmless**: store the message id with the effect in one transaction, skip known ids. → see lab step 6

Worked example (demo output): o5 is received at t=2, charged, crash; it reappears at 2 + 3 = t=5, charged, crash; at t=8 charged and acked. Overall 9 charges for 6 orders, none lost.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Losing a message is worse than handling it twice | Duplicates are costly and the handler cannot be idempotent |
| Another consumer can safely retry the work | Work outlasts any visibility timeout (extend it while working) |

A low dead-letter limit isolates poison fast but also parks unlucky good messages (tryIt 2: 12 of 30 runs at limit 2, 2 of 30 at limit 5).

## Common mistakes
- Acking before the work is done: a crash loses the message (at-most-once).
- A dead-letter queue nobody watches.
- Remembering processed ids only in memory: a restart forgets them.
