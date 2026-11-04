**Concept: Event-driven integration with an outbox and AsyncAPI**

## Why it matters
After a loan is created, the notification service should email the member and the statistics view
should update. If the loan service calls them directly, it waits for them and fails with them. If it
sends a message after committing and then crashes, the message is lost. If it sends before committing,
the email goes out for a loan that was rolled back.

## Mental model
The outbox is a tray on the clerk's desk. The loan card and its note go onto the tray together. A courier
empties the tray in order, and recipients ignore a note they have already read.

```
borrow() ─► [ loans row + outbox row ] one transaction
                        │ relay polls in seq order
                        ▼
                 bus ─► NotificationConsumer (idempotent)
                     └► ActiveLoansProjection (idempotent)
asyncapi.json ── describes channels, operations, payloads ── checks every event
```

## How it works
1. **Same transaction.** `LoansWithOutbox.borrow` inserts the loan and its `LoanCreated` event inside
   one `with db:` block, so both are written or neither is → see lab step 1
2. **Relay, at least once.** `Relay` reads pending rows in commit order, publishes them, then marks them.
   A crash between those two steps means the event is sent again → see lab step 2
3. **Idempotent consumers.** Each event carries an `eventId`, and consumers skip ids they have already
   processed → see lab step 4
4. **Contract.** `asyncapi.json` (AsyncAPI 3.1.0) declares channels, `send` operations and payload
   schemas. Code validates the document and every published event → see lab step 3

**Worked example** (`research/L200_concept_examples.py`): a borrow and a return leave outbox rows
`(1, loanCreated)` and `(2, loanReturned)` next to one loan row. When the relay crashes once after
publishing, a naive consumer sends 2 emails and the idempotent one sends 1.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Other parts react to changes and may be slow or down | The caller needs the result now (use a request) |
| You must never lose or invent an event | One process, one database, no other consumers |
| Several teams consume the same events | You cannot make consumers idempotent |

## Common mistakes
- Publishing to the broker inside the database transaction, or after it without an outbox.
- Assuming exactly-once delivery: design for duplicates.
- Treating the AsyncAPI file as documentation only. Validate real events against it in tests.
