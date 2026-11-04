# 18 · CRDTs for local-first collaboration

Design question: a shopping-list app must work offline on a phone and a laptop and merge when they reconnect, with no server deciding and with a sync that loses, reorders and duplicates messages. Which data types? The lab implements four state-based **CRDTs** (Shapiro et al. 2011) - **G-Counter**, **PN-Counter**, **OR-Set** (add wins) and **LWW-Register** - and tests their **merge laws** (commutative, associative, idempotent) and **convergence** with a small seeded **property-based tester** that generates random histories and **shrinks** a failing one to a minimal counterexample.

Files: `crdts.py` (lesson: the four CRDTs, the two-phone story, the like-counter options) · `helpers.py` (plumbing: history generator, replay, law and convergence checks, shrinker) · `solution_crdts.py` (build task) · `automerge_equivalent.mjs` + `package.json` (Automerge 3.3.2, pending CI) · `test_crdts.py` · `test_build_task.py` · `test_fitness.py` · `ADR-018-crdts-for-local-first.md` · `try_it.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python crdts.py
```

## Expected output (real run, Python 3.12.15, Linux - identical on every run; seeded)
```
1) phone+laptop: ['eggs', 'milk'] == ['eggs', 'milk']: True
2) merge laws and convergence over 500 seeded random histories per type:
   G-Counter     {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   PN-Counter    {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   OR-Set        {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   LWW-Register  {"commutative": "407/500", "associative": "500/500", "idempotent": "500/500", "converged": "386/500"}
                 shrunk counterexample: commutative fails after: r0.assign('r0', 'r0.9', 0); r1.assign('r1', 'r1.10', 0)
                 shrunk counterexample: replicas diverge after: r0.assign('r0', 'r0.10', 0); r1.assign('r1', 'r1.11', 0)
3) like-counter, truth 140: LWW number [81, 81, 81] (concurrent adds lost), PN-Counter [140, 140, 140]; sync bytes LWW 15, PN 76
```
The counters and the OR-Set are joins: every law holds on 500 histories and every replica converges. The LWW-Register breaks commutativity when two replicas write at the **same Lamport timestamp**: `merge` keeps "my" value, so the two orders of merging disagree and 114 of 500 histories end with replicas that never converge. The shrinker reduces each failure to two concurrent assignments. Option evidence (3): storing the like-count as a plain number with last-writer-wins drops concurrent increments (81 instead of 140); the PN-Counter is exact at 76 bytes per sync.

## Test
```bash
python -m unittest -v     # Ran 10 tests ... OK  (5 lesson + 3 build-task + 2 fitness, against the solution)
```

## Build task: a deterministic tie-break
Order LWW writes by `(timestamp, replica id)` in `LWWRegister.merge`. Before your change (real run): `Ran 3 tests in 0.159s / FAILED (failures=2)`. The reference prints `LWW-Register {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}`.

## Fitness function (keeps ADR-018 true)
`test_fitness.py`: OR-Set, PN-Counter and LWW-Register obey the laws and converge on seeds 18-20 (500 histories each), and a reference cart session (60 adds, 5 removes) ships at most 4,096 bytes per sync (1,311 today).

## Automerge equivalent (pending CI)
`npm install` then `node automerge_equivalent.mjs` (Node 24, `@automerge/automerge` 3.3.2, MIT; version from npm, checked 2026-10-28): the same two-device story with a map, a `Counter` and a conflicting title; it asserts both documents are equal, likes = 5, and two conflicting titles are kept. Not run here (npm is not reachable from the authoring sandbox).

## Try it (real run - `python try_it.py`)
```
tryIt 1: G-Counter with sum-merge: {'commutative': '500/500', 'associative': '500/500', 'idempotent': '7/500'}, converged 0/500
         idempotent fails after: r0.inc('r0', 1)
tryIt 2:   10 add/remove cycles -> value ['milk'], tombstones 10, state 311 bytes
tryIt 2:  100 add/remove cycles -> value ['milk'], tombstones 100, state 3012 bytes
tryIt 2: 1000 add/remove cycles -> value ['milk'], tombstones 1000, state 31813 bytes
```
tryIt 1: a G-Counter whose merge **adds** slots instead of taking the max is commutative and associative but not idempotent - one re-delivered sync double-counts, and nothing converges. tryIt 2: OR-Set tombstones are never collected here; one item re-added and removed 1,000 times costs 31,813 bytes of state (Shapiro et al., section 4: collection needs coordination).

## Platform notes
Pure computation on simulated time: no sockets, no sleeps, no files written. Seeded, so the output is identical on macOS, Windows and Linux (CI matrix pending).
