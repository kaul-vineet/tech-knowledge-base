# 10 · Caching and invalidation: cache-aside, TTL, stale reads, thundering herd

`cache.py` puts a **cache-aside** layer (`PriceService`) with a 30 s TTL in front of a slow price database (`PriceDB`, 0.2 s per read, counts reads). The demo shows a miss followed by hits, a **stale read** after a write without invalidation (until the TTL runs out), **invalidate-on-write**, and a **thundering herd**: 50 threads read one cold key at the same moment and all 50 go to the database. TTLs use a simulated clock; the herd uses real threads and a real 0.2 s delay.

Files: `cache.py` (the lesson code) · `helpers.py` (`SimClock`) · `try_it.py` · `test_cache.py` · build task: `solution_cache.py` + `test_build_task.py` · `valkey_equivalent.py` (the same in Valkey; CI only) + `test_valkey_client.py` (its RESP client against a fake socket server, runs locally).

## Run (Mac mini and Windows: same command inside the venv)
```bash
python cache.py
```

## Expected output (real run, Python 3.12.15, Linux — same on every run of 3)
```
cache-aside  : [5, 5, 5] -> db reads 1 (1 miss, 2 hits)
no invalidate: t= 0s read 5 (STALE, db has 7)
no invalidate: t=10s read 5 (STALE, db has 7)
no invalidate: t=29s read 5 (STALE, db has 7)
no invalidate: t=30s read 7 (fresh)
invalidate   : t=100s write 9 -> read 9 (fresh)
herd         : 50 concurrent reads of a cold key -> 50 db reads, values [9]
```
The herd count depends on thread scheduling: all 50 threads check the cache within microseconds of the barrier, long before the first 0.2 s read returns, so 50 is expected on the Mac mini and the Windows PC too; on a heavily loaded machine a few late threads could find the value already cached (the test only asserts `> 1`).

## Test
```bash
python -m unittest -v     # Ran 6 tests ... OK (3 cache + 2 build-task tests against the solution + 1 RESP client test)
```

## Build task: request coalescing (single-flight)
Change `PriceService.get_price` so that, on a miss, only the **first** caller for a key reads the database; concurrent callers for the same key wait for that result (a dict of in-flight loads + `threading.Event`, guarded by a lock). Go's `golang.org/x/sync/singleflight` does exactly this ("only one execution is in-flight for a given key at a time").
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change: `Ran 2 tests ... FAILED (failures=2)`. Reference: `solution_cache.py` → `herd : 50 concurrent reads of a cold key -> 1 db reads, values [9]`.

## Try it (real run — `python try_it.py`)
```
tryIt 1: TTL 30 s -> 30 stale reads of 60, 2 db reads
tryIt 1: TTL  5 s -> 5 stale reads of 60, 12 db reads
tryIt 2: race -> db has 11, cache serves 5 until t=30 (TTL)
```
tryIt 2 is the classic invalidation race: a slow reader fetched the old value, the writer deleted the cache entry, then the reader stored the old value. The TTL is the backstop; memcache-style leases (see sources) close the race.

## Same thing in Valkey (pending-ci)
```bash
podman run -d --name valkey -p 6379:6379 docker.io/valkey/valkey:9.1.3     # Mac mini: Podman/Colima; Windows: Podman Desktop
python valkey_equivalent.py
```
`GET`, `SET price:apple 5 EX 30` (fill with TTL), `DEL` on write, and `SET lock:apple me NX EX 5` so only one process loads a cold key. Not run here (no Valkey in the sandbox); the CI job `valkey` runs it against a service container. The RESP2 client itself is tested locally by `test_valkey_client.py` against a fake socket server — that proves the framing, not Valkey's behaviour.

## Platform notes
No ports for the lesson code (in-process); the RESP test binds `127.0.0.1` on an OS-chosen port. The herd's 0.2 s delay is far larger than the OS timer granularity on macOS or Windows, so it behaves the same.
