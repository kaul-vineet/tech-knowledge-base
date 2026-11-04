# 12 · Replicated log with Raft (simplified)

Three Raft nodes (`n1`, `n2`, `n3`) run in one process over a **deterministic simulated network** (messages arrive one tick after they are sent; crashed nodes and cut links drop them). You see terms, randomized election timeouts, a leader elected by a majority, log replication with the AppendEntries consistency check, the **commit index**, a leader crash with re-election, and the old leader catching up. Then the **failure lab**: a follower that missed committed entries wins an election and overwrites them. Time is in ticks and every random draw is seeded, so the output is identical on every run.

Files: `raft.py` (the lesson: `Node` — RequestVote, AppendEntries, commit rule — and the failure-lab scenario) · `helpers.py` (plumbing: `Network`, `Cluster` driver, `SafetyChecker`, and `demo()` — the narrated run that `python raft.py` prints) · `try_it.py` · `test_raft.py` · build task: `solution_raft.py` + `test_build_task.py`.

Simplified on purpose: no disk (a "crash" keeps term, vote and log as if persisted), no snapshots, no membership changes, no PreVote, no client redirects. The real thing: etcd's `raft` library (`go.etcd.io/raft/v3`).

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python raft.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run)
```
t=15 n1 starts election for term 1 (log -)
t=17 n1 becomes leader for term 1 with votes ['n1', 'n2']
1) happy path: 3 entries replicated and committed
   n1 term 1 leader    log [1:x=1 1:x=2 1:x=3] commit 3
   n2 term 1 follower  log [1:x=1 1:x=2 1:x=3] commit 3
   n3 term 1 follower  log [1:x=1 1:x=2 1:x=3] commit 3
t=40 n2 starts election for term 2 (log 1:x=1 1:x=2 1:x=3)
t=40 n3 starts election for term 2 (log 1:x=1 1:x=2 1:x=3)
t=55 n3 starts election for term 3 (log 1:x=1 1:x=2 1:x=3)
t=57 n3 becomes leader for term 3 with votes ['n2', 'n3']
2) n1 crashed at t=23; n3 leads term 3 after 34 ticks
3) x=4 committed without n1; n1 restarted and caught up:
   n1 term 3 follower  log [1:x=1 1:x=2 1:x=3 3:x=4] commit 4
   n2 term 3 follower  log [1:x=1 1:x=2 1:x=3 3:x=4] commit 4
   n3 term 3 leader    log [1:x=1 1:x=2 1:x=3 3:x=4] commit 4
safety violations: 0
t=15 n1 starts election for term 1 (log -)
t=17 n1 becomes leader for term 1 with votes ['n1', 'n2']
t=24 n3 starts election for term 2 (log -)
t=26 n3 becomes leader for term 2 with votes ['n2', 'n3']
4) failure lab: stale follower elected, then writes x=9
   n1 term 1 DOWN      log [1:x=1 1:x=2] commit 2
   n2 term 2 follower  log [2:x=9] commit 2
   n3 term 2 leader    log [2:x=9] commit 1
safety violations: 3
   t=27 LOST committed entry 1 (1:x=1): n2 now has 2:x=9 there
   t=27 LOST committed entry 2 (1:x=2): n2 now has nothing there
   t=28 LOST committed entry 1 (1:x=1): n3 now has 2:x=9 there
```
How to read it:
- **1)** `n1` timed out first (t=15), voted for itself, got `n2`'s vote (2 of 3 = majority) and leads term 1. Three entries are on all logs and `commit 3` everywhere.
- **2)** After `n1` crashes, `n2` and `n3` time out in the same tick (t=40): each votes for itself, nobody gets 2 votes — a **split vote**. New random timeouts separate them; `n3` wins term 3 at t=57.
- **3)** `x=4` commits on `n2` + `n3` (a majority) while `n1` is down; the restarted `n1` sees term 3, becomes a follower and receives `x=4`.
- **4) failure lab.** `n3` was down while `x=1`, `x=2` committed on `n1` + `n2`; then `n1` crashed and `n3`'s timer fired first. `n2` granted its vote only because the term was newer — `raft.py` never looks at the candidate's log. `n3` (empty log) leads term 2, appends `x=9` at index 1 and the AppendEntries conflict rule deletes `n2`'s committed entries. The `SafetyChecker` reports the lost entries.

## Test
```bash
python -m unittest -v     # Ran 8 tests ... OK  (5 lesson tests + 3 build-task tests against the solution)
```

## Build task: the election restriction (Raft paper section 5.4.1)
In `Node.receive`, grant a vote only if the candidate's log is **at least as up-to-date** as yours: compare the last entries' terms; if equal, the longer log wins — `(m["last_term"], m["last_index"]) >= self.last()`.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change (real run): `Ran 3 tests ... FAILED (failures=3)` — e.g. `AssertionError: Lists differ: ['t=27 LOST committed entry 1 (1:x=1): n2 ...'] != []`. The reference is `solution_raft.py`; its failure lab prints:
```
t=24 n3 starts election for term 2 (log -)
t=25 n2 denies n3: candidate log (term, index) (0, 0) < mine (1, 2)
t=33 n2 starts election for term 3 (log 1:x=1 1:x=2)
t=35 n2 becomes leader for term 3 with votes ['n2', 'n3']
4) failure lab: stale follower elected, then writes x=9
   n1 term 1 DOWN      log [1:x=1 1:x=2] commit 2
   n2 term 3 leader    log [1:x=1 1:x=2 3:x=9] commit 3
   n3 term 3 follower  log [1:x=1 1:x=2 3:x=9] commit 3
safety violations: 0
```
`n3` still disrupts the cluster (its term 2 forces `n2` to step up to term 2), but it cannot win; `n2` wins term 3 with `n3`'s vote, and `x=9` lands at index 3.

## Try it (real run — `python try_it.py`)
```
tryIt 1: followers down -> n1 log has 2 entries, commit index stays 1 (x=5 appended, never committed)
tryIt 2: raft.py (no log check): committed entries lost in 11 of 20 seeds
tryIt 2: solution_raft.py (log check): committed entries lost in 0 of 20 seeds
```
tryIt 2 is the point of the lesson: without the check the bug shows up only when timers line up (11 of 20 seeds) — exactly the kind of bug that passes a happy-path test suite.

## Optional: Maelstrom (pending a manual run)
Maelstrom's Raft chapter builds a linearizable key-value store on Raft and checks it with the `lin-kv` workload; see `documentation/LEARNING-TOOLS.md`.

## Platform notes
Pure computation: no sockets, no sleeps, no files. Same output on macOS, Windows and Linux (a string seed such as `"7-n1"` is converted to an integer by `random.seed` version 2 using all of its bits — not by the per-process, randomized `hash()`).
