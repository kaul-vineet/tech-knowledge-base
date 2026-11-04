# 17 · Consistency models in practice: quorums, staleness and PACELC

Design question: one replicated key-value store (N = 3; zones A and B in one region, zone C in another) serves a cart badge, feature flags and a lock-owner/config key. Which **read quorum R** and **write quorum W** does each use? The lab measures, on a seeded simulated network with a 5% slow-message tail, **read/write latency**, **stale reads** (and how stale), **read-your-writes** violations, **new-then-old inversions** (the anomaly that separates *linearizable* from weaker models) and **availability with region C down** - the two halves of **PACELC** (Abadi 2012): if Partition, Availability vs Consistency; Else, Latency vs Consistency. `decide()` then picks the fastest setting that meets each use case's constraints.

Files: `quorum.py` (lesson: replicas, quorum read/write, workload, `measure`, `decide`) · `helpers.py` (plumbing: discrete-event simulator, zone latency model, percentiles, the single-writer history checks) · `solution_quorum.py` (build task: read write-back) · `test_quorum.py` · `test_build_task.py` · `test_fitness.py` (ADR fitness function) · `ADR-017-consistency-per-use-case.md` · `try_it.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python quorum.py
```

## Expected output (real run, Python 3.12.15, Linux - identical on every run; seeded)
```
{"seed": 17, "run_ms": 10000.0, "replicas": "a@A b@B c@C (C = other region)"}
N R W wb R+W>N  read p50/p99 ms  write p99  stale% (max age ms)  ryw  inversions  linearizable  avail, C down
3 1 1 -  False      3.8/60.5        34.0  16.74 ( 86.9)        15        902  False         100.0%
3 1 2 -  False      3.8/60.4        64.5   7.89 ( 62.7)         1        790  False         100.0%
3 2 2 -  True      12.5/65.9        68.3    0.0 (  0.0)         0          2  False         100.0%
3 1 3 -  True       3.8/60.4       125.8    0.0 (  0.0)         0        401  False           0.0%
3 3 1 -  True      62.3/135.3       12.1    0.0 (  0.0)         0          0  True            0.0%
3 2 2 +  True      12.5/65.9        68.3    0.0 (  0.0)         0          2  False         100.0%
decide cart badge (shows a count): N=3 R=1 W=1
decide feature flag (writer sees own change): N=3 R=2 W=2
decide lock owner / config (linearizable): NO setting meets the constraints
```
Read it as PACELC. **Else (no partition):** R=1 W=1 is fastest and returns a stale value in 16.74% of reads (up to 86.9 ms old); R + W > N removes stale reads of *finished* writes. **Partition (region C down):** settings that need all three replicas (W=3 or R=3) stop answering. The surprise is row 3: R=2 W=2 overlaps, has no stale reads, and is **still not linearizable** - 2 reads (of about 2,100) returned an older value than a read that had already finished (new-then-old while a write was in flight). The `+wb` row asks for write-back, but the lesson file ignores it, so no setting meets the config use case.

## Test
```bash
python -m unittest -v     # Ran 10 tests ... OK  (6 lesson + 3 build-task + 1 fitness, against the solution)
```
`test_quorum.py` also cross-checks the fast single-writer checks against the exhaustive L300 #13 checker on 300 short histories: both reject the same 89.

## Build task: read write-back (ABD-style)
In `Cluster.finish_read`, when `write_back` is set and fewer than W of the R replies already hold the newest version, write that version back to a write quorum before returning (Attiya, Bar-Noy and Dolev's two-phase read). Before your change (real run): `Ran 3 tests in 9.953s / FAILED (failures=2)`. The reference `solution_quorum.py` prints the same table with the last row and decisions changed:
```
3 2 2 +  True      12.7/124.5       67.5    0.0 (  0.0)         0          0  True          100.0%
decide cart badge (shows a count): N=3 R=1 W=1
decide feature flag (writer sees own change): N=3 R=2 W=2
decide lock owner / config (linearizable): N=3 R=2 W=2 + read write-back
```
Write-back costs one extra round trip only when replicas disagree: read p50 12.5 -> 12.7 ms, read p99 65.9 -> 124.5 ms.

## Fitness function (keeps ADR-017 true)
`test_fitness.py`: the config setting (R=2 W=2 + write-back) must be linearizable on seeds 11-20, keep read p99 <= 150 ms and answer with region C down. Against the unmodified lesson file it fails on 8 of 10 seeds.

## Try it (real run - `python try_it.py`)
```
tryIt 1: TAIL_P=0.05: R=2 W=2 inversions=2 read p99=65.9 ms write p99=68.3 ms
tryIt 1: TAIL_P=0.00: R=2 W=2 inversions=0 read p99=62.4 ms write p99=17.9 ms
tryIt 2: R=1 W=1: reads 100.0% writes 100.0% answered
tryIt 2: R=1 W=2: reads 100.0% writes 0.0% answered
tryIt 2: R=2 W=2: reads 0.0% writes 0.0% answered
tryIt 2: R=1 W=3: reads 100.0% writes 0.0% answered
tryIt 2: R=3 W=1: reads 0.0% writes 100.0% answered
tryIt 2: R=2 W=2 +wb: reads 0.0% writes 0.0% answered
```
tryIt 1: without the slow tail the in-flight window is too short for an inversion - the anomaly needs a slow message, which production always has. tryIt 2: with only replica a reachable, R=1 W=1 keeps answering (PA) while R=2 W=2 refuses (PC).

## Platform notes
Pure computation on simulated time: no sockets, no sleeps, no files written. Seeded, so the output is identical on macOS, Windows and Linux (CI matrix pending).
