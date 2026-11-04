# 19 · Multi-region design: latency budget, leader placement, failover RTO/RPO

Design question: order writes come from us (50%), eu (35%) and ap (15%). Which replication design and where does the leader live, so that us/eu write p99 stays <= 350 ms, **no acknowledged order is lost when a whole region fails (RPO = 0)**, writes work again within 5 s (**RTO**), and two regions never accept conflicting writes? The lab simulates 100 writes/s for 20 s across three regions (one-way latencies us-eu 40, eu-ap 70, us-ap 110 ms - assumptions in `helpers.py`, not measurements), fails a region at t = 10 s and measures each design: **single leader** (async or **majority-sync**, Raft-style), **multi-leader**, **leaderless** W=2.

Files: `multiregion.py` (lesson: designs, failover, `evaluate`, `violations`, `place_leader`) · `helpers.py` (plumbing: latency model with a 2% slow tail, FIFO replication streams, Poisson write stream, conflict counter) · `solution_multiregion.py` (build task) · `test_multiregion.py` · `test_build_task.py` · `test_fitness.py` · `ADR-019-multi-region-orders.md` · `try_it.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python multiregion.py
```

## Expected output (real run, Python 3.12.15, Linux - identical on every run; seeded)
```
design               write p99 us / eu / ap ms   lag p99  conflicts  RPO lost  RTO ms  rejected
async@ap                346.0 /  265.3 /  102.3     266.6          0        16    1129       108
async@us                128.0 /  205.3 /  320.3     256.1          0        17    1142        72
sync-majority@us        310.9 /  354.9 /  445.8      95.9          0         0    1209        74
sync-majority@eu        304.6 /  267.8 /  341.7      67.9          0         0    1313        73
sync-majority@ap        497.2 /  450.1 /  354.5      38.4          0         0    1009       102
multi-leader            140.6 /  127.1 /  112.8     197.4        434         2      65         0
leaderless              203.9 /  147.1 /  221.9      34.2        409         0      65         0
deployed {'replication': 'async', 'leader': 'ap'}: violations ['RPO: 16 acknowledged writes lost']
place_leader('sync-majority') -> ap
```
The deployed design (async, leader in ap - where the team first launched) answers fast, but losing ap loses **16 acknowledged writes**: the leader acked them before they reached a follower. Majority-sync never loses a committed write (the new leader is the most up-to-date survivor, Raft section 5.4.1) and pays a round trip to the nearest follower on every write; its RTO is one election (1-2 s timeout + a vote). Multi-leader and leaderless answer locally and keep writing through the failure, but accept 434 / 409 concurrent writes to the same key that last-writer-wins would silently drop. `place_leader` in the lesson file still returns the historical choice.

## Test
```bash
python -m unittest -v     # Ran 10 tests ... OK  (5 lesson + 3 build-task + 2 fitness, against the solution)
```

## Build task: decide by measurement
1. Implement `place_leader(replication)`: simulate the design with the leader in each region and return the region with the lowest **traffic-weighted write p99**.
2. Set `DESIGN` to majority-sync with the measured leader.

Before your change (real run): `Ran 3 tests in 0.461s / FAILED (failures=3)`. The reference prints the same table and:
```
deployed {'replication': 'sync-majority', 'leader': 'eu'}: violations none
place_leader('sync-majority') -> eu
```
eu wins although us has the most users: eu's nearest follower is close for everyone, so every user's commit is cheaper.

## Fitness function (keeps ADR-019 true)
`test_fitness.py`: the chosen design meets the brief on seeds 19-28 and eu is still the best-placed leader on seeds 19-21. Margin is thin: the us p99 peaked at 339.2 ms over seeds 19-38 (budget 350).

## Try it (real run - `python try_it.py`)
```
tryIt 1: us follower read: ~2 ms, stale by up to 12.4 ms (p99 lag); leader read: ~80 ms + jitter, current if the leader confirms it still leads (Raft section 8)
tryIt 1: ap follower read: ~2 ms, stale by up to 103.6 ms (p99 lag); leader read: ~140 ms + jitter, current if the leader confirms it still leads (Raft section 8)
tryIt 2: election timeout 1000-2000 ms -> RTO 1313 ms, 73 writes rejected during failover, RPO 0
tryIt 2: election timeout 150-300 ms -> RTO 278 ms, 21 writes rejected during failover, RPO 0
```
tryIt 1: follower reads are local (~2 ms) but stale by the replication lag - fine for the catalogue, not for stock. tryIt 2: a LAN-style election timeout cuts RTO to 278 ms on the simulated WAN; real WAN jitter would also trigger needless elections (not modelled - see the concept note).

## Platform notes
Pure computation on simulated time: no sockets, no sleeps, no files written. Seeded, so the output is identical on macOS, Windows and Linux (CI matrix pending).
