# 07 · Leader election with leases and fencing tokens

Three nodes (`n1`, `n2`, `n3`) compete for the key `leader` in a shared HTTP key-value store with **TTL + compare-and-swap** (`kv_store.py`). The winner renews every tick (1 s, TTL 3 s). At t=3 `n1` pauses (think: a long GC pause); its lease expires at t=5 and `n2` takes over with a **higher fencing token**. When `n1` wakes up at t=7 it still believes it leads and writes — storage rejects the write because its token is lower. Time is simulated, so the output is identical on every run.

Files: `election.py` (the lesson code: nodes, renew/acquire, fenced storage, demo) · `kv_store.py` (the lease store: TTL, CAS, store-wide revision) · `helpers.py` (plumbing: JSON handler, `call()`, `serve()`, `SimClock`) · `try_it.py` · `test_election.py` · build task: `solution_election.py` + `test_build_task.py` · `etcd_equivalent.py` (the same on etcd; CI only).

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python election.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; simulated clock)
```
t=0 n1 acquired the lease, fencing token 1
t=1 n1 writes with token 1: accepted
t=2 n1 writes with token 1: accepted
t=3 n1 pause
t=5 n2 acquired the lease, fencing token 4
t=6 n2 writes with token 4: accepted
t=7 n1 resume
t=7 n1 writes with token 1: REJECTED (token 1 < 4)
t=7 n1 renew failed (rev 3 != 5) -> steps down
t=7 n2 writes with token 4: accepted
t=8 n2 writes with token 4: accepted
lease holder per tick: 0:n1 1:n1 2:n1 3:n1 4:n1 5:n2 6:n2 7:n2 8:n2
storage value: n2@t8 | highest token seen: 4
```
Why token 4: the store's revision counter went 1 (n1 created the key), 2 and 3 (n1's renewals at t=1, t=2), 4 (n2 created it again). The token is the key's *creation* revision, so it stays 1 for all of n1's tenure and jumps when the holder changes.

## Test
```bash
python -m unittest -v     # Ran 7 tests ... OK  (4 lesson tests + 3 build-task tests against the solution)
```

## Build task: graceful hand-off with `resign()`
Add `Node.resign()` to `election.py`: if the node holds the lease, CAS-delete the key with **its own** revision (`POST /delete {"key", "expect": self.rev}`), then stop acting. `simulate(events={3: ("n1", "resign")})` must show `n2` holding the lease **at t=3** instead of t=5.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change: `Ran 3 tests ... FAILED (errors=3)` (`AttributeError: 'Node' object has no attribute 'resign'`). The reference answer is `solution_election.py` (`python solution_election.py` shows `t=3 n2 acquired the lease, fencing token 4`).

## Try it (real run — `python try_it.py`)
```
tryIt 1: fencing off -> accepted | n1's stale write landed after n2's write at t=6
tryIt 2: TTL 3 s -> holder per tick 111112222 | n2 takes over at t=5
tryIt 2: TTL 6 s -> holder per tick 111111111 | no failover: n1 renewed in time after its pause
```

## Same thing on etcd (pending-ci)
`etcd_equivalent.py` drives a real etcd with `etcdctl`: `lease grant`, a `txn` with `create("leader") = "0"` (create-if-absent = CAS), `get -w json` for `create_revision` (the fencing token), lease expiry, then `etcdctl elect` (etcd's election API) with a resign on SIGTERM. Not run here (no etcd in the sandbox); the CI job `etcd` starts `gcr.io/etcd-development/etcd:v3.7.3` and runs it.
```bash
podman run -d --name etcd -p 2379:2379 gcr.io/etcd-development/etcd:v3.7.3 /usr/local/bin/etcd \
  --listen-client-urls http://0.0.0.0:2379 --advertise-client-urls http://127.0.0.1:2379
python etcd_equivalent.py          # needs etcdctl on PATH (release tarball), or set ETCDCTL
```
On the Mac mini use Podman/Colima as in lesson 1; on Windows run the container in Podman Desktop and use `etcdctl.exe` from the Windows release zip (`$env:ETCDCTL="C:\etcd\etcdctl.exe"`). `etcdctl elect` resigns only on a signal (Ctrl+C); on Windows `terminate()` kills it without resigning, so failover there waits for the lease TTL (60 s default for `elect`) — expected, not verified.

## Platform notes
Ports are OS-chosen on `127.0.0.1` (no fixed port, so the Windows `SO_REUSEADDR` issue from lesson 1 does not apply). No sleeps in the demo: the simulated clock makes Windows timer resolution irrelevant.
