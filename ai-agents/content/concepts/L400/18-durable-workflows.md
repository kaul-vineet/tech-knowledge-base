**Concept: durable agent workflows – checkpoints, replay after a crash, long human waits, exactly-once effects**

## Why it matters
A chat agent can restart from scratch; one that waits two days for a manager and then moves money cannot. Processes die: deploys, out-of-memory kills, a closed laptop lid. When it restarts, two things must hold. It must not redo effects that already happened, and it must not forget that it was waiting for someone. Lesson 15 made one refund call safe; this lesson makes a whole workflow safe: a crash at *any* step resumes without a duplicate side effect.

## Mental model
A durable workflow is a function whose memory lives in a log. Each completed step appends its result to an event history. On restart, the code runs from the top again but *reads* recorded results instead of redoing the work. Temporal's documentation describes the same mechanism: activity results are recorded once and reused on replay.

```
run():  lookup ──► propose(LLM) ──► approval(wait) ──► refund(API) ──► notify
          │            │                 │                  │            │
history:  ✓ result     ✓ amount          signal:approve     ✓ refund_id   ✓ + outbox row
restart:  replay       replay (no LLM)   re-read signals    key replays   same transaction
```
Waiting is a database state, not a sleeping thread; "approved" is a signal event any process can read later.

## Design space
- **In-memory loop with retries.** Simple, and enough for read-only agents. A restart re-runs everything: the model is asked again, and the refund is sent again.
- **Checkpoint journal (SQLite) + idempotency keys + outbox.** Each step result is committed in one transaction. SQLite's atomic commit survives a crash or power loss. External calls carry a key derived from workflow id + step, so a resend after "sent, not yet recorded" is replayed by the API (lesson 15, IETF Idempotency-Key draft). Local effects go into an outbox row in the *same* transaction as the checkpoint. The cost: one writer process, and you maintain the engine.
- **Workflow engine (Temporal).** The same model as a service: event history, timers that survive restarts (a 48 h approval wait is a durable timer), activity retries, a Web UI per execution. Workflow code must be deterministic: no direct I/O, time or randomness outside activities. You run a server (the dev server in the CLI, or a cluster). Keys are still needed, because an activity can run twice.

## How to decide
Criteria: side effects? can a run outlive a process (human waits)? how many workers and hosts? what can you operate? Evidence comes from a crash sweep: kill at every step boundary and inside the dangerous gap, restart, finish, then count effects.

Worked example (lab, 12 crash points, refund workflow → see lab steps 2 and 4):

| variant | points with a 2nd refund | points that re-asked the model |
|---|---|---|
| in-memory loop | 4 of 12 | 9 of 12 |
| checkpoints, no key | 1 (after the API answered, before the checkpoint) | 1 |
| checkpoints + key + outbox | 0 | 1 |

That last "1" is a crash between the model's answer and its checkpoint. It costs tokens, not money. A double-clicked approval stores one signal (UNIQUE constraint) and moves money once (try it 2). The long wait survives restarts too: a workflow still "waiting" after 30 h in a new process completes when the approval arrives. With a 48 h deadline (build task), a click at hour 50 is ignored and the workflow escalates instead.

Decision rule from the lab's ADR: an SQLite history while one process owns the workflows; move the same steps to Temporal when you need several workers, cross-host timers or per-execution history browsing.

## Failure modes at scale
- **Key per attempt** (`uuid4()` inside the retry): duplicates come back. Watch the payment log for two rows that share an order but have different keys.
- **Non-deterministic replay:** code that reads the clock or calls the model outside a recorded step takes a different path on restart. Temporal raises a non-determinism error; a home-grown engine silently diverges.
- **Unbounded waits:** approvals without deadlines pile up and act on stale facts. Watch the count of `waiting` rows by age.

## Common mistakes
- Checkpointing *before* the effect and calling that "exactly once"; you still need the key for the gap.
- Holding a thread or HTTP request open while a human decides.
- Treating the model call as an effect to deduplicate, while forgetting the email or ticket that comes after it.
