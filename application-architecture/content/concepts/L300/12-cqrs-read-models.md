**Concept: CQRS and read models that survive crashes**

## Why it matters
The loans desk asks "who has book b6?" thousands of times a day. The lesson-8 Member aggregate protects
rules; it is not built for such queries. CQRS
(Command Query Responsibility Segregation) splits the two jobs: commands go to the aggregate, queries
go to a read model shaped for the screen. The price: two copies of the truth. When the query copy drifts,
members see wrong data and nothing raises an error.

## Mental model
The event log is the ledger, in ink. The read model is a whiteboard copied from it.
A clerk (the projector) copies new lines to the board and pencils in the last line number copied.
You can always wipe the board and copy again.

```
command ─► Member aggregate ─► events (append-only, seq 1..n)   write side
                                   │ projector polls after its checkpoint
                                   ▼
          query ◄── LoansView ◄── read DB: member_loans, book_status, checkpoint   read side
```

## How it works
1. **Commands never touch the view.** `LoanCommands` replays the member's events, lets the aggregate
   decide, and appends one event → see lab step 1
2. **The view is behind on purpose.** The projector polls every 20 ms, so a read right after a write is
   often stale. The projector logs this consistency window as `lag_ms` → see lab step 2
3. **A checkpoint is the projector's position.** It records the last applied `seq`, so a restarted
   projector carries on where it stopped instead of starting from zero → see lab step 3
4. **Atomic and idempotent.** The hardened projector commits the view change and the checkpoint in one
   transaction. It recounts `active` from state instead of adding 1, so a replayed event changes nothing
   → see lab step 5
5. **Rebuild and drift check.** `rebuild()` wipes the view and replays every event. `drift()` rebuilds into
   a scratch database and lists every row where the live view disagrees → see lab step 3

**Worked example** (`research/L300_concept_examples.py`): 40 seeded commands produce 33 events, and the
projector is killed at seq 31. The base projector has already saved checkpoint 31, so after a restart
it resumes at 32 and never applies event 31: `member_loans[m3]: view 1, events say 2`. The "half fix"
(apply first, checkpoint second, still `active + 1`) replays seq 31 and shows `view 3, events say 2`.
The solution shows no drift.

## Failure modes
- **Lost event:** the checkpoint moves before the view does. You notice only through a drift check or a
  complaint ("the app says I have 1 loan, I have 2").
- **Double count:** a replayed event hits a non-idempotent handler; counters drift upward.
- **Lag grows:** the projector is slow or stopped. Watch `lag_ms` and the gap from checkpoint to last seq.
- **View schema change:** needs a rebuild; replay time grows with the event log.

## Common mistakes
- Using CQRS for the whole system. Fowler warns that it "adds risky complexity", so keep it to the parts
  where reads and writes really differ.
- Saving the checkpoint in a different store, or a different transaction, from the view it describes.
- Treating a stale read straight after a command as a bug. Return the command's result, or wait until
  the checkpoint reaches the event's seq.
