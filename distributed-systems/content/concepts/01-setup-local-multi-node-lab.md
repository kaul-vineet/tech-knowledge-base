## Why it matters
You want to watch a timeout fire or a retry double-charge, but you have one laptop. If every "service" lives in one process, nothing can fail on its own, so nothing you learn transfers to real systems.

## Mental model
Each Python process is a separate office: its own memory, its own phone number (port), reachable only by calling. `lab.py` is the building manager who opens the offices, rings each one, and closes them.

```
lab.py ─spawn─▶ node1 :8001 ◀─ GET /health ─▶ 200 {"node": "node1", ...}
       ─spawn─▶ node2 :8002
       ─spawn─▶ node3 :8003        stop = SIGTERM to each PID
```

## How it works
1. **Process = node, port = address.** `subprocess.Popen([sys.executable, "node.py", ...])` starts a fresh interpreter that binds `127.0.0.1:<port>`; a second process cannot bind the same port. → see lab step 2
2. **Readiness by polling.** Start-up is asynchronous, so `start()` polls `GET /health` until every node answers (or a deadline passes) instead of sleeping a guessed time. `lab.py demo 3` uses ports `[8001, 8002, 8003]`. → see lab step 3
3. **Stop by PID.** `start` saves each PID to `.lab_nodes.json`; `stop` sends SIGTERM to each one, and its port is free again. → see lab step 4

## Common mistakes
- Sleeping a fixed time after start instead of polling a health endpoint.
- Binding `0.0.0.0` on a laptop and exposing the demo server to the network; only containers need it.
- Leaving orphan processes holding ports — always run `stop`.
