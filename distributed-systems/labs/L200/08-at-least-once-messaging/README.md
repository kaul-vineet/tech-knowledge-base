# 08 · At-least-once messaging: ack, visibility timeout, redelivery, dead-letter queue

A tiny broker over HTTP (`broker.py`): `POST /send`, `POST /receive` (hands out the oldest visible message and hides it for `VISIBILITY` = 3 s), `POST /ack` (deletes it). A message that is not acked becomes visible again and is **redelivered**; after `MAX_RECEIVES` = 3 unacked receives it moves to the **dead-letter queue**. Two consumers charge an order (the side effect) and then crash 30% of the time **before** acking (seeded). One `poison` message crashes the handler every time. Simulated clock, identical output on every run.

Files: `broker.py` (the lesson code: broker semantics, consumer, demo) · `helpers.py` (plumbing: JSON handler, `call()`, `serve()`, `SimClock`) · `try_it.py` · `test_broker.py` · build task: `solution_broker.py` + `test_build_task.py`.

## Run (Mac mini and Windows: same command inside the venv)
```bash
python broker.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; seed 9)
```
t=0 c1 m1=o1 receive #1: charged, acked
t=0 c2 m2=o2 receive #1: charged, acked
t=1 c1 m3=o3 receive #1: charged, CRASHED before ack
t=1 c2 m4=o4 receive #1: charged, acked
t=2 c1 m5=o5 receive #1: charged, CRASHED before ack
t=2 c2 m6=o6 receive #1: charged, acked
t=3 c1 m7=poison receive #1: CRASHED while parsing
t=4 c1 m3=o3 receive #2: charged, acked
t=5 c1 m5=o5 receive #2: charged, CRASHED before ack
t=6 c1 m7=poison receive #2: CRASHED while parsing
t=8 c1 m5=o5 receive #3: charged, acked
t=9 c1 m7=poison receive #3: CRASHED while parsing
ledger: 9 charges for 6 orders -> 3 duplicates
dead-letter queue: ['poison']
```
Read it: nothing is lost (all 6 orders charged), but `o3` was charged twice and `o5` three times — the crash happened after the charge and before the ack. `m3` comes back at t=4 = received at t=1 + 3 s visibility. The poison message is dead-lettered on its 4th visible moment (t=12; no log line, the queue is then empty).

## Test
```bash
python -m unittest -v     # Ran 6 tests ... OK (4 broker tests + 2 build-task tests against the solution)
```

## Build task: make the consumer idempotent
Change `consume()` in `broker.py` so a redelivered message is **not charged again**: before the side effect, check whether this message id is already in the ledger; if so, ack it and log `duplicate -> skipped, acked`. In a real system the check and the charge share one database transaction (a unique key on the message id) — lesson 5's idempotency key, applied by the consumer.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change: `Ran 2 tests ... FAILED (failures=2)`. Reference: `solution_broker.py` (`python solution_broker.py` ends with `ledger: 6 charges for 6 orders -> 0 duplicates`).

## Try it (real run — `python try_it.py`, ~30 s: it runs the broker 92 times)
```
tryIt 1: VISIBILITY 3 s -> last delivery at t=9, 9 charges, DLQ ['poison']
tryIt 1: VISIBILITY 10 s -> last delivery at t=23, 9 charges, DLQ ['poison']
tryIt 2: MAX_RECEIVES 2 -> 12/30 runs dead-lettered a good order
tryIt 2: MAX_RECEIVES 3 -> 5/30 runs dead-lettered a good order
tryIt 2: MAX_RECEIVES 5 -> 2/30 runs dead-lettered a good order
```

## Platform notes
Same on the Mac mini and the Windows PC: `127.0.0.1`, OS-chosen port, simulated time (no sleeps). The real brokers in `equivalents` (RabbitMQ, NATS, Kafka) run in containers (Podman/Colima/Podman Desktop, lesson 1) — not used by this lab.
