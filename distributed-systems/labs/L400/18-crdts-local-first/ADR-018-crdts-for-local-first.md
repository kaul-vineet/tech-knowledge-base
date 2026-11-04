# ADR-018: State-based CRDTs for the offline shopping list, with a deterministic LWW tie-break

## Status
Accepted (lab 18, 2026-10-28). Fitness function: `test_fitness.py`.

## Context
The shopping-list app must work offline on a phone and a laptop and merge when they reconnect, with no server
deciding. Sync is unreliable: messages can be lost, reordered or delivered twice. Options measured in `crdts.py`
(seed 18, 500 random histories per type, 20% duplicated syncs):

| Option | Evidence | Verdict |
|---|---|---|
| Store plain values, last writer wins (whole value) | like-counter truth 140, LWW number ends at 81 on all replicas: concurrent increments lost | reject for counters and sets |
| State-based CRDTs (OR-Set, PN-Counter, LWW-Register) | laws 500/500 and convergence 500/500 for G/PN-Counter and OR-Set; LWW-Register only 407/500 commutative, 386/500 converged until ties are broken by replica id | adopt, with the tie-break |
| Automerge 3.3.2 (op-based JSON CRDT) | `automerge_equivalent.mjs` asserts the same stories; pending CI (npm not reachable here) | equivalent library when the document model grows |

## Decision
Items: OR-Set (add wins over a concurrent remove). Counters: PN-Counter. Single fields (list title): LWW-Register
ordered by (Lamport timestamp, replica id).

## Consequences
- Concurrent title edits keep one winner chosen by replica id; the other edit is silently dropped (Automerge keeps it
  as a conflict the UI could show).
- OR-Set tombstones are never collected here: 1,000 add/remove cycles of one item grow the state to 31,813 bytes
  (tryIt 2). Garbage collection needs coordination (Shapiro et al., section 4).
- `test_fitness.py` fails the build if any chosen type breaks a merge law or diverges on 3 seeds x 500 histories, or
  if the reference cart session ships more than 4,096 bytes per sync (1,311 today).
