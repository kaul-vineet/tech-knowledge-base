# Explain runs — commands and real output quoted in content/explain/

Every output quoted in a "What you see" or "See it in numbers" block of `content/explain/NN.md` comes from the runs
below, executed in this Linux sandbox (Python 3.12, stdlib only) on 2026-11-02, one lab at a time. Each entry records
the date, the working directory, the exact command and the full output. `research/explain_checks.py` checks every
number in those blocks against this file.

Not run here (marked "Expected (not run here)" in the explanations): etcd (lesson 7), k6 (lessons 11, 16),
OpenTelemetry SDK (lesson 15), Automerge via npm (lesson 18), TLC / TLA+ tools (lesson 21), real local models
(agent assists use the deterministic fake server only).

Differences from the lab READMEs / lesson JSON (the explanations quote what was observed here):
- Lesson 1: the first `python -m unittest` attempt failed 3 of 4 tests with `node1 did not start` while the shared
  sandbox was under heavy load (interpreter start-up exceeded the 15 s readiness deadline); the re-run passed 4/4.
- Lesson 2: latencies are machine-dependent (median 2.3 ms here; the concept note quotes the README's 4.7 ms).
- Lesson 15: span times vary per run (orders self time 82 ms here vs README 88 ms; tryIt 2 46% / 78% vs 55% / 76%).
- Lesson 16: `serve_realtime.py --check` is timing-based (765 x 200 / 435 x 503 / p99 197 ms here vs README 780 / 420 / 193).
- Lesson 18: `solution_crdts.py` part 3 prints a plain-LWW like-counter of 79 (lesson file: 81); both lose increments.
- Lesson 21: tryIt timings differ from the README (machine-dependent); verdicts and state counts match.
- Lessons 26 and 27 have no lab; their worked-problem arithmetic was recomputed with the short scripts recorded below.

### 01-demo
date: 2026-11-02T12:32Z
cwd: distributed-systems/labs/L100/01-setup-local-lab
cmd: env LAB_BASE_PORT=18001 python3 lab.py demo 3
```
node1 up on port 18001 -> /health OK
node2 up on port 18002 -> /health OK
node3 up on port 18003 -> /health OK
stopped 3 nodes
exit: 0
```

### 01-tests (earlier attempt, sandbox under load)
date: 2026-11-02T12:36Z
cwd: distributed-systems/labs/L100/01-setup-local-lab
cmd: python3 -m unittest
```
.EEE
======================================================================
ERROR: test_second_bind_on_same_port_fails (test_lab.TestLocalLab.test_second_bind_on_same_port_fails)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/test_lab.py", line 45, in test_second_bind_on_same_port_fails
    dup = subprocess.run([sys.executable, str(lab.HERE / "node.py"), "--port",
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/subprocess.py", line 550, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/subprocess.py", line 1209, in communicate
    stdout, stderr = self._communicate(input, endtime, timeout)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/subprocess.py", line 2116, in _communicate
    self._check_timeout(endtime, orig_timeout, stdout, stderr)
  File "/usr/lib/python3.12/subprocess.py", line 1253, in _check_timeout
    raise TimeoutExpired(
subprocess.TimeoutExpired: Command '['/opt/venv/bin/python3', '/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/node.py', '--port', '43235']' timed out after 10 seconds

======================================================================
ERROR: test_start_health_stop (test_lab.TestLocalLab.test_start_health_stop)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/lib/python3.12/urllib/request.py", line 1357, in do_open
    h.request(req.get_method(), req.selector, req.data, headers,
  File "/usr/lib/python3.12/http/client.py", line 1386, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1432, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1381, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1141, in _send_output
    self.send(msg)
  File "/usr/lib/python3.12/http/client.py", line 1085, in send
    self.connect()
  File "/usr/lib/python3.12/http/client.py", line 1051, in connect
    self.sock = self._create_connection(
                ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 865, in create_connection
    raise exceptions[0]
  File "/usr/lib/python3.12/socket.py", line 850, in create_connection
    sock.connect(sa)
ConnectionRefusedError: [Errno 111] Connection refused

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 26, in start
    health(n["port"]); break
    ^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 12, in health
    with OPENER.open(f"http://{host}:{port}/health", timeout=timeout) as r:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 515, in open
    response = self._open(req, data)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 532, in _open
    result = self._call_chain(self.handle_open, protocol, protocol +
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 492, in _call_chain
    result = func(*args)
             ^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 1386, in http_open
    return self.do_open(http.client.HTTPConnection, req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 1360, in do_open
    raise URLError(err)
urllib.error.URLError: <urlopen error [Errno 111] Connection refused>

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/test_lab.py", line 23, in test_start_health_stop
    nodes = lab.start(ports)
            ^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 29, in start
    stop(nodes); raise RuntimeError(f"{n['name']} did not start")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: node1 did not start

======================================================================
ERROR: test_stop_by_saved_pid (test_lab.TestLocalLab.test_stop_by_saved_pid)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/lib/python3.12/urllib/request.py", line 1357, in do_open
    h.request(req.get_method(), req.selector, req.data, headers,
  File "/usr/lib/python3.12/http/client.py", line 1386, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1432, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1381, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.12/http/client.py", line 1141, in _send_output
    self.send(msg)
  File "/usr/lib/python3.12/http/client.py", line 1085, in send
    self.connect()
  File "/usr/lib/python3.12/http/client.py", line 1051, in connect
    self.sock = self._create_connection(
                ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 865, in create_connection
    raise exceptions[0]
  File "/usr/lib/python3.12/socket.py", line 850, in create_connection
    sock.connect(sa)
ConnectionRefusedError: [Errno 111] Connection refused

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 26, in start
    health(n["port"]); break
    ^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 12, in health
    with OPENER.open(f"http://{host}:{port}/health", timeout=timeout) as r:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 515, in open
    response = self._open(req, data)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 532, in _open
    result = self._call_chain(self.handle_open, protocol, protocol +
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 492, in _call_chain
    result = func(*args)
             ^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 1386, in http_open
    return self.do_open(http.client.HTTPConnection, req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/urllib/request.py", line 1360, in do_open
    raise URLError(err)
urllib.error.URLError: <urlopen error [Errno 111] Connection refused>

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/test_lab.py", line 36, in test_stop_by_saved_pid
    nodes = lab.start(free_ports(1))
            ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/distributed-systems/labs/L100/01-setup-local-lab/lab.py", line 29, in start
    stop(nodes); raise RuntimeError(f"{n['name']} did not start")
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: node1 did not start

----------------------------------------------------------------------
Ran 4 tests in 75.407s

FAILED (errors=3)
exit: 1
```


### 01-tests
date: 2026-11-02T14:16Z
cwd: distributed-systems/labs/L100/01-setup-local-lab
cmd: python3 -m unittest
```
....
----------------------------------------------------------------------
Ran 4 tests in 22.348s

OK
exit: 0
```

### 01-tryit
date: 2026-11-02T12:35Z
cwd: distributed-systems/labs/L100/01-setup-local-lab
cmd: python3 try_it.py
```
tryIt 1: second node exit code 1: OSError: [Errno 98] Address already in use
         node1 still healthy: True
tryIt 2: node1=OK, node2=ConnectionRefusedError, node3=OK
exit: 0
```

### 02-demo
date: 2026-11-02T12:39Z
cwd: distributed-systems/labs/L100/02-two-services
cmd: python3 two_services.py
```
service B listening on http://127.0.0.1:41303
A -> B  GET /price?item=apple -> 200 {'item': 'apple', 'price': 3}  (7.0 ms)
A -> B  GET /price?item=pear  -> 200 {'item': 'pear', 'price': 4}  (2.3 ms)
A -> B  GET /price?item=plum  -> 200 {'item': 'plum', 'price': 5}  (3.6 ms)
A -> B  GET /price?item=apple -> 200 {'item': 'apple', 'price': 3}  (2.0 ms)
A -> B  GET /price?item=pear  -> 200 {'item': 'pear', 'price': 4}  (2.3 ms)
A -> B  GET /price?item=kiwi  -> 404 {'error': "unknown item 'kiwi'"}
latency ms: min=2.0 median=2.3 max=7.0
exit: 0
```

### 02-tests
date: 2026-11-02T12:41Z
cwd: distributed-systems/labs/L100/02-two-services
cmd: python3 -m unittest
```
..
----------------------------------------------------------------------
Ran 2 tests in 0.581s

OK
exit: 0
```

### 02-tryit
date: 2026-11-02T12:40Z
cwd: distributed-systems/labs/L100/02-two-services
cmd: python3 try_it.py
```
tryIt 1: URLError -> ConnectionRefusedError: Connection refused
tryIt 2: every call >= 50 ms: True; 3 sequential calls >= 150 ms: True (total 156 ms)
exit: 0
```

### 03-demo
date: 2026-11-02T12:42Z
cwd: distributed-systems/labs/L100/03-timeouts
cmd: python3 timeouts.py
```
B takes 2.0 s to answer.
A timeout=None -> 200 ok               after 2.0 s
A timeout=0.5  -> FAILED TimeoutError  after 0.5 s
B latency: p50=40 ms  p99=88 ms  p99.9=116 ms
suggested timeout for A->B: 0.116 s
exit: 0
```

### 03-strict
date: 2026-11-02T12:43Z
cwd: distributed-systems/labs/L100/03-timeouts
cmd: python3 -c import timeouts; print(timeouts.choose_timeout(false_timeout_rate=0.01))
```
B latency: p50=40 ms  p99=88 ms  p99.9=116 ms
0.088
exit: 0
```

### 03-tryit
date: 2026-11-02T12:43Z
cwd: distributed-systems/labs/L100/03-timeouts
cmd: python3 try_it.py
```
tryIt 1: delay=0.05 timeout=0.1 -> 200 ok
tryIt 1: delay=0.2  timeout=0.1 -> FAILED TimeoutError
tryIt 2: call 1 timeout=0.5 s -> 200 ok after 0.3 s
tryIt 2: call 2 timeout=0.2 s -> FAILED TimeoutError after 0.2 s
exit: 0
```

### 04-agent
date: 2026-11-02T12:47Z
cwd: distributed-systems/labs/L100/04-retries-backoff-jitter
cmd: python3 agent_assist.py --fake
```
log: 126 attempts from 80 requests (seeded, seed 7)
field        agent     code  verdict
attempts       126      126  ok
errors          46       46  ok
p50_ms        32.7     24.1  WRONG
p99_ms       210.6    141.0  WRONG
agent prose (unverified): most requests succeed; about 37% of attempts fail with 503 and are retried, and a few slow calls stretch the latency tail.
flagged: p50_ms, p99_ms -> report the code's numbers, not the agent's
exit: 0
```

### 04-demo
date: 2026-11-02T12:47Z
cwd: distributed-systems/labs/L100/04-retries-backoff-jitter
cmd: python3 retries.py
```
full-jitter ceilings (s): [0.02, 0.04, 0.08, 0.16, 0.32, 0.5]
GET /missing -> ('gave up (404)', 1) (404: not retried)
--- B flaky (30% 503) ---
req 01: 200                          attempts=1 sleeps=[] tokens=10.0
req 02: 200                          attempts=4 sleeps=[0.006, 0.006, 0.052] tokens=7.5
req 03: 200                          attempts=1 sleeps=[] tokens=8.0
req 04: 200                          attempts=1 sleeps=[] tokens=8.5
req 05: 200                          attempts=2 sleeps=[0.001] tokens=8.0
req 06: 200                          attempts=3 sleeps=[0.011, 0.015] tokens=6.5
req 07: gave up (retry budget empty) attempts=2 sleeps=[0.001] tokens=4.5
req 08: 200                          attempts=1 sleeps=[] tokens=5.0
req 09: 200                          attempts=1 sleeps=[] tokens=5.5
req 10: gave up (retry budget empty) attempts=1 sleeps=[] tokens=4.5
8/10 succeeded, 17 attempts (load x1.7, worst case x4.0)
--- B sick (90% 503) ---
req 01: gave up (retry budget empty) attempts=1 sleeps=[] tokens=3.5
req 02: gave up (retry budget empty) attempts=1 sleeps=[] tokens=2.5
req 03: gave up (retry budget empty) attempts=1 sleeps=[] tokens=1.5
req 04: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.5
req 05: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 06: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 07: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 08: 200                          attempts=1 sleeps=[] tokens=0.5
req 09: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 10: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
1/10 succeeded, 10 attempts (load x1.0, worst case x4.0)
exit: 0
```

### 04-tryit
date: 2026-11-02T12:47Z
cwd: distributed-systems/labs/L100/04-retries-backoff-jitter
cmd: python3 try_it.py
```
tryIt 1: max_attempts=1: 5/10 succeeded, 10 attempts
tryIt 1: max_attempts=4: 8/10 succeeded, 17 attempts
tryIt 2: no jitter  : busiest 10 ms slot has 100 of 100 retries
tryIt 2: full jitter: busiest 10 ms slot has 17 of 100 retries
exit: 0
```

### 05-demo
date: 2026-11-02T12:48Z
cwd: distributed-systems/labs/L100/05-idempotency-keys
cmd: python3 idempotency.py
```
--- Idempotency-Key OFF: 5 orders x 10 ---
order 1: 201 {'charge_id': 'ch_2'} after 2 attempt(s)
order 2: 201 {'charge_id': 'ch_4'} after 2 attempt(s)
order 3: 201 {'charge_id': 'ch_5'} after 1 attempt(s)
order 4: 201 {'charge_id': 'ch_8'} after 3 attempt(s)
order 5: 201 {'charge_id': 'ch_11'} after 3 attempt(s)
ledger: 11 charges, total 110 (expected 50)
--- Idempotency-Key ON: 5 orders x 10 ---
order 1: 201 {'charge_id': 'ch_1'} after 2 attempt(s)
order 2: 201 {'charge_id': 'ch_2'} after 1 attempt(s)
order 3: 201 {'charge_id': 'ch_3'} after 2 attempt(s)
order 4: 201 {'charge_id': 'ch_4'} after 1 attempt(s)
order 5: 201 {'charge_id': 'ch_5'} after 1 attempt(s)
ledger: 5 charges, total 50 (expected 50)
reuse key with amount 99 -> (422, {'title': 'Idempotency-Key is already used'})
no key at all            -> (400, {'title': 'Idempotency-Key is missing or malformed'})
exit: 0
```

### 05-tryit
date: 2026-11-02T12:48Z
cwd: distributed-systems/labs/L100/05-idempotency-keys
cmd: python3 try_it.py
```
tryIt 1: new key per attempt -> ledger 11 charges, total 110 (expected 50)
tryIt 2: same key x3 -> [(201, {'charge_id': 'ch_1'}), (201, {'charge_id': 'ch_1'}), (201, {'charge_id': 'ch_1'})]; ledger 1 charge(s)
exit: 0
```

### 06-demo
date: 2026-11-02T12:49Z
cwd: distributed-systems/labs/L100/06-lamport-clocks
cmd: python3 lamport.py
```
--- sorted by wall clock: 2 causality violation(s) ---
  L=3  wall=-0.050s  B: recv 'create order' from A
  L=4  wall=-0.040s  B: reserve stock
  L=5  wall=-0.030s  B: send 'charge card' to C
  L=1  wall=+0.010s  A: user clicks Buy
  L=2  wall=+0.020s  A: send 'create order' to B
  L=8  wall=+0.080s  A: recv 'payment ok' from C
  L=6  wall=+0.100s  C: recv 'charge card' from B
  L=9  wall=+0.100s  A: show receipt
  L=7  wall=+0.110s  C: send 'payment ok' to A
  L=8  wall=+0.130s  C: write audit log
--- sorted by (Lamport, node): 0 causality violation(s) ---
  L=1  wall=+0.010s  A: user clicks Buy
  L=2  wall=+0.020s  A: send 'create order' to B
  L=3  wall=-0.050s  B: recv 'create order' from A
  L=4  wall=-0.040s  B: reserve stock
  L=5  wall=-0.030s  B: send 'charge card' to C
  L=6  wall=+0.100s  C: recv 'charge card' from B
  L=7  wall=+0.110s  C: send 'payment ok' to A
  L=8  wall=+0.080s  A: recv 'payment ok' from C
  L=8  wall=+0.130s  C: write audit log
  L=9  wall=+0.100s  A: show receipt
exit: 0
```

### 06-tryit
date: 2026-11-02T12:49Z
cwd: distributed-systems/labs/L100/06-lamport-clocks
cmd: python3 try_it.py
```
tryIt 1: without max(): m1 send L=2, recv L=1; (Lamport, node) order has 2 violation(s)
tryIt 2: B  5 ms slow -> wall-clock order 0 violation(s), (Lamport, node) order 0
tryIt 2: B 15 ms slow -> wall-clock order 1 violation(s), (Lamport, node) order 0
exit: 0
```

### 07-buildtask
date: 2026-11-02T13:00Z
cwd: distributed-systems/labs/L200/07-leader-election-leases
cmd: python3 -m unittest test_build_task
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.855s

OK
exit: 0
```

### 07-demo
date: 2026-11-02T13:00Z
cwd: distributed-systems/labs/L200/07-leader-election-leases
cmd: python3 election.py
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
exit: 0
```

### 07-tryit
date: 2026-11-02T13:00Z
cwd: distributed-systems/labs/L200/07-leader-election-leases
cmd: python3 try_it.py
```
tryIt 1: fencing off -> accepted | n1's stale write landed after n2's write at t=6
tryIt 2: TTL 3 s -> holder per tick 111112222 | n2 takes over at t=5
tryIt 2: TTL 6 s -> holder per tick 111111111 | no failover: n1 renewed in time after its pause
exit: 0
```

### 08-buildtask
date: 2026-11-02T13:03Z
cwd: distributed-systems/labs/L200/08-at-least-once-messaging
cmd: python3 -m unittest test_build_task
```
..
----------------------------------------------------------------------
Ran 2 tests in 1.264s

OK
exit: 0
```

### 08-demo
date: 2026-11-02T13:02Z
cwd: distributed-systems/labs/L200/08-at-least-once-messaging
cmd: python3 broker.py
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
exit: 0
```

### 08-tryit
date: 2026-11-02T13:02Z
cwd: distributed-systems/labs/L200/08-at-least-once-messaging
cmd: python3 try_it.py
```
tryIt 1: VISIBILITY 3 s -> last delivery at t=9, 9 charges, DLQ ['poison']
tryIt 1: VISIBILITY 10 s -> last delivery at t=23, 9 charges, DLQ ['poison']
tryIt 2: MAX_RECEIVES 2 -> 12/30 runs dead-lettered a good order
tryIt 2: MAX_RECEIVES 3 -> 5/30 runs dead-lettered a good order
tryIt 2: MAX_RECEIVES 5 -> 2/30 runs dead-lettered a good order
exit: 0
```

### 09-agent
date: 2026-11-02T13:06Z
cwd: distributed-systems/labs/L200/09-consistent-hashing
cmd: python3 agent_assist.py --fake
```
agent proposal: S0: n1,n4,n5 | S1: n2,n3,n6 | S2: n1,n4,n5 | S3: n2,n3,n6 | S4: n1,n4,n5 | S5: n2,n1,n6 | S6: n1,n4,n5 | S7: n2,n3,n6
agent prose (unverified): every shard spans all zones and every node holds the same number of replicas.
checker: REJECTED
  - S5: zones ['a', 'a', 'c'] -> two replicas share a zone
  - n1: 5 replicas > capacity 4
exit: 0
```

### 09-demo
date: 2026-11-02T13:05Z
cwd: distributed-systems/labs/L200/09-consistent-hashing
cmd: python3 ring.py
```
add E   : hash % N moves 80.3% of 10,000 keys; ring moves 18.9% (ideal 1/5 = 20.0%)
remove D: ring moves 24.5%; only D's keys moved: True
vnodes=1  : keys per node {'A': 309, 'B': 124, 'C': 4077, 'D': 5490} imbalance 2.20
vnodes=10 : keys per node {'A': 1169, 'B': 3969, 'C': 2147, 'D': 2715} imbalance 1.59
vnodes=100: keys per node {'A': 2577, 'B': 2466, 'C': 2509, 'D': 2448} imbalance 1.03
hot key : user:42 lives on B; requests per node {'A': 20790, 'B': 39738, 'C': 19976, 'D': 19496} imbalance 1.59
exit: 0
```

### 09-tryit
date: 2026-11-02T13:05Z
cwd: distributed-systems/labs/L200/09-consistent-hashing
cmd: python3 try_it.py
```
tryIt 1: vnodes=1   add E -> moves 17.0%, taken from {'D': 1695}
tryIt 1: vnodes=100 add E -> moves 18.9%, taken from {'A': 488, 'B': 227, 'C': 540, 'D': 634}
tryIt 2: hot key split 8 ways -> requests per node {'A': 25565, 'B': 27462, 'C': 24940, 'D': 22033} imbalance 1.10
exit: 0
```

### 10-demo
date: 2026-11-02T13:07Z
cwd: distributed-systems/labs/L200/10-caching-invalidation
cmd: python3 cache.py
```
cache-aside  : [5, 5, 5] -> db reads 1 (1 miss, 2 hits)
no invalidate: t= 0s read 5 (STALE, db has 7)
no invalidate: t=10s read 5 (STALE, db has 7)
no invalidate: t=29s read 5 (STALE, db has 7)
no invalidate: t=30s read 7 (fresh)
invalidate   : t=100s write 9 -> read 9 (fresh)
herd         : 50 concurrent reads of a cold key -> 50 db reads, values [9]
exit: 0
```

### 10-solution
date: 2026-11-02T13:07Z
cwd: distributed-systems/labs/L200/10-caching-invalidation
cmd: python3 -c 
import solution_cache as s
from helpers import SimClock
db=s.PriceDB(); svc=s.PriceService(db, s.TTLCache(30, SimClock()))
print('coalesced herd:', s.herd(svc))
```
coalesced herd: (1, [5])
exit: 0
```

### 10-tryit
date: 2026-11-02T13:07Z
cwd: distributed-systems/labs/L200/10-caching-invalidation
cmd: python3 try_it.py
```
tryIt 1: TTL 30 s -> 30 stale reads of 60, 2 db reads
tryIt 1: TTL  5 s -> 5 stale reads of 60, 12 db reads
tryIt 2: race -> db has 11, cache serves 5 until t=30 (TTL)
exit: 0
```

### 11-buildtask
date: 2026-11-02T13:09Z
cwd: distributed-systems/labs/L200/11-rate-limiting
cmd: python3 -m unittest test_build_task
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.159s

OK
exit: 0
```

### 11-demo
date: 2026-11-02T13:09Z
cwd: distributed-systems/labs/L200/11-rate-limiting
cmd: python3 ratelimit.py
```
alice trace: 200 200 200 200 200 429(wait 1) 200 200 429(wait 1) 200 200 429(wait 1) 200 200 429(wait 1) 200
alice (honors Retry-After): 12 ok, 4 x 429, done at t=4s
bob   (retries every 0.1 s): 12 ok, 35 x 429, done at t=3.5s
carol (honors Retry-After): 3 ok, 0 x 429, done at t=0s
exit: 0
```

### 11-tryit
date: 2026-11-02T13:09Z
cwd: distributed-systems/labs/L200/11-rate-limiting
cmd: python3 try_it.py
```
tryIt 1: 10 requests within 10 ms across a second boundary -> fixed window allows 10, token bucket allows 5
tryIt 2: BURST 5 -> alice 12 ok, 4 x 429, done at t=4s
tryIt 2: BURST 1 -> alice 12 ok, 11 x 429, done at t=11s
exit: 0
```

### 12-buildtask-mine
date: 2026-11-02T13:13Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: env BUILD_TARGET=mine python3 -m unittest test_build_task
```
FFF
======================================================================
FAIL: test_safe_for_many_seeds (test_build_task.ElectionRestriction.test_safe_for_many_seeds)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/12-raft-replicated-log/test_build_task.py", line 23, in test_safe_for_many_seeds
    self.assertEqual(rf.stale_leader_scenario(rf.Node, seed).checker.violations, [], f"seed {seed}")
AssertionError: Lists differ: ['t=23 LOST committed entry 1 (1:x=1): n2 [144 chars]ere'] != []

First list contains 3 additional elements.
First extra element 0:
't=23 LOST committed entry 1 (1:x=1): n2 now has 2:x=9 there'

+ []
- ['t=23 LOST committed entry 1 (1:x=1): n2 now has 2:x=9 there',
-  't=23 LOST committed entry 2 (1:x=2): n2 now has nothing there',
-  't=24 LOST committed entry 1 (1:x=1): n3 now has 2:x=9 there'] : seed 1

======================================================================
FAIL: test_stale_follower_cannot_win_and_nothing_committed_is_lost (test_build_task.ElectionRestriction.test_stale_follower_cannot_win_and_nothing_committed_is_lost)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/12-raft-replicated-log/test_build_task.py", line 17, in test_stale_follower_cannot_win_and_nothing_committed_is_lost
    self.assertEqual(s.checker.violations, [])
AssertionError: Lists differ: ['t=27 LOST committed entry 1 (1:x=1): n2 [144 chars]ere'] != []

First list contains 3 additional elements.
First extra element 0:
't=27 LOST committed entry 1 (1:x=1): n2 now has 2:x=9 there'

+ []
- ['t=27 LOST committed entry 1 (1:x=1): n2 now has 2:x=9 there',
-  't=27 LOST committed entry 2 (1:x=2): n2 now has nothing there',
-  't=28 LOST committed entry 1 (1:x=1): n3 now has 2:x=9 there']

======================================================================
FAIL: test_vote_rule_compares_last_term_then_length (test_build_task.ElectionRestriction.test_vote_rule_compares_last_term_then_length)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/12-raft-replicated-log/test_build_task.py", line 33, in test_vote_rule_compares_last_term_then_length
    self.assertEqual(node.voted_for == "n3", expected, (last_term, last_index))
AssertionError: True != False : (2, 1)

----------------------------------------------------------------------
Ran 3 tests in 0.013s

FAILED (failures=3)
exit: 1
```

### 12-buildtask-solution
date: 2026-11-02T13:14Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: python3 -m unittest test_build_task
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.070s

OK
exit: 0
```

### 12-demo
date: 2026-11-02T13:13Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: python3 raft.py
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
exit: 0
```

### 12-solution-demo
date: 2026-11-02T13:14Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: python3 solution_raft.py
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
t=25 n2 denies n3: candidate log (term, index) (0, 0) < mine (1, 2)
t=33 n2 starts election for term 3 (log 1:x=1 1:x=2)
t=35 n2 becomes leader for term 3 with votes ['n2', 'n3']
4) failure lab: stale follower elected, then writes x=9
   n1 term 1 DOWN      log [1:x=1 1:x=2] commit 2
   n2 term 3 leader    log [1:x=1 1:x=2 3:x=9] commit 3
   n3 term 3 follower  log [1:x=1 1:x=2 3:x=9] commit 3
safety violations: 0
exit: 0
```

### 12-solution-lab
date: 2026-11-02T13:14Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: python3 -c 
import solution_raft as s
c = s.stale_leader_scenario(s.Node, 7)
print('safety violations:', len(c.checker.violations))
```
safety violations: 0
exit: 0
```

### 12-tryit
date: 2026-11-02T13:13Z
cwd: distributed-systems/labs/L300/12-raft-replicated-log
cmd: python3 try_it.py
```
tryIt 1: followers down -> n1 log has 2 entries, commit index stays 1 (x=5 appended, never committed)
tryIt 2: raft.py (no log check): committed entries lost in 11 of 20 seeds
tryIt 2: solution_raft.py (log check): committed entries lost in 0 of 20 seeds
exit: 0
```

### 13-agent
date: 2026-11-02T13:20Z
cwd: distributed-systems/labs/L300/13-partitions-fault-injection
cmd: python3 agent_assist.py --fake
```
linearizable  agent: no             code: no             OK
stale_leader  agent: n2             code: n1             WRONG
lost_write    agent: c1 write 1     code: c1 write 3     WRONG
agent prose (unverified): during the partition n2 kept writing with an old lease, so the first acknowledged write was overwritten and later reads missed it.
exit: 0
```

### 13-buildtask-mine
date: 2026-11-02T13:20Z
cwd: distributed-systems/labs/L300/13-partitions-fault-injection
cmd: env BUILD_TARGET=mine python3 -m unittest test_build_task
```
FFF
======================================================================
FAIL: test_fenced_out_node_steps_down (test_build_task.Fencing.test_fenced_out_node_steps_down)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/13-partitions-fault-injection/test_build_task.py", line 26, in test_fenced_out_node_steps_down
    self.assertEqual(leaders[8], ["n2"])  # n1 gave up at t=7, before the heal at t=9
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: ['n1', 'n2'] != ['n2']

First differing element 0:
'n1'
'n2'

First list contains 1 additional elements.
First extra element 1:
'n2'

- ['n1', 'n2']
+ ['n2']

======================================================================
FAIL: test_stale_write_is_rejected_and_history_is_linearizable (test_build_task.Fencing.test_stale_write_is_rejected_and_history_is_linearizable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/13-partitions-fault-injection/test_build_task.py", line 20, in test_stale_write_is_rejected_and_history_is_linearizable
    self.assertFalse(stale["ok"])
AssertionError: True is not false

======================================================================
FAIL: test_storage_keeps_the_newest_value (test_build_task.Fencing.test_storage_keeps_the_newest_value)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/13-partitions-fault-injection/test_build_task.py", line 32, in test_storage_keeps_the_newest_value
    self.assertEqual(s.value, "new")
AssertionError: 'old' != 'new'
- old
+ new


----------------------------------------------------------------------
Ran 3 tests in 0.008s

FAILED (failures=3)
exit: 1
```

### 13-demo
date: 2026-11-02T13:18Z
cwd: distributed-systems/labs/L300/13-partitions-fault-injection
cmd: python3 partition.py
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
exit: 0
```

### 13-solution
date: 2026-11-02T13:20Z
cwd: distributed-systems/labs/L300/13-partitions-fault-injection
cmd: python3 solution_partition.py
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
t=7 n1 write 3 rejected: token 1 < 2 -> steps down
t=9 fault: heal
leaders per tick: 0:n1 1:n1 2:n1 3:n1 4:n1+n2 5:n1+n2 6:n1+n2 7:n1+n2 8:n2 9:n2 10:n2
history (JSON lines):
  {"time": 1, "process": "c1", "type": "invoke", "f": "write", "value": 1, "node": "n1"}
  {"time": 1.5, "process": "c1", "type": "ok", "f": "write", "value": 1, "node": "n1"}
  {"time": 6, "process": "c2", "type": "invoke", "f": "write", "value": 2, "node": "n2"}
  {"time": 6.5, "process": "c2", "type": "ok", "f": "write", "value": 2, "node": "n2"}
  {"time": 7, "process": "c1", "type": "invoke", "f": "write", "value": 3, "node": "n1"}
  {"time": 7.8, "process": "c1", "type": "fail", "f": "write", "value": 3, "node": "n1", "error": "rejected: token 1 < 2"}
  {"time": 8, "process": "c2", "type": "invoke", "f": "read", "value": null, "node": "n2"}
  {"time": 8.5, "process": "c2", "type": "ok", "f": "read", "value": 2, "node": "n2"}
linearizable: True
exit: 0
```

### 13-tryit
date: 2026-11-02T13:19Z
cwd: distributed-systems/labs/L300/13-partitions-fault-injection
cmd: python3 try_it.py
```
tryIt 1: seed 13: n2 takes the lease at t=3, ticks with two leaders: 0
tryIt 1: seed 14: n2 takes the lease at t=5, ticks with two leaders: 1
tryIt 1: seed 15: n2 takes the lease at t=5, ticks with two leaders: 0
tryIt 2: without fencing: c1 read via n1 -> 1, linearizable: False
tryIt 2: with fencing: c1 read via n1 -> 1, linearizable: False
exit: 0
```

### 14-buildtask-mine
date: 2026-11-02T13:24Z
cwd: distributed-systems/labs/L300/14-sagas-compensation
cmd: env BUILD_TARGET=mine python3 -m unittest test_build_task
```
FFEF
======================================================================
ERROR: test_crash_before_charge_is_logged_is_also_safe (test_build_task.Compensation.test_crash_before_charge_is_logged_is_also_safe)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/14-sagas-compensation/test_build_task.py", line 48, in test_crash_before_charge_is_logged_is_also_safe
    sg.Orchestrator(orders, payments, shipping, log).recover()  # charge is in doubt -> compensated
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Orchestrator' object has no attribute 'recover'

======================================================================
FAIL: test_compensations_run_in_reverse_order (test_build_task.Compensation.test_compensations_run_in_reverse_order)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/14-sagas-compensation/test_build_task.py", line 25, in test_compensations_run_in_reverse_order
    self.assertEqual(steps, [("charge", "compensating"), ("charge", "compensated"),
AssertionError: Lists differ: [] != [('charge', 'compensating'), ('charge', 'c[88 chars]ed')]

Second list contains 5 additional elements.
First extra element 0:
('charge', 'compensating')

- []
+ [('charge', 'compensating'),
+  ('charge', 'compensated'),
+  ('create', 'compensating'),
+  ('create', 'compensated'),
+  ('saga', 'compensated')]

======================================================================
FAIL: test_crash_after_refund_then_recover_refunds_once (test_build_task.Compensation.test_crash_after_refund_then_recover_refunds_once)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/14-sagas-compensation/test_build_task.py", line 33, in test_crash_after_refund_then_recover_refunds_once
    with self.assertRaises(Crash):
         ^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Crash not raised

======================================================================
FAIL: test_failed_shipping_refunds_and_cancels (test_build_task.Compensation.test_failed_shipping_refunds_and_cancels)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/14-sagas-compensation/test_build_task.py", line 19, in test_failed_shipping_refunds_and_cancels
    self.assertEqual(sg.audit(*services), [])
AssertionError: Lists differ: ['o1: FAILED, shipped=False, money kept=10[103 chars] 60'] != []

First list contains 3 additional elements.
First extra element 0:
'o1: FAILED, shipped=False, money kept=10 of 10'

+ []
- ['o1: FAILED, shipped=False, money kept=10 of 10',
-  'o5: FAILED, shipped=False, money kept=50 of 50',
-  'o6: FAILED, shipped=False, money kept=60 of 60']

----------------------------------------------------------------------
Ran 4 tests in 0.018s

FAILED (failures=3, errors=1)
exit: 1
```

### 14-choreo
date: 2026-11-02T13:23Z
cwd: distributed-systems/labs/L300/14-sagas-compensation
cmd: python3 choreography.py
```
choreography: 21 events delivered, audit: OK
exit: 0
```

### 14-demo
date: 2026-11-02T13:23Z
cwd: distributed-systems/labs/L300/14-sagas-compensation
cmd: python3 saga.py
```
happy path: {'o1': 'completed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'completed', 'o6': 'completed'} | audit: OK
fault (30% of shipments fail, seed 14): {'o1': 'failed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'failed', 'o6': 'failed'}
saga log of o1 (JSON lines):
  {"saga": "o1", "step": "saga", "status": "started", "amount": 10}
  {"saga": "o1", "step": "create", "status": "done"}
  {"saga": "o1", "step": "charge", "status": "done"}
  {"saga": "o1", "step": "ship", "status": "failed", "error": "no courier slot"}
audit:
  o1: FAILED, shipped=False, money kept=10 of 10
  o5: FAILED, shipped=False, money kept=50 of 50
  o6: FAILED, shipped=False, money kept=60 of 60
exit: 0
```

### 14-solution
date: 2026-11-02T13:24Z
cwd: distributed-systems/labs/L300/14-sagas-compensation
cmd: python3 solution_saga.py
```
happy path: {'o1': 'completed', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'completed', 'o6': 'completed'} | audit: OK
fault (30% of shipments fail, seed 14): {'o1': 'compensated', 'o2': 'completed', 'o3': 'completed', 'o4': 'completed', 'o5': 'compensated', 'o6': 'compensated'}
saga log of o1 (JSON lines):
  {"saga": "o1", "step": "saga", "status": "started", "amount": 10}
  {"saga": "o1", "step": "create", "status": "done"}
  {"saga": "o1", "step": "charge", "status": "done"}
  {"saga": "o1", "step": "ship", "status": "failed", "error": "no courier slot"}
  {"saga": "o1", "step": "charge", "status": "compensating"}
  {"saga": "o1", "step": "charge", "status": "compensated"}
  {"saga": "o1", "step": "create", "status": "compensating"}
  {"saga": "o1", "step": "create", "status": "compensated"}
  {"saga": "o1", "step": "saga", "status": "compensated"}
audit:
  OK
exit: 0
```

### 14-tryit
date: 2026-11-02T13:23Z
cwd: distributed-systems/labs/L300/14-sagas-compensation
cmd: python3 try_it.py
```
    orchestrator died right after refund('o1', 10)
tryIt 1: idempotent refund=False: refunds [-10, -10], audit: ['o1: CANCELLED, shipped=False, money kept=-10 of 10']
    orchestrator died right after refund('o1', 10)
tryIt 1: idempotent refund=True: refunds [-10], audit: OK
tryIt 2: lesson Payments: 32 deliveries, audit: | o6: CANCELLED, shipped=False, money kept=-60 of 60
tryIt 2: solution Payments: 32 deliveries, audit: | OK
exit: 0
```

### 15-buildtask-mine
date: 2026-11-02T13:31Z
cwd: distributed-systems/labs/L300/15-distributed-tracing
cmd: env BUILD_TARGET=mine python3 -m unittest test_build_task
```
FFF.
======================================================================
FAIL: test_authorize_is_a_child_of_create (test_build_task.Propagation.test_authorize_is_a_child_of_create)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/15-distributed-tracing/test_build_task.py", line 26, in test_authorize_is_a_child_of_create
    self.assertEqual(self.by_name["GET /authorize"]["parent_id"], self.by_name["GET /create"]["span_id"])
AssertionError: None != 'e9bb466a28738582'

======================================================================
FAIL: test_critical_path_now_sees_payments (test_build_task.Propagation.test_critical_path_now_sees_payments)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/15-distributed-tracing/test_build_task.py", line 30, in test_critical_path_now_sees_payments
    self.assertEqual(path, ["GET /checkout", "GET /create", "GET /authorize", "GET /receipt"])
AssertionError: Lists differ: ['GET /checkout', 'GET /create', 'GET /receipt'] != ['GET /checkout', 'GET /create', 'GET /authorize', 'GET /receipt']

First differing element 2:
'GET /receipt'
'GET /authorize'

Second list contains 1 additional elements.
First extra element 3:
'GET /receipt'

- ['GET /checkout', 'GET /create', 'GET /receipt']
+ ['GET /checkout', 'GET /create', 'GET /authorize', 'GET /receipt']
?                                      ++++++++++++++++++


======================================================================
FAIL: test_one_trace_no_orphans (test_build_task.Propagation.test_one_trace_no_orphans)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/15-distributed-tracing/test_build_task.py", line 22, in test_one_trace_no_orphans
    self.assertEqual(len(traces(self.spans)), 1)
AssertionError: 2 != 1

----------------------------------------------------------------------
Ran 4 tests in 1.776s

FAILED (failures=3)
exit: 1
```

### 15-demo
date: 2026-11-02T13:28Z
cwd: distributed-systems/labs/L300/15-distributed-tracing
cmd: python3 tracing.py
```
spans (JSON lines, one per request):
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0942dc06bc69f265", "parent_id": null, "service": "gateway", "name": "GET /checkout", "start": 0.0, "end": 98.7}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "e9bb466a28738582", "parent_id": "0942dc06bc69f265", "service": "orders", "name": "GET /create", "start": 5.6, "end": 87.5}
  {"trace_id": "0e11160004524a7c3d2bd371fc80be13", "span_id": "ce0c3f08e12656f1", "parent_id": null, "service": "payments", "name": "GET /authorize", "start": 26.7, "end": 86.9}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "25b2116aae6cff55", "parent_id": "0942dc06bc69f265", "service": "payments", "name": "GET /receipt", "start": 88.3, "end": 98.4}
trace 85750621..: 3 span(s): gateway GET /checkout, orders GET /create, payments GET /receipt
trace 0e111600..: 1 span(s): payments GET /authorize
critical path: gateway GET /checkout self 7 ms | orders GET /create self 82 ms | payments GET /receipt self 10 ms
trace problems:
  2 trace ids for one request (a hop did not propagate traceparent)
  extra root span: payments GET /authorize started a new trace
exit: 0
```

### 15-solution
date: 2026-11-02T13:30Z
cwd: distributed-systems/labs/L300/15-distributed-tracing
cmd: python3 solution_tracing.py
```
spans (JSON lines, one per request):
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0942dc06bc69f265", "parent_id": null, "service": "gateway", "name": "GET /checkout", "start": 0.0, "end": 113.4}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "e9bb466a28738582", "parent_id": "0942dc06bc69f265", "service": "orders", "name": "GET /create", "start": 11.2, "end": 98.3}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "3d2bd371fc80be13", "parent_id": "e9bb466a28738582", "service": "payments", "name": "GET /authorize", "start": 35.0, "end": 97.8}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0e11160004524a7c", "parent_id": "0942dc06bc69f265", "service": "payments", "name": "GET /receipt", "start": 103.0, "end": 113.0}
trace 85750621..: 4 span(s): gateway GET /checkout, orders GET /create, payments GET /authorize, payments GET /receipt
critical path: gateway GET /checkout self 16 ms | orders GET /create self 24 ms | payments GET /authorize self 63 ms | payments GET /receipt self 10 ms
trace problems:
  none
exit: 0
```

### 15-tryit
date: 2026-11-02T13:30Z
cwd: distributed-systems/labs/L300/15-distributed-tracing
cmd: python3 try_it.py
```
tryIt 1: 00-4bf92f3577b34da6a... -> gateway trace 4bf92f3577b3.., parent 00f067aa0ba902b7 | traces: 1
tryIt 1: 00-4BF92F3577B34DA6A... -> gateway trace 0e1116000452.., parent None | traces: 1
tryIt 1: 00-00000000000000000... -> gateway trace 77616364568c.., parent None | traces: 1
tryIt 2: authorize work 60 ms -> its span is 46% of the checkout, on the critical path: True
tryIt 2: authorize work 180 ms -> its span is 78% of the checkout, on the critical path: True
exit: 0
```

### 16-buildtask-mine
date: 2026-11-02T13:34Z
cwd: distributed-systems/labs/L300/16-backpressure-load-shedding
cmd: env BUILD_TARGET=mine python3 -m unittest test_build_task
```
F.FF
======================================================================
FAIL: test_goodput_beats_the_unbounded_queue (test_build_task.LoadShedding.test_goodput_beats_the_unbounded_queue)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/16-backpressure-load-shedding/test_build_task.py", line 30, in test_goodput_beats_the_unbounded_queue
    self.assertEqual(self.s["goodput"], self.s["ok"])  # every 200 arrives before the 1 s client timeout
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 3781 != 10686

======================================================================
FAIL: test_p99_stays_bounded_during_the_burst (test_build_task.LoadShedding.test_p99_stays_bounded_during_the_burst)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/16-backpressure-load-shedding/test_build_task.py", line 22, in test_p99_stays_bounded_during_the_burst
    self.assertLess(self.s["p99_ms"], 250)  # queue bound (~100 ms) + service time tail
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 4619.1 not less than 250

======================================================================
FAIL: test_sheds_with_retry_after_of_at_least_one_second (test_build_task.LoadShedding.test_sheds_with_retry_after_of_at_least_one_second)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L300/16-backpressure-load-shedding/test_build_task.py", line 26, in test_sheds_with_retry_after_of_at_least_one_second
    self.assertGreater(len(shed), 0)
AssertionError: 0 not greater than 0

----------------------------------------------------------------------
Ran 4 tests in 6.383s

FAILED (failures=3)
exit: 1
```

### 16-demo
date: 2026-11-02T13:33Z
cwd: distributed-systems/labs/L300/16-backpressure-load-shedding
cmd: python3 backpressure.py
```
capacity 400 requests/s (4 workers x 10 ms)
1) load sweep, 20 s each:  load  throughput/s  mean wait  p99
                         50%        193       0.8 ms   46.1 ms
                         80%        312       5.9 ms   59.3 ms
                         90%        352      14.1 ms   78.1 ms
                         95%        371      30.4 ms  204.6 ms
2) burst: 5 s at 60%, 10 s at 150%, 15 s at 60% - per-second metrics (JSON lines):
{"t": 3, "offered": 221, "ok": 221, "shed": 0, "p99_ms": 43}
{"t": 6, "offered": 589, "ok": 589, "shed": 0, "p99_ms": 812}
{"t": 9, "offered": 552, "ok": 552, "shed": 0, "p99_ms": 2317}
{"t": 12, "offered": 603, "ok": 603, "shed": 0, "p99_ms": 3733}
{"t": 15, "offered": 256, "ok": 256, "shed": 0, "p99_ms": 4689}
{"t": 18, "offered": 247, "ok": 247, "shed": 0, "p99_ms": 3507}
{"t": 21, "offered": 250, "ok": 250, "shed": 0, "p99_ms": 2307}
{"t": 24, "offered": 224, "ok": 224, "shed": 0, "p99_ms": 1279}
{"t": 27, "offered": 229, "ok": 229, "shed": 0, "p99_ms": 46}
summary: {"offered": 10686, "ok": 10686, "shed": 0, "throughput_per_s": 356, "mean_wait_ms": 1928.5, "p50_ms": 1840.8, "p99_ms": 4619.1, "goodput": 3781}
exit: 0
```

### 16-realtime-check
date: 2026-11-02T13:35Z
cwd: distributed-systems/labs/L300/16-backpressure-load-shedding
cmd: env LAB_PORT=18016 python3 serve_realtime.py --check
```
1200 requests at 120/s for 10 s (capacity 80/s, queue bound 8): {'200': 765, '503': 435, 'p99_ms': 197, '503_without_retry_after': 0}
exit: 0
```

### 16-solution
date: 2026-11-02T13:33Z
cwd: distributed-systems/labs/L300/16-backpressure-load-shedding
cmd: python3 solution_backpressure.py
```
capacity 400 requests/s (4 workers x 10 ms)
1) load sweep, 20 s each:  load  throughput/s  mean wait  p99
                         50%        193       0.8 ms   46.1 ms
                         80%        312       5.9 ms   59.3 ms
                         90%        352      14.1 ms   78.1 ms
                         95%        370      25.1 ms  127.6 ms
2) burst: 5 s at 60%, 10 s at 150%, 15 s at 60% - per-second metrics (JSON lines):
{"t": 3, "offered": 221, "ok": 221, "shed": 0, "p99_ms": 43}
{"t": 6, "offered": 589, "ok": 418, "shed": 171, "p99_ms": 138}
{"t": 9, "offered": 552, "ok": 377, "shed": 175, "p99_ms": 159}
{"t": 12, "offered": 603, "ok": 400, "shed": 203, "p99_ms": 167}
{"t": 15, "offered": 256, "ok": 256, "shed": 0, "p99_ms": 88}
{"t": 18, "offered": 247, "ok": 247, "shed": 0, "p99_ms": 54}
{"t": 21, "offered": 250, "ok": 250, "shed": 0, "p99_ms": 46}
{"t": 24, "offered": 224, "ok": 224, "shed": 0, "p99_ms": 46}
{"t": 27, "offered": 229, "ok": 229, "shed": 0, "p99_ms": 60}
summary: {"offered": 10686, "ok": 8779, "shed": 1907, "throughput_per_s": 293, "mean_wait_ms": 44.2, "p50_ms": 27.1, "p99_ms": 154.5, "goodput": 8779}
exit: 0
```

### 16-tryit
date: 2026-11-02T13:34Z
cwd: distributed-systems/labs/L300/16-backpressure-load-shedding
cmd: python3 try_it.py
```
tryIt 1: max_queue  10: p99   65.1 ms, shed 1939, ok 8747, goodput 8747
tryIt 1: max_queue  40: p99  154.5 ms, shed 1907, ok 8779, goodput 8779
tryIt 1: max_queue 400: p99 1115.2 ms, shed 1547, ok 9139, goodput 6710
tryIt 2: no client limit: 503s the server had to send 1907, rejected locally 0, ok 8779, p99 154.5 ms
tryIt 2: AIMD client limit: 503s the server had to send 23, rejected locally 1885, ok 8778, p99 151.6 ms, final limit 95.5
exit: 0
```

### 17-demo
date: 2026-11-02T13:39Z
cwd: distributed-systems/labs/L400/17-consistency-quorums
cmd: python3 quorum.py
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
exit: 0
```

### 17-fitness-mine
date: 2026-11-02T13:41Z
cwd: distributed-systems/labs/L400/17-consistency-quorums
cmd: env BUILD_TARGET=mine python3 -m unittest test_fitness
```
FFFFFFFF
======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=11)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.5, 'read_p99': 65.9, 'write_p99': 64.6, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 1, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=12)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.4, 'read_p99': 65.5, 'write_p99': 66.4, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 3, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=13)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.6, 'read_p99': 66.7, 'write_p99': 64.6, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 2, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=15)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.6, 'read_p99': 70.3, 'write_p99': 75.8, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 2, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=16)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.6, 'read_p99': 65.4, 'write_p99': 64.2, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 1, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=17)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.5, 'read_p99': 65.9, 'write_p99': 68.3, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 2, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=18)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.5, 'read_p99': 66.5, 'write_p99': 78.0, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 4, 'linearizable': False, 'avail_c_down_pct': 100.0}

======================================================================
FAIL: test_linearizable_fast_enough_and_survives_region_loss (test_fitness.ConfigStoreFitness.test_linearizable_fast_enough_and_survives_region_loss) (seed=20)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/17-consistency-quorums/test_fitness.py", line 20, in test_linearizable_fast_enough_and_survives_region_loss
    self.assertTrue(m["linearizable"], m)
AssertionError: False is not true : {'R': 2, 'W': 2, 'write_back': True, 'overlap': True, 'read_p50': 12.5, 'read_p99': 69.0, 'write_p99': 62.1, 'stale_pct': 0.0, 'stale_age_max': 0.0, 'ryw': 0, 'inversions': 2, 'linearizable': False, 'avail_c_down_pct': 100.0}

----------------------------------------------------------------------
Ran 1 test in 10.689s

FAILED (failures=8)
exit: 1
```

### 17-fitness-ref
date: 2026-11-02T13:40Z
cwd: distributed-systems/labs/L400/17-consistency-quorums
cmd: python3 -m unittest test_fitness
```
.
----------------------------------------------------------------------
Ran 1 test in 2.885s

OK
exit: 0
```

### 17-solution
date: 2026-11-02T13:39Z
cwd: distributed-systems/labs/L400/17-consistency-quorums
cmd: python3 solution_quorum.py
```
{"seed": 17, "run_ms": 10000.0, "replicas": "a@A b@B c@C (C = other region)"}
N R W wb R+W>N  read p50/p99 ms  write p99  stale% (max age ms)  ryw  inversions  linearizable  avail, C down
3 1 1 -  False      3.8/60.5        34.0  16.74 ( 86.9)        15        902  False         100.0%
3 1 2 -  False      3.8/60.4        64.5   7.89 ( 62.7)         1        790  False         100.0%
3 2 2 -  True      12.5/65.9        68.3    0.0 (  0.0)         0          2  False         100.0%
3 1 3 -  True       3.8/60.4       125.8    0.0 (  0.0)         0        401  False           0.0%
3 3 1 -  True      62.3/135.3       12.1    0.0 (  0.0)         0          0  True            0.0%
3 2 2 +  True      12.7/124.5       67.5    0.0 (  0.0)         0          0  True          100.0%
decide cart badge (shows a count): N=3 R=1 W=1
decide feature flag (writer sees own change): N=3 R=2 W=2
decide lock owner / config (linearizable): N=3 R=2 W=2 + read write-back
exit: 0
```

### 17-tryit
date: 2026-11-02T13:40Z
cwd: distributed-systems/labs/L400/17-consistency-quorums
cmd: python3 try_it.py
```
tryIt 1: TAIL_P=0.05: R=2 W=2 inversions=2 read p99=65.9 ms write p99=68.3 ms
tryIt 1: TAIL_P=0.00: R=2 W=2 inversions=0 read p99=62.4 ms write p99=17.9 ms
tryIt 2: R=1 W=1: reads 100.0% writes 100.0% answered
tryIt 2: R=1 W=2: reads 100.0% writes 0.0% answered
tryIt 2: R=2 W=2: reads 0.0% writes 0.0% answered
tryIt 2: R=1 W=3: reads 100.0% writes 0.0% answered
tryIt 2: R=3 W=1: reads 0.0% writes 100.0% answered
tryIt 2: R=2 W=2 +wb: reads 0.0% writes 0.0% answered
exit: 0
```

### 18-demo
date: 2026-11-02T13:44Z
cwd: distributed-systems/labs/L400/18-crdts-local-first
cmd: python3 crdts.py
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
exit: 0
```

### 18-fitness-mine
date: 2026-11-02T13:46Z
cwd: distributed-systems/labs/L400/18-crdts-local-first
cmd: env BUILD_TARGET=mine python3 -m unittest test_fitness
```
FFF.
======================================================================
FAIL: test_every_chosen_type_is_a_join (test_fitness.CRDTFitness.test_every_chosen_type_is_a_join) (cls='LWWRegister', seed=18)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/18-crdts-local-first/test_fitness.py", line 23, in test_every_chosen_type_is_a_join
    self.assertEqual(set(check_laws(cls, seed)["counts"].values()), {"500/500"})
AssertionError: Items in the first set but not the second:
'407/500'

======================================================================
FAIL: test_every_chosen_type_is_a_join (test_fitness.CRDTFitness.test_every_chosen_type_is_a_join) (cls='LWWRegister', seed=19)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/18-crdts-local-first/test_fitness.py", line 23, in test_every_chosen_type_is_a_join
    self.assertEqual(set(check_laws(cls, seed)["counts"].values()), {"500/500"})
AssertionError: Items in the first set but not the second:
'408/500'

======================================================================
FAIL: test_every_chosen_type_is_a_join (test_fitness.CRDTFitness.test_every_chosen_type_is_a_join) (cls='LWWRegister', seed=20)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/18-crdts-local-first/test_fitness.py", line 23, in test_every_chosen_type_is_a_join
    self.assertEqual(set(check_laws(cls, seed)["counts"].values()), {"500/500"})
AssertionError: Items in the first set but not the second:
'395/500'

----------------------------------------------------------------------
Ran 2 tests in 9.261s

FAILED (failures=3)
exit: 1
```

### 18-fitness-ref
date: 2026-11-02T13:45Z
cwd: distributed-systems/labs/L400/18-crdts-local-first
cmd: python3 -m unittest test_fitness
```
..
----------------------------------------------------------------------
Ran 2 tests in 6.079s

OK
exit: 0
```

### 18-solution
date: 2026-11-02T13:44Z
cwd: distributed-systems/labs/L400/18-crdts-local-first
cmd: python3 solution_crdts.py
```
1) phone+laptop: ['eggs', 'milk'] == ['eggs', 'milk']: True
2) merge laws and convergence over 500 seeded random histories per type:
   G-Counter     {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   PN-Counter    {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   OR-Set        {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
   LWW-Register  {"commutative": "500/500", "associative": "500/500", "idempotent": "500/500", "converged": "500/500"}
3) like-counter, truth 140: LWW number [79, 79, 79] (concurrent adds lost), PN-Counter [140, 140, 140]; sync bytes LWW 15, PN 76
exit: 0
```

### 18-tryit
date: 2026-11-02T13:45Z
cwd: distributed-systems/labs/L400/18-crdts-local-first
cmd: python3 try_it.py
```
tryIt 1: G-Counter with sum-merge: {'commutative': '500/500', 'associative': '500/500', 'idempotent': '7/500'}, converged 0/500
         idempotent fails after: r0.inc('r0', 1)
tryIt 2:   10 add/remove cycles -> value ['milk'], tombstones 10, state 311 bytes
tryIt 2:  100 add/remove cycles -> value ['milk'], tombstones 100, state 3012 bytes
tryIt 2: 1000 add/remove cycles -> value ['milk'], tombstones 1000, state 31813 bytes
exit: 0
```

### 19-demo
date: 2026-11-02T13:49Z
cwd: distributed-systems/labs/L400/19-multi-region
cmd: python3 multiregion.py
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
exit: 0
```

### 19-fitness-mine
date: 2026-11-02T13:51Z
cwd: distributed-systems/labs/L400/19-multi-region
cmd: env BUILD_TARGET=mine python3 -m unittest test_fitness
```
FFFFFFFFFF.
======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=19)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 16 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 16 acknowledged writes lost'

- ['RPO: 16 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=20)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 15 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 15 acknowledged writes lost'

- ['RPO: 15 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=21)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['us write p99 354.4 > 350.0 ms', 'RPO: 3 acknowledged writes lost'] != []

First list contains 2 additional elements.
First extra element 0:
'us write p99 354.4 > 350.0 ms'

- ['us write p99 354.4 > 350.0 ms', 'RPO: 3 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=22)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['us write p99 350.3 > 350.0 ms', 'RPO: 12 acknowledged writes lost'] != []

First list contains 2 additional elements.
First extra element 0:
'us write p99 350.3 > 350.0 ms'

- ['us write p99 350.3 > 350.0 ms', 'RPO: 12 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=23)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['us write p99 358.4 > 350.0 ms', 'RPO: 4 acknowledged writes lost'] != []

First list contains 2 additional elements.
First extra element 0:
'us write p99 358.4 > 350.0 ms'

- ['us write p99 358.4 > 350.0 ms', 'RPO: 4 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=24)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 7 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 7 acknowledged writes lost'

- ['RPO: 7 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=25)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['us write p99 362.6 > 350.0 ms', 'RPO: 10 acknowledged writes lost'] != []

First list contains 2 additional elements.
First extra element 0:
'us write p99 362.6 > 350.0 ms'

- ['us write p99 362.6 > 350.0 ms', 'RPO: 10 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=26)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 11 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 11 acknowledged writes lost'

- ['RPO: 11 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=27)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 10 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 10 acknowledged writes lost'

- ['RPO: 10 acknowledged writes lost']
+ []

======================================================================
FAIL: test_brief_holds_on_ten_seeds (test_fitness.MultiRegionFitness.test_brief_holds_on_ten_seeds) (seed=28)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/19-multi-region/test_fitness.py", line 19, in test_brief_holds_on_ten_seeds
    self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN, seed)), [])
AssertionError: Lists differ: ['RPO: 7 acknowledged writes lost'] != []

First list contains 1 additional elements.
First extra element 0:
'RPO: 7 acknowledged writes lost'

- ['RPO: 7 acknowledged writes lost']
+ []

----------------------------------------------------------------------
Ran 2 tests in 17.800s

FAILED (failures=10)
exit: 1
```

### 19-fitness-ref
date: 2026-11-02T13:50Z
cwd: distributed-systems/labs/L400/19-multi-region
cmd: python3 -m unittest test_fitness
```
..
----------------------------------------------------------------------
Ran 2 tests in 7.703s

OK
exit: 0
```

### 19-solution
date: 2026-11-02T13:50Z
cwd: distributed-systems/labs/L400/19-multi-region
cmd: python3 solution_multiregion.py
```
design               write p99 us / eu / ap ms   lag p99  conflicts  RPO lost  RTO ms  rejected
async@ap                346.0 /  265.3 /  102.3     266.6          0        16    1129       108
async@us                128.0 /  205.3 /  320.3     256.1          0        17    1142        72
sync-majority@us        310.9 /  354.9 /  445.8      95.9          0         0    1209        74
sync-majority@eu        304.6 /  267.8 /  341.7      67.9          0         0    1313        73
sync-majority@ap        497.2 /  450.1 /  354.5      38.4          0         0    1009       102
multi-leader            140.6 /  127.1 /  112.8     197.4        434         2      65         0
leaderless              203.9 /  147.1 /  221.9      34.2        409         0      65         0
deployed {'replication': 'sync-majority', 'leader': 'eu'}: violations none
place_leader('sync-majority') -> eu
exit: 0
```

### 19-tryit
date: 2026-11-02T13:50Z
cwd: distributed-systems/labs/L400/19-multi-region
cmd: python3 try_it.py
```
tryIt 1: us follower read: ~2 ms, stale by up to 12.4 ms (p99 lag); leader read: ~80 ms + jitter, current if the leader confirms it still leads (Raft section 8)
tryIt 1: ap follower read: ~2 ms, stale by up to 103.6 ms (p99 lag); leader read: ~140 ms + jitter, current if the leader confirms it still leads (Raft section 8)
tryIt 2: election timeout 1000-2000 ms -> RTO 1313 ms, 73 writes rejected during failover, RPO 0
tryIt 2: election timeout 150-300 ms -> RTO 278 ms, 21 writes rejected during failover, RPO 0
exit: 0
```

### 20-demo
date: 2026-11-02T13:53Z
cwd: distributed-systems/labs/L400/20-chaos-engineering
cmd: python3 chaos.py
```
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 60, "experiment": "saga/shipping-outage", "experiment_harmed": 60, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 60, "experiment": "saga/crash-after-charge", "experiment_harmed": 60, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 0, "experiment": "saga/shipping-outage", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
{"aborted": false, "blast_radius_pct": 100.0, "control_harmed": null, "customers_hurt": 0, "experiment": "saga/crash-after-charge", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
experiment              target          hypothesis held   customers hurt by the experiment
saga/shipping-outage    L300 lesson       0/1   runs           60
saga/crash-after-charge L300 lesson       0/1   runs           60
saga/shipping-outage    L300 hardened     1/1   runs            0
saga/crash-after-charge L300 hardened     1/1   runs            0
raft/random-crash       L300 lesson      20/20  runs            0
raft/rolling-restart    L300 lesson      19/20  runs            0
raft/random-crash       L300 hardened    20/20  runs            0
raft/rolling-restart    L300 hardened    20/20  runs            0
exit: 0
```

### 20-fitness-mine
date: 2026-11-02T13:56Z
cwd: distributed-systems/labs/L400/20-chaos-engineering
cmd: env BUILD_TARGET=mine python3 -m unittest test_fitness
```
FFFF.
======================================================================
FAIL: test_experiments_are_bounded (test_fitness.ChaosFitness.test_experiments_are_bounded) (target='L300 lesson', fault='shipping-outage')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/20-chaos-engineering/test_fitness.py", line 22, in test_experiments_are_bounded
    self.assertLessEqual(r["blast_radius_pct"], 10.0)
AssertionError: 100.0 not less than or equal to 10.0

======================================================================
FAIL: test_experiments_are_bounded (test_fitness.ChaosFitness.test_experiments_are_bounded) (target='L300 lesson', fault='crash-after-charge')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/20-chaos-engineering/test_fitness.py", line 22, in test_experiments_are_bounded
    self.assertLessEqual(r["blast_radius_pct"], 10.0)
AssertionError: 100.0 not less than or equal to 10.0

======================================================================
FAIL: test_experiments_are_bounded (test_fitness.ChaosFitness.test_experiments_are_bounded) (target='L300 hardened', fault='shipping-outage')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/20-chaos-engineering/test_fitness.py", line 22, in test_experiments_are_bounded
    self.assertLessEqual(r["blast_radius_pct"], 10.0)
AssertionError: 100.0 not less than or equal to 10.0

======================================================================
FAIL: test_experiments_are_bounded (test_fitness.ChaosFitness.test_experiments_are_bounded) (target='L300 hardened', fault='crash-after-charge')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/20-chaos-engineering/test_fitness.py", line 22, in test_experiments_are_bounded
    self.assertLessEqual(r["blast_radius_pct"], 10.0)
AssertionError: 100.0 not less than or equal to 10.0

----------------------------------------------------------------------
Ran 2 tests in 18.437s

FAILED (failures=4)
exit: 1
```

### 20-fitness-ref
date: 2026-11-02T13:56Z
cwd: distributed-systems/labs/L400/20-chaos-engineering
cmd: python3 -m unittest test_fitness
```
..
----------------------------------------------------------------------
Ran 2 tests in 3.930s

OK
exit: 0
```

### 20-solution
date: 2026-11-02T13:54Z
cwd: distributed-systems/labs/L400/20-chaos-engineering
cmd: python3 solution_chaos.py
```
{"aborted": true, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 1, "experiment": "saga/shipping-outage", "experiment_harmed": 1, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": true, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 1, "experiment": "saga/crash-after-charge", "experiment_harmed": 1, "held": false, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 lesson"}
{"aborted": false, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 0, "experiment": "saga/shipping-outage", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
{"aborted": false, "blast_radius_pct": 10.0, "control_harmed": 0, "customers_hurt": 0, "experiment": "saga/crash-after-charge", "experiment_harmed": 0, "held": true, "seed": 14, "steady_state": "harmed orders = 0", "target": "L300 hardened"}
experiment              target          hypothesis held   customers hurt by the experiment
saga/shipping-outage    L300 lesson       0/1   runs            1
saga/crash-after-charge L300 lesson       0/1   runs            1
saga/shipping-outage    L300 hardened     1/1   runs            0
saga/crash-after-charge L300 hardened     1/1   runs            0
raft/random-crash       L300 lesson      20/20  runs            0
raft/rolling-restart    L300 lesson      19/20  runs            0
raft/random-crash       L300 hardened    20/20  runs            0
raft/rolling-restart    L300 hardened    20/20  runs            0
exit: 0
```

### 20-tryit
date: 2026-11-02T13:55Z
cwd: distributed-systems/labs/L400/20-chaos-engineering
cmd: python3 try_it.py
```
tryIt 1: blast 10%, abort after 1 harmed order: customers hurt 1, hypothesis held False
tryIt 1: blast 10%, abort after never: customers hurt 6, hypothesis held False
tryIt 1: blast 50%, abort after never: customers hurt 30, hypothesis held False
tryIt 2: rolling restart, wait 0-4 ticks between nodes: L300 lesson Raft refuted in 1/20 seeds
tryIt 2: rolling restart, wait 20-30 ticks between nodes: L300 lesson Raft refuted in 0/20 seeds
exit: 0
```

### 21-buildtask-ref
date: 2026-11-02T14:01Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 -m unittest test_build_task
```
..
----------------------------------------------------------------------
Ran 2 tests in 0.034s

OK
exit: 0
```

### 21-demo
date: 2026-11-02T13:59Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 modelcheck.py
```
BFS: 4519 distinct states explored, invariant ElectionSafety violated
  1. n0 times out -> candidate, term 1
  2. n1 votes for n0 in term 1
  3. n0 becomes leader of term 1
  4. n2 times out -> candidate, term 1
  5. n1 restarts (votedFor forgotten)
  6. n1 votes for n2 in term 1
  7. n2 becomes leader of term 1
random simulation: bug hit in 16/1000 walks of <= 30 steps (shortest 8 steps)
exit: 0
```

### 21-fitness-mine
date: 2026-11-02T14:01Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: env BUILD_TARGET=mine python3 -m unittest test_fitness
```
.F
======================================================================
FAIL: test_protocol_has_no_reachable_violation (test_fitness.VerificationFitness.test_protocol_has_no_reachable_violation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/distributed-systems/labs/L400/21-verifying-correctness/test_fitness.py", line 20, in test_protocol_has_no_reachable_violation
    self.assertIsNone(violated, trace)
AssertionError: 'ElectionSafety' is not None : ['n0 times out -> candidate, term 1', 'n1 votes for n0 in term 1', 'n0 becomes leader of term 1', 'n2 times out -> candidate, term 1', 'n1 restarts (votedFor forgotten)', 'n1 votes for n2 in term 1', 'n2 becomes leader of term 1']

----------------------------------------------------------------------
Ran 2 tests in 0.552s

FAILED (failures=1)
exit: 1
```

### 21-fitness-ref
date: 2026-11-02T14:01Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 -m unittest test_fitness
```
..
----------------------------------------------------------------------
Ran 2 tests in 10.287s

OK
exit: 0
```

### 21-lincheck
date: 2026-11-02T13:59Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 lincheck.py
```
1) Porcupine README histories: True, False (README says true, false)
2) lab 17 R=2 W=2 write-back=False: 2273 ops, linearizable False, 48590 steps, 63 ms
   longest partial linearization 433 ops; cannot place r6 read -> 28 [1738.9, 1799.6] ms
2) lab 17 R=2 W=2 write-back=True: 1947 ops, linearizable True, 2890 steps, 45 ms
exit: 0
```

### 21-solution
date: 2026-11-02T13:59Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 solution_modelcheck.py
```
BFS: 1853 distinct states explored, invariant none violated
random simulation: bug hit in 0/1000 walks of <= 30 steps (shortest - steps)
exit: 0
```

### 21-tryit
date: 2026-11-02T14:00Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 try_it.py
```
tryIt 1:  11 ops: memoised False in 0.37 ms, exhaustive (L300) False in 30.1 ms
tryIt 1:  26 ops: memoised False in 0.27 ms, exhaustive (L300) False in 227.3 ms
tryIt 1:  41 ops: memoised False in 4.49 ms, exhaustive (L300) False in 203.5 ms
tryIt 2: MAX_TERM=2: 1853 distinct states, 59 ms, violation: none
tryIt 2: MAX_TERM=3: 29221 distinct states, 946 ms, violation: none
exit: 0
```

### 21-vote-once
date: 2026-11-02T14:01Z
cwd: distributed-systems/labs/L400/21-verifying-correctness
cmd: python3 -c 
import solution_modelcheck as s
s.PERSIST_VOTE = False
r = s.bfs()
print(r)
```
('VoteOnce', ['n0 times out -> candidate, term 1', 'n1 times out -> candidate, term 1', 'n0 restarts (votedFor forgotten)', 'n0 votes for n1 in term 1'], 513, 3)
exit: 0
```

### 22-explain
date: 2026-11-02T14:05Z
cwd: distributed-systems/labs/L400/22-capstone
cmd: python3 run_capstone.py --explain --fake
```
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 56, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 90, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 80, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 48}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 43}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 43}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 108, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 48}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 118, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 43}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 104, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 43}
{"criterion": "money invariant (audit)", "measure": "passes in 27/27 runs (baseline: 0 violations)", "pass": true}
{"criterion": "no lost orders", "measure": "passes in 27/27 runs (baseline: 60/60 final)", "pass": true}
{"criterion": "one order and one charge per key", "measure": "passes in 27/27 runs (baseline: max created 1, max charges 1)", "pass": true}
{"criterion": "exactly-once effects", "measure": "passes in 27/27 runs (baseline: max emails per event 1, revenue mismatches 0)", "pass": true}
{"criterion": "outbox delivered", "measure": "passes in 27/27 runs (baseline: 180 events, 180 publishes)", "pass": true}
{"criterion": "one trace per order", "measure": "passes in 27/27 runs (baseline: split 0, orphans 0, bad headers 0)", "pass": true}
{"criterion": "bounded queue", "measure": "passes in 27/27 runs (baseline: over bound 0, p99 wait 2 ticks)", "pass": true}
{"criterion": "config via Raft", "measure": "passes in 27/27 runs (baseline: safety violations 0, committed versions [2])", "pass": true}
{"criterion": "chaos hypotheses held", "measure": "27/27 experiments", "pass": true}
{"criterion": "blast radius of order faults", "measure": "max 10.0% (limit 10%)", "pass": true}
{"scorecard": "10/10", "pass": true}
agent check baseline            agent: ('yes', 0) code: ('yes', 0) OK
agent check shipping-outage     agent: ('yes', 0) code: ('yes', 0) OK
agent check crash-after-charge  agent: ('yes', 0) code: ('yes', 0) OK
agent check relay-crash         agent: ('no', 0) code: ('yes', 0) WRONG
agent check bus-duplicates      agent: ('yes', 0) code: ('yes', 0) OK
agent check lost-acks           agent: ('yes', 0) code: ('yes', 0) OK
agent check burst               agent: ('yes', 3) code: ('yes', 0) WRONG
agent check raft-leader-crash   agent: ('yes', 0) code: ('yes', 0) OK
agent check everything          agent: ('yes', 0) code: ('yes', 0) OK
agent summary (number OK): idempotent consumers absorbed 586 duplicate deliveries; the relay crash is the weak spot.
agent verdict IGNORED (code decides): PASS - safe to release
exit: 0
```

### 22-pipeline
date: 2026-11-02T14:03Z
cwd: distributed-systems/labs/L400/22-capstone
cmd: python3 pipeline.py
```
ticks 33, sagas {'completed': 60}, events published 180, delivered 360, spans 660, config {'version': 2, 'max_queue': 12}, audit: OK
exit: 0
```

### 22-scorecard
date: 2026-11-02T14:04Z
cwd: distributed-systems/labs/L400/22-capstone
cmd: python3 run_capstone.py
```
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "baseline", "failed": [], "faults": [], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "shipping-outage", "failed": [], "faults": ["shipping-outage"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 0, "experiment": "crash-after-charge", "failed": [], "faults": ["crash-after-charge"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 10, "experiment": "relay-crash", "failed": [], "faults": ["relay-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 56, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 90, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 80, "experiment": "bus-duplicates", "failed": [], "faults": ["bus-duplicates"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 33}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "lost-acks", "failed": [], "faults": ["lost-acks"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 32}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "burst", "failed": [], "faults": ["burst"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 38}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 48}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 43}
{"blast_radius_pct": null, "compensated": 0, "duplicates_absorbed": 0, "experiment": "raft-leader-crash", "failed": [], "faults": ["raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 43}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 108, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 22, "ticks": 48}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 118, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 23, "ticks": 43}
{"blast_radius_pct": 10.0, "compensated": 6, "duplicates_absorbed": 104, "experiment": "everything", "failed": [], "faults": ["shipping-outage", "crash-after-charge", "relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash"], "harmed_orders": 0, "held": true, "hypothesis": "all 8 checks hold", "seed": 24, "ticks": 43}
{"criterion": "money invariant (audit)", "measure": "passes in 27/27 runs (baseline: 0 violations)", "pass": true}
{"criterion": "no lost orders", "measure": "passes in 27/27 runs (baseline: 60/60 final)", "pass": true}
{"criterion": "one order and one charge per key", "measure": "passes in 27/27 runs (baseline: max created 1, max charges 1)", "pass": true}
{"criterion": "exactly-once effects", "measure": "passes in 27/27 runs (baseline: max emails per event 1, revenue mismatches 0)", "pass": true}
{"criterion": "outbox delivered", "measure": "passes in 27/27 runs (baseline: 180 events, 180 publishes)", "pass": true}
{"criterion": "one trace per order", "measure": "passes in 27/27 runs (baseline: split 0, orphans 0, bad headers 0)", "pass": true}
{"criterion": "bounded queue", "measure": "passes in 27/27 runs (baseline: over bound 0, p99 wait 2 ticks)", "pass": true}
{"criterion": "config via Raft", "measure": "passes in 27/27 runs (baseline: safety violations 0, committed versions [2])", "pass": true}
{"criterion": "chaos hypotheses held", "measure": "27/27 experiments", "pass": true}
{"criterion": "blast radius of order faults", "measure": "max 10.0% (limit 10%)", "pass": true}
{"scorecard": "10/10", "pass": true}
exit: 0
```

### 22-tryit
date: 2026-11-02T14:05Z
cwd: distributed-systems/labs/L400/22-capstone
cmd: python3 try_it.py
```
tryIt 1: consumers without dedupe, bus-duplicates: failed checks {'exactly-once effects': 'max emails per event 2, revenue mismatches 14'}
tryIt 2: gateway without idempotency keys, lost-acks: failed checks {'one order and one charge per key': 'max created 2, max charges 1', 'exactly-once effects': 'max emails per event 2, revenue mismatches 0'}
exit: 0
```

### 23-clock
date: 2026-11-02T14:08Z
cwd: distributed-systems/labs/L500/23-system-models-time
cmd: python3 clocks_proofs.py clock
```
T23.1 Lamport clock condition: 300 random executions, 3 processes, 54,600 ordered event pairs
  pairs with a->b: 13,599; violations of L(a) < L(b): 0
  (L, pid) total order: duplicate keys 0; a->b ordered the other way 0
  converse fails: 11,063 of 27,402 concurrent pairs still have L(a) < L(b)
  broken receive rule (tick only, no max): 990 violations
exit: 0
```

### 23-detector
date: 2026-11-02T14:09Z
cwd: distributed-systems/labs/L500/23-system-models-time
cmd: python3 clocks_proofs.py detector
```
T23.4 failure detection: round-trip heartbeat, live peer, 200,000 heartbeats each
  asynchronous model (Pareto alpha=1.5, min 1 ms, no upper bound): timeout -> false suspicions
        5 ms -> 17,960 (8.9800%); theory 8.9443%
       20 ms ->  2,180 (1.0900%); theory 1.1180%
      100 ms ->    194 (0.0970%); theory 0.1000%
     1000 ms ->      5 (0.0025%); theory 0.0032%
  synchronous model (one-way <= 50 ms, processing <= 5 ms): timeout 105 ms -> 0 false suspicions; max observed 104.4 ms
exit: 0
```

### 23-safety
date: 2026-11-02T14:08Z
cwd: distributed-systems/labs/L500/23-system-models-time
cmd: python3 clocks_proofs.py safety
```
T23.3 safety vs liveness: all 9,841 traces over {req, resp, idle} up to length 8
  safety S = 'never more responses than requests': 3,292 good traces, 6,549 bad
  S prefix-closed: good traces with a bad prefix = 0
  bad traces repaired by any extension up to length 3: 0
  liveness L = 'every request eventually answered': good prefixes that cannot be completed = 0
exit: 0
```

### 23-vector
date: 2026-11-02T14:08Z
cwd: distributed-systems/labs/L500/23-system-models-time
cmd: python3 clocks_proofs.py vector
```
T23.2 vector clocks: same 300 executions, 54,600 ordered pairs
  mismatches between a->b and V(a) < V(b): 0
  concurrent pairs 27,402; incomparable vectors 27,402
  broken receive rule (no element-wise max): 4,546 mismatches
exit: 0
```

### 24-cap
date: 2026-11-02T14:10Z
cwd: distributed-systems/labs/L500/24-impossibility-consensus
cmd: python3 consensus_proofs.py cap
```
T24.3 CAP: partition {n1} | {n2}, all messages between the groups lost; write v1 @n1, then read @n2
  AP-local               ok                               read -> v0                                   available=True linearizable=False
  AP-sync-then-timeout   ok                               read -> v0                                   available=True linearizable=False
  CP-majority            no response (needs 2 of 3 acks)  read -> no response (needs 2 of 3 replies)   available=False linearizable=True
exit: 0
```

### 24-flp
date: 2026-11-02T14:10Z
cwd: distributed-systems/labs/L500/24-impossibility-consensus
cmd: python3 consensus_proofs.py flp
```
T24.2 FLP illustrated: 2 proposers, 3 acceptors, adversarial schedule for 1000 rounds
  ballots started 2000, accepts issued 2000, acceptances 0, values chosen 0 (safe, never live)
  with random backoff U[0, 4) after a clash (a timing assumption): 10,000 runs, all decided: True, mean attempts 4.35, max 37
exit: 0
```

### 24-generals
date: 2026-11-02T14:10Z
cwd: distributed-systems/labs/L500/24-impossibility-consensus
cmd: python3 consensus_proofs.py generals
```
T24.1 two generals: 140 protocols (M = 0..6 messengers, every threshold pair)
  protocols with a disagreeing or never-attacking run: 140; correct protocols: 0
  e.g. M=2, tA=1, tB=1: 1 delivered: A waits, B attacks
  e.g. M=6, tA=3, tB=3: 5 delivered: A waits, B attacks
exit: 0
```

### 24-paxos
date: 2026-11-02T14:10Z
cwd: distributed-systems/labs/L500/24-impossibility-consensus
cmd: python3 consensus_proofs.py paxos
```
T24.4 quorum intersection, exhaustive for N = 1..7, every (R, W):
  21,343 (read quorum, write quorum) pairs checked
  R + W > N with a disjoint pair: 0; R + W <= N configurations with a disjoint pair: 56 of 56
  correct single-decree Paxos     : 3000 random runs (loss 15%, dup 10%, reorder), decided 3000, runs with 2 values chosen 0, runs violating P2b 0
  broken (ignores phase-1 values): 3000 random runs (loss 15%, dup 10%, reorder), decided 3000, runs with 2 values chosen 2296, runs violating P2b 2498
exit: 0
```

### 25-little
date: 2026-11-02T14:11Z
cwd: distributed-systems/labs/L500/25-performance-theory
cmd: python3 perf_proofs.py little
```
T25.2 Little's law on a G/G/1 queue (uniform-jitter arrivals, log-normal service), seeded
  window [0, 124,978.064] starts and ends empty, 100,011 customers:
    area under n(t) = 163,913.199728; sum of sojourn times = 163,913.199728; relative difference 1.1e-15
    L = 1.311536; lambda * W = 0.800228 * 1.638952 = 1.311536
  arbitrary window [0, 124,966.47]: L = 1.3113, lambda * W (W truncated at the edge) = 1.3113
exit: 0
```

### 25-mm1
date: 2026-11-02T14:11Z
cwd: distributed-systems/labs/L500/25-performance-theory
cmd: python3 perf_proofs.py mm1
```
T25.1 M/M/1, mu = 1 per ms, 400,000 customers per load (seeded simulation vs closed form)
  rho=0.5: W sim  2.001 theory  2.000 | L sim  1.000 theory  1.000 | P(N=0) sim 0.501 theory 0.500 | P(N=2) sim 0.124 theory 0.125
  rho=0.8: W sim  4.992 theory  5.000 | L sim  3.990 theory  4.000 | P(N=0) sim 0.202 theory 0.200 | P(N=2) sim 0.129 theory 0.128
  rho=0.9: W sim  9.838 theory 10.000 | L sim  8.846 theory  9.000 | P(N=0) sim 0.103 theory 0.100 | P(N=2) sim 0.083 theory 0.081
exit: 0
```

### 25-tail
date: 2026-11-02T14:11Z
cwd: distributed-systems/labs/L500/25-performance-theory
cmd: python3 perf_proofs.py tail
```
T25.3 tail amplification: each leaf log-normal (median 10 ms), 'slow' = above the leaf p99 (64.3 ms); 100,000 root requests per fan-out
  fan-out   1: P(root waits for a slow leaf) sim 0.0095, 1 - 0.99^n = 0.0100
  fan-out  10: P(root waits for a slow leaf) sim 0.0954, 1 - 0.99^n = 0.0956
  fan-out 100: P(root waits for a slow leaf) sim 0.6329, 1 - 0.99^n = 0.6340
  to keep the root's p99 at the leaf-p99 level with fan-out 100, each leaf must meet its 0.999900 quantile (about p99.99)
exit: 0
```

### 25-usl
date: 2026-11-02T14:12Z
cwd: distributed-systems/labs/L500/25-performance-theory
cmd: python3 perf_proofs.py usl
```
T25.4 Amdahl and USL
  Amdahl sigma=0.05: S(2)=1.90, S(8)=5.93, S(16)=9.14, S(64)=15.42, S(1024)=19.64; bound 1/sigma = 20
  USL sigma=0.02, kappa=0.0005: p* formula 44.27, integer argmax 44, C(p*)=15.68
  USL sigma=0.1, kappa=0.001: p* formula 30.00, integer argmax 30, C(p*)=6.29
  USL sigma=0.03, kappa=0.0001: p* formula 98.49, integer argmax 98, C(p*)=20.16
  simulated closed system (p workers, think Exp(1), shared FIFO lock held 0.05 + 0.004(p-1)): C(1)=1.00, C(4)=3.99, C(8)=7.49, C(12)=9.97, C(16)=9.54, C(24)=7.40, C(32)=6.04, C(40)=5.10
  USL fit (sigma >= 0): sigma=0.0000, kappa=0.00429 -> predicted peak p*=15.3; measured peak at p=13 (C=10.17); throughput falls after the peak: C(40)/C(peak)=0.50
exit: 0
```

### 26-arithmetic
date: 2026-11-02T14:13Z
cwd: distributed-systems/labs/L500
cmd: python3 -c 
print('26-P1 99.95% of 30 days, minutes:', round((1-0.9995)*30*24*60, 2))
print('26-P2 outage minutes 07:30-14:22:', 14*60+22-(7*60+30), '; 99.99% yearly budget:', round((1-0.9999)*365*24*60, 2), '; ratio:', round((14*60+22-(7*60+30))/((1-0.9999)*365*24*60), 1))
print('26-P5 40 kW x PUE 1.4 x 8760 h, MWh:', round(40*1.4*8760/1000, 1), '; hot standby total MWh:', round(2*40*1.4*8760/1000, 1))

```
26-P1 99.95% of 30 days, minutes: 21.6
26-P2 outage minutes 07:30-14:22: 412 ; 99.99% yearly budget: 52.56 ; ratio: 7.8
26-P5 40 kW x PUE 1.4 x 8760 h, MWh: 490.6 ; hot standby total MWh: 981.1
exit: 0
```

### 27-arithmetic
date: 2026-11-02T14:14Z
cwd: distributed-systems/labs/L500
cmd: python3 -c 
N=5; print('27-P1 messages 3(N-1) for N=5:', 3*(N-1))
d,k,tau,xi=3,1e-6,1.0,0.001; e=d*(2*k*tau+xi); print('27-P4 epsilon ms:', round(e*1000,3), '; drift term ms:', round(d*2*k*tau*1000,3))
print('27-P5 majority of 5:', 5//2+1, '; tolerated failures:', 5-(5//2+1))

```
27-P1 messages 3(N-1) for N=5: 12
27-P4 epsilon ms: 3.006 ; drift term ms: 0.006
27-P5 majority of 5: 3 ; tolerated failures: 2
exit: 0
```
