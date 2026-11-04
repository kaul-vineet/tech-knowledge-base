## Why it matters
A shopping list lives on a phone and a laptop. The phone is offline on a train; the laptop edits too. When they meet, both edits must survive, without a server deciding and without asking the user to resolve a "conflicted copy". Sync channels lose, reorder and repeat messages. A data type whose merge is safe under all of that lets the app write locally, instantly, and sync whenever it can.

## Mental model
A state-based CRDT is a value plus a **merge** that computes a least upper bound: replicas only ever move "up", and merging is like taking a union.

```
phone  {milk:(p,1)}  -remove milk->  tombs {(p,1)}          merge = union of adds,
laptop {milk:(p,1)}  -add milk->     adds  {(p,1),(l,1)}     union of tombstones
both after merge:    milk alive, because tag (l,1) was never tombstoned  -> add wins
```

Because merge is **commutative** (order of merging does not matter), **associative** (grouping does not matter) and **idempotent** (merging twice changes nothing), any two replicas that have seen the same updates hold the same state, whatever path, order or duplication the sync took (Shapiro et al., 2011).

## Design space
- **Server-authoritative / last-writer-wins on the whole value**: simple and compact, but concurrent updates overwrite each other.
- **State-based CRDTs** (this lab): G-Counter (one slot per replica, merge = per-slot max), PN-Counter (two G-Counters), OR-Set (every add carries a unique tag; remove tombstones only the tags it has seen, so a concurrent add wins), LWW-Register (highest timestamp wins). Ship whole states; tolerate any channel.
- **Operation-based CRDTs / libraries** such as Automerge: ship operations (smaller), need reliable causal delivery, model whole JSON documents and keep conflicting values visible.

The forces: what "correct" means for concurrent operations (add wins? remove wins? keep both?), metadata size, and how much the channel can be trusted.

## How to decide
1. For each field, write what should happen when two replicas change it concurrently. That picks the type: counts -> PN-Counter; collections -> OR-Set; a single field -> LWW-Register (or a multi-value register if both values matter).
2. Test the merge laws and convergence with **seeded random histories**, including duplicated syncs; shrink any failure to the smallest history.
3. Budget the metadata a sync ships and watch it grow.

Worked example (lab output, seed 18, 500 histories per type): G-Counter, PN-Counter and OR-Set pass 500/500 on all three laws and on convergence. The lesson's LWW-Register passes only 407/500 commutativity and 386/500 convergence; the shrinker reduces a failure to two steps, `r0.assign('r0', 'r0.9', 0); r1.assign('r1', 'r1.10', 0)`: two writes at the same Lamport timestamp. Merge kept "my" value on a tie, so the two merge orders disagree. Breaking ties by replica id makes it 500/500. Option evidence: a like-counter with truth 140 ends at 81 on every replica when stored as a last-writer-wins number, and at 140 as a PN-Counter (76 bytes per sync versus 15).

## Failure modes at scale
- **Tombstone growth**: the OR-Set never forgets removed tags. One item added and removed 1,000 times costs 31,813 bytes (tryIt 2). Garbage collection needs agreement that every replica has seen a tombstone, which is coordination again.
- **Vector size**: counters keep one slot per replica that ever wrote; with many short-lived devices the state keeps growing unless slots are compacted.
- **Ties and clocks**: LWW with wall clocks lets a fast clock win forever; Lamport timestamps plus replica id give a deterministic, though arbitrary, winner.
- **Global invariants** ("stock never below zero") cannot be enforced by merging local states; they need reservations or coordination.

## Common mistakes
- Merging by adding numbers (tryIt 1: idempotence 7/500; nothing converges once a sync is repeated).
- Testing merge with a few hand-picked examples instead of random histories with duplicates.
- Choosing last-writer-wins for data where both concurrent updates matter (counts, carts).
