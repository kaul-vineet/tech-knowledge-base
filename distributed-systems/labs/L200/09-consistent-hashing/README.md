# 09 · Sharding with consistent hashing (virtual nodes, key movement, hot keys)

`ring.py` puts each node on a hash ring at 100 positions (**virtual nodes**); a key belongs to the first vnode clockwise from the key's own hash. The demo measures, on 10,000 keys, how many keys move when node `E` joins or `D` leaves — ring vs naive `hash % N` — how even the load is with 1 / 10 / 100 vnodes, and what one hot key (20% of 100,000 requests) does to its shard. Hashes are md5 (stable across processes and OSes; Python's built-in `hash()` is salted per process), traffic is seeded: identical output on every run.

Files: `ring.py` (the lesson code) · `try_it.py` · `test_ring.py` · build task: `solution_ring.py` + `test_build_task.py` · optional agent assist: `agent_assist.py` + `test_agent_assist.py` (uses `labs/_shared/local_agent`). No HTTP in this lab — placement is pure computation.

## Run (Mac mini and Windows: same command inside the venv)
```bash
python ring.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run)
```
add E   : hash % N moves 80.3% of 10,000 keys; ring moves 18.9% (ideal 1/5 = 20.0%)
remove D: ring moves 24.5%; only D's keys moved: True
vnodes=1  : keys per node {'A': 309, 'B': 124, 'C': 4077, 'D': 5490} imbalance 2.20
vnodes=10 : keys per node {'A': 1169, 'B': 3969, 'C': 2147, 'D': 2715} imbalance 1.59
vnodes=100: keys per node {'A': 2577, 'B': 2466, 'C': 2509, 'D': 2448} imbalance 1.03
hot key : user:42 lives on B; requests per node {'A': 20790, 'B': 39738, 'C': 19976, 'D': 19496} imbalance 1.59
```
`imbalance` = busiest node ÷ average node. With `hash % N`, going from 4 to 5 nodes keeps a key only if `h % 4 == h % 5`, i.e. for about 1 key in 5 — so ~80% move.

## Test
```bash
python -m unittest -v     # Ran 10 tests ... OK (4 ring + 3 build-task tests against the solution + 3 agent-assist tests, fake server)
```

## Build task: replica placement with `nodes_for(key, n=3)`
Add `HashRing.nodes_for(key, n)` to `ring.py`: start where `node_for` starts and keep walking clockwise, **skipping vnodes of nodes you already picked**, until you have `n` different physical nodes; raise `ValueError` if the ring has fewer than `n` nodes. That is how Dynamo-style stores pick replicas (Cassandra's SimpleStrategy).
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change: `Ran 3 tests ... FAILED (errors=3)`. Reference: `solution_ring.py`, whose demo adds:
```
replicas: user:1 -> ['A', 'D', 'C'] | user:42 -> ['B', 'A', 'D']
add E   : E now holds a replica of 61.6% of keys (fair share 3 of 5 nodes = 60.0%)
```

## Try it (real run — `python try_it.py`)
```
tryIt 1: vnodes=1   add E -> moves 17.0%, taken from {'D': 1695}
tryIt 1: vnodes=100 add E -> moves 18.9%, taken from {'A': 488, 'B': 227, 'C': 540, 'D': 634}
tryIt 2: hot key split 8 ways -> requests per node {'A': 25565, 'B': 27462, 'C': 24940, 'D': 22033} imbalance 1.10
```

## Agent assist (optional): a local model proposes a replica layout — code decides
`agent_assist.py` asks a model to place 8 shards × 3 replicas on 6 nodes in 3 zones (n1,n2 → a; n3,n4 → b; n5,n6 → c), at most 4 replicas per node, one line per shard. `check()` enforces every rule (all shards present, 3 different known nodes, 3 different zones, capacity) and prints REJECTED with reasons; a rejected layout is never applied.
```bash
python agent_assist.py --fake     # deterministic fake model server (used by the tests)
python agent_assist.py            # a real local model: Ollama on the Mac mini (Metal) or the Windows PC
```
Real run with `--fake` (identical on every run):
```
agent proposal: S0: n1,n4,n5 | S1: n2,n3,n6 | S2: n1,n4,n5 | S3: n2,n3,n6 | S4: n1,n4,n5 | S5: n2,n1,n6 | S6: n1,n4,n5 | S7: n2,n3,n6
agent prose (unverified): every shard spans all zones and every node holds the same number of replicas.
checker: REJECTED
  - S5: zones ['a', 'a', 'c'] -> two replicas share a zone
  - n1: 5 replicas > capacity 4
```
The fake model breaks S5 on purpose and still claims the layout is perfect — exactly the kind of confident error the checker exists for. Real model: `ollama pull qwen2.5:1.5b`, then `LOCAL_MODEL=qwen2.5:1.5b python agent_assist.py` (Windows: `$env:LOCAL_MODEL="qwen2.5:1.5b"`). Not run against a real model here.
