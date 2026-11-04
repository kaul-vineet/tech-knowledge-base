## Why it matters
Networks rarely fail cleanly. A link drops some packets, a switch isolates one rack, a node can reach the database but not the lock service. Code written for "up" or "down" meets "up for some peers, slow for others" and produces two leaders, stale reads and lost writes. You only find these bugs by injecting the faults on purpose and checking what clients actually observed.

## Mental model
Put a proxy on every link you care about and decide per link what the network does. Record every client operation with its start and end time; afterwards ask one question: could a single copy of the data have produced these results?

```
         lease store            storage (register)
   n1 --X--  |  <- partition       |
   n1 --------------- slow ------->|   n1: "I still lead" (token 1)
   n2 -------|-------------------->|   n2: acquired lease (token 2)
history: c2 write 2 ok @6.5 | c1 write 3 ok @7.8 | c2 read -> 2 @8.5  => NOT linearizable
```

## How it works
1. **Proxy toxics.** Each (source, destination) link can be down, delayed or lossy. A lost request becomes a timeout, so the caller cannot tell a dead peer from a slow one; seeded randomness makes runs repeatable. → see lab step 2
2. **Split brain.** The partition hides the lease store from n1. Its renewals time out and it keeps acting on its old lease; the store expires that lease and gives n2 a higher token. Both now accept writes. → see lab step 2
3. **History as data.** Every operation is one invoke and one completion line: process, function, value, time, ok or fail. → see lab step 3
4. **Linearizability check.** Search for an order of the successful operations that respects real time (an operation that finished before another began comes first) and in which every read returns the latest write. No such order means a client saw something impossible. → see lab step 3
5. **Fencing fixes the writes.** The storage remembers the highest token and rejects lower ones; the rejected node steps down and its client gets a failure, which the checker ignores. → see lab step 5

Worked example (lab output): leaders per tick are `4:n1+n2` through `8:n1+n2`. c1's write 3 through n1 (token 1) finishes at 7.8; c2's read through n2 at 8 returns 2, so the checker says False and names the stale read. With fencing the same write fails with "rejected: token 1 < 2", n1 steps down at t=7, and the checker says True.

## Failure modes
- **Stale writes:** two leaders overwrite each other; noticed by a checker, an audit, or lost customer data.
- **Stale reads:** a deposed leader answers from memory. Fencing does not help (tryIt 2); reads must reach the fenced resource or a quorum.
- **Flapping leadership** under partial loss: leadership moves at different times per seed (tryIt 1). Watch for frequent "acquired" events and term or token jumps.
- **Checker blind spots:** failed operations are dropped; real timeouts are indeterminate and must be checked both ways.

## Common mistakes
- Treating a timeout as "nothing happened" or as "still mine".
- Testing only clean partitions instead of delay, loss and one-way cuts.
- Asserting on final state instead of checking the whole client history.
