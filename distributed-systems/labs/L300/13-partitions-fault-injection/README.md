# 13 · Network partitions and fault injection

The lease election from lesson 7 meets a hostile network. Three nodes reach the **lease store** (TTL + compare-and-set, a token that grows with each new holder) and a shared **register** (`Storage`) only through a **Toxiproxy-style proxy**: per link it can be `down` (Toxiproxy: `enabled: false`), add `latency`, or `drop` requests with a seeded probability (`toxicity`). Clients send writes and reads to whichever node they think leads; every operation is recorded as a Jepsen-style **history (JSON lines)** and judged by a small **linearizability checker** for one register (`checker.py`, the idea behind Knossos and Porcupine).

Happy path: one leader, history linearizable. Fault: at t=2 the proxy cuts `n1` off the lease store (and slows `n1` → storage by 0.3). `n1`'s renewals time out — and it keeps acting as leader. At t=4 the lease expires and `n2` takes it with token 2. For five ticks **two nodes believe they lead**, both write, and the history stops being linearizable.

Files: `partition.py` (lesson: `Proxy`, `Storage`, `Node`, the scenario) · `checker.py` (linearizability check + `stale_reads` explanation) · `helpers.py` (plumbing: in-process `LeaseStore` like lesson 7, JSON-lines writer) · `agent_assist.py` (optional local model explains the history; code checks every claim) · `try_it.py` · tests: `test_partition.py`, `test_agent_assist.py` · build task: `solution_partition.py` + `test_build_task.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python partition.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; simulated ticks, seeded proxy)
```
happy path (no faults): leaders per tick n1 n1 n1 n1 n1 n1 n1 n1 n1 n1 n1
  linearizable: True
t=0 n1 acquired the lease, token 1, loaded value 0
t=2 fault: partition n1 | lease store; latency 0.3 n1->storage
t=2 n1 renew timed out (n1->lease) -> still thinks it leads
t=3 n1 renew timed out (n1->lease) -> still thinks it leads
t=4 n1 renew timed out (n1->lease) -> still thinks it leads
t=4 n2 acquired the lease, token 2, loaded value 1
t=5 n1 renew timed out (n1->lease) -> still thinks it leads
t=6 n1 renew timed out (n1->lease) -> still thinks it leads
t=7 n1 renew timed out (n1->lease) -> still thinks it leads
t=8 n1 renew timed out (n1->lease) -> still thinks it leads
t=9 fault: heal
t=9 n1 renew refused -> steps down
leaders per tick: 0:n1 1:n1 2:n1 3:n1 4:n1+n2 5:n1+n2 6:n1+n2 7:n1+n2 8:n1+n2 9:n2 10:n2
history (JSON lines):
  {"time": 1, "process": "c1", "type": "invoke", "f": "write", "value": 1, "node": "n1"}
  {"time": 1.5, "process": "c1", "type": "ok", "f": "write", "value": 1, "node": "n1"}
  {"time": 6, "process": "c2", "type": "invoke", "f": "write", "value": 2, "node": "n2"}
  {"time": 6.5, "process": "c2", "type": "ok", "f": "write", "value": 2, "node": "n2"}
  {"time": 7, "process": "c1", "type": "invoke", "f": "write", "value": 3, "node": "n1"}
  {"time": 7.8, "process": "c1", "type": "ok", "f": "write", "value": 3, "node": "n1"}
  {"time": 8, "process": "c2", "type": "invoke", "f": "read", "value": null, "node": "n2"}
  {"time": 8.5, "process": "c2", "type": "ok", "f": "read", "value": 2, "node": "n2"}
linearizable: False
  stale read: c2 read -> 2 via n2 [8, 8.5], but c1 write 3 via n1 [7, 7.8] had already finished
```
Why it is not linearizable: `c1 write 3` (via the deposed `n1`, token 1) finished at 7.8, *before* `c2`'s read began at 8 — so any single-copy register must return 3. `n2` answered 2 from its local copy, because it has no idea a second leader exists. No ordering of the four operations explains every result.

## Test
```bash
python -m unittest -v     # Ran 13 tests ... OK  (6 lesson + 4 agent-assist + 3 build-task tests against the solution)
```

## Build task: fencing tokens at the resource
Make `Storage.write` remember the highest token it has seen and reject any write with a lower one (`"rejected: token 1 < 2"`); in `Node.handle`, a rejected write makes the node **step down** (`self.token = None`) and the client gets a failure.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change (real run): `Ran 3 tests ... FAILED (failures=3)` (`AssertionError: True is not false` — the stale write was accepted). The reference `solution_partition.py` prints:
```
t=7 n1 write 3 rejected: token 1 < 2 -> steps down
  {"time": 7.8, "process": "c1", "type": "fail", "f": "write", "value": 3, "node": "n1", "error": "rejected: token 1 < 2"}
linearizable: True
```
A failed operation had no effect, so the checker leaves it out and the remaining history is linearizable.

## Try it (real run — `python try_it.py`)
```
tryIt 1: seed 13: n2 takes the lease at t=3, ticks with two leaders: 0
tryIt 1: seed 14: n2 takes the lease at t=5, ticks with two leaders: 1
tryIt 1: seed 15: n2 takes the lease at t=5, ticks with two leaders: 0
tryIt 2: without fencing: c1 read via n1 -> 1, linearizable: False
tryIt 2: with fencing: c1 read via n1 -> 1, linearizable: False
```
tryIt 1: a flaky link (50% of `n1`'s lease requests dropped) instead of a clean partition — leadership moves at different ticks per seed and a two-leader window appears in only one of three seeds. tryIt 2: fencing protects **writes**; a deposed leader that answers reads from its own memory still returns stale data. Reads must go through the fenced resource or a quorum (etcd's raft library: the leader checks with a quorum before serving a linearizable read), or rely on a lease whose safety depends on bounded clock drift.

## Agent assist (optional; tests use the fake model server only)
```bash
python agent_assist.py --fake        # deterministic stand-in model (no download)
python agent_assist.py               # a local model: LOCAL_MODEL_URL (default Ollama http://localhost:11434/v1), LOCAL_MODEL
```
Real run with `--fake`:
```
linearizable  agent: no             code: no             OK
stale_leader  agent: n2             code: n1             WRONG
lost_write    agent: c1 write 1     code: c1 write 3     WRONG
agent prose (unverified): during the partition n2 kept writing with an old lease, so the first acknowledged write was overwritten and later reads missed it.
```
The model only explains. `facts()` computes the truth from the events and the history (checker verdict; the node with the **lower** token during the two-leader window; the write a later read should have seen) and marks each claim `OK` or `WRONG`. The fake model makes two classic mistakes on purpose (it blames the newest lease holder and the first write). Never let the agent decide which node is fenced or which data to repair; never paste secrets into a prompt.

## Optional tools (pending a manual run)
Toxiproxy (a proxy with `enabled: false` = the `down` used here; `latency`, `timeout`, `packet_loss` toxics) and Maelstrom's `lin-kv` workload with a partition nemesis — see `documentation/LEARNING-TOOLS.md`.

## Platform notes
Pure computation except `agent_assist.py` (fake model server on `127.0.0.1`, OS-chosen port). Same output on macOS, Windows and Linux.
