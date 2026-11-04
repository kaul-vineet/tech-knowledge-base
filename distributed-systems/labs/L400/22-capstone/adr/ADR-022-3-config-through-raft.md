# ADR-022-3: Gateway limits are versioned config committed through Raft, applied only when committed

## Status
Accepted (capstone, 2026-10-28; reuses L300 #12's Raft with the election restriction). Fitness function: "config via Raft".

## Context
The queue bound changes at runtime (8 -> 12 at tick 25). Every gateway must apply the same value, a crash of the
config leader must not lose the change, and no gateway may go back to an older value.

## Decision
The operator proposes `<version>:<max_queue>` to the Raft leader and re-proposes every 5 ticks until that version is
committed (the version makes duplicates harmless). The pipeline applies only committed entries and only versions
newer than the one it has; before the first commit it uses a safe default bound of 1. The run is not finished
until the wanted version is committed.

## Consequences
- While building, the `raft-leader-crash` experiment failed "config via Raft" (committed versions [1]): the run had
  ended before the re-proposed change committed. Waiting for the commit fixed it (ticks 33 -> 48 in that run).
- Config changes take an election timeout longer when the leader dies; the gateway keeps the last committed value.
- A deposed leader could serve an old committed view; versions make the pipeline ignore it (monotonic reads).
